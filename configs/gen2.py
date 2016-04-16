#!/usr/bin/env python3

num_ch = 120
num_fft = 0
num_vu = 144

with open('gen2config.yaml', 'w') as file:
    file.write('numchannels: ' + str(num_ch) + '\n')
    file.write('numfft: ' + str(num_fft) + '\n')
    file.write('numvu: ' + str(num_vu) + '\n')
    file.write('audiogain: 0.7\n')
    file.write('fftN: 2048\n')
    file.write('fftlog: Y\n')
    file.write('vulog: Y\n')
    section_idx = 0
    for i in range(4): # starbursts left
        for j in range(4): # section 0
            s = str(i * 8 + j) + ': vu ' + str(section_idx) + '\n'
            file.write(s)
        section_idx += 1
        for j in range(4):  # section 1
            s = str(i * 8 + 4 + j) + ': vu ' + str(section_idx) + '\n'
            file.write(s)
        section_idx += 1

    section_idx = 7
    for i in range(4): # starbursts right
        for j in range(4): # section 0
            s = str(32 + i * 8 + j) + ': vu ' + str(section_idx) + '\n'
            file.write(s)
        section_idx -= 1
        for j in range(4):  # section 1
            s = str(32 + i * 8 + 4 + j) + ': vu ' + str(section_idx) + '\n'
            file.write(s)
        section_idx -= 1

    file.flush()
