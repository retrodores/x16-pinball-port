"""Compare the display score to actual native note, drum and volume events."""
import argparse
from pathlib import Path
import os
import re
import subprocess
import tempfile
import time

from carol_lamps import (CRASH_KICK, INNER_CHASE, INNER_PING, RADIAL_BURST,
                         STRIDE, TICKS, TWIN_TRAILS, register_events, score)
from christmas_music import light_scene


def verify(track):
    events = register_events(track.read_bytes())
    cues = score(events)
    assert len(cues) == TICKS // STRIDE
    bell_ticks = [tick for tick, e in sorted(events.items()) if e.bells]
    assert bell_ticks[:4] == [0, 28, 42, 56]
    assert cues[0] & 15 == INNER_PING
    crashes = [tick for tick, e in sorted(events.items())
               if any(i == CRASH_KICK for i, _ in e.drums)]
    assert crashes[0] == 336 and 2520 in crashes and crashes[-1] == 4200
    for tick in crashes:
        first = (tick + STRIDE - 1) // STRIDE
        begin, peak = cues[first], cues[first+7]
        assert begin & 15 == peak & 15 == RADIAL_BURST
        assert begin >> 4 == 0 and peak >> 4 == 8
        center = light_scene(RADIAL_BURST, begin >> 4)
        rim = light_scene(RADIAL_BURST, peak >> 4)
        assert center[27] and not any(center[28:])
        assert all(rim)
    laser_peaks = [tick for tick, e in sorted(events.items()) if e.laser]
    sweep_starts = [tick for tick in laser_peaks if tick-1 not in laser_peaks]
    assert sweep_starts == [662, 1335, 2005, 2511, 3686]
    for tick in sweep_starts:
        assert cues[(tick+STRIDE-1)//STRIDE] & 15 == TWIN_TRAILS
    assert not any(cues[4332//STRIDE:])
    print(f'{len(cues)} cues with five measured sweep starts and restart on the bell motif')


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
