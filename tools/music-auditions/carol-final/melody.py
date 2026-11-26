"""Render a melody-first Shchedryk arrangement on the X16 at 60 score ticks/s."""
from collections import defaultdict
import json
from pathlib import Path
import sys

from arrange import Score

TICK = 1 / 60
BEAT = 28 * TICK
BAR = 3 * BEAT
# One continuous statement, a shorter reprise, then the original G-minor cadence.
FORM = [*range(1, 31), *range(13, 33), 65, 66, 67]
voices = json.loads(Path(__file__).with_name("shchedryk-notes.json").read_text())
score = Score(len(FORM) * BAR)

# The four choral lines are kept separately. Melody tracks use the original
# onsets and note relationships, with small synthesizer releases at reattacks.
for part, (chip, octave) in enumerate(((0, 12), (2, 0), (3, 0), (6, -12))):
    by_bar = defaultdict(list)
    for start, length, pitch in voices[part]:
        bar, within = divmod(start, 6)
        by_bar[bar+1].append((within, length, pitch))

    for i, measure in enumerate(FORM):
        t = i * BAR
        for step, length, pitch in by_bar[measure]:
            onset = t + step * BEAT/2
            length = min(length * BEAT/2, score.duration*TICK-onset)
            high_point = measure in range(21,29)
            rising = measure in range(17,21)
            reprise = 30 <= i < 50
            final = i >= 50
            if part == 0:
                gain = .83 if high_point else .79 if rising else .72
                gain *= (1.08 if step == 0 else .91 if step in (2,3) else 1.02)
                if reprise:
                    gain *= 1.06
            else:
                gain = (.54, .47, .56)[part-1]
                if high_point and part==1:
                    gain *= .82
                if reprise:
                    gain *= 1.08
            decay = .16 if final else min(.043, length * .14)
            stop = onset + length - decay
            score.note(chip, onset, stop, pitch+octave, gain)
            if part==0 and not final:
                delayed = min(.17, length*.52)
                score.note(10+(i%2), onset+.036,onset+.036+delayed,pitch+12,.033)
                if high_point:
                    score.note(7, onset+.012, stop, pitch+12,.35 if reprise else .29)
                elif rising and step == 0:
                    score.note(1, onset+.010, min(stop,onset+.25),pitch+12,.39)
            elif part in (1,2) and reprise and not final:
                score.note(11+part, onset+.015, min(stop,onset+.49),pitch,.043)

# Rock accents follow the phrase boundaries and the original bass motion.
# In the rising eighth-note phrases, the guitar sustains under the answer.
roots = (43, 41, 39, 38)
for i, measure in enumerate(FORM):
    t = i * BAR
    if i < 4 or i >= 51:
        continue
    if i==50:
        score.trigger(t,65,8)
        for channel, note, volume, seconds in ((4,55,.66,1.46),(5,62,.58,1.25),
                                               (8,43,.17,2.20),(13,67,.065,2.76)):
            score.note(channel,t,t+seconds,note,volume)
        continue
    if 25 <= measure <= 27:
        root = 38
    elif measure == 28:
        root = 39
    elif measure in (17,18,19,20):
        root = 43
    elif measure >= 29:
        root = (41,39,38,36)[measure-29]
    else:
        root = roots[(measure-1)%4]
        if measure in (13,14,15,16):
            root = (39,43,36,43)[measure-13]
    pullback = 28 <= i < 30
    accents = i in (4, 8, 12, 16, 20, 24, 30, 34, 38, 42, 46)
    full = (12 <= i < 28) or (30 <= i < 49)
    if pullback:
        if i == 29:
            score.trigger(t+BEAT+BEAT/2,8,6)
            score.trigger(t+BEAT*2.5,4,7)
        continue
    if not full and not accents:
        continue
    score.trigger(t,65 if accents else 17,8 if accents else 7)
    if full and measure not in (25,26,27,28):
        score.trigger(t+2*BEAT,18,7)
    if i in (11,15,19,23,33,37,41):
        score.trigger(t+BEAT*2.5,4,6)
    if not full or measure in range(21,29):
        guitar = ((0, .60, .57),)
    else:
        guitar = ((0, .39, .58),(1.5,.16,.46))
    for beat, length, strength in guitar:
        at = t+beat*BEAT
        score.note(4,at,at+length,root+12,strength)
        score.note(5,at+.019,at+length+.012,root+19,strength*.85)
    if measure < 13:
        score.note(6,t,t+BEAT*.79,root,.5)
    if full:
        score.note(8,t,t+BEAT*.85,root,.15)
        if accents:
            score.note(21,t,t+.26,88,.025)

def laser(at, voice, low, high, peak):
    """Sweep one VERA PSG voice for 133 ms with a soft attack and release."""
    reg = 4 * voice
    start = round(at / TICK)
    pan = 128 if voice == 10 else 64
    score.events[0].append(('p', reg+3, 0x80))  # triangle
    envelope = (.22, .70, 1, .82, .56, .32, .16, .06)
    for tick, amplitude in enumerate(envelope):
        hz = low * (high/low)**(tick/(len(envelope)-1))
        frequency = round(hz * 131072 / (25_000_000/512))
        score.events[start+tick].extend((
            ('p', reg, frequency & 255), ('p', reg+1, frequency >> 8),
            ('p', reg+2, pan | round(peak*amplitude)),
        ))
    score.events[start+len(envelope)].append(('p', reg+2, 0))


# Tuck the sweeps under the endings of phrases. The two rising pickups
# finish on the following downbeat, where the band is already entering.
laser(8*BAR-.19, 10, 1180, 460, 25)
laser(16*BAR-.17, 11, 390, 980, 27)
laser(24*BAR-.20, 10, 1420, 490, 24)
laser(30*BAR-.17, 11, 430, 1140, 28)
laser(44*BAR-.19, 10, 1250, 470, 25)

raw, counts = score.compile()
assert score.duration == 4452 and len(FORM) == 53
assert raw[3:6] == bytes(3)
psg_mask = int.from_bytes(raw[10:12], 'little') | (1 << 10) | (1 << 11)
raw = raw[:10] + psg_mask.to_bytes(2, 'little') + raw[12:]
# Offset 16 repeats the patch setup and first downbeat.
Path(sys.argv[1]).write_bytes(raw[:3]+(16).to_bytes(3,"little")+raw[6:])
print(f'{score.duration/60:.1f}s, {len(counts)+2} voices, {len(score.drum_events)} drum triggers')
