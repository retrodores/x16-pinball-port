"""Cover-only conversion of ZSM music gain commands."""
from ast import literal_eval
from pathlib import Path

_SOURCE = Path(__file__).resolve().parents[1] / 'build_music.py'
_LEVELS = literal_eval(next(line[4:] for line in _SOURCE.read_text().splitlines() if line.startswith('lut=')))
_HALF = [min(range(64), key=lambda i: abs(2*_LEVELS[i]-level)) for level in _LEVELS]
# YM2151 TL register slots follow operator order 1, 3, 2, 4.
_CARRIERS = (8, 8, 8, 8, 12, 14, 14, 15)


def attenuate(commands):
    """Change only the gains of the native PSG and FM carrier writes."""
    result = bytearray(commands)
    algorithms = [0] * 8
    pos = 0
    while pos < len(commands):
        cmd = commands[pos]
        pos += 1
        if cmd >= 128:
            continue
        if cmd == 64:
            pos += 1 + (commands[pos] & 63)
            continue
        if cmd < 64:
            value = commands[pos]
            if cmd % 4 == 2:
                result[pos] = (value & 192) | _HALF[value & 63]
            pos += 1
            continue
        for _ in range(cmd & 63):
            reg, value = commands[pos:pos+2]
            channel = reg & 7
            if 0x20 <= reg < 0x28:
                algorithms[channel] = value & 7
            if 0x60 <= reg < 0x80:
                slot = (reg - 0x60) >> 3
                if _CARRIERS[algorithms[channel]] & (1 << slot):
                    result[pos+1] = min(127, (value & 127) + 8)
            pos += 2
    assert pos == len(commands)
    return result
