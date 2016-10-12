import numpy as np
import scipy.io.wavfile 

def read_audio(filename):
    """ Read audio file """
    sr, d = scipy.io.wavfile.read(filename)
    return sr, np.asarray(d, dtype=np.float32)

def write_audio(filename, sample_rate, data):
    """ Write audio file """
    scaled = np.int16(data/np.max(np.abs(data)) * 32767)
    scipy.io.wavfile.write(filename, sample_rate, scaled)

def normalize(data, min_value = -1., max_value = 1.):
    """ Normalize audio data """
    data = np.asarray(data, dtype=np.float32)
    min_data = np.min(data)
    max_data = np.max(data)
    data_std = (data - min_data) / (max_data - min_data)
    data_scaled = data_std * (max_value - min_value) + min_value
    return data_scaled

def normalize_pcm16(data):
    range = 2**(data.itemsize*8)
    return data / range    