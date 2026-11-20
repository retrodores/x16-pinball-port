"""Prepare the optional 2 MB GTR3QQ cover from a local ZSM export."""
import argparse
import hashlib
from pathlib import Path
from cover_gain import attenuate

BANK = 8192
LOW_COMMAND_BYTES = 13 * BANK
SOURCE_SHA256 = '4160e79d73474e9effd7e93c7426315c5c53f0fafe4bc92902885d2ff886cc05'


def number(data):
    return int.from_bytes(data, 'little')


def address(offset, bank):
    return bank + offset // BANK, 0xa000 + offset % BANK


def pack(source, out, extra_db=0):
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
        raise ValueError('Expected the original Pinball_R6.zsm export from pinball.7z')
    loop = number(data[3:6]) - 16
    pcm_offset = number(data[6:9])
    commands = data[16:pcm_offset]
    count = data[pcm_offset + 3] + 1
    table = data[pcm_offset + 4:pcm_offset + 4 + count * 16]
    samples = data[pcm_offset + 4 + count * 16:]
    sample_banks = (len(samples) + BANK - 1) // BANK
    transition = 64 + sample_banks
    assert len(commands) > LOW_COMMAND_BYTES
    assert transition + (len(commands) - LOW_COMMAND_BYTES + BANK - 1) // BANK <= 256
    assert data[:3] == b'zm\x01' and number(data[12:14]) == 92
    assert commands[-1] == 0x80 and 0 <= loop < LOW_COMMAND_BYTES
    loop_bank, loop_ptr = address(loop, 32)

    entries = []
    for index in range(count):
        entry = table[16 * index:16 * (index + 1)]
        start, size = number(entry[2:5]), number(entry[5:8])
        assert entry[:2] == bytes((index, 0x10)) and not entry[8]
        assert not ((start | size) & 1) and start + size <= len(samples)
        bank, ptr = address(start, 64)
        frames = size // 2
        entries.append(f'.byte {bank},{ptr & 255},{ptr >> 8},'
                       f'{frames & 255},{frames >> 8 & 255},{frames >> 16}')

    out.mkdir(parents=True, exist_ok=True)
    if extra_db:
        ratio = 10**(-extra_db/20)
        scale = bytes(round((v if v < 128 else v-256)*ratio) & 255 for v in range(256))
        samples = samples.translate(scale)
    (out / 'COVER.PCM').write_bytes(samples)
    commands = attenuate(commands, extra_db)
    (out / 'COVER.CMD').write_bytes(commands[:LOW_COMMAND_BYTES])
    (out / 'COVER.HI').write_bytes(commands[LOW_COMMAND_BYTES:])
    (out / 'music_cover_data.inc').write_text(
        f'COVER_CMD_HIGH = {transition}\nCOVER_LOOP_BANK = {loop_bank}\n'
        f'COVER_LOOP_PTR = {loop_ptr}\nCOVER_INSTRUMENTS = {count}\n'
        'cover_instruments:\n' + '\n'.join(entries) + '\n')
    (out / 'music_cover_data.h').write_text(
        f'#define COVER_CMD_HIGH {transition}\n#define COVER_LAST_BANK {transition + (len(commands) - LOW_COMMAND_BYTES - 1) // BANK}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('zsm', type=Path)
    parser.add_argument('output', type=Path, nargs='?', default=Path('cadet/play-build'))
    parser.add_argument('--extra-db', type=float, choices=(0, 4), default=0)
    args = parser.parse_args()
    pack(args.zsm, args.output, args.extra_db)
