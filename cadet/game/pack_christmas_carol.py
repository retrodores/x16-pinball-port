"""Map the approved stereo Christmas audition into the game's banked ZSM reader."""
import hashlib
from pathlib import Path

BANK_SIZE = 8192
FIRST_BANK = 80
ZSM_SHA256 = 'f4cc99564f3a0a23367c22b0d24d7b04a17b8bf950fe01d6b29508de650c57a9'
PCM_VOLUME = (0, 1, 2, 3, 4, 5, 6, 8, 11, 14, 18, 23, 30, 38, 49, 64)
MIX_VOLUME = 14


def prepare(source, output):
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != ZSM_SHA256:
        raise ValueError('Christmas build requires the approved CAROL.ZSM rock audition')
    pcm = int.from_bytes(data[6:9], 'little')
    count = data[pcm + 3] + 1
    payload = pcm + 4 + 16 * count
    assert data[:6] == b'zm\x01\x00\x00\x00' and data[12:14] == b'<\x00'
    assert data[pcm-1:pcm+3] == b'\x80PCM'
    # An even stereo-frame address keeps L/R together at page and bank boundaries.
    bias = payload & 1
    addr = 0xa000 + bias
    end = FIRST_BANK + (len(data) + bias - 1) // BANK_SIZE
    assert end < 256
    inc = [f'CAROL_BANK = {FIRST_BANK}', f'CAROL_COMMAND = {addr + 16}',
           f'COVER_LOOP_BANK = {FIRST_BANK}', f'COVER_LOOP_PTR = {addr + 16}',
           f'COVER_INSTRUMENTS = {count}', 'cover_instruments:']
    end_sample = 0
    for i in range(count):
        row = data[pcm+4+16*i:pcm+20+16*i]
        off, size = int.from_bytes(row[2:5], 'little'), int.from_bytes(row[5:8], 'little')
        assert row[:2] == bytes((i, 0x10)) and not any(row[8:])
        assert off == end_sample and not ((off|size)&1) and size > 0
        end_sample += size
        bank, index = divmod(bias + payload + off, BANK_SIZE)
        pos = 0xa000 + index
        frames = size // 2
        entry = (FIRST_BANK + bank, pos & 255, pos >> 8, frames & 255,
                 frames >> 8 & 255, frames >> 16)
        inc.append('.byte ' + ','.join(map(str, entry)))
    assert payload + end_sample == len(data)
    pos, levels, ticks = 16, set(), 0
    while pos < pcm:
        cmd = data[pos]
        pos += 1
        if cmd == 128:
            assert pos == pcm
        elif cmd > 128:
            ticks += cmd-128
        elif cmd < 64:
            pos += 1
        elif cmd > 64:
            pos += 2*(cmd-64)
        else:
            n = data[pos]
            pos += 1
            assert 0 < n <= 63 and not n & 1
            for reg,value in zip(data[pos:pos+n:2], data[pos+1:pos+n:2]):
                if reg==0:
                    assert value <= MIX_VOLUME
                    levels.add(value)
                elif reg==1:
                    assert value == 42
                else:
                    assert reg==2 and value<count
            pos += n
    assert pos == pcm and ticks == 13960
    inc.extend(['carol_volume_pages:', '.byte ' + ','.join(
        str(sorted(levels).index(v)) if v in levels else '0' for v in range(16)),
        '.section .holiday.rodata,"a",@progbits', '.balign 256'])
    inc.append('carol_gain_start:')
    for level in sorted(levels):
        inc.append(f'carol_gain_{level}:')
        values = [round((v if v < 128 else v-256) * PCM_VOLUME[level] /
                        PCM_VOLUME[MIX_VOLUME]) & 255 for v in range(256)]
        for i in range(0,256,16):
            inc.append('.byte ' + ','.join(map(str, values[i:i+16])))
    # Scale just the mono game effects for overlay on the approved stereo mix.
    inc.append('carol_effect_gain:')
    values = [round((v if v < 128 else v-256) * 5/16) & 255 for v in range(256)]
    for i in range(0,256,16):
        inc.append('.byte ' + ','.join(map(str, values[i:i+16])))
    inc.append('.section .text.lab,"ax",@progbits')
    output.mkdir(parents=True, exist_ok=True)
    (output/'carol_audio.inc').write_text('\n'.join(inc)+'\n')
    (output/'carol_audio.h').write_text(
        f'#define CAROL_BANK {FIRST_BANK}\n#define CAROL_ADDRESS {addr}u\n')
    if source.resolve() != (output/'CAROL.ZSM').resolve():
        (output/'CAROL.ZSM').write_bytes(data)
