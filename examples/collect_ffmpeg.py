

import argparse
import numpy as np
import logging

from tonedetect import detectors
from tonedetect.tones import Tones
from tonedetect.window import Window
from tonedetect.helpers import normalize_audio


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

def launch_ffmpeg(args):
    import subprocess as sp

    command = [
        args.ffmpeg,
        '-i', args.source,
        '-loglevel', 'panic',
        '-f', 's16le',
        '-acodec', 'pcm_s16le',
        '-ar', str(args.samplerate), 
        '-ac', '1',
        '-'
    ]

    return sp.Popen(command, stdout=sp.PIPE, shell=False)

def read_audio_parts(proc, length):
    while True:
        data = proc.stdout.read(length)
        if not data:
            break
        audio = np.fromstring(data, dtype="int16")
        audio_n = normalize_audio(audio)
        yield audio_n

def on_window_complete(w, d_f, d_t, d_s):
    cur_f = d_f.detect(w)
    cur_t = d_t.detect(w, cur_f)
    cur_s, start, stop = d_s.detect(w, cur_t)
    
    if len(cur_s) > 0:
        print("Found sequence {} in range {:.2f}-{:.2f}".format(cur_s, start, stop))

def main():
    

    args = parse_args()
    proc = launch_ffmpeg(args)

    tones = Tones.from_json_file(args.tones)
    
    all_freqs = tones.all_tone_frequencies()
    window_size = Window.estimate_size(args.samplerate, all_freqs, 20)
    logging.info("Tuning window size to %d", window_size)

    wnd = Window(window_size, args.samplerate)
    
    d_f = detectors.FrequencyDetector(all_freqs, amp_threshold=0.1)
    d_t = detectors.ToneDetector(tones, min_presence=0.070, min_pause=0.070)
    d_s = detectors.ToneSequenceDetector(max_tone_interval=1, min_sequence_length=2)

    numbered_parts = enumerate(read_audio_parts(proc, args.buffersize))
    for i, part in numbered_parts:
        wnd.update(part, on_window_complete, d_f, d_t, d_s)


if __name__ == "__main__":
    main()
    