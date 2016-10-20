
import math
import numpy as np
import itertools
import logging
from enum import Enum
from sys import float_info

logger = logging.getLogger(__name__)

class Window:
    """A window capturing discrete parts of a time domain signal."""

    class Type(Enum):
        """Types of available window functions."""
        rectangle = 0
        hanning = 1 

    def __init__(self, nsamples, sample_rate, npads=0, wndtype=Type.rectangle, dtype=np.float_):        
        self.nsamples = int(nsamples)
        self.npads = int(npads)
        self.ntotal = nsamples + npads

        assert self.nsamples % 2 == 0, "Even window size expected"
        
        self.sample_rate = sample_rate
        self.temporal_resolution = self.nsamples / self.sample_rate
        self.frequency_resolution = self.sample_rate / self.nsamples
        self.fft_resolution = self.sample_rate / self.ntotal
        
        self._values = np.zeros(self.ntotal, dtype)
        self._shifts = 0
        self._idx = 0
        self._nsamples_half = int(nsamples / 2)
        self._half_temp_res = self.temporal_resolution / 2

        self._wndfnc = {
            Window.Type.rectangle: lambda: np.full(nsamples, 1, dtype=dtype),
            Window.Type.hanning: lambda: np.hanning(nsamples)
        }[wndtype]()

        self._wndfnc_norm = 1. / np.average(self._wndfnc)
        self._wndfnc = np.append(self._wndfnc, np.zeros(npads))

    @property
    def window_function(self):
        return self._wndfnc, self._wndfnc_norm

    @property
    def values(self):
        return self._values

    @property
    def samples(self):
        return self._values[:self.nsamples]

    @property
    def temporal_center(self):
        """ Returns the position of the window in the data stream.
            Position is specified as window's center position.
        """
        return self._half_temp_res + self._shifts * self._half_temp_res

    @property
    def temporal_range(self):
        """Returns the temporal span of this window in terms of two timepoints."""
        pos = self.temporal_center
        return [pos - self._half_temp_res, pos + self._half_temp_res]
            
    def update(self, data):
        if isinstance(data, (list, tuple, np.ndarray)):
            yield from self.update_with_samples(data)
        else:
            for part in data:
                yield from self.update(part)

    def update_with_samples(self, samples):
        """ Update by adding new samples. Invokes callback for every full window encountered. """
        nsamples_input = len(samples)
        idx_input = 0
        while nsamples_input > 0:
            nleft = self.nsamples - self._idx
            nconsume = min(nleft, nsamples_input)
            self._values[self._idx : self._idx + nconsume] = samples[idx_input : idx_input + nconsume]
            
            self._idx += nconsume
            idx_input += nconsume
            nsamples_input -= nconsume

            if self._idx == self.nsamples:
                # Invoke callback and shift window
                yield self
                self._values[:self._nsamples_half] = self._values[self._nsamples_half : self.nsamples]
                self._idx = self._nsamples_half
                self._shifts += 1
        
    @staticmethod
    def tuned(sample_rate, freqs, min_fres=None, power_of_2=False, use_padding=True, wndtype=Type.rectangle, dtype=np.float_):
        """ Return a window that is tuned for the given parameters. """        
        freqs = np.atleast_1d(freqs)        
        high_f = np.max(freqs)
        assert (sample_rate / 2) >= high_f, "Highest target frequency violates Nyquist sampling theorem."
        
        logger.info("Tuning window size for frequencies {}".format(", ".join([str(e) for e in freqs])))

        if min_fres is None:            
            if len(freqs) > 1:
                # Compute minimal pairwise absolute frequency diffs. 
                dists = [math.fabs(pair[0]-pair[1]) for pair in itertools.combinations(freqs, 2)]
                min_fres = np.min(dists) / 2 # Should give us 2 bins between target frequencies.
            else:
                min_fres = freqs[0] / 5 # For a single frequency we just use a fifth for spacing.
            logger.info("Minimum frequency resolution not specified. Set to {:.2f}Hz".format(min_fres))
        else:
            logger.info("Minimum frequency resolution given {:.2f}Hz".format(min_fres))

        # From f_res = 1 / T = fs / ws we can compute the required number of samples as        
        nsamples = int(math.ceil(sample_rate / min_fres))
        nsamples += nsamples % 2 
        
        ntotal = nsamples
        if power_of_2:
            # Find next power of 2
            ntotal = 2**((nsamples-1).bit_length())

        npad = 0
        if use_padding:
            npad = (ntotal - nsamples)
        else:
            nsamples = ntotal

        logger.info("Window tuned. Length {} ({} data, {} padding). Capture time of {:.5f}s".format(ntotal, nsamples, npad, nsamples / sample_rate))                   
        return Window(nsamples, sample_rate, npads=npad, wndtype=Window.Type.rectangle, dtype=dtype)
