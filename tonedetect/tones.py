
import json

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

    @staticmethod
    def from_json_file(filename):
        t = Tones()
        with open(filename) as f: 
            t.items = json.load(f)
        return t
