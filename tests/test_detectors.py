from tonedetect import generators
from tonedetect import window
from tonedetect import debug
from tonedetect import detectors
import numpy as np


def test_frequency_detector():
    sf = 1000
    d = 1
    freqs = [10., 20., 30.]
    amps = [0.5, 1., 2.]
    s = generators.generate_signal(sf, 1, freqs, amps)

    wnd = window.Window(1000, 0, sf, window.WindowingFunction(1000))
    fd = detectors.FrequencyDetector(freqs[0:2], amp_threshold=0.1)
    
    w = next(wnd.update(s))
    result = fd.detect(w)
    assert np.all(result)

def test_frequency_detector():
    sf = 1000
    d = 1
    freqs = [10., 20., 30.]
    amps = [0.5, 1., 2.]
    s = generators.generate_signal(sf, 1, freqs, amps)

    wnd = window.Window(1000, 0, sf, window.WindowingFunction(1000, wndtype=window.WindowingFunction.Type.hanning))
    fd = detectors.FrequencyDetector(freqs, amp_threshold=0.1)
    
    w = next(wnd.update(s))
    result = fd.detect(w)
    assert np.all(result)

        
        


