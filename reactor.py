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

sys.path.append("plugins/enttec-usb-dmx-pro/")
import Plugins.enttec_usb_dmx_pro.EnttecUsbDmxPro as DMX
import pyaudio
import Net.Server as Server
import Utils.Audio as Audio
import Utils.MyMath as MyMath
import Utils.ChannelUtils as ChannelUtils
import VUMeter
import SimpleBeatDetection as SimpleBeatDetection
import Globals


dmx = DMX.EnttecUsbDmxPro()

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

mm = MyMath.MyMath()
audio = Audio.Audio(device_index=pya_device_index,samplerate=pya_samplerate,channels=pya_channels,samples=pya_samples,gain=2)
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
    vu = VUMeter.VUMeter(7)
    cu = ChannelUtils.ChannelUtils();
    bd = SimpleBeatDetection.SimpleBeatDetection(boolean=False)
    range_low = audio.range[0]
    range_high = audio.range[1]
    Globals.dts['fftrange'] = (0,1024)
    Globals.dts['vurange'] = (0,1024)
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
            Globals.dts['vumeter'] = [vuval]
            Globals.dts['fftchannel'] = fftrun_deb
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
