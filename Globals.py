
SILENT = False
DEBUG = {'General':False, 'TCP':False, 'Audio':False, 'DMX':False}
INFO = {'General':True, 'TCP':True, 'Audio':True, 'DMX':True}
if SILENT:
    DEBUG = {'General':False, 'TCP':False, 'Audio':False, 'DMX':False}
    INFO = {'General':False, 'TCP':False, 'Audio':False, 'DMX':False}

dts = {"fftchannel": [], "fftrange":(), "vumeter":[], "vurange":()}