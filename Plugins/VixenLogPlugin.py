
class VixenLogPlugin():
    prefix = " " * 30

    def __init__(self, filename = "/tmp/emcee_printer_output.txt", mode = "a"):
        # 1 in third argument indicates line-buffered output
        self.file = open(filename, mode, 1)

    def isopen(self):
        return self.file.closed == False

    def close(self):
        self.file.close()

    def send(self,channels=[]):
        hex_output = ' '.join('%02X'%c for c in channels)
        output = VixenLogPlugin.prefix + hex_output + '\n'
        self.file.write(output)
        #print(channels)

    def recieve(self):
        raise ValueError("VixenLogPlugin can't receieve")
