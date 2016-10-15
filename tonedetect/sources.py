
import subprocess as sp
import numpy as np
from tonedetect import helpers

class FFMPEGSource(object):  # pylint: disable=too-few-public-methods

    @staticmethod
    def generate_parts(source, ffmpeg_binary="ffmpeg", sample_rate=44100, part_length=1024, eof_size=44100):
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
                if eof_size > 0:
                    yield np.zeros(eof_size)
                break
            audio = np.fromstring(data, dtype="int16")
            yield helpers.normalize_pcm16(audio)



