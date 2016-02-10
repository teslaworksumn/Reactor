# Reactor

A simple Python-based audio analysis tool that can output to various plugins including DMX


## Usage

`./reactor.py list_dmx`: lists the available serial ports that can be used for the Enttec USB DMX 
Pro output

`./reactor.py list_audio`: lists the available audio devices with their indices.  Select the one 
you wish to use for the input.

`./reactor.py dmx=/dev/ttyUSB0 audio=4`: starts reactor with the dmx interface on /dev/ttyUSB0 and
listening to audio on the input with index 4.

Unfortunately, right now, the layout has to be hard-coded in place in the run function. 
This is done by default using the `d2s` variable in the `run()` function.  `d2s` should be a list
of integers 0-255 that represent the values of the DMX channels to send.  The `d2s` list is then 
passed to the Enttec module for trasmission.

Adding the ability to use a configuration file is a high development priority.

## Requirements

Reactor is written in Python 3, and tested in Python 3.4.  It may be compatible with Python 2, but 
we cannot guarantee it.

| Dependency | Used by                           |
-------------|-----------------------------------|
| pyaudio    | reactor.py                        |
| numpy      | reactor.py, ffttest.py            |
| pySerial   | plugins.py                        |

## License
This project is licensed under the MIT license (see LICENSE)
