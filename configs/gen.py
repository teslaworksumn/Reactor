#!/usr/bin/env python3

num_ch = 144
num_fft = 24
num_vu = 8

with open('genconfig.yaml', 'w') as file:
    file.write('numchannels: ' + str(num_ch) + '\n')
    file.write('numfft: ' + str(num_fft) + '\n')
    file.write('numvu: ' + str(num_vu) + '\n')
    file.write('fftgain: 0.3\n')
    file.write('vugain: 1.0\n')
    file.write('fftN: 2048\n')
    file.write('fftlog: Y\n')
    file.write('vulog: Y\n')
    box_idx = 0
    box_count = 0
    for i in range(48):
        s = str(i*2) + ': fft ' + str(box_idx) + '\n' + \
        str(i*2+1) + ': fft ' + str(box_idx + 1) + '\n'
        file.write(s)
        box_count += 2
        if box_count == 8:
            box_count = 0
            box_idx += 2
    for i in range(8):
        s = str(96+i) + ': vu ' + str(i) + '\n'
        file.write(s)
    for i in range(8):
        s = str(104 + i) + ': none -1\n'
        file.write(s)
    for i in range(8):
        s = str(112 + i) + ': vu ' + str(7-i) + '\n'
        file.write(s)
    for i in range(8):
        s = str(120 + i) + ': none -i\n'
        file.write(s)
    for i in range(16):
        s = str(128 + i) + ': none -1\n'
        file.write(s)

    file.flush()
