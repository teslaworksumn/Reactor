
import numpy
import math


class VUMeter:
    def __init__(self):
        pass

    def calc_max(self,data):
        if data[0] == -1:
            return 0
        return self._get_max(data)

    def calc_avg(self,data):

        if len(data) == 0 or data[0] == -1:
            return 0

        dl = math.floor(len(data)/4)
        m1 = self._get_max(data[0:dl])
        m2 = self._get_max(data[dl:dl*2])
        m3 = self._get_max(data[dl*2:dl*3])
        m4 = self._get_max(data[dl*3:dl*4])
        return numpy.average([m1,m2,m3,m4])

    def _get_max(self, data):
        if len(data) == 0:
            return 0

        return max(numpy.absolute(data))
