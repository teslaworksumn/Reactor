# Reactor

A simple Python-based audio analysis tool that can output to various plugins including DMX

## Usage

`./reactor.py list_dmx`: lists the available serial ports that can be used for the Enttec USB DMX 
Pro output

`./reactor.py list_audio`: lists the available audio devices with their indices.  Select the one 
you wish to use for the input.

`./reactor.py dmx=/dev/ttyUSB0 audio=4`: starts reactor with the dmx interface on /dev/ttyUSB0 and
listening to audio on the input with index 4.

The layout is read from configs/config.yaml

## Requirements

Reactor is written in Python 3, and tested in Python 3.4.  It may be compatible with Python 2, but 
we cannot guarantee it.

| Dependency | Used by                           |
-------------|-----------------------------------|
| pyaudio    | reactor.py                        |
| numpy      | reactor.py, ffttest.py            |
| pySerial   | plugins.py                        |

All of these can be installed with pip

pyaudio also depends on portaudio, which can be found at http://portaudio.com/download.html
Instructions for installing portaudio can be found at http://stackoverflow.com/questions/20023131/cannot-install-pyaudio-gcc-error

## License
This project is licensed under the MIT license (see LICENSE)
