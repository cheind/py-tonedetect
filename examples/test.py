
import tonedetect as td

sr, d = td.helpers.read_audio('etc/radio0.wav')
n = td.helpers.normalize(d)

mytones = td.tones.tones.from_json_file('etc/dtmf.json')
freqs = mytones.all_tone_frequencies()

ws = td.window.overlapping_window.estimate_size(sr, freqs, 20)
wnd = td.window.overlapping_window(ws, sr)

d_f = td.detector.frequency_detector(freqs)
d_t = td.detector.tone_detector(mytones)
d_s = td.detector.tone_sequence_detector(max_tone_interval=0.5, min_sequence_length=1)

def cb(w):
    cur_f = d_f.detect(w)
    cur_t = d_t.detect(w, cur_f)
    cur_s, start, stop = d_s.detect(w, cur_t)
    if len(cur_s) > 0:
        print("Found sequence {} in range {:.2f}-{:.2f}".format(cur_s, start, stop))


# gstreamer pipeline d:\gstreamer\1.0\x86_64\bin\gst-launch-1.0.exe playbin uri=http://mp3stream7.apasf.apa.at:8000/