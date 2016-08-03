
import Utils.MyMath as MyMath
import numpy


class ChannelUtils:
    def __init__(self):
        self.mymath = MyMath.MyMath()

    def int2range(self, val, val_range, num_channels, minmax=(0,255), soft=False):
        c = []
        if soft:
            q = minmax[1] - minmax[0]
            vr = (0, num_channels*q)
            rv = self.mymath.scale(val, val_range, vr)
            for i in range(0, num_channels):
                neg = q * i
                c += [int(rv - neg)]
            c = numpy.clip(c, minmax[0], minmax[1]).tolist()
        else:
            vr = (0, val_range[1] - val_range[0])
            rv = self.mymath.scale(val, val_range, vr)
            q = vr[1] / (num_channels + 1)
            for i in range(1, num_channels + 1):
                if rv >= q * i:
                    c += [minmax[1]]
                else:
                    c += [minmax[0]]
        return c

    def vuintensitybuckets(self, vupct, numbuckets, log=False, maxval=255):
        N = int(numbuckets)
        # Give the vu meter a boost
        vupct += 0.1

        bucketized = numpy.array([0] * N, dtype=float)
        if log:
            steps = numpy.logspace(0, 1, N + 1, endpoint=True) / 10
        else:
            steps = numpy.linspace(0, 1, N + 1, endpoint=True)

        # Fill buckets until not maxed out
        i = 0
        while i < N-1 and vupct > steps[i+1]:
            bucketized[i] = maxval
            i += 1
        # Fractionally fill last bucket
        remaining = vupct - steps[i]
        bucketized[i] = maxval * min(1, remaining / (steps[1] - steps[0]))

        return bucketized

    def bucketize(self, data, numbuckets, log):
        numbuckets = int(numbuckets)
#        numbuckets *= 2
        length = len(data)
        bucketized = numpy.array([0] * numbuckets, dtype=float)
        if length < numbuckets:
            for i in range(length):
                bucketized[i] = int(data[i])
        else:
            if log:
                steps = numpy.logspace(0, 1, numbuckets + 1, endpoint=True) / 10 * length
            else:
                steps = numpy.linspace(0, 1, numbuckets + 1, endpoint=True) * length
            for i in range(numbuckets):
                left = int(steps[i])
                right = int(steps[i+1])
                bucketized[i] = numpy.average(data[left:right])

        return bucketized
#       return bucketized[:len(bucketized) // 2]

    def fft(self, data, length, log=False, N=1024, samplerate=44100):
        length = length * 2  # Because it looks cooler
        # N is number of fft samples
        # T is time per sample
        T = 1.0 / samplerate
        # Compute the fft
        fft = numpy.fft.fft(data, n=N)
        # Ignore the second half since it is the first half mirrored
        # Also ignore the first bin, since it is unrelated info
        if len(fft) % 2 == 0:
            fft = numpy.split(fft, 2)[0]
            fft = fft[1:]
        else:
            fft = fft[1:]
            fft = numpy.split(fft, 2)[0]
        # Find the magnitudes of the complex frequencies
        fft = numpy.absolute(fft)
        # Average out into buckets of frequencies
        fft = self.bucketize(fft, length, log=log)
        # Return the fft
        return fft[:len(fft)//2] # See first comment
