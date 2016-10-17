
import numpy as np
import logging
import itertools

from tonedetect import detectors
from tonedetect.sources import SilenceSource
from tonedetect.tones import Tones
from tonedetect.window import Window

class DefaultDetectionPipeline:

    def __init__(self, source, tones, min_tone_amp=0.1, max_inter_tone_amp=0.1, min_presence=0.04, min_pause=0.04, max_tone_interval=1, min_sequence_length=1):
        self.tones = tones
        self.freqs = tones.all_tone_frequencies()

        self.wnd = Window.tuned(source.sample_rate, self.freqs, power_of_2=True)

        self.d_f = detectors.FrequencyDetector(self.freqs)
        self.d_t = detectors.ToneDetector(tones, min_tone_amp=min_tone_amp, max_inter_tone_amp=max_inter_tone_amp, min_presence=min_presence, min_pause=min_pause)
        self.d_s = detectors.ToneSequenceDetector(max_tone_interval=max_tone_interval, min_sequence_length=min_sequence_length)

        silence = SilenceSource(max_tone_interval*2, source.sample_rate)
        self.gen_windows = self.wnd.update(itertools.chain(source.generate_parts(), silence.generate_parts()))

    def read(self):
        yield from self.gen_windows

    def detect(self, w):
        cur_f = self.d_f.update(w) 
        cur_t = self.d_t.update(w, cur_f)
        return self.d_s.update(w, cur_t)