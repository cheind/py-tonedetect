
import numpy as np

class fft_detector(object):
    """ Detect frequencies in sampled signals """

    def __init__(self, frequencies, amp_threshold=0.1):
        self.frequencies = np.atleast_1d(frequencies)
        self.threshold = amp_threshold

    def fft(self, wnd):
        norm = (2 / wnd.size) * wnd.windowing_function_normalizer
        return norm * np.abs(np.fft.fft(wnd.windowing_function * wnd.samples))

    def f2b(self, fres, f):
        """ Frequency to frequency bin conversion """
        return f / fres

    def detect(self, wnd):
        y = self.fft(wnd)
        fres = wnd.frequency_resolution
        amp = lambda f: y[int(round(self.f2b(fres, f)))]
        return [amp(fb) >= self.threshold for fb in self.frequencies]


class tones(object):
    """ A list of tones """

    def __init__(self):
        self.items = []

    def add_tone(self, frequencies, sym=None):
        sym = sym if sym is not None else len(self.items)
        self.items.append({'f': frequencies, 'sym': sym})
    
    def all_tone_frequencies(self):
        """ Return a list of all frequencies across all tones """        
        f = []
        for e in self.items:
            f.extend(e['f'])
        return list(set(f))
    

class tone_detector(object):
    """ Detect the presence of multiple frequencies in sampled signals """

    def __init__(self, list_of_tones, min_presence_time = 0.070):
        self.tones = list_of_tones.items
        self.freqs = list_of_tones.all_tone_frequencies()
        self.tone_data = []
        for e in self.tones:
            self.tone_data.append({
                # The ids of frequencies that need to be present in window
                'ids': [self.freqs.index(f) for f in e['f']],
                # Accumulator counting the number of repetetive occurances of tone
                'acc': 0.,
                # Whether or not the tone still present has already been reported before.
                'reported': False
            })
        self.min_presence = min_presence_time


    def detect(self, wnd, current_frequencies):
        r = current_frequencies
        time_span = wnd.temporal_resolution / 2 # due to overlapping window shifts
        new_tones = []
        for i in range(len(self.tones)):
            data = self.tone_data[i]
            required_f = [r[id] for id in data['ids']]

            if np.all(required_f):
                data['acc'] =  data['acc'] + time_span
                if data['acc'] > self.min_presence and not data['reported']:
                    new_tones.append(self.tones[i]['sym'])
                    data['reported'] = True
            else:
                data['acc'] = 0.
                data['reported'] = False
                
        return new_tones






    