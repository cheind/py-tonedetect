
from tonedetect import normalization
import numpy as np

def test_integral_normalization():
    d = normalization.normalize_audio(np.asarray([0, 255], dtype='u8'))
    np.testing.assert_allclose(d, [-1, 1])

    d = normalization.normalize_audio(np.asarray([-128, 0, 127], dtype='i8'))
    np.testing.assert_allclose(d, [-1, 0, 1], atol=0.01)

def test_floating_normalization():
    d = normalization.normalize_audio(np.asarray([0, 1000], dtype='float32'))
    np.testing.assert_allclose(d, [-1, 1], atol=0.01)