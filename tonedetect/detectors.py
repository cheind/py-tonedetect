
import numpy as np

class FrequencyDetector(object):
    """ Detect frequencies in sampled signals."""

    def __init__(self, frequencies, amp_threshold=0.1):
        self.frequencies = np.atleast_1d(frequencies)
        self.threshold = amp_threshold
        self.fft_values = None

    def fft(self, wnd):
        norm = (2 / wnd.ntotal) * wnd.windowing_function.normalizer
        self.fft_values = norm * np.abs(np.fft.fft(wnd.windowing_function.values * wnd.values))
        return self.fft_values

    def f2b(self, fres, f):
        return f / fres

    def detect(self, wnd):
        y = self.fft(wnd)
        amp = lambda f: y[int(round(self.f2b(wnd.fft_resolution, f)))]
        return [amp(fb) >= self.threshold for fb in self.frequencies]
    
class ToneDetector(object):
    """ Detect the presence of multiple frequencies in sampled signals."""

    def __init__(self, tones, min_presence=0.070, min_pause=0.070):
        self.tones = tones.items
        self.freqs = tones.all_tone_frequencies()
        self.tone_data = []
        for e in self.tones:
            self.tone_data.append({
                # The ids of frequencies that need to be present in window
                'ids': [self.freqs.index(f) for f in e['f']],
                # Accumulator for active tone state
                'acc_on': 0.,
                # Accumulator for muted tone state
                'acc_off': 0.,
                # Whether or not the tone still present has already been reported before.
                'reported': False
            })
        self.min_presence = min_presence
        self.min_pause = min_pause


    def update(self, wnd, current_frequencies):
        """ Returns the list of active tones given the state of frequencies currently present in signal."""
        r = current_frequencies
        time_span = wnd.temporal_resolution / 2 # due to overlapping window shifts
        new_tones = []
        for i in range(len(self.tones)):
            data = self.tone_data[i]
            required_f = [r[id] for id in data['ids']]

            if np.all(required_f):
                # All required frequencies for this tone are present
                data['acc_on'] =  data['acc_on'] + time_span
                if data['acc_on'] > self.min_presence and not data['reported']:
                    # Even if tone stays active, won't be reported again before at least min_pause time has passed.
                    new_tones.append(self.tones[i]['sym'])
                    data['reported'] = True 
                    data['acc_off'] = 0.
            else:
                # At least one required frequency is not present
                if data['reported']:
                    data['acc_off'] =  data['acc_off'] + time_span
                    if data['acc_off'] > self.min_pause:
                        data['reported'] = False
                        data['acc_on'] = 0.
                
        return new_tones

class ToneSequenceDetector(object):
    def __init__(self, max_tone_interval=1., min_sequence_length=2):
        self.max_tone_interval = max_tone_interval
        self.min_sequence_length = min_sequence_length
        self.last_tone = 0.
        self.first_tone = 0.
        self.sequence = []

    def update(self, wnd, current_tones):
        s = []
        first, last = None, None

        pos = wnd.temporal_position()
        delta = pos - self.last_tone
        
        if delta > self.max_tone_interval:
            if len(self.sequence) >= self.min_sequence_length:
                s.extend(self.sequence)
                first = self.first_tone - wnd.temporal_resolution / 2
                last = self.last_tone + wnd.temporal_resolution / 2
                self.sequence.clear()
        
        if len(current_tones) > 0:
            self.first_tone = pos if len(self.sequence) == 0 else self.first_tone
            self.last_tone = pos
            self.sequence.extend(current_tones)            

        return s, first, last
    