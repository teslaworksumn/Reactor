#!/usr/bin/env python3

num_ch = 120
num_fft = 96
num_vu = 8

with open('config.yaml', 'w') as file:
    file.write('numchannels: ' + str(num_ch) + '\n')
    file.write('numfft: ' + str(num_fft) + '\n')
    file.write('numvu: ' + str(num_vu) + '\n')
    file.write('audiogain: 1\n')
    file.write('fftN: 1024\n')
    file.write('fftlog: Y\n')
    file.write('vulog: Y\n')
    for i in range(96):
        s = str(i) + ': fft ' + str(i) + '\n'
        file.write(s)
    for i in range(8):
        s = str(96+i) + ': vu ' + str(i) + '\n'
        file.write(s)
    for i in range(8):
        s = str(104 + i) + ': none -1\n'
        file.write(s)
    for i in range(8):
        s = str(112 + i) + ': vu ' + str(7-i) + '\n'
        file.write(s)

    file.flush()
