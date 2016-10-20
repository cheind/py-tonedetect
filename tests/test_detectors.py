from tonedetect import generators
from tonedetect import window
from tonedetect import detectors
import numpy as np


def test_frequency_detector_rectangle():
    sf = 1000
    d = 1
    freqs = [10., 20., 30.]
    amps = [0.5, 1., 2.]
    s = generators.generate_signal(sf, 1, freqs, amps)

    wnd = window.Window(1000, 0, sf, window.WindowingFunction(1000, 0))
    fd = detectors.FrequencyDetector(freqs[0:2])
    
    w = next(wnd.update(s))
    result = fd.update(w)
    assert np.all([a >= 0.1 for a in result])

def test_frequency_detector_hanning():
    sf = 1000
    d = 1
    freqs = [10., 20., 30.]
    amps = [0.5, 1., 2.]
    s = generators.generate_signal(sf, 1, freqs, amps)

    wnd = window.Window(1000, 0, sf, window.WindowingFunction(1000, 0, wndtype=window.WindowingFunction.Type.hanning))
    fd = detectors.FrequencyDetector(freqs)
    
    w = next(wnd.update(s))
    result = fd.update(w)
    assert np.all([a >= 0.1 for a in result])

        
        


