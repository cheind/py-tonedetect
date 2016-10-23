
import numpy as np
from sys import float_info
from tonedetect.timespan import Timespan

class FrequencyDetector(object):
    """Compute the discrete Fourier transform of a discrete time signal and return the amplitudes of specific frequencies."""

    def __init__(self, freqs):
        self.frequencies = np.atleast_1d(freqs)
        self.fft_values = None

    def fft(self, wnd):
        data = wnd.values
        f, wndnorm = wnd.window_function

        norm = (2 / len(data)) * wndnorm

        # Using real variant of the DFT as our input signal is purely real. 
        # The rfft method only computes the first half of the frequency spectrum (up to Nyquist frequency)
        # as by definition the second half will be a mirrored version of the first half for real valued signals,
        # expecting a runtime improvement by a factor of 2.
        
        self.fft_values = norm * np.abs(np.fft.rfft(f * data))
        return self.fft_values

    def f2b(self, fres, f):
        """Return floating point bin number for frequency."""
        return f / fres

    def update(self, wnd):
        """Update frequencies from values given in window."""
        y = self.fft(wnd)
        amp = lambda f: y[int(round(self.f2b(wnd.fft_resolution, f)))]
        amps = [amp(fb) for fb in self.frequencies]
        return amps
    
class ToneDetector:
    """ Detect the presence of multiple frequencies in sampled signals."""    

    class ToneData:
        pass    

    def __init__(self, tones, min_tone_amp=0.1, max_inter_tone_amp=0.1, min_presence=0.070, min_pause=0.070):
        self.freqs = tones.all_tone_frequencies()
        self.min_presence = min_presence
        self.min_pause = min_pause
        self.min_tone_amp = min_tone_amp
        self.max_inter_tone_amp = max_inter_tone_amp
        self.tones = []
        for e in tones.items:
            t = ToneDetector.ToneData()
            t.ids = [self.freqs.index(f) for f in e["f"]]
            t.sym = e["sym"]
            t.on = Timespan()
            t.off = Timespan()
            t.reported = False
            self.tones.append(t)


    def update(self, wnd, amps):
        """ Returns the list of active tones given the state of frequencies currently present in signal."""        
        tspan = wnd.timespan
        new_tones = []
        for t in self.tones:
            
            tone_amps = [amps[id] for id in t.ids]
            tone_amp_active = [a >= self.min_tone_amp for a in tone_amps]
            tone_amp_range = abs(np.max(tone_amps) - np.min(tone_amps))
            if np.all(tone_amp_active) and tone_amp_range <= self.max_inter_tone_amp:
                #print("{} - {}".format([amps[id] for id in data['ids']], self.tones[i]['sym']))
                # All required frequencies for this tone are present
                t.on.union(tspan)
                if t.on.duration >= self.min_presence and not t.reported:
                    # Even if tone stays active, won't be reported again before at least min_pause time has passed.
                    new_tones.append(t.sym)
                    t.reported = True
                    t.off.reset()
            else:
                # At least one required frequency is not present
                if t.reported:
                    t.off.union(tspan)
                    if t.off.duration >= self.min_pause:
                        t.reported = False
                        t.on.reset()
                
        return new_tones

class ToneSequenceDetector(object):
    def __init__(self, max_tone_interval=1., min_sequence_length=2):
        self.max_tone_interval = max_tone_interval
        self.min_sequence_length = min_sequence_length
        self.sequence = []
        self.acc = Timespan()
        
    def update(self, wnd, current_tones):
        result_seq = None
        result_tspan = None

        tspan = wnd.timespan
        delta = tspan.start - self.acc.end
        
        if delta > self.max_tone_interval:
            # No tones detected in max inter tone interval, report what we have.
            if len(self.sequence) >= self.min_sequence_length:
                result_seq = []
                result_seq.extend(self.sequence)
                result_tspan = self.acc.copy()                       
                
            # In any case we need to clear sequences and reset accumulator.
            self.sequence.clear()
            self.acc.reset()
        
        if len(current_tones) > 0:
            self.acc.union(wnd.timespan)
            self.sequence.extend(current_tones)                       

        return result_seq, result_tspan
    