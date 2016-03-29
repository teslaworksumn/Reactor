#!/usr/bin/env python3
# reactor.py
# Program for reactive sequencing
# Written for the Tesla Works Winter Light Show by Ryan Smith <smit7595@umn.edu>
#
# FFT algorithm based on http://julip.co/2012/05/arduino-python-soundlight-spectrum/ and http://stackoverflow.com/questions/25735153/plotting-a-fast-fourier-transform-in-python
# Client communication modified from http://ilab.cs.byu.edu/python/threadingmodule.html

import sys
import atexit
import time
import numpy
import serial
import serial.tools.list_ports
import pyaudio
import Net.Server as Server
import Utils.Audio as Audio
import Utils.MyMath as MyMath
import Utils.ChannelUtils as ChannelUtils
import VUMeter
import SimpleBeatDetection as SimpleBeatDetection
import Globals
import Plugins.enttec_usb_dmx_pro.EnttecUsbDmxPro as EnttecUsbDmxPro
import Plugins.VixenLogPlugin as VixenLogPlugin
import Utils.ConfigParser as ConfigParser

dmx = EnttecUsbDmxPro.EnttecUsbDmxPro()
vixenlog = VixenLogPlugin.VixenLogPlugin()

config = ConfigParser.ConfigParser("configs/config.yaml")

pya_device_index = -1
pya_samplerate = 44100
pya_channels = 1
pya_samples = 2**11 # 2048
pya_gain = config.gain

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

mm = MyMath.MyMath()
audio = Audio.Audio(device_index=pya_device_index, samplerate=pya_samplerate, channels=pya_channels, samples=pya_samples, gain=pya_gain)
server = Server.Server()
#server = Server(ip=socket.gethostname())
if not dmx.getPort() == "":
    dmx.connect()

def init():
    audio.start()
    server.start()

def allstop():
    if Globals.INFO['General']:
        sys.stdout.write("GEN_INFO: Allstop called.  Closing program...\n")
    if not dmx.getPort() == "":
        dmx.disconnect()
    audio.stop()
    server.stop()
atexit.register(allstop)

def run():
    vu = VUMeter.VUMeter()
    cu = ChannelUtils.ChannelUtils();
#    bd = SimpleBeatDetection.SimpleBeatDetection(boolean=False)
#    range_low = audio.range[0]
#    range_high = audio.range[1]
    maxfft = 256
    maxvu = 1024
    Globals.dts['fftrange'] = (0,maxfft)
    Globals.dts['vurange'] = (0,maxvu)
    numfftchannels = config.numfftchannels
    numvuchannels = config.numvuchannels
    fftN = config.fftN
    try:
        while True:
            frame = audio.getLastFrame()
            if numfftchannels > 0:
                fft = cu.fft(frame, numfftchannels, N=fftN, log=True, samplerate=44100)
                fftrun = [int(mm.scale(x,(0,1),(0,maxfft))) for x in fft]
                fftrun256 = []
                for i in fftrun:
                    if (i > 255):
                        i = 255
                    elif (i < 0):
                        i = 0
                    fftrun256 += [i]
            else:
                fftrun = [0]
                fftrun256 = [0]

            if numvuchannels > 0:
                vuavg = vu.calc_avg(frame)
                vuscaled = mm.scale(vuavg,(0,1),(0,maxvu))
                vuchannelscaled = cu.int2range(vuscaled, (0,maxvu), 1, soft=True)
                vuchannels = cu.vuintensitybuckets(vuavg, numvuchannels, log=True, maxval=255)[:numvuchannels]
            else:
                vuchannels = [0]
                vuchannelscaled = [0]

            datatosend = config.getdatatosend(fftrun256, vuchannels)
            Globals.dts['vumeter'] = vuchannelscaled
            Globals.dts['fftchannel'] = datatosend
            dmx.sendDMX(datatosend)
            vixenlog.send(datatosend)
            time.sleep(0.01)
    except (KeyboardInterrupt,SystemExit):
        pass
    finally:
        if Globals.INFO['General']:
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
