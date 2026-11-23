"""Sequence a native instrumental Shchedryk arrangement and private lamp cues."""
from collections import defaultdict
from pathlib import Path

HZ = 92
BAR = 184
BARS = 102
MOTIF = (67, 66, 67, 64)
MINOR = ((40, 59, 64), (36, 60, 64), (45, 60, 64), (47, 59, 63))
LIFT = ((36, 60, 67), (38, 62, 69), (43, 59, 67), (47, 63, 66))
BRIDGE = ((71, 69, 67), (64, 66, 67), (69, 71, 74), (72, 71, 66))
KEY_CODES = (0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14)


def arrange():
    events = defaultdict(list)

    def fm(tick, register, value):
        events[tick].append((1, register, value))

    def psg(tick, voice, note, level, wave=0x80):
        frequency = round(440 * 2 ** ((note - 69) / 12) * (1 << 17) / (25_000_000 / 512))
        for register, value in enumerate((frequency & 255, frequency >> 8, 192 | level, wave)):
            events[tick].append((0, voice * 4 + register, value))

    def lead(tick, note, level, duration):
        # VERA carries the melody immediately, including on setups where
        # the FM bell layer is quiet or unavailable.
        psg(tick, 5, note, level)
        events[tick + 8].append((0, 5 * 4 + 2, 192 | (level - 5)))
        events[tick + duration].append((0, 5 * 4 + 2, 192))

    def bell(tick, channel, note, level, duration):
        fm(tick, 8, channel)
        fm(tick, 0x28 + channel, ((note // 12 - 1) << 4) | KEY_CODES[note % 12])
        fm(tick, 0x70 + channel, 127 - level)
        fm(tick, 0x78 + channel, 130 - level)
        fm(tick, 8, 0x78 | channel)
        fm(tick + duration, 8, channel)

    for channel in range(4):
        fm(0, 0x20 + channel, 0xC0 | (4 if channel < 2 else 3) << 3 | 4)
        for operator, ratio in ((0, 3 if channel < 2 else 2), (8, 2), (16, 1), (24, 1)):
            reg = channel + operator
            fm(0, 0x40 + reg, ratio)
            fm(0, 0x60 + reg, 38 if operator < 16 else 60)
            fm(0, 0x80 + reg, 0x1f if channel < 2 else 0x19)
            fm(0, 0xa0 + reg, 13 if channel < 2 else 4)
            fm(0, 0xc0 + reg, 5)
            fm(0, 0xe0 + reg, 0x48)

    for bar in range(96):
        tick = bar * BAR
        if bar < 16:
            energy = min(4, 1 + bar // 5)
        elif bar < 47:
            energy = min(8, 4 + (bar - 16) // 4)
            if 38 <= bar < 42:
                energy = 5
        elif bar < 62:
            energy = 2 if bar < 59 else 4
        else:
            energy = min(10, 6 + (bar - 62) // 3)
            if 74 <= bar < 77:
                energy = 7
        changes = LIFT if 8 <= bar % 16 <= 11 else MINOR
        chord = changes[(bar // 2) % 4]
        if 47 <= bar < 59:
            phrase = BRIDGE[(bar - 47) % len(BRIDGE)]
            melody = zip((0, 61, 122), phrase)
        else:
            notes = MOTIF if bar % 8 != 7 else (67, 69, 67, 64)
            melody = zip((0, 61, 92, 122), notes)
        for index, (offset, note) in enumerate(melody):
            bell(tick + offset, index % 2, note, 79 + energy + (3 if index == 0 else 0), 34)
            lead(tick + offset, note, min(62, 56 + energy + (3 if index == 0 else 0)), 28)
            if energy >= 6 and index in (0, 3):
                psg(tick + offset, 4, note + 12, energy + 3, 0x80)
                psg(tick + offset + 19, 4, note + 12, 0, 0x80)
        if energy >= 3:
            psg(tick, 0, chord[0], energy + 9, 0x5f)
            psg(tick + 160, 0, chord[0], 0, 0x5f)
        if energy >= 4:
            for i, note in enumerate(chord[1:]):
                bell(tick, i + 2, note + (12 if bar % 8 == 7 else 0), 65 + energy, 149)
        if energy >= 5:
            for offset in (0, 61, 122):
                psg(tick + offset, 1, 31 if offset == 0 else 46, energy + 5, 0xc0)
                psg(tick + offset + 7, 1, 31, 0, 0xc0)
        if energy >= 8 and bar % 8 in (4, 5, 6, 7):
            phrase = BRIDGE[bar % 4]
            for beat, note in enumerate(phrase):
                offset = beat * 61
                psg(tick + offset, 3, note, energy + 5)
                psg(tick + offset + 53, 3, note, 0)
        if energy >= 7:
            for j, offset in enumerate((30, 91, 153)):
                psg(tick + offset, 2, chord[1 + j % 2] - 12, energy + 2, 0x4e)
                psg(tick + offset + 25, 2, 48, 0, 0x4e)
        for beat, offset in enumerate((0, 61, 122)):
            intensity = energy if beat == 0 else max(1, energy - 2)
            phase = (bar * 3 + beat) % 16
            events[tick + offset].append((2, 0, (phase << 4) | intensity))

    tick = 96 * BAR
    for channel, note in enumerate((52, 59, 64, 67)):
        bell(tick, channel, note, 94 - channel, 170)
    lead(tick, 64, 60, 120)
    for index, intensity in enumerate((10, 8, 6, 4, 2, 1, 0)):
        events[tick + 61 * index].append((2, 0, (7 << 4) | intensity))
    return events


def encode(events, lamps):
    stream = bytearray()
    previous = 0
    for tick, writes in sorted(events.items()):
        commands = bytearray()
        for kind, register, value in writes:
            if kind == 2:
                if lamps:
                    commands.extend((0x40, 0x81, value))
            elif kind == 1:
                commands.extend((0x41, register, value))
            else:
                commands.extend((register, value))
        if commands:
            delay = tick - previous
            while delay:
                step = min(127, delay)
                stream.append(128 + step)
                delay -= step
            stream.extend(commands)
            previous = tick
    delay = BARS * BAR - previous
    while delay:
        step = min(127, delay)
        stream.append(128 + step)
        delay -= step
    stream.append(0x80)
    return bytes(stream)


def build(output):
    output.mkdir(parents=True, exist_ok=True)
    events = arrange()
    commands = encode(events, lamps=True)
    assert len(commands) < 13 * 8192
    (output / 'COVER.CMD').write_bytes(commands)
    header = b'zm\x01' + (16).to_bytes(3, 'little') + bytes(3) + bytes((0x0f, 0x3f, 0))
    header += HZ.to_bytes(2, 'little') + bytes(2)
    (output / 'SHCHEDRYK.ZSM').write_bytes(header + encode(events, lamps=False))


if __name__ == '__main__':
    import sys
    build(Path(sys.argv[1]))
