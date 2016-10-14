
import numpy as np


def normalize_audio_by_bit_depth(data, dtype='float64'):
    """Convert integral signal to [-1., 1.] using bit depth range of input type."""

    data = np.asarray(data)
    if data.dtype.kind not in 'iu':
        raise TypeError("Data needs to be integral type")

    dtype = np.dtype(dtype)
    if dtype.kind != 'f':
        raise TypeError("Destination type needs to be floating point type")

    i = np.iinfo(data.dtype)
    absolute_max = 2 ** (i.bits - 1)
    print(i.min)
    print(i.bits)
    offset = i.min + absolute_max
    return (data.astype(dtype) - offset) / absolute_max

def normalize_audio_by_value_range(data, dtype='float64'):
    """Convert integral or floating point signal to floating point with a range from -1 to 1."""

    data = np.asarray(data)
    if data.dtype.kind not in 'iuf':
        raise TypeError("Data needs to be either integral or floating type")

    dtype = np.dtype(dtype)
    if dtype.kind != 'f':
        raise TypeError("Destination type needs to be floating point type")

    data = data.astype(dtype)
    min_data = np.min(data)
    max_data = np.max(data)
    data_std = (data - min_data) / (max_data - min_data)

    new_max_value = 1.
    new_min_value = -1.
    return data_std * (new_max_value - new_min_value) + new_min_value
