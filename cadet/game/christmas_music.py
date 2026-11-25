"""A Shchedryk concert arrangement in E minor for OPM, VERA PSG and the center lamps."""
from collections import defaultdict
from pathlib import Path

HZ = 92
BAR = 120                     # Three beats of 40 ticks, dotted pulse = 46/min.
BARS = 157
KEY_CODES = (0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14)  # C# through C
MOTIF = (67, 66, 67, 64)
# Bass, third, fifth and upper chord tone. The dominant has a raised D#.
EM, C, AM, B = (40, 55, 59, 64), (36, 55, 60, 64), (45, 57, 60, 64), (35, 54, 59, 63)
G, D = (43, 55, 59, 62), (38, 54, 57, 62)
GROUND = (EM, EM, C, C, AM, AM, B, B)
RISE = (C, D, EM, G, AM, C, B, B)
ANSWER = ((71, 69, 67), (66, 67, 64), (72, 71, 67), (69, 67, 66),
          (69, 72, 76), (74, 72, 69), (71, 69, 66), (63, 66, 71))
BRIDGE = ((64, 67), (71, 69), (67, 64), (62, 64),
          (69, 72), (76, 74), (71, 66), (63, 59))

# Each entry starts a musical phrase. Drops leave space for the next entrance.
DYNAMICS = ((0, 2), (4, 5), (6, 6), (8, 8), (9, 6), (12, 7),
            (16, 9), (17, 8), (20, 5), (22, 3), (24, 4),
            (30, 5), (36, 6), (43, 7), (46, 8), (49, 10), (58, 7),
            (66, 9), (72, 5), (74, 3), (86, 4), (90, 5), (94, 6),
            (96, 7), (98, 8), (100, 10), (112, 9), (114, 7), (116, 10),
            (128, 10), (132, 11), (140, 10), (146, 9), (147, 5),
            (148, 4), (151, 3), (154, 2))


def key_code(note):
    # The chip's octave boundary falls between C and C#. A4 is KC $4A.
    octave, degree = divmod(note - 13, 12)
    return octave * 16 + KEY_CODES[degree]


# Two modulator/carrier pairs (algorithm 4). Tuple fields are ratio,
# initial attenuation, attack, first decay, second decay, sustain/release.
BELL = ((7, 33, 31, 20, 8, 0x38), (3, 39, 31, 15, 7, 0x49),
        (1, 28, 31, 12, 5, 0x48), (2, 31, 31, 16, 6, 0x59))
BOW = ((1, 31, 20, 6, 1, 0x29), (2, 43, 21, 9, 2, 0x39),
       (1, 27, 17, 6, 1, 0x29), (1, 33, 19, 7, 2, 0x39))
PICK = ((2, 28, 31, 19, 11, 0x78), (4, 41, 31, 18, 9, 0x68),
        (1, 28, 31, 13, 5, 0x49), (1, 39, 31, 15, 6, 0x59))
BRASS = ((1, 23, 23, 12, 3, 0x39), (3, 34, 25, 13, 4, 0x49),
         (1, 25, 23, 8, 1, 0x28), (2, 34, 24, 9, 2, 0x38))


# A quick-decaying high harmonic gives the muted strokes a pick transient.
# Sustained fifths use the second pair of operators for their lower body.
GUITAR = ((1, 20, 31, 18, 4, 0x5d), (5, 30, 31, 23, 9, 0x8d),
          (1, 24, 31, 8, 1, 0x2d), (2, 29, 31, 14, 3, 0x4d))
TWIN_TRAILS, INNER_CHASE, RADIAL_BURST = 12, 13, 14


