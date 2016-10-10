
import numpy as np
import math
from sys import float_info
import matplotlib.pyplot as plt

fs = 200.0 # Hz sampling frequency
t = np.arange(0.0, 20, 1/fs)
f = 3.0 # Frequency of signal in Hz
A = 100.0 # Amplitude in Unit
s = A * np.sin(2*np.pi*f*t)

plt.figure(1)
plt.title("Signal")
plt.xlabel("Time ($s$)")
plt.ylabel("Amplitude ($Unit$)")
plt.plot(t, s)

# FFT part


N = int(len(s) / 2)
hann = np.hanning(len(s))
norm = (4. / len(s)) # Normalization of amplitude using Hanning window
y = norm * np.abs(np.fft.fft(hann * s))

# Convert FFT bins to frequencies so we get real frequencies for x-labels
xlabel = np.linspace(0, fs/2, N, endpoint=True)

# Convert 

plt.figure(2)
plt.title("FFT")
plt.xlabel("Frequency ($Hz$)")
plt.plot(xlabel, y[:N], "r+")

plt.show()




