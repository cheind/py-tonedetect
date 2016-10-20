import numpy as np
import scipy.io.wavfile 
from datetime import datetime

def read_audio(filename):
    """ Read audio file """
    sr, d = scipy.io.wavfile.read(filename)
    return sr, normalize_audio_by_bit_depth(d)

def write_audio(filename, sample_rate, data):
    """ Write audio file """
    scaled = np.int16(data/np.max(np.abs(data)) * 32767)
    scipy.io.wavfile.write(filename, sample_rate, scaled)

def normalize_audio_by_bit_depth(data, dtype=np.float_):
    """Convert integral signal to [-1., 1.] using bit depth range of input type."""

    data = np.asarray(data)
    if data.dtype.kind not in 'iu':
        raise TypeError("Data needs to be integral type")

    dtype = np.dtype(dtype)
    if dtype.kind != 'f':
        raise TypeError("Destination type needs to be floating point type")

    i = np.iinfo(data.dtype)
    absolute_max = 2 ** (i.bits - 1)
    offset = i.min + absolute_max
    return (data.astype(dtype) - offset) / absolute_max

def normalize_audio_by_value_range(data, dtype=np.float_):
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


def pretty_size(num, suffix='Bytes'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def pretty_date(time=False, suffix="ago"):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds" + suffix
        if second_diff < 120:
            return "a minute"
        if second_diff < 3600:
            return "{:.2f} minutes".format(second_diff / 60) + suffix
        if second_diff < 7200:
            return "an hour"
        if second_diff < 86400:
            return "{:.2f} hours".format(second_diff / 3600) + suffix
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days" + suffix
    if day_diff < 31:
        return str(day_diff / 7) + " weeks" + suffix
    if day_diff < 365:
        return str(day_diff / 30) + " months" + suffix
    return str(day_diff / 365) + " years" + suffix