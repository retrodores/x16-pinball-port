"""Generate two original electronic pulses at the resident PCM rate."""
from math import exp, pi, sin
from pathlib import Path
import sys

SAMPLE_RATE = 11062.6220703125
NOTE_BYTES = 384


def pulse(frequency, amplitude):
    data = bytearray()
    phase = 0.0
    for i in range(NOTE_BYTES):
        t = i/SAMPLE_RATE
        phase += 2*pi*(frequency + 220*exp(-t*125))/SAMPLE_RATE
        attack = min(1, i/24)
        release = min(1, (NOTE_BYTES-1-i)/65)
        envelope = amplitude*attack*release*exp(-t*72)
        data.append(round(envelope*(sin(phase)+0.24*sin(phase*2))) & 255)
    return data


if __name__ == '__main__':
    Path(sys.argv[1]).write_bytes(pulse(1140, 90) + pulse(810, 68))
