from tonedetect import generators

from tonedetect.window import Window
from tonedetect.detectors import FrequencyDetector
from tonedetect import detectors
import numpy as np


def test_frequency_detector_rectangle():
    sf = 1000
    d = 1
    freqs = [10., 20., 30.]
    amps = [0.5, 1., 2.]
    s = generators.generate_signal(sf, 1, freqs, amps)

    wnd = Window(1000, sf)
    fd = FrequencyDetector(freqs[0:2])
    
    w = next(wnd.update(s))
    result = fd.update(w)
    assert np.all([a >= 0.1 for a in result])

def test_frequency_detector_hanning():
    sf = 1000
    d = 1
    freqs = [10., 20., 30.]
    amps = [0.5, 1., 2.]
    s = generators.generate_signal(sf, 1, freqs, amps)

    wnd = Window(1000, sf, wndtype=Window.Type.hanning)
    fd = FrequencyDetector(freqs)
    
    w = next(wnd.update(s))
    result = fd.update(w)
    assert np.all([a >= 0.1 for a in result])

        
        


