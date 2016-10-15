
import math
import numpy as np
import itertools
import logging
from enum import Enum
from sys import float_info

logger = logging.getLogger(__name__)

class WindowingFunction:
    """ Encapsulates a windowing function for a given window size."""
    
    class Type(Enum):
        """ Types of available windowing functions """
        rectangle = 0
        hanning = 1

    def __init__(self, n, npads, wndtype=Type.rectangle):
        self.type = type

        if wndtype == WindowingFunction.Type.rectangle:
            self.values = np.full(n + npads, 1.)
        elif wndtype == WindowingFunction.Type.hanning:
            self.values = np.append(np.hanning(n), np.zeros(npads))

        self.normalizer = 1. / np.average(self.values[:n])

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
        self.sample_values = self.values[:self.nsamples]

        self.shifts = 0
        self.idx = 0
        self.nsamples_half = int(nsamples / 2)
        self.windowing_function = WindowingFunction(self.nsamples, self.npads) if wndfnc is None else wndfnc
        
    @staticmethod
    def tuned(sample_rate, freqs, min_fres=None, power_of_2=False, use_padding=True):
        """ Return a window that is tuned for the given parameters. """        
        freqs = np.atleast_1d(freqs)        
        high_f = np.max(freqs)
        assert (sample_rate / 2) >= high_f, "Highest target frequency violates Nyquist sampling theorem."
        
        logger.info("Tuning window size for frequencies {} in Hz".format(freqs))

        if min_fres is None:            
            if len(freqs) > 1:
                # Compute minimal pairwise absolute frequency diffs. 
                dists = [math.fabs(pair[0]-pair[1]) for pair in itertools.combinations(freqs, 2)]
                min_fres = np.min(dists) / 2 # Should give us 2 bins between target frequencies.
            else:
                min_fres = freqs[0] / 5 # For a single frequency we just use a fifth for spacing.
            logger.info("Minimum frequency resolution not specified. Auto tuned to {:.2f}Hz".format(min_fres))
        else:
            logger.info("Minimum frequency resolution given {:.2f}Hz".format(min_fres))

        # From f_res = 1 / T = fs / ws we can compute the required number of samples as        
        nsamples = int(math.ceil(sample_rate / min_fres))
        nsamples += nsamples % 2 
        logger.info("Minimum required number of samples {}".format(nsamples))

        ntotal = nsamples
        if power_of_2:
            # Find next power of 2
            ntotal = 2**((nsamples-1).bit_length())

        npad = 0
        if use_padding:
            npad = (ntotal - nsamples)
        else:
            nsamples = ntotal

        logger.info("Total number of data samples required {}, corresponding to capture time of {:.5f}s".format(nsamples, nsamples / sample_rate))   
        
        return Window(nsamples, npad, sample_rate)


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
        