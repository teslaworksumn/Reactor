#!/usr/bin/env python3
# reactor.py
# Program for reactive sequencing
# Written for the Tesla Works Winter Light Show by Ryan Smith <smit7595@umn.edu>
#
# FFT algorithm based on http://julip.co/2012/05/arduino-python-soundlight-spectrum/ and http://stackoverflow.com/questions/25735153/plotting-a-fast-fourier-transform-in-python
# Client communication modified from http://ilab.cs.byu.edu/python/threadingmodule.html

import sys
import atexit
import traceback
import socket
import threading
import time
import json
import struct
import math
import numpy
import scipy.fftpack
import serial
sys.path.append("plugins/enttec-usb-dmx-pro/")
import EnttecUsbDmxPro as DMX
import pyaudio

dmx = DMX.EnttecUsbDmxPro()
jse = json.JSONEncoder()
SILENT = False
DEBUG = {'General':False, 'TCP':False, 'Audio':False, 'DMX':False}
INFO = {'General':True, 'TCP':True, 'Audio':True, 'DMX':True}
if SILENT:
    DEBUG = {'General':False, 'TCP':False, 'Audio':False, 'DMX':False}
    INFO = {'General':False, 'TCP':False, 'Audio':False, 'DMX':False}

pya_device_index = -1
pya_samplerate = 44100
pya_channels = 1
pya_samples = 2**11 # 2048

for arg in sys.argv:
    if arg.startswith('dmx='):
        dmx.setPort(arg[4:])
    if arg.startswith('list_dmx'):
        serial.tools.list_ports.comports()
    if arg.startswith('audio='):
        pya_device_index = int(arg[6:])
    if arg.startswith('list_audio'):
        pya = pyaudio.PyAudio()
        for i in range(0,pya.get_device_count()):
            device = pya.get_device_info_by_index(i)
            sys.stdout.write("{0}: {1}\n".format(i,device['name']))
        pya.terminate()
        sys.exit(0)

class Server:
    def __init__(self,ip='localhost',port=57201,buffersize=1024,backlog=5,timeout=10):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.TCP_BUFFER_SIZE = buffersize
        self.TCP_BACKLOG = backlog
        self.TCP_TIMEOUT = timeout
        self.clients = []
        self.events = {'close_all':threading.Event()}
    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Uncomment for issues with rebinding sockets
        self.server.bind((self.TCP_IP, self.TCP_PORT))
        self.server.listen(self.TCP_BACKLOG)
        self.server.settimeout(self.TCP_TIMEOUT)
        self.server_thread = threading.Thread(target=self.run)
        self.server_thread.setName("TCP Server on {0}:{1}".format(self.TCP_IP,self.TCP_PORT))
        self.server_thread.daemon=True
        self.events['close_all'].clear()
        self.server_thread.start()
        if INFO['TCP']:
            sys.stdout.write("SERVER_INFO: Listening on {0}:{1}\n".format(self.TCP_IP,self.TCP_PORT))
    def stop(self):
        self.events['close_all'].set()
        if INFO['TCP']:
                sys.stdout.write("CLIENT_INFO: Disconnecting all clients...\n")
        for c in self.clients:
            c.close()
        for c in self.clients: 
            c.closeEvent.wait()
            c.join()
        if INFO['TCP']:
            sys.stdout.write("SERVER_INFO: Closing server...\n")
        self.server_thread.join()
        self.server.close()
        self.events['close_all'].clear()
    def run(self):
        while True:
            if DEBUG['TCP']:
                sys.stdout.write('SERVER_DEBUG: Beginning loop\n')
            try:
                c = Client(self.server.accept(),self.TCP_BUFFER_SIZE) 
                c.start() 
                self.clients.append(c)
            except socket.timeout:
                if DEBUG['TCP']:
                    sys.stdout.write('SERVER_DEBUG: Socket accept timed out\n')
            except:
                e = sys.exc_info()
                sys.stderr.write('SERVER_ERROR: {0}: {1}\n'.format(e[0],e[1]))
                traceback.print_tb(e[2])
            if self.events['close_all'].isSet():
                break
            time.sleep(0.01)
