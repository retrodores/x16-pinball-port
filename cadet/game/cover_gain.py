"""Cover-only conversion of ZSM music gain commands."""
from ast import literal_eval
from pathlib import Path

_SOURCE = Path(__file__).resolve().parents[1] / 'build_music.py'
_LEVELS = literal_eval(next(line[4:] for line in _SOURCE.read_text().splitlines() if line.startswith('lut=')))
# YM2151 TL register slots follow operator order 1, 3, 2, 4.
_CARRIERS = (8, 8, 8, 8, 12, 14, 14, 15)


def attenuate(commands, extra_db=0):
    """Change only the gains of the native PSG and FM carrier writes."""
    ratio = 0.5 * 10**(-extra_db/20)
    scaled = [min(range(64), key=lambda i: abs(_LEVELS[i]-level*ratio))
              for level in _LEVELS]
    fm_steps = 8 + round(extra_db/0.75)
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
                result[pos] = (value & 192) | scaled[value & 63]
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
                    result[pos+1] = min(127, (value & 127) + fm_steps)
            pos += 2
    assert pos == len(commands)
    return result
