
import math
import numpy as np
from enum import Enum

class WindowingFunction:
    """ Encapsulates a windowing function for a given window size."""
    
    class Type(Enum):
        """ Types of available windowing functions """
        rectangle = 0
        hanning = 1

    def __init__(self, n, wndtype=Type.rectangle):
        self.type = type

        if wndtype == WindowingFunction.Type.rectangle:
            self.values = np.full(n, 1.)
        elif wndtype == WindowingFunction.Type.hanning:
            self.values = np.hanning(n)

        self.normalizer = 1. / np.average(self.values)

class Window:

    def __init__(self, nsamples, npads, sample_rate, wndfnc=None):        
        self.nsamples = int(nsamples)
        self.npads = int(npads)
        self.ntotal = nsamples + npads
        assert self.nsamples % 2 == 0, "Even window size expected"
        
        self.sample_rate = sample_rate
        self.temporal_resolution = self.nsamples / self.sample_rate
        self.frequency_resolution = self.sample_rate / self.nsamples
        self.fft_resolution = self.sample_rate / self.ntotal
        self.values = np.zeros(self.ntotal)

        self.shifts = 0
        self.idx = 0
        self.nsamples_half = int(nsamples / 2)
        self.windowing_function = wndfnc if wndfnc is not None else WindowingFunction(self.nsamples)
        
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


    def update(self, data):
        if isinstance(data, (list, tuple, np.ndarray)):
            yield from self.update_with_samples(data)
        else:
            for part in data:
                yield from self.update(part)

    def update_with_samples(self, samples):
        """ Update by adding new samples. Invokes callback for every full window encountered. """
        nsamples = len(samples)
        idx = 0
        while nsamples > 0:
            nleft = self.nsamples - self.idx
            nconsume = min(nleft, nsamples)
            self.values[self.idx : self.idx + nconsume] = samples[idx : idx + nconsume]
            self.idx += nconsume
            idx += nconsume
            nsamples -= nconsume
            if self.idx == self.nsamples:
                # Invoke callback and shift window
                yield self
                self.values[:self.nsamples_half] = self.values[self.nsamples_half:self.nsamples]
                self.idx = self.nsamples_half
                self.shifts += 1

    def temporal_position(self):
        """ Returns the position of the window in the data stream.
            Position is specified as window's center position.
        """
        half_res = self.temporal_resolution / 2
        return half_res + self.shifts * half_res

    def temporal_span(self):
        """Returns the temporal span of this window."""
        pos = self.temporal_position()
        half_res = self.temporal_resolution / 2
        return [pos - half_res, pos + half_res]
        