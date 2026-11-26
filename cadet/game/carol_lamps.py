"""Score the Christmas overlay from the register events in the accepted rock ZSM."""
import argparse
from collections import defaultdict
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path

from christmas_music import INNER_CHASE, RADIAL_BURST, TWIN_TRAILS

from pack_christmas_carol import SONG_TICKS, ZSM_SHA256

TICKS = SONG_TICKS
STRIDE = 4
INNER_PING = 15
# Instrument indices in this arrangement's stereo sample directory.
SNARE_HAT, CRASH_KICK = 3, 4
TOM_FILLS = {0, 1}
LASER_REGS = (42, 46)


@dataclass
class Beat:
    bells: list = field(default_factory=list)
    drums: list = field(default_factory=list)
    laser: bool = False


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
            if cmd in LASER_REGS and (value & 63) >= 17:
                events[tick].laser = True
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
    bell = drum = crash = tom = laser = -1000
    finale = max(t for t, event in events.items() if event.drums)
    for tick in range(TICKS):
        event = events.get(tick)
        if event:
            if event.bells:
                bell = tick
                bell_count += 1
            if event.laser:
                laser = tick
            for instrument, _ in event.drums:
                drum = tick
                phase += 1 if instrument == SNARE_HAT else 2
                if instrument in TOM_FILLS:
                    tom = tick
                if instrument == CRASH_KICK:
                    crash = tick
        if tick % STRIDE:
            continue
        if tick - crash < 56:
            cue = pack((tick-crash)*16//56, RADIAL_BURST)
        elif tick >= finale:
            # After the final crash, let the center ring settle before the motif.
            cue = pack(8, INNER_PING) if tick-finale < 132 else 0
        elif tick - laser < 14:
            cue = pack(phase+8, TWIN_TRAILS)
        elif tick - tom < 14:
            cue = pack(phase+2, INNER_PING)
        elif tick - drum < 15:
            cue = pack(phase, INNER_CHASE)
        elif tick - bell < 12:
            cue = pack(bell_count*3, INNER_PING)
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
