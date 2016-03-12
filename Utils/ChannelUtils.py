
import math
import Utils.MyMath as MyMath
import numpy
import scipy.fftpack


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

    def fft(self, data, minmax=(0,255), length=None, samplerate=44100):
        # Primarially based on http://stackoverflow.com/questions/25735153/plotting-a-fast-fourier-transform-in-python,
        #  with the final data processing from http://julip.co/2012/05/arduino-python-soundlight-spectrum/
        if not data[0] == -1:
            N = len(data)
            # sample spacing
            T = 1.0 / samplerate
            fftbase = scipy.fftpack.fft(data)  # y
            fftaxis = numpy.linspace(0.0, 1.0 / (2.0 * T), N / 2)  # x
            #fftaxis = numpy.logspace(0.0, 1.0, N / 2) / (2.0 * T)  # x
            fft = 2.0 / N * numpy.abs(fftbase[1:N/2])
            size = len(fft)
            if length == None or size < length:
                return (fft, fftaxis)
            fftfinal = []
            stepsize = int(size / length)
            for i in range(0, size, stepsize):
                fftfinal += [(math.sqrt(max(fft[i:i + stepsize]) * 100) * 10) / 100]
            return (fftfinal[:length], fftaxis)
        else:
            if length == None:
                return ([0], [0])
            else:
                r = []
                for i in range(0, length):
                    r += [0]
                return (r, [0])
