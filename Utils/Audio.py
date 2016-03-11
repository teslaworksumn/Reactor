
import threading
import traceback
import pyaudio
import sys
import numpy
import Globals


class Audio:
    def __init__(self,device_index=-1,samplerate=44100,gain=1,channels=1,samples=2**10):
        self.pya = pyaudio.PyAudio()
        self.device_index = device_index
        self.samplerate = samplerate
        self.channels = channels
        self.samples = samples
        self.range = (-2**15,2**15)
        self.eventstop = threading.Event()
        self.audiowait = threading.Event()
        self.chunk = b''
        self.frame = [-1]
        self.gain = gain
        self.eventstop.clear()
        self.audiowait.set()
    def start(self):
        if self.device_index != -1:
            self.stream = self.pya.open(format=pyaudio.paInt16,rate=self.samplerate,channels=self.channels,input_device_index=self.device_index,input=True)
            self.device = self.pya.get_device_info_by_index(self.device_index)
            if Globals.INFO['Audio']:
                sys.stdout.write("AUDIO_INFO: Opened {0}\n".format(self.device['name']))
            self.eventstop.clear()
            self.audiowait.set()
            self.audio_thread = threading.Thread(target=self.run)
            self.audio_thread.daemon=True
            self.audio_thread.setName("Audio device {0}".format(self.device['name']))
            self.audio_thread.start()
    def run(self):
        while True:
            self.audiowait.set()
            try:
                self.chunk = self.stream.read(self.samples)
                unorm = numpy.fromstring(self.chunk,dtype=numpy.int16)
                self.frame = []
                for i in unorm:
                    self.frame += [i/32768.0]
            except:
                e = sys.exc_info()
                sys.stderr.write('AUDIO_ERROR: {0}: {1}\n'.format(e[0],e[1]))
                traceback.print_tb(e[2])
            if (self.eventstop.isSet()):
                self.eventstop.clear()
                break
            self.audiowait.clear()
        self.eventstop.clear()

    def getLastChunk(self):
        if self.audiowait.wait(3):
            return self.chunk
        else:
            return b''
    def getLastFrame(self):
        if self.audiowait.wait(3):
            #return self.frame
            r = []
            for i in self.frame:
                i = i*self.gain
                if (i > 1):
                    i = 1
                elif (i < -1):
                    i = -1
                r += [i]
            return r
        else:
            return []
    def stop(self):
        if self.device_index != -1:
            if Globals.INFO['Audio']:
                sys.stdout.write("AUDIO_INFO: Closing {0}...\n".format(self.device['name']))
            self.eventstop.set()
            self.eventstop.wait()
            self.audio_thread.join()
            self.stream.stop_stream()
            self.stream.close()
        self.pya.terminate()

