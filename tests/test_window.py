from tonedetect import generators
from tonedetect import window
import numpy as np
import pytest

def test_window_properties():
    sf = 1000
    n = 100
    p = 10

    w = window.Window(n, p, sf)
    assert w.ntotal == 110
    assert w.frequency_resolution == sf / n
    assert w.fft_resolution == sf / 110
    assert w.shifts == 0
    assert w.sample_rate == sf
    assert w.idx == 0
    assert w.npads == p
    assert w.nsamples == n
    assert w.temporal_resolution == n / sf
    assert len(w.values) == w.ntotal

def test_window_shifts_correctly():

    sf = 10
    n = 4

    data = np.arange(0, 100, 1)    
    w = window.Window(n, 0, sf)
    
    gen = w.update(data)
    w = next(gen)
    assert w.temporal_position() == 0.2
    assert w.temporal_span() == [0., 0.4] 
    w = next(gen)
    assert w.temporal_position() == 0.4 
    np.testing.assert_allclose(w.temporal_span(), [0.2, 0.6]) 


def test_window_yields_correctly():
    data = np.arange(0, 10, 1)    
    w = window.Window(4, 2, 10)

    gen = w.update(data)
    np.testing.assert_allclose(next(gen).values, [0,1,2,3,0,0])
    np.testing.assert_allclose(next(gen).values, [2,3,4,5,0,0])
    np.testing.assert_allclose(next(gen).values, [4,5,6,7,0,0])
    np.testing.assert_allclose(next(gen).values, [6,7,8,9,0,0])
    with pytest.raises(StopIteration):
        next(gen)
