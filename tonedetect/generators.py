
import numpy as np

def generate_time_samples(sample_rate, duration, start=0):
    """ Returns time samples for a given duration and sample rate """
    return np.arange(start, start + duration, 1 / sample_rate)

def generate_signal(sample_rate, duration, frequencies, amplitudes, start=0):
    """ Encodes a set of frequencies into a time signal """
    frequencies = np.atleast_1d(frequencies)
    amplitudes = np.atleast_1d(amplitudes)

    assert len(frequencies) == len(amplitudes), "Number of frequencies and amplitudes need to match"
    
    samples = generate_time_samples(sample_rate, duration, start)
    signal = np.zeros(len(samples))
    for f, a in zip(frequencies, amplitudes):
        signal += a * np.sin(2 * np.pi * f * samples)
    return signal, samples
    