class Client(threading.Thread): # Modified from http://ilab.cs.byu.edu/python/threadingmodule.html
    def __init__(self,client,size): 
        threading.Thread.__init__(self) 
        self.client = client[0]
        self.address = client[1] 
        self.size = size
        self.closeEvent = threading.Event()

    def run(self): 
        try:
            if INFO['TCP']:
                sys.stdout.write("CLIENT_INFO: New client {0}\n".format(self.address))
            while True:
                data = self.client.recv(self.size)
                if data:
                    if DEBUG['TCP']:
                        sys.stdout.write("CLIENT_INFO: Recieved {0} from {1}\n".format(data,self.address))
                    flag = b'fr\x00'
                    if data == flag:
                        csend = bytearray(jse.encode(dts)+'\x00',"UTF-8")
                        self.client.send(csend)
                else:
                    if INFO['TCP']:
                        sys.stdout.write("CLIENT_INFO: Closing client {0}\n".format(self.address))
                    break
                if self.closeEvent.isSet():
                    self.closeEvent.clear()
                    break
        except:
            e = sys.exc_info()
            sys.stderr.write('CLIENT_ERROR: {0}: {1}\n'.format(e[0],e[1]))
            traceback.print_tb(e[2])
            if INFO['TCP']:
                sys.stdout.write("CLIENT_INFO: Closing client {0}\n".format(self.address))
        finally:
            self.client.close()

    def close(self):
        self.closeEvent.set();
    def getCloseEvent(self):
        return self.closeEvent

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
            if INFO['Audio']:
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
            if INFO['Audio']:
                sys.stdout.write("AUDIO_INFO: Closing {0}...\n".format(self.device['name']))
            self.eventstop.set()
            self.eventstop.wait()
            self.audio_thread.join()
            self.stream.stop_stream()
            self.stream.close()
        self.pya.terminate()

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

class SimpleBeatDetection: # Thanks http://stackoverflow.com/questions/12344951/detect-beat-and-play-wav-file-in-a-syncronised-manner
    # Modified by Ryan Smith
    """
    Simple beat detection algorithm from
    http://archive.gamedev.net/archive/reference/programming/features/beatdetection/index.html
    """
    def __init__(self, history = 43, boolean=True):
        self.local_energy = numpy.zeros(history) # a simple ring buffer
        self.local_energy_index = 0 # the index of the oldest element
        self.boolean = boolean

    def detect_beat(self, signal):
        samples = [int(i*32768) for i in signal]
        #samples = signal.astype(numpy.int) # make room for squares
        # optimized sum of squares, i.e faster version of (samples**2).sum()
        instant_energy = numpy.dot(samples, samples) / float(0xffffffff) # normalize

        local_energy_average = self.local_energy.mean()
        local_energy_variance = self.local_energy.var()

        beat_sensibility = (-0.0025714 * local_energy_variance) + 1.15142857
        beat = instant_energy > beat_sensibility * local_energy_average

        self.local_energy[self.local_energy_index] = instant_energy
        self.local_energy_index -= 1
        if self.local_energy_index < 0:
            self.local_energy_index = len(self.local_energy) - 1
        if self.boolean:
            return beat
        else:
            return self.local_energy_index

class MyMath:
    def add(self,a,b):
        if type(a) == list:
            if type(b) == list:
                return [i+j for i,j in zip(a,b)]
            else:
                return [i+b for i in a]
        else:
            return a+b
    def pow(self,base,power):
        if type(base) == list:
            # ALL YOUR BASE ARE BELONG TO US!
            return [i ** power for i in base]
        else:
            return base ** power
    def scale(self, val, src, dst):
        # Thanks, Stackoverflow http://stackoverflow.com/a/4155197/1778122
        return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]
mm = MyMath()

