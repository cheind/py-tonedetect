import os 
import re
import itertools
import numpy as np
from tonedetect.tones import Tones
from tonedetect.window import Window
from tonedetect import helpers
from tonedetect import sources
from tonedetect import detectors

PROJ_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
TEST_SAMPLE_DIR = os.path.join(PROJ_PATH, "etc", "samples", "dtmf_test")
DTMF_TONES = Tones.from_json_file(os.path.join(PROJ_PATH, "etc", "dtmf.json"))

class InMemorySource(object):

    @staticmethod
    def generate_parts(data):
        yield data


def run(sample_rate, data, expected_string, min_expected_detections):
    freqs = DTMF_TONES.all_tone_frequencies()

    wnd = Window.tuned(sample_rate, freqs, power_of_2=True)

    d_f = detectors.FrequencyDetector(freqs, amp_threshold=0.1)
    d_t = detectors.ToneDetector(DTMF_TONES, min_presence=0.04, min_pause=0.04)
    d_s = detectors.ToneSequenceDetector(max_tone_interval=1, min_sequence_length=1)

    gen_parts = InMemorySource.generate_parts(data)
    gen_silence = sources.SilenceSource.generate_parts(1, sample_rate)
    gen_windows = wnd.update(itertools.chain(gen_parts, gen_silence))

    num_detections = 0
    expected_left = expected_string
    for full_window in gen_windows:
        cur_f = d_f.update(full_window) 
        cur_t = d_t.update(full_window, cur_f)
        cur_s, start, stop = d_s.update(full_window, cur_t)
        if len(cur_s) > 0:
            num_detections += 1
            detect_str = "".join([str(e) for e in cur_s])
            compare_str = expected_left[:len(detect_str)]
            assert detect_str == compare_str
            expected_left = expected_left[len(detect_str):]
    
    print("Success {} found. Took {} sub-part detections".format(expected_string, num_detections))
    assert num_detections >= min_expected_detections

def run_with_noiselevel(noise_std):
    print("Running DTMF tests with noise level {:.2f}".format(noise_std))
    print("*"*20)
    rf = r'([0-9A-DspPd]+)\.wav'
    for dirname, dirnames, filenames in os.walk(TEST_SAMPLE_DIR):
        for filename in filenames:
            path = os.path.join(dirname, filename) 
            m = re.match(rf, filename, re.M)
            if m:
                expected = m.group(1)
                expected = expected.replace('p', '#') # Hash
                expected = expected.replace('s', '*') # Star
                expected = expected.replace('P', '') # Long pause
                expected = expected.replace('d', '') # Short pause     
                sr, data = helpers.read_audio(path)
                noise = np.zeros(len(data)) if noise_std == 0. else np.random.normal(0., noise_std, len(data))
                data += noise
                print("Testing file {}".format(path))
                run(sr, data, expected, 1)
            else:
                print("Skipping file {}".format(path))


def test_dtmf_pipeline():     
    run_with_noiselevel(0.)
    run_with_noiselevel(0.1)
    