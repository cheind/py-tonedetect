
import subprocess as sp
import numpy as np
import logging
from tonedetect import helpers
from sys import stdin, getsizeof
from urllib.parse import urlparse

import shutil
import os

logger = logging.getLogger(__name__)

class BaseSource(object):
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.bytes_processed = 0

class FFMPEGSource(BaseSource):  # pylint: disable=too-few-public-methods

    def __init__(self, source, ffmpeg_binary="ffmpeg", sample_rate=44100, chunk_size=1024, reconnect=None):
        super().__init__(sample_rate)

        self.ffmpeg = ffmpeg_binary
        if not os.path.isfile(ffmpeg_binary):
            self.ffmpeg = shutil.which(ffmpeg_binary)
            if self.ffmpeg is None:            
                raise FileNotFoundError("FFMPEG binary not found at {}".format(ffmpeg_binary))
        
        self.chunk_size = chunk_size
        self.command = [
            self.ffmpeg,
            "-i", source,
            "-loglevel", "error",
            "-f", "s16le",
            "-acodec", "pcm_s16le",
            "-ar", str(sample_rate),
            "-ac", "1"
        ]

        url = urlparse(source)
        if reconnect or url.scheme == "http" or url.scheme == "https":
            logger.info("Enabling stream reconnection")
            self.command.extend([
                "-reconnect", "1",
            ])

        self.command.append('-')

    def generate_parts(self):
        
        proc = sp.Popen(self.command, stdout=sp.PIPE, shell=False)

        while True:
            data = proc.stdout.read(self.chunk_size)
            if not data:
                break
            self.bytes_processed += getsizeof(data)
            audio = np.fromstring(data, dtype="int16")
            yield helpers.normalize_audio_by_bit_depth(audio)
            
class SilenceSource(BaseSource):
    """Generates silence for a desired duration. Useful to flush pending detector results once real input has ended."""

    def __init__(self, duration, sample_rate):
        super().__init__(sample_rate)
        self.duration = duration

    def generate_parts(self):
        zeros = np.zeros(int(self.duration * self.sample_rate), dtype=np.float_) 
        self.bytes_processed += zeros.nbytes
        yield zeros

class InMemorySource(BaseSource):

    def __init__(self, data, sample_rate):
        super().__init__(sample_rate)
        self.data = data

    def generate_parts(self):
        self.bytes_processed += self.data.nbytes
        yield self.data

class STDINSource(BaseSource):

    def __init__(self, sample_rate=44100, chunk_size=1024, source_type="int16"):
        super().__init__(sample_rate)
        self.chunk_size = chunk_size
        self.source_type = source_type

    def generate_parts(self):
        while True:
            data = stdin.buffer.read(self.chunk_size)
            if not data:
                break
            audio = np.fromstring(data, self.source_type)
            yield helpers.normalize_audio_by_bit_depth(audio)