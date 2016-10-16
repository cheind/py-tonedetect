

import argparse
import numpy as np
import logging
import itertools
from datetime import datetime
import threading

from tonedetect import detectors
from tonedetect import sources
from tonedetect import helpers
from tonedetect import debug
from tonedetect.tones import Tones
from tonedetect.window import Window



logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="the source of audio. Can be a local file path or remote stream address.")
    parser.add_argument("--tones", help="the json file containing the tone description.", required=True)
    parser.add_argument("--samplerate", type=int, help="Desired sample rate of audio", default=44100)
    parser.add_argument("--ffmpeg", help="Path to FFMPEG executable.", default="ffmpeg")
    parser.add_argument("--buffersize", help="buffer size for process pipes", type=int, default=1024)

    return parser.parse_args()

def pretty_size(num, suffix='Bytes'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def pretty_date(time=False, suffix="ago"):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds" + suffix
        if second_diff < 120:
            return "a minute"
        if second_diff < 3600:
            return "{:.2f} minutes".format(second_diff / 60) + suffix
        if second_diff < 7200:
            return "an hour"
        if second_diff < 86400:
            return "{:.2f} hours".format(second_diff / 3600) + suffix
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days" + suffix
    if day_diff < 31:
        return str(day_diff / 7) + " weeks" + suffix
    if day_diff < 365:
        return str(day_diff / 30) + " months" + suffix
    return str(day_diff / 365) + " years" + suffix



status = {
    'sequences': [],
    'since': datetime.now(),
    'update': datetime.now()
}

def print_status():
    logger.info("Status: found {} sequences, running since: {}, last updated: {}".format(len(status['sequences']), pretty_date(status['since'], suffix=""), pretty_date(status['update'])))
    t = threading.Timer(10, print_status)
    t.daemon = True
    t.start()

def main():
    
    args = parse_args()

    tones = Tones.from_json_file(args.tones)
    freqs = tones.all_tone_frequencies()

    wnd = Window.tuned(args.samplerate, freqs, power_of_2=True)

    d_f = detectors.FrequencyDetector(freqs)
    d_t = detectors.ToneDetector(tones, min_tone_amp=0.1, max_inter_tone_amp=0.1, min_presence=0.04, min_pause=0.04)
    d_s = detectors.ToneSequenceDetector(max_tone_interval=1, min_sequence_length=1)

    gen_parts = sources.FFMPEGSource.generate_parts(
        args.source,
        ffmpeg_binary=args.ffmpeg,
        sample_rate=args.samplerate,
        part_length=args.buffersize)

    # Use the silence source to flush any pending tone detections.
    gen_silence = sources.SilenceSource.generate_parts(1, args.samplerate)    
    gen_windows = wnd.update(itertools.chain(gen_parts, gen_silence))

    print_status()
    for full_window in gen_windows:
        cur_f = d_f.update(full_window) 
        cur_t = d_t.update(full_window, cur_f)
        cur_s, start, stop = d_s.update(full_window, cur_t)
    
        if len(cur_s) > 0:
            logger.info("Sequence found! {} around {:.2f}-{:.2f}".format(cur_s, start, stop))
            status['sequences'].append(cur_s)

        status['update'] = datetime.now()
    

if __name__ == "__main__":
    main()
    