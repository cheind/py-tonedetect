
import subprocess as sp
import numpy as np
from tonedetect import helpers
from sys import stdin


class FFMPEGSource(object):  # pylint: disable=too-few-public-methods

    @staticmethod
    def generate_parts(source, ffmpeg_binary="ffmpeg", sample_rate=44100, part_length=1024):
        command = [
            ffmpeg_binary,
            '-i', source,
            '-loglevel', 'error',
            '-f', 's16le',
            '-acodec', 'pcm_s16le',
            '-ar', str(sample_rate),
            '-ac', '1',
            '-'
        ]

        proc = sp.Popen(command, stdout=sp.PIPE, shell=False)

        while True:
            data = proc.stdout.read(part_length)
            if not data:
                break
            audio = np.fromstring(data, dtype="int16")
            yield helpers.normalize_audio_by_bit_depth(audio)

class STDINSource(object):

    @staticmethod
    def generate_parts(part_length=1024, stype="int16"):
        while True:
            data = stdin.read(part_length)
            if not data:
                break
            audio = np.fromstring(data, stype)
            yield helpers.normalize_audio_by_bit_depth(audio)
            
class SilenceSource(object):
    """Generates silence for a desired duration. Useful to flush pending detector results once real input has ended."""
    
    @staticmethod
    def generate_parts(duration, sample_rate=44100):
        yield np.zeros(int(duration * sample_rate))

