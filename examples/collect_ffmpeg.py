

import argparse
import numpy as np
import logging

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

def main():
    
    args = parse_args()

    tones = Tones.from_json_file(args.tones)
    freqs = tones.all_tone_frequencies()

    wnd = Window.tuned(args.samplerate, freqs)

    d_f = detectors.FrequencyDetector(freqs, amp_threshold=0.1)
    d_t = detectors.ToneDetector(tones, min_presence=0.04, min_pause=0.04)
    d_s = detectors.ToneSequenceDetector(max_tone_interval=1, min_sequence_length=1)

    gen_parts = sources.FFMPEGSource.generate_parts(
        args.source,
        ffmpeg_binary=args.ffmpeg,
        sample_rate=args.samplerate,
        part_length=args.buffersize,
        eof_size=44100)

    gen_windows = wnd.update(gen_parts)

    for full_window in gen_windows:
        cur_f = d_f.update(full_window) 
        cur_t = d_t.update(full_window, cur_f)
        cur_s, start, stop = d_s.update(full_window, cur_t)
    
        if len(cur_s) > 0:
            logging.info("Sequence found! {} at {:.2f}-{:.2f}".format(cur_s, start, stop))
    

if __name__ == "__main__":
    main()
    