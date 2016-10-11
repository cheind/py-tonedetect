
import json
import itertools
import math
import numpy as np

class Tones(object):
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

    def minimum_frequency_step(self):
        dists = [math.fabs(pair[0]-pair[1]) for pair in itertools.combinations(self.all_tone_frequencies(), 2)]
        return np.min(dists)

    @staticmethod
    def from_json_file(filename):
        t = Tones()
        with open(filename) as f: 
            t.items = json.load(f)
        return t