def light_scene(scene, phase):
    """Outer 18, inner nine, then the center, left side, right side and top."""
    colors = []
    for index in range(27):
        if index < 18:
            head = phase * 18 // 16
            if scene == RADIAL_BURST:
                # Two fans leave the poles, meet at the sides and fold back in.
                reach = min(phase, 16 - phase) - 2
                distance = min(index % 9, 9 - index % 9)
                color = (1 if index < 9 else 2) if distance <= reach else 0
            else:
                green = (head - index) % 18
                red = (index - (9 - head)) % 18
                width = 5 if scene == INNER_CHASE else 3
                color = 1 if green < width else 2 if red < width else 0
        else:
            spoke = index - 18
            if scene == RADIAL_BURST:
                color = 1 + (spoke & 1)
            elif scene == INNER_CHASE:
                color = 1 + ((spoke + phase // 4) & 1)
            else:
                color = 0
        colors.append(color)
    # Extend the second chord past the rim. The apex is the last lamp
    # to answer and the first to go dark as the chord releases.
    if scene == RADIAL_BURST:
        reach = min(phase, 16 - phase)
        colors.extend((2, 2 if reach >= 5 else 0, 1 if reach >= 5 else 0,
                       1 if reach >= 7 else 0))
    else:
        colors.extend((2 if scene == INNER_CHASE else 0, 0, 0, 0))
    return colors


def accent_lights(bar):
    """Return (tick in bar, phase, scene) from the same clock as the notes."""
    if bar in (8, 49):
        return [(off, step, INNER_CHASE) for step, off in enumerate(range(0, BAR, 15))]
    if bar in (16, 100, 132):
        return [(off, pos, RADIAL_BURST) for off, pos in
                ((0, 0), (10, 2), (21, 4), (32, 6), (48, 8), (68, 10),
                 (82, 12), (96, 14), (110, 15))]
    if 1 <= bar < 20:
        stride = 20 if 4 <= bar < 8 or bar >= 12 else 40
        direction = -1 if 9 <= bar < 16 else 1
        return [(off, (direction * (bar * BAR + off) // 20) % 16, TWIN_TRAILS)
                for off in range(0, BAR, stride)]
    return []


def arrange():
    events = defaultdict(list)

    def fm(tick, reg, value):
        events[tick].append((1, reg, value))

    patches = (BELL, BELL, BOW, PICK, BRASS, BOW, GUITAR, GUITAR)
    # A centered lead/bass and complementary left/right backing voices.
    for ch, (patch, pan, feedback) in enumerate(zip(
            patches, (192, 128, 192, 64, 192, 128, 128, 64), (2, 2, 4, 5, 5, 3, 6, 5))):
        setup = 0 if ch < 6 else 10 + (ch - 6) * 3
        fm(setup, 0x20 + ch, pan | feedback << 3 | 4)
        fm(setup, 0x30 + ch, 0)  # Clear inherited key fraction and modulation sensitivity.
        fm(setup, 0x38 + ch, 0)
        for slot, params in enumerate(patch):
            for base, value in zip((0x40, 0x60, 0x80, 0xa0, 0xc0, 0xe0), params):
                fm(setup, base + slot * 8 + ch, value)

    def note(t, ch, pitch, ticks, tl):
        # Calibrated against the game's opening PCM. Move both carriers,
        # preserving their ratio and leaving modulator timbre independent.
        tl = max(0, tl - 7)
        fm(t, 8, ch)
        fm(t, 0x28 + ch, key_code(pitch))
        fm(t, 0x70 + ch, tl)
        fm(t, 0x78 + ch, tl + (patches[ch][3][1] - patches[ch][2][1]))
        fm(t, 8, 0x78 | ch)
        fm(t + ticks, 8, ch)

    def level(t, ch, volume):
        events[t].append((0, ch * 4 + 2, 192 | (min(63, volume + 6) if volume else 0)))

    def pitch(t, ch, midi):
        freq = round(440 * 2 ** ((midi - 69) / 12) * (1 << 17) / (25_000_000 / 512))
        events[t].extend(((0, ch * 4, freq & 255), (0, ch * 4 + 1, freq >> 8)))

    def synth(t, ch, midi, volume, hold, steps=()):
        pitch(t, ch, midi)
        level(t, ch, volume)
        for delay, drop in steps:
            level(t + delay, ch, max(0, volume - drop))
        level(t + hold, ch, 0)

    for ch, wave in ((0, 0x80), (1, 0x80), (2, 0xc0), (3, 0x19), (4, 0xc0), (5, 0x80)):
        events[0].append((0, ch * 4 + 3, wave))

    def cue(t, pos, intensity):
        events[t].append((2, 0, ((pos % 16) << 4) | intensity))

    for bar in range(BARS):
        t = bar * BAR
        energy = next(e for first, e in reversed(DYNAMICS) if first <= bar)
        buildup = 43 <= bar < 49 or 94 <= bar < 100 or 128 <= bar < 132
        bridge = 74 <= bar < 94
        peak = energy >= 9
        chord = (RISE if buildup or 49 <= bar < 58 or 132 <= bar < 146 else GROUND)[bar % 8]
        bass, third, fifth, top = chord
        if bar >= 153:
            chord = (B, EM, EM, EM)[bar - 153]
            bass, third, fifth, top = chord
        if bar == BARS - 1:
            # A release on E leads back into the first G of the bell figure.
            note(t, 0, 76, 56, 43)
            note(t, 2, 52, 75, 40)
            synth(t, 5, 64, 36, 73, ((20, 5), (42, 11), (60, 19)))
            cue(t, 0, 4)
            cue(t + 40, 0, 2)
            cue(t + 80, 0, 0)
            continue

        break_bar = bar in (48, 99)
        notes = MOTIF if bar % 8 != 7 else (67, 69, 67, 64)
        if bridge:
            # Long cello phrases over high, lightly picked bell fragments.
            line = BRIDGE[bar % 8]
            note(t, 2, line[0] - 12, 70, 24)
            note(t + 80, 2, line[1] - 12, 35, 27)
            if bar % 2:
                notes = (71, 69, 67, 66)
        for j, (offset, duration) in enumerate(((0, 32), (40, 16), (60, 16), (80, 34))):
            if break_bar and offset >= 60:
                break
            n = notes[j]
            note(t + offset, j & 1, n + (12 if bridge else 0), duration, 24 + (j != 0)*3)
            lead_level = (42 if bridge else 53) + min(4, energy // 2) - (j & 1)*2
            if bar >= 147:
                lead_level -= (bar - 147) * 2
            synth(t + offset, 5, n + (12 if bridge else 0), lead_level, duration,
                  ((6, 4), (12, 8)))
        if bar >= 2 and not bridge:
            note(t + 1, 2, bass + 12, 52 if energy >= 5 else 107, 29 - min(8, energy))
            if energy >= 5 and not break_bar:
                note(t + 68, 2, fifth, 44, 30)
        if energy >= 3:
            # Off-beat picked chords leave the center free for pinball contacts.
            for j, off in enumerate((20, 60, 100) if energy >= 5 else (20, 80)):
                if break_bar and off >= 60:
                    break
                note(t + off, 3, (third, fifth, top)[j], 15, 35 - min(7, energy))
        if energy >= 4:
            synth(t + 2, 0, bass, 47 + energy // 2, 47, ((8, 3), (25, 5)))
            if energy >= 6 and not break_bar:
                synth(t + 80, 0, bass + (7 if bar % 2 else 12), 46 + energy // 2, 28)
        if energy >= 5 and not break_bar:
            a = ANSWER[bar % 8]
            if peak or buildup:
                for beat, n in enumerate(a):
                    note(t + 3 + 40 * beat, 4, n, 31, 30 - (energy - 5))
            else:
                note(t + 42, 4, a[1], 65, 32)
            if energy >= 7:
                note(t + 4, 5, third + 12, 100, 32 - (energy - 7))
        if energy >= 5:
            # Tuned kick with a falling skin pitch, then noise snare/brushes.
            synth(t + 3, 1, 45, 54, 14, ((4, 3), (9, 11)))
            pitch(t + 6, 1, 34)
            if not break_bar:
                for off in ((40, 80) if peak else (80,)):
                    synth(t + off, 2, 70, 47 if peak else 43, 10, ((3, 7), (7, 15)))
                if energy >= 7:
                    for off in (20, 60, 100):
                        synth(t + off, 2, 87, 34, 4, ((2, 8),))
                if buildup and bar % 4 == 2:
                    synth(t + 110, 2, 76, 43, 7, ((3, 6),))
        if peak and not break_bar:
            # Split the octave attack from the main bell so the hit has an edge.
            synth(t + 2, 3, notes[0] + 12, 40 + energy // 2, 23, ((7, 5), (16, 10)))
        # The opening, the two later ensemble entrances and the final drive
        # share the same pair of amplifiers. A root and a fifth are played
        # separately so a palm mute and a ringing chord have different shapes.
        if 1 <= bar < 20 or 49 <= bar < 57 or 100 <= bar < 108 or 132 <= bar < 146:
            arrival = bar in (8, 16, 49, 100, 132)
            if arrival:
                for ch, interval in ((6, 0), (7, 7)):
                    note(t, ch, bass + 12 + interval, 71, 14 if bar == 16 else 18)
                note(t + 83, 6, bass + 12, 12, 24)
                note(t + 101, 7, bass + 19, 11, 25)
                synth(t, 4, 93, 48 if bar == 16 else 44, 32, ((4, 7), (15, 14), (25, 22)))
            else:
                strokes = (60, 100) if bar < 4 else (0, 30, 50, 80, 100)
                for j, off in enumerate(strokes):
                    gate = 14 if off in (0, 80) else 7
                    note(t + off, 6, bass + 12, gate, (25 if bar < 4 else 21) + (j & 1)*3)
                    if bar >= 4 and off in (0, 80):
                        note(t + off, 7, bass + 19, gate, 26)
                if 12 <= bar < 16 or 17 <= bar < 20:
                    upper = ANSWER[bar % 8]
                    for off, n in zip((20, 60, 100), upper):
                        note(t + off, 7, n, 18, 21)
            if bar in (6, 7, 15):
                for off, n in zip((10, 50, 90), (45, 47, 51)):
                    synth(t + off, 4, 74, n, 7, ((3, 10),))

        scenes = accent_lights(bar)
        if scenes:
            for off, pos, scene in scenes:
                cue(t + off, pos, scene)
            continue
        for beat, off in enumerate((0, 40, 80)):
            pos = bar * 3 + beat
            if break_bar and off >= 40:
                cue(t + off, pos, 0)
                continue
            strength = energy if beat == 0 else max(1, energy - (1 if buildup else 3))
            # The inner ring fills on the arrival and recedes with each accent.
            cue(t + off, pos, strength)
            if energy >= 7:
                cue(t + off + 22, pos, max(1, strength - 3))
    # The final half beat before each opening hit belongs to the release.
    # Eliminate scheduled envelopes within it and key off every sounding
    # part at its start. Table effects continue through these musical rests.
    for arrival in (8, 16):
        end = arrival * BAR
        cut = end - 20
        for tick in range(cut, end):
            events.pop(tick, None)
        for ch in range(8):
            fm(cut, 8, ch)
        for ch in range(6):
            level(cut, ch, 0)
        cue(cut, 0, 0)
    return events


def encode(events, lamps):
    stream = bytearray()
    previous = 0
    registers = {}
    for tick, writes in sorted(events.items()):
        commands = bytearray()
        for kind, register, value in writes:
            if kind == 2:
                if lamps:
                    commands.extend((0x40, 0x81, value))
                continue
            key = (kind, register)
            # Key-on/off is a strobe. Other identical writes have no effect.
            if key != (1, 8) and registers.get(key) == value:
                continue
            registers[key] = value
            if kind == 1:
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
    if len(commands) > 13 * 8192:
        raise ValueError('Christmas command stream exceeds banks 32..44')
    (output / 'COVER.CMD').write_bytes(commands)
    header = b'zm\x01' + (16).to_bytes(3, 'little') + bytes(3) + bytes((0xff, 0x3f, 0))
    header += HZ.to_bytes(2, 'little') + bytes(2)
    (output / 'SHCHEDRYK.ZSM').write_bytes(header + encode(events, lamps=False))


if __name__ == '__main__':
    import sys
    build(Path(sys.argv[1]))
