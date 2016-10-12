
import numpy as np

def normalize_audio(data, dtype='float64'):
    """Convert integral signal to floating point with a range from -1 to 1.

    Taken and adapted from https://github.com/mgeier/python-audi

    """

    data = np.asarray(data)
    if data.dtype.kind not in 'iuf':
        raise TypeError("Data needs to be either integral or floating type")

    dtype = np.dtype(dtype)
    if dtype.kind != 'f':
        raise TypeError("Destination type needs to be floating point type")

    if data.dtype.kind == 'ui':
        i = np.iinfo(data.dtype)
        abs_max = 2 ** (i.bits - 1)
        offset = i.min + abs_max
        return (data.astype(dtype) - offset) / abs_max
    else:
        min_data = np.min(data)
        max_data = np.max(data)
        data_std = (data - min_data) / (max_data - min_data)
        max_value = 1.
        min_value = -1.
        data_scaled = data_std * (max_value - min_value) + min_value
        return data_scaled.astype(dtype)