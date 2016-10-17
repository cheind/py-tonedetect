
import numpy as np
import logging
import itertools

from tonedetect import detectors
from tonedetect import sources
from tonedetect.tones import Tones
from tonedetect.window import Window

logger = logging.getLogger(__name__)


class DefaultDetectionPipeline:

    def __init__(self, gen_parts, sample_rate, tones):
        self.tones = tones
        self.freqs = tones.all_tone_frequencies()

        self.wnd = Window.tuned(sample_rate, self.freqs, power_of_2=True)

        self.d_f = detectors.FrequencyDetector(self.freqs)
        self.d_t = detectors.ToneDetector(tones, min_tone_amp=0.1, max_inter_tone_amp=0.1, min_presence=0.04, min_pause=0.04)
        self.d_s = detectors.ToneSequenceDetector(max_tone_interval=1, min_sequence_length=1)

        self.gen_parts = gen_parts
        self.gen_silence = sources.SilenceSource.generate_parts(1, sample_rate)
        self.gen_windows = self.wnd.update(itertools.chain(self.gen_parts, self.gen_silence))

    def read(self):
        yield from self.gen_windows

    def detect(self, w):
        cur_f = self.d_f.update(w) 
        cur_t = self.d_t.update(w, cur_f)
        return self.d_s.update(w, cur_t)