
import numpy as np
from tonedetect import helpers
from collections import deque
from os import path

class RingBuffer:
    def __init__(self, maxitems):
        self.buffer = deque(maxlen=maxitems)

    def add(self, data):
        self.buffer.extend(data)
    
    def get(self):
        return np.array(list(self.buffer))

class AudioBuffer(RingBuffer):
    
    def __init__(self, sample_rate, duration):
        self.sample_rate = sample_rate    
        len = int(sample_rate * duration)
        super().__init__(len)
    
    def write_audio(self, directory, prefix):
        fp = path.join(directory, str(prefix) + ".wav")
        helpers.write_audio(fp, self.sample_rate, self.get())
    
class NoopAudioBuffer:
    def __init__(self):
        pass

    def add(self, data):
        pass
    
    def write_audio(self, directory, prefix):
        pass