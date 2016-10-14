
from tonedetect import normalization as norm
import numpy as np

def test_bit_depth_range_normalization():
    d = norm.normalize_audio_by_bit_depth(np.asarray([0, 255], dtype=np.uint8))
    np.testing.assert_allclose(d, [-1, 1], atol=0.01)

    d = norm.normalize_audio_by_bit_depth(np.asarray([-128, 0, 127], dtype=np.int8))
    np.testing.assert_allclose(d, [-1, 0, 1], atol=0.01)

def test_value_range_normalization():
    d = norm.normalize_audio_by_value_range(np.asarray([0, 1000], dtype='float32'))
    np.testing.assert_allclose(d, [-1, 1], atol=0.01)