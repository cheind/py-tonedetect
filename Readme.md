
## FFMPEG Source


## STDIN Source
"""
c:\dev\ffmpeg\ffmpeg.exe -i etc\samples\dtmf_test\100by100at8000Hz\0123456789PpsPABCD.wav -f s16le -acodec pcm_s16le -ar 8000 -ac 1 -loglevel error - | python -m examples.tone_collect stdin --tones etc\dtmf.json --sample-rate 8000
"""

"""
youtube-dl.exe https://www.youtube.com/watch?v=evp9WrWUooI -o - | c:\dev\ffmpeg\ffmpeg.exe -i pipe:0 -f s16le -acodec pcm_s16le -ar 44100 -ac 1 - | python -m examples.tone_collect stdin --tones etc\dtmf.json --sample-rate 44100 --source-type=int16
"""