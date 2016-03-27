import yaml

class ConfigParser:
    def __init__(self, fname):
        self.numchannels = 0
        self.numfftchannels = 0
        self.numvuchannels = 0
        self.gain = 1
        self.fftN = 1024
        self._channeltypes = []
        self.fftlog = False
        self.vulog = False
        self.setconfig(fname)

    def getdatatosend(self, fftdata, vudata):
        datatosend = [0] * self.numchannels
        fftidx = 0
        vuidx = 0
        for i in range(self.numchannels):
            dtype = self._channeltypes[i]
            if dtype == 'fft':
                datatosend[i] = fftdata[fftidx]
                fftidx = (fftidx + 1) % len(fftdata)
            elif dtype == 'vu':
                datatosend[i] = vudata[vuidx]
                vuidx = (vuidx + 1) % len(vudata)
        return datatosend

    def setconfig(self, filename):

        # Reset variables
        self.numfftchannels = 0
        self.numvuchannels = 0

        # Load from file
        config = yaml.load(open(filename, 'r').read())

        # Validate
        # Sets values
        if not self._checkvalid(config):
            print("Invalid configuration file loaded")

    # Validates the configuration @config
    # Also sets values
    def _checkvalid(self, config):
        if config is None:
            return False

        keys = config.keys()

        # Check for numeric types
        if 'numchannels' not in keys or 'audiogain' not in keys or 'fftN' not in keys:
            print("Missing 'numvusteps', 'numchannels', 'fftN', or 'audiogain' key")
            return False

        channels = config['numchannels']
        audiogain = config['audiogain']
        N = config['fftN']

        try:
            self.numchannels = int(channels)
            self.gain = float(audiogain)
            self.fftN = int(N)
        except TypeError:
            print("numchannels or fftN is not an integer, or audiogain is not a float")
            return False

        # Check for booleans
        if 'fftlog' not in keys or 'vulog' not in keys:
            print("Missing 'fftlog' or 'vulog' key")
            return False

        self.fftlog = config['fftlog'] in ['y', 'Y', 'yes', 'Yes']
        self.vulog = config['vulog'] in ['y', 'Y', 'yes', 'Yes']

        # Set size of _channeltypes
        self._channeltypes = ['none'] * self.numchannels

        valid = True
        # Each channel has its own key
        # Each value should be 'fft', 'vu', or 'none'
        for i in range(self.numchannels):
            if i not in keys:
                print("Missing key '", i, "' from config file", sep='')
                valid = False
            elif config[i] not in ['fft', 'vu', 'none']:
                print("Invalid value for key '", i, "' in config file", sep='')
                valid = False
            else:
                # Set channel type
                self._channeltypes[i] = config[i]
                # Increment counters
                if (config[i] == 'fft'):
                    self.numfftchannels += 1
                elif (config[i] == 'vu'):
                    self.numvuchannels += 1

        return valid
