
import numpy as np
from sys import float_info

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

    def update(self, wnd):
        y = self.fft(wnd)
        amp = lambda f: y[int(round(self.f2b(wnd.fft_resolution, f)))]
        return [amp(fb) >= self.threshold for fb in self.frequencies]


class TimepointAccumulator:
    """ Time accumulator """
    def __init__(self):
        self.reset()

    def copy(self):
        acc = TimepointAccumulator()
        acc.union([self.start, self.end])
        return acc 

    def reset(self):
        self.start = float_info.max
        self.end = -float_info.max
    
    def union(self, timepoints):
        self.start = min(self.start, timepoints[0])
        self.end = max(self.end, timepoints[1])

    @property
    def empty(self):
        return self.start is float_info.max

    @property
    def center(self):
        return (self.start + self.end) * 0.5 if not self.empty else 0.

    @property
    def timespan(self):
        return self.end - self.start if not self.empty else 0.   

    @property
    def range(self):
        return [self.start, self.end]
    
class ToneDetector:
    """ Detect the presence of multiple frequencies in sampled signals."""        

    def __init__(self, tones, min_presence=0.070, min_pause=0.070):
        self.tones = tones.items
        self.freqs = tones.all_tone_frequencies()
        self.min_presence = min_presence
        self.min_pause = min_pause
        self.tone_data = []
        for e in self.tones:
            self.tone_data.append({
                # The ids of frequencies that need to be present in window
                'ids': [self.freqs.index(f) for f in e['f']],
                # Accumulator for active tone state
                'on': TimepointAccumulator(),
                # Accumulator for muted tone state
                'off': TimepointAccumulator(),
                # Whether or not the tone still present has already been reported before.
                'reported': False
            })


    def update(self, wnd, current_frequencies):
        """ Returns the list of active tones given the state of frequencies currently present in signal."""
        r = current_frequencies
        tpoints = wnd.temporal_range
        new_tones = []
        for i in range(len(self.tones)):
            data = self.tone_data[i]
            acc_on = data['on']
            acc_off = data['off']
            reported = data['reported']
            
            required_f = [r[id] for id in data['ids']]
            if np.all(required_f):
                # All required frequencies for this tone are present
                acc_on.union(tpoints)
                if acc_on.timespan >= self.min_presence and not reported:
                    # Even if tone stays active, won't be reported again before at least min_pause time has passed.
                    new_tones.append(self.tones[i]['sym'])
                    data['reported'] = True 
                    acc_off.reset()
            else:
                # At least one required frequency is not present
                if reported:
                    acc_off.union(tpoints)
                    if acc_off.timespan >= self.min_pause:
                        data['reported'] = False
                        acc_on.reset()
                
        return new_tones

class ToneSequenceDetector(object):
    def __init__(self, max_tone_interval=1., min_sequence_length=2):
        self.max_tone_interval = max_tone_interval
        self.min_sequence_length = min_sequence_length
        self.last_tone = 0.
        self.sequence = []
        self.acc = TimepointAccumulator()
        
    def update(self, wnd, current_tones):
        s = []
        first, last = None, None

        pos = wnd.temporal_center
        delta = pos - self.last_tone
        
        if delta > self.max_tone_interval:
            # No tones detected in max inter tone interval, report what we have.
            if len(self.sequence) >= self.min_sequence_length:
                s.extend(self.sequence)
                first, last = self.acc.range                            
                self.sequence.clear()
                self.acc.reset()
        
        if len(current_tones) > 0:
            self.acc.union(wnd.temporal_range)
            self.sequence.extend(current_tones)
            self.last_tone = pos                        

        return s, first, last
    