"""Score the Christmas overlay from the register events in the accepted rock ZSM."""
import argparse
from collections import defaultdict
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path

from christmas_music import INNER_CHASE, RADIAL_BURST, TWIN_TRAILS

from pack_christmas_carol import ZSM_SHA256

TICKS = 13960
STRIDE = 4
INNER_PING = 15
# Instrument indices in this arrangement's stereo sample directory.
SNARE_HAT, CRASH_KICK = 5, 10
TOM_FILLS = {1, 2, 3, 8, 9}


@dataclass
class Beat:
    bells: list = field(default_factory=list)
    drums: list = field(default_factory=list)
    bass_level: int | None = None


def register_events(data):
    if sha256(data).hexdigest() != ZSM_SHA256:
        raise ValueError('This choreography requires the accepted Carol rock audition ZSM')
    pos, tick, pcm_volume = 16, 0, 0
    events = defaultdict(Beat)
    end = int.from_bytes(data[6:9], 'little')
    while pos < end:
        cmd = data[pos]
        pos += 1
        if cmd == 128:
            break
        if cmd > 128:
            tick += cmd - 128
        elif cmd < 64:
            value = data[pos]
            pos += 1
            if cmd == 2:  # PSG voice 0 supplies the final chord's swell and fade.
                events[tick].bass_level = value & 63 if value & 192 else 0
        elif cmd == 64:
            extension = data[pos]
            size = extension & 63
            pos += 1
            if extension >> 6 == 0:
                for reg, value in zip(data[pos:pos+size:2], data[pos+1:pos+size:2]):
                    if reg == 0:
                        pcm_volume = value & 15
                    elif reg == 2:
                        events[tick].drums.append((value, pcm_volume))
            pos += size
        else:
            size = (cmd - 64) * 2
            for reg, value in zip(data[pos:pos+size:2], data[pos+1:pos+size:2]):
                if reg == 8 and value & 120 and (value & 7) < 2:
                    events[tick].bells.append(value & 7)
            pos += size
    if tick != TICKS or cmd != 128 or pos != end:
        raise ValueError('The ZSM must complete its full song before its PCM directory')
    return events


def pack(phase, scene):
    return (phase & 15) << 4 | scene


def score(events):
    result = []
    phase = bell_count = 0
    bell = drum = crash = tom = -1000
    loud = False
    bass_level = 0
    finale = max(t for t, event in events.items() if event.drums)
    for tick in range(TICKS):
        event = events.get(tick)
        if event:
            if event.bass_level is not None:
                bass_level = event.bass_level
            if event.bells:
                bell = tick
                bell_count += 1
            for instrument, volume in event.drums:
                drum = tick
                if instrument in TOM_FILLS:
                    tom = tick
                elif instrument in (4, SNARE_HAT, CRASH_KICK):
                    # The kit marks both sections' backbeats at level 9. The
                    # middle breakdown returns to softer strokes at level 6.
                    loud = volume >= 9
                    phase += 2 if instrument != SNARE_HAT else 1
                if instrument == CRASH_KICK:
                    crash = tick
        if tick % STRIDE:
            continue
        if tick >= finale:
            if tick == finale or tick == finale + 1:
                cue = pack(0, RADIAL_BURST)
            elif bass_level >= 47:
                cue = pack(min(8, bass_level - 46), RADIAL_BURST)
            elif bass_level >= 33:
                cue = pack(0, INNER_CHASE)
            elif bass_level >= 15:
                cue = pack(8, INNER_PING)
            else:
                cue = 0
        elif tick - crash < 56:
            # Kick/crash opens the center and sends an expanding red/green
            # fan to both sides and the upper rollover, then back to the ring.
            cue = pack(min(15, (tick - crash) * 16 // 56), RADIAL_BURST)
        elif loud and tick - drum < 56:
            cue = pack(phase, INNER_CHASE if tick - drum < 17 else TWIN_TRAILS)
        elif tick - tom < 14:
            cue = pack(phase + 2, INNER_PING)
        elif tick - drum < 22:
            cue = pack(phase, TWIN_TRAILS)
        elif tick - bell < 18:
            # Each of the eight first bell strikes gets a short center/ring
            # answer; quiet passages return to this smaller vocabulary.
            cue = pack(bell_count * 3, INNER_PING)
        else:
            cue = 0
        result.append(cue)
    return bytes(result)


def write_header(track, output):
    cues = score(register_events(track.read_bytes()))
    rows = [','.join(map(str, cues[i:i+32])) for i in range(0, len(cues), 32)]
    header = (f'#define CAROL_SONG_TICKS {TICKS}u\n#define HOLIDAY_INNER_PING {INNER_PING}\n'
              f'static const uint8_t carol_cues[{len(cues)}] '
              '__attribute__((section(".holiday.rodata"))) = {\n' + ',\n'.join(rows) + '\n};\n')
    output.write_text(header)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('track', type=Path)
    parser.add_argument('header', type=Path)
    args = parser.parse_args()
    write_header(args.track, args.header)
