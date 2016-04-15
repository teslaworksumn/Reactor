#!/usr/bin/env python3

num_ch = 120
num_fft = 144
num_vu = 144

with open('gen2config.yaml', 'w') as file:
    file.write('numchannels: ' + str(num_ch) + '\n')
    file.write('numfft: ' + str(num_fft) + '\n')
    file.write('numvu: ' + str(num_vu) + '\n')
    file.write('audiogain: 0.7\n')
    file.write('fftN: 2048\n')
    file.write('fftlog: Y\n')
    file.write('vulog: Y\n')
    vu_idx = 0
    counter = 0
    for i in range(num_ch):
        s = str(i) + ': vu ' + str(vu_idx*4+counter) + '\n'
        file.write(s)
        counter += 1
        if counter == 4:
            counter = 0
            vu_idx += 1

    file.flush()
