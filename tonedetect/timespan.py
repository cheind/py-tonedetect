
from sys import float_info

class Timespan:
    """ A time span represented by two time points. """

    def __init__(self, start=0., end=0.):
        self.start = start
        self.end = end

    def copy(self):
        t = Timespan()
        t.union(self)
        return t

    def reset(self):
        self.start = 0.
        self.end = 0.

    @property
    def empty(self):
        return self.start == 0. and self.end == 0.
    
    def union(self, other):
        e = self.empty
        self.start = other.start if e else min(self.start, other.start)
        self.end = other.end if e else max(self.end, other.end)

    @property
    def center(self):
        return (self.start + self.end) * 0.5 

    @property
    def duration(self):
        return self.end - self.start