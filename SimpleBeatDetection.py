
import numpy


class SimpleBeatDetection: # Thanks http://stackoverflow.com/questions/12344951/detect-beat-and-play-wav-file-in-a-syncronised-manner
    # Modified by Ryan Smith
    """
    Simple beat detection algorithm from
    http://archive.gamedev.net/archive/reference/programming/features/beatdetection/index.html
    """
    def __init__(self, history=43, boolean=True):
        self.local_energy = numpy.zeros(history) # a simple ring buffer
        self.local_energy_index = 0 # the index of the oldest element
        self.boolean = boolean

    def detect_beat(self, signal):
        samples = [int(i * 32768) for i in signal]
        #samples = signal.astype(numpy.int) # make room for squares
        # optimized sum of squares, i.e faster version of (samples**2).sum()
        instant_energy = numpy.dot(samples, samples) / float(0xffffffff) # normalize

        local_energy_average = self.local_energy.mean()
        local_energy_variance = self.local_energy.var()

        beat_sensibility = (-0.0025714 * local_energy_variance) + 1.15142857
        beat = instant_energy > beat_sensibility * local_energy_average

        self.local_energy[self.local_energy_index] = instant_energy
        self.local_energy_index -= 1
        if self.local_energy_index < 0:
            self.local_energy_index = len(self.local_energy) - 1
        if self.boolean:
            return beat
        else:
            return self.local_energy_index
