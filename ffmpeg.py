FFMPEG_BIN = "C:\\dev\\ffmpeg\\ffmpeg.exe"
#FILENAME = "C:\\dev\\phonenumber-collector\\etc\\radio0.wav"
FILENAME = "http://mp3stream7.apasf.apa.at:8000/"

import subprocess as sp

command = [FFMPEG_BIN,
        '-i', FILENAME,
        '-f', 's16le',
        '-acodec', 'pcm_s16le',
        '-ar', '8000', 
        '-ac', '1',
        '-']
pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)

raw_audio = pipe.stdout.read(10**4)

print("got something!")

import numpy
audio_array = numpy.fromstring(raw_audio, dtype="int16")

import matplotlib.pyplot as plt

plt.plot(audio_array)
plt.show()

#audio_array = audio_array.reshape((len(audio_array)/2,2))