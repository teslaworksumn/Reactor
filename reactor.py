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
from docopt import docopt
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

help_message = """Reactor

Usage:
    reactor.py list_dmx
    reactor.py list_audio
    reactor.py --audio=<audio-idx> [--dmx=<dmx-path>]
    reactor.py --version
    reactor.py (-h | --help)

Options:
    --dmx=<dmx-path>    Path to the dmx block device
    --audio=<audio-idx> Index of used audio device, found with list_audio
    --version           Show version
    -h --help           Show this message
"""

pya_device_index = -1
pya_samplerate = 44100
pya_channels = 1
pya_samples = 2**11 # 2048

fft_gain = config.gain_fft
vu_gain = config.gain_vu
pya_gain = vu_gain

arguments = docopt(help_message, version='Reactor 1.0')

if arguments['list_dmx']:
    serial.tools.list_ports.comports()
    sys.exit(0)
if arguments['list_audio']:
    pya = pyaudio.PyAudio()
    for i in range(0,pya.get_device_count()):
        device = pya.get_device_info_by_index(i)
        sys.stdout.write("{0}: {1}\n".format(i,device['name']))
    pya.terminate()
    sys.exit(0)
if arguments['--dmx'] != None:
    dmx.setPort(arguments['--dmx'])
if arguments['--audio'] != None:
    pya_device_index = int(arguments['--audio'])

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
    maxvu = 255
    Globals.dts['fftrange'] = (0,maxfft)
    Globals.dts['vurange'] = (0,maxvu)
    numfftchannels = config.numfftchannels
    numvuchannels = config.numvuchannels
    fftN = config.fftN
    try:
        while True:
            vu_frame = audio.getLastFrame()
            fft_frame = [x*fft_gain/vu_gain for x in vu_frame]
            if numfftchannels > 0:
                fft = cu.fft(fft_frame, numfftchannels, N=fftN, log=True, samplerate=44100)
                fftrun = [int(mm.scale(x,(0,1),(0,maxfft))) for x in fft]
                fftrun256 = []
                for i in fftrun:
                    if (i > 255):
                        i = 255
                    elif (i < 0):
                        i = 0
                    fftrun256 += [i]
            else:
                fftrun256 = [0]

            if numvuchannels > 0:
                vuavg = vu.calc_avg(vu_frame)
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
