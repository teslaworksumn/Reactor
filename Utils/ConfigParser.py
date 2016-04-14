import yaml

class ConfigParser:
    def __init__(self, fname):
        self.numchannels = 0
        self.numfftchannels = 0
        self.numvuchannels = 0
        self.gain = 1
        self.fftN = 1024
        self._channeldata = []
        self.fftlog = False
        self.vulog = False
        self.setconfig(fname)

    def getdatatosend(self, fftdata, vudata):
        datatosend = [0] * self.numchannels
        for i in range(self.numchannels):
            channel_type = self._channeldata[i][0]
            channel_map = int(self._channeldata[i][1])
            if channel_type == 'fft':
                datatosend[i] = int(fftdata[channel_map])
            elif channel_type == 'vu':
                datatosend[i] = int(vudata[channel_map])
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
        if 'numchannels' not in keys or \
            'numfft' not in keys or \
            'numvu' not in keys or \
            'audiogain' not in keys or \
            'fftN' not in keys:

            print("Missing 'numchannels', 'numfft', 'numvu', 'fftN', or 'audiogain' key")
            return False

        channels = config['numchannels']
        count_fft = config['numfft']
        count_vu = config['numvu']
        audiogain = config['audiogain']
        N = config['fftN']

        try:
            self.numchannels = int(channels)
            self.numfftchannels = int(count_fft)
            self.numvuchannels = int(count_vu)
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
        self._channeldata = [('none', -1)] * self.numchannels

        valid = True
        # Each channel has its own key
        # Each value should be 'fft', 'vu', or 'none'
        for i in range(self.numchannels):
            if i not in keys:
                print("Missing key '", i, "' from config file", sep='')
                valid = False
            else:
                (dtype, ch) = config[i].split()
                if dtype not in ['fft', 'vu', 'none']:
                    print("Invalid value for key '", i, "' in config file", sep='')
                    valid = False
                else:
                    # Set channel type and mapping
                    self._channeldata[i] = (dtype, ch)

        return valid
