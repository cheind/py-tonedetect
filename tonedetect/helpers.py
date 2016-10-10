import numpy as np
import scipy.io.wavfile 

def generate_time_samples(sample_rate, duration, start = 0):
    """ Returns time samples for a given duration and sample rate """
    return np.arange(start, start + duration, 1 / sample_rate)

def generate_signal(sample_rate, duration, frequencies, amplitudes, start = 0):
    """ Encodes a set of frequencies into a time signal """
    frequencies = np.atleast_1d(frequencies)
    amplitudes = np.atleast_1d(amplitudes)

    assert len(frequencies) == len(amplitudes), "Number of frequencies and amplitudes need to match"
    
    samples = generate_time_samples(sample_rate, duration, start)
    signal = np.zeros(len(samples))
    for f, a in zip(frequencies, amplitudes):
        signal += a * np.sin(2 * np.pi * f * samples)
    return signal, samples

def read_audio(filename):
    """ Read audio file """
    sr, d = scipy.io.wavfile.read(filename)
    return sr, np.asarray(d, dtype=np.float32)

def write_audio(filename, sample_rate, data):
    """ Write audio file """
    scaled = np.int16(data/np.max(np.abs(data)) * 32767)
    scipy.io.wavfile.write(filename, sample_rate, scaled)

def normalize_audio(data, min_value = -1., max_value = 1.):
    """ Normalize audio data """
    data = np.asarray(data, dtype=np.float32)
    min_data = np.min(data)
    max_data = np.max(data)
    data_std = (data - min_data) / (max_data - min_data)
    data_scaled = data_std * (max_value - min_value) + min_value
    return data_scaled

