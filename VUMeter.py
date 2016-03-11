
import numpy
import math


class VUMeter:
    def __init__(self,steps):
        self.steps = steps
    def calc_max(self,data):
        if data[0] == -1:
            return 0
        return max(numpy.absolute(data))
    def calc_avg(self,data):
        if data[0] == -1:
            return 0
        dl = math.floor(len(data)/4)
        m1 = max(numpy.absolute(data[0:dl]))
        m2 = max(numpy.absolute(data[dl:dl*2]))
        m3 = max(numpy.absolute(data[dl*2:dl*3]))
        m4 = max(numpy.absolute(data[dl*3:dl*4]))
        return numpy.average([m1,m2,m3,m4])