
import matplotlib.pyplot as plt
import numpy as np

def plot_temporal_domain(samples, title="Signal"):
    plt.figure()
    plt.plot(samples)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Amplitude ($Unit$)")

def plot_frequency_domain(fft_data, sample_rate, title="Frequencies"):
    nyquist = int(len(fft_data) / 2)
    xlabels = np.linspace(0, sample_rate/2, nyquist, endpoint=True)
    plt.figure()
    plt.title(title)
    plt.xlabel("Frequency ($Hz$)")
    plt.ylabel("Amplitude ($Unit$)")
    plt.plot(xlabels, fft_data[:nyquist], marker='*')