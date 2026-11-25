"""Compare the display score to actual native note, drum and volume events."""
import argparse
from pathlib import Path
import os
import re
import subprocess
import tempfile
import time

from carol_lamps import (CRASH_KICK, INNER_CHASE, INNER_PING, RADIAL_BURST,
                         STRIDE, TICKS, register_events, score)
from christmas_music import light_scene


def verify(track):
    events = register_events(track.read_bytes())
    cues = score(events)
    assert len(cues) == TICKS // STRIDE
    bells = [t for t in sorted(events) if events[t].bells][:8]
    assert bells == [61, 90, 119, 148, 176, 205, 234, 263]
    assert all(cue == 0 for cue in cues[:16])
    for bell in bells:
        first = (bell + STRIDE - 1) // STRIDE
        assert cues[first] & 15 == INNER_PING
        assert cues[first + 5] == 0

    crashes = [t for t, event in sorted(events.items())
               if any(instrument == CRASH_KICK for instrument, _ in event.drums)]
    assert crashes[0] == 2361 and crashes[-1] == 13168
    assert next(t for t in crashes if t >= 149.5 * 60) == 9031
    for tick in crashes[:-1]:
        first = (tick + STRIDE - 1) // STRIDE
        begin, peak = cues[first], cues[first+7]
        assert begin & 15 == peak & 15 == RADIAL_BURST
        assert begin >> 4 == 0 and peak >> 4 == 8
        center = light_scene(RADIAL_BURST, begin >> 4)
        rim = light_scene(RADIAL_BURST, peak >> 4)
        assert center[27] and not any(center[28:])
        assert all(rim[27:]) and all(rim[:27])

    breakdown = cues[129*60//STRIDE:148*60//STRIDE]
    assert any(value & 15 == INNER_PING for value in breakdown)
    assert all(value & 15 != RADIAL_BURST for value in breakdown)
    # The ending uses the actual volume ramp, even as percussive beats stop.
    assert cues[13168//STRIDE] == RADIAL_BURST
    assert cues[13280//STRIDE] == (8 << 4 | RADIAL_BURST)
    assert cues[13540//STRIDE] & 15 == INNER_CHASE
    assert cues[13680//STRIDE] & 15 == INNER_PING
    assert not any(cues[13740//STRIDE:])
    print(f'{len(cues)} cues, eight opening attacks, {len(crashes)-1} band crashes, final swell and silence verified')


def verify_renderer(track, emulator, rom, compiler):
    # Read back actual sprite attribute bytes after bounded eight-slot updates.
    # The fixture supplies controllable game claims; full game timing is separate.
    from carol_lamps import write_header
    src = Path(__file__).resolve().parent
    base_headers = src.parent / 'play-build'
    with tempfile.TemporaryDirectory() as temp:
        work = Path(temp)
        write_header(track, work / 'carol_lamp_score.h')
        prg = work / 'LAMPS.PRG'
        subprocess.run([str(compiler), '-Oz', '-DCHRISTMAS', '-I'+str(work),
                        '-I'+str(base_headers), str(src / 'test_carol_lamp_renderer.c'),
                        '-o', str(prg)], check=True, timeout=60)
        env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
        for ram in (512, 2048):
            log = work / f'{ram}.log'
            args = [str(emulator), '-rom', str(rom), '-c02', '-mhz', '8', '-ram', str(ram),
                    '-warp', '-echo', 'raw', '-fsroot', str(work), '-prg', str(prg), '-run']
            with log.open('wb') as output:
                proc = subprocess.Popen(args, cwd=work, env=env, stdout=output, stderr=output)
                try:
                    deadline = time.monotonic()+30
                    while b'# DONE' not in log.read_bytes():
                        if proc.poll() is not None or time.monotonic() > deadline:
                            raise RuntimeError(log.read_text(errors='replace')[-500:])
                        time.sleep(.1)
                finally:
                    proc.terminate()
                    try:
                        proc.wait(timeout=4)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
            result = re.search(rb'# SCORE-LAMP 00000000 ([0-9a-f]{8})', log.read_bytes())
            assert result, log.read_text(errors='replace')[-500:]
            cycles = int(result[1],16)
            assert cycles <= 133333
            print(f'{ram} KB: sprite readback passed; largest measured eight-slot update {cycles} cycles')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('track', type=Path)
    parser.add_argument('--native', action='store_true', help='also verify actual VERA sprite registers under r49')
    parser.add_argument('--emulator', type=Path, default=Path('/opt/x16emu-r49/x16emu'))
    parser.add_argument('--rom', type=Path, default=Path('/opt/x16emu-r49/rom.bin'))
    parser.add_argument('--compiler', type=Path, default=Path('/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang'))
    args = parser.parse_args()
    verify(args.track)
    if args.native:
        verify_renderer(args.track, args.emulator, args.rom, args.compiler)
