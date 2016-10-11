
import numpy as np
import math

class Window:
    def __init__(self, size, sample_rate):
        self.size = int(size)
        assert self.size % 2 == 0, "Even window size expected"
        self.sample_rate = sample_rate
        self.temporal_resolution = self.size / self.sample_rate
        self.frequency_resolution = self.sample_rate / self.size
        self.samples = np.zeros(self.size)
        self.shifts = 0
        self.idx = 0
        self.half_length = int(self.size / 2)
        self.windowing_function = np.hanning(self.size)
        self.windowing_function_normalizer = 2.0 # Hanning function has average of 0.5

    @staticmethod
    def estimate_size(sample_rate, frequencies, frequency_resolution = 1000):
        frequencies = np.atleast_1d(frequencies)
        lowest_frequency = np.min(frequencies)
        # We require 3 times the sample rate of the lowest frequency
        ws_f = int(math.ceil(3 * sample_rate / lowest_frequency)) 
        # To calculate the window size given a frequency resolution we use
        #   fr = sr / ws => ws = sr / fr
        ws_r = (int)(math.ceil(sample_rate / frequency_resolution))
        # Then take the max of both and make it even
        ws = max(ws_f, ws_r)
        return ws if ws % 2 == 0 else ws + 1


    def generate_windows(self, sample_generator):
        for part in sample_generator:
            yield from self.populate_window(part)

    def populate_window(self, samples):
        """ Update by adding new samples. Invokes callback for every full window encountered. """
        nsamples = len(samples)
        idx = 0
        while nsamples > 0:
            nleft = self.size - self.idx
            nconsume = min(nleft, nsamples)
            self.samples[self.idx : self.idx + nconsume] = samples[idx : idx + nconsume]
            self.idx += nconsume
            idx += nconsume
            nsamples -= nconsume
            if self.idx == self.size:
                # Invoke callback and shift window
                yield self
                self.samples[:self.half_length] = self.samples[self.half_length:]
                self.idx = self.half_length
                self.shifts += 1

    def temporal_position(self):
        half_res = self.temporal_resolution / 2
        return half_res + self.shifts * half_res  