class ChannelUtils:
    def __init__(self):
        pass
    def int2range(self,val,val_range,num_channels,minmax=(0,255),soft=False):
        c = []
        if soft:
            q = minmax[1]-minmax[0]
            vr = (0,num_channels*q)
            rv = mm.scale(val,val_range,vr)
            for i in range(0,num_channels):
                neg = q*i
                c += [int(rv-neg)]
            c = numpy.clip(c,minmax[0],minmax[1]).tolist()
        else:
            vr = (0,val_range[1]-val_range[0])
            rv = mm.scale(val,val_range,vr)
            q = vr[1]/(num_channels+1)
            for i in range(1,num_channels+1):
                if rv >= q*i:
                    c += [minmax[1]]
                else:
                    c += [minmax[0]]
        return c

    def fft(self,data,minmax=(0,255),length=None,samplerate=44100):
        # Primarially ased on http://stackoverflow.com/questions/25735153/plotting-a-fast-fourier-transform-in-python,
        #  with the final data processing from http://julip.co/2012/05/arduino-python-soundlight-spectrum/
        if not data[0] == -1:
            N = len(data)
            # sample spacing
            T = 1.0 / samplerate
            fftbase = scipy.fftpack.fft(data)
            fftaxis = numpy.linspace(0.0, 1.0/(2.0*T), N/2)
            fft = 2.0/N * numpy.abs(fftbase[1:N/2])
            size = len(fft)
            if length == None:
                return (fft,fftaxis)
            fftfinal = []
            for i in range(0, size, int(size/length)):
                fftfinal += [(math.sqrt(max(fft[i:int(i+size/length)])*100)*10)/100]
            return (fftfinal[:length],fftaxis)
        else:
            if length == None:
                return ([0],[0])
            else:
                r = []
                for i in range(0,length):
                    r += [0]
                return (r,[0])

audio = Audio(device_index=pya_device_index,samplerate=pya_samplerate,channels=pya_channels,samples=pya_samples,gain=2)
server = Server()
#server = Server(ip=socket.gethostname())
if not dmx.getPort() == "":
	dmx.connect()

def init():
    audio.start()
    server.start()

def allstop():
    if INFO['General']:
        sys.stdout.write("GEN_INFO: Allstop called.  Closing program...\n")
    if not dmx.getPort() == "":
        dmx.disconnect()
    audio.stop()
    server.stop()
atexit.register(allstop)

dts = {"fftchannel": [],"fftrange":(), "vumeter":[],"vurange":()}
def run():
    vu = VUMeter(7)
    cu = ChannelUtils();
    bd = SimpleBeatDetection(boolean=False)
    range_low = audio.range[0]
    range_high = audio.range[1]
    dts['fftrange'] = (0,1024)
    dts['vurange'] = (0,1024)
    box = [ [],[],[],[],[],[] ]
    try:
        while True:
            frame = audio.getLastFrame()
            fourier = numpy.fft.fft(frame)
            vuval = mm.scale(vu.calc_avg(frame),(0,1),(0,1024))
            
            fft = cu.fft(frame,length=12)
            fft_deb = cu.fft(frame,length=40)
            fftrun = [int(mm.scale(i,(0,1),(0,256))) for i in fft[0][0:6]]
            fftrun_deb = [mm.scale(i,(0,1),(0,1024)) for i in fft_deb[0][0:20]]
            fftrunlimited = []
            for i in fftrun:
                if (i > 255):
                    i = 255
                elif (i < 0):
                    i = 0
                fftrunlimited += [i]
            dts['vumeter'] = [vuval]
            dts['fftchannel'] = fftrun_deb
            vuch = cu.int2range(vuval,(0,1024),8,soft=True)
            #box[0] = fftrunlimited + vuch
            #box[0] = [ fftrunlimited[0], fftrunlimited[1], 0, fftrunlimited[2], fftrunlimited[3], fftrunlimited[4], fftrunlimited[5]]
            box[0] = vuch[1:]
            # TODO: Add configuration file to replace hardcode
            d2s =  box[0]
            #d2s = , 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 0]
            dmx.sendDMX(d2s)
            time.sleep(0.01)
    except (KeyboardInterrupt,SystemExit):
        pass
    finally:
        if INFO['General']:
            sys.stdout.write("GEN_INFO: Exiting run...\n")

init()

def allOn(i):
	dmx.sendDMX([255]*i)

def allOff(i):
	dmx.sendDMX([0]*i)

if not sys.flags.interactive:
    run()
else:
    print("Entering interactive mode.  Please call allstop() before exit() to avoid a hang condition.")
