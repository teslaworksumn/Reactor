

class MyMath:

    def add(self, a, b):
        if type(a) == list:
            if type(b) == list:
                return [i + j for i,j in zip(a,b)]
            else:
                return [i + b for i in a]
        else:
            return a + b

    def pow(self, base, power):
        if type(base) == list:
            # ALL YOUR BASE ARE BELONG TO US!
            return [i ** power for i in base]
        else:
            return base ** power

    def scale(self, val, src, dst):
        # Thanks, Stackoverflow http://stackoverflow.com/a/4155197/1778122
        return ((val - src[0]) / (src[1]-src[0])) * (dst[1] - dst[0]) + dst[0]