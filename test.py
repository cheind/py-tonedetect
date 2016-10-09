
import helpers
import window
import detector

import numpy as np

sr, d = helpers.read_audio('etc/radio0.wav')
n = helpers.normalize(d)

tones = detector.tones()
tones.add_tone([770, 1209], 4)

freqs = tones.all_tone_frequencies()

ws = window.overlapping_window.estimate_size(sr, freqs, 20)
wnd = window.overlapping_window(ws, sr)

dt_low = detector.fft_detector(freqs)
dt_high = detector.tone_detector(tones)


def cb(w):
    f = dt_low.detect(w)
    tones = dt_high.detect(w, f)
    for t in tones: 
        print("Found tone {} at {}".format(t, w.temporal_position()))
