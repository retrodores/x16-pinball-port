"""Independently check the standalone rock audition's encoded ZSM v1 bytes."""
import argparse
from collections import Counter
from pathlib import Path
import struct


def inspect(data):
    if data[:3] != b'zm\x01':
        raise ValueError('expected ZSM version 1')
    songs_end = int.from_bytes(data[6:9], 'little')
    header_fm = data[9]
    header_psg, rate, reserved = struct.unpack_from('<HHH', data, 10)
    if rate != 60 or reserved or any(data[3:6]):
        raise ValueError('unexpected rate, reserved flags, or loop')
    pos, ticks = 16, 0
    fm, psg, hits = Counter(), Counter(), Counter()
    while pos < songs_end:
        cmd = data[pos]
        pos += 1
        if cmd == 128:
            break
        if cmd > 128:
            ticks += cmd-128
        elif cmd < 64:
            value = data[pos]
            pos += 1
            if cmd % 4 == 2 and value & 63 and value & 192:
                psg[cmd//4] += 1
        else:
            if cmd == 64:
                size = data[pos]
                pos += 1
                if size > 63 or size % 2:
                    raise ValueError('unknown extension')
                payload = data[pos:pos+size]
                for reg, value in zip(payload[::2], payload[1::2]):
                    if reg == 2:
                        hits[value] += 1
                    elif reg not in (0,1):
                        raise ValueError('unknown PCM register')
            else:
                size = 2*(cmd-64)
                payload = data[pos:pos+size]
                for reg, value in zip(payload[::2], payload[1::2]):
                    if reg == 8 and value & 120:
                        fm[value & 7] += 1
            pos += size
    if cmd != 128 or pos != songs_end or data[pos:pos+3] != b'PCM':
        raise ValueError('invalid song end or PCM offset')
    if sum(1<<i for i in fm)!=header_fm or sum(1<<i for i in psg)!=header_psg:
        raise ValueError('channel mask does not match actual use')
    count = data[pos+3]+1
    sample_start = pos+4+count*16
    sample_end = 0
    for i in range(count):
        v = data[pos+4+16*i:pos+20+16*i]
        offset, length = int.from_bytes(v[2:5],'little'), int.from_bytes(v[5:8],'little')
        if v[0]!=i or v[1]!=0x10 or any(v[8:]) or not length or length%2 or offset!=sample_end:
            raise ValueError('invalid stereo PCM entry')
        sample_end += length
    if sample_start+sample_end!=len(data) or set(hits)!=set(range(count)):
        raise ValueError('instrument table and trigger usage disagree')
    if len(fm)!=8 or len(psg)!=16 or ticks!=13960:
        raise ValueError('audition has lost a part or changed duration')
    return dict(ticks=ticks, seconds=ticks/rate, fm_voices=len(fm), fm_attacks=sum(fm.values()),
                psg_voices=len(psg), stereo_pcm_entries=count, pcm_triggers=sum(hits.values()),
                pcm_payload_bytes=sample_end)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file',type=Path)
    print(inspect(parser.parse_args().file.read_bytes()))
