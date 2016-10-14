

from tonedetect import generators
from tonedetect import debug
import numpy as np

def test_generate_time_samples():
    s = generators.generate_time_samples(8000, 1.5)
    assert len(s) == 12000
    np.testing.assert_allclose(s[1]-s[0], 1. / 8000)

def test_generate_signal():

    # sin(2 pi x)
    s = generators.generate_signal(8000, 1, 1, 1)
    np.testing.assert_allclose(s[[0, 1999, 7999]], [0, 1.0, 0], atol=0.01)

    # sin(2 pi x)+sin(4 pi x)
    # roots at n/2, n - 1/3, n+1/3 for every n in Z
    # min at -0.148958 + n with
    s = generators.generate_signal(8000, 1, [1,2], [1,1])
    zeros = [int(n * 8000) for n in (0.5, 2/3, 1/3)]
    np.testing.assert_allclose(s[zeros], 0, atol=0.01)

    min_at = int((-0.148958 + 1) * 8000)
    np.testing.assert_allclose(s[min_at], -1.760, atol=0.01)