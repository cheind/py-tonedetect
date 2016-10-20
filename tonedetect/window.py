
import math
import numpy as np
import itertools
import logging
from enum import Enum
from sys import float_info

logger = logging.getLogger(__name__)

class Window:
    """A window capturing discrete parts of a time domain signal.

    Each window holds list of data samples and additional zero samples for padding.
    Once enough samples have been provided, the window will yield itself allowing for 
    any postprocessing on the current values before the window will shift by an amount
    corresponding to 50 percent overlap.

    Windows additionally hold a window function that can be used reduce the effects of
    truncated time signals when applying the FFT.

    Args: 
        nsamples (int): Number of data samples. Even numbers required
        sample_rate (float): Number of samples per second (Hz)

    Kwargs:
        npads (int): Number of zero paddings
        wndtype (Window.Type): Type of window function to provide
        dtype: Data type of sample values

    """

    class Type(Enum):
        """Types of available window functions.

        See https://en.wikipedia.org/wiki/Window_function for an overview.
        """

        rectangle = 0 
        """Box-like window shape."""
        
        hanning = 1   
        """Von Hanning window shape."""

    def __init__(self, nsamples, sample_rate, npads=0, wndtype=Type.rectangle, dtype=np.float_):        
        
        assert nsamples % 2 == 0, "Even window size expected"

        self.nsamples = int(nsamples)
        """Number of data samples."""
        
        self.npads = int(npads)
        """Number of zero padding elements."""

        self.ntotal = nsamples + npads
        """Total number of elements."""

        self.sample_rate = sample_rate
        """Sample rate in Hz."""

        self.temporal_resolution = self.nsamples / self.sample_rate
        """Temporal span of window in seconds."""

        self.frequency_resolution = self.sample_rate / self.nsamples
        """Frequency resolution in Hz without data paddding."""

        self.fft_resolution = self.sample_rate / self.ntotal
        """Frequency resolution in Hz including data padding."""
        
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
        """Returns the window function values and the data normalizer.

        Note:
            Although the length of the window function corresponds to the total number of data elements
            (including padding), the number of elements used to compute the window function is nsamples.
            Similar things hold for the normalizer.
        """
        return self._wndfnc, self._wndfnc_norm

    @property
    def values(self):
        """Returns the list of data elements including zero padding elements."""
        return self._values

    @property
    def samples(self):
        """Returns the list of data elements excluding zero padding elements."""
        return self._values[:self.nsamples]

    @property
    def temporal_center(self):
        """ Returns the center position of the window in seconds."""
        return self._half_temp_res + self._shifts * self._half_temp_res

    @property
    def temporal_range(self):
        """Returns the temporal span of this window in terms of two timepoints.

        Returns:
            Array of start and end timepoints measured in seconds. Start is inclusive, end is exclusive.
        """
        pos = self.temporal_center
        return [pos - self._half_temp_res, pos + self._half_temp_res]
            
    def update(self, data):
        """Update with samples.

        Args:
            data (list, generator): Data is either an array of samples or a generator function that returns one.
        """
        if isinstance(data, (list, tuple, np.ndarray)):
            yield from self.update_with_samples(data)
        else:
            for part in data:
                yield from self.update(part)

    def update_with_samples(self, samples):
        """ Update by adding new samples and yield for every full window.

        Yields:
            self: The next full Window.

        """
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
        """ Tunes a window settings for the given parameters.

        Args:
            sample_rate (float): Sample rate of signal in Hz
            freqs (list): List of target frequencies in Hz.
        
        Kwargs:
            min_fres (float): When given the minimum frequency resolution between two frequency bins only considering data samples.
                              When not specified, it is automatically calculated as the minimum frequency step / 2 from target frequencies
            power_of_2 (bool): Whether or not the size of the returned window should be a power of 2. 
            use_padding (bool): Whether or not to use zero padding (true) or data samples (false) to fill up to the next power of 2.
            wndtype (Window.Type): Which type of window function to use.
            dtype (Window.Type): Data type of data samples.
        """

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
