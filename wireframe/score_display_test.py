#!/usr/bin/env python3
"""Play the distribution PRG and verify the live score changes on screen."""
from pathlib import Path
from PIL import Image, ImageChops
import os, subprocess as sp, time

r = Path(__file__).resolve().parents[1]
o = r / 'wireframe/evidence'
with (o / 'score-display.log').open('w') as stream:
    p = sp.Popen(['/opt/x16emu-r49/x16emu', '-c02', '-rom',
                  '/opt/x16emu-r49/rom.bin', '-ram', '512', '-mhz', '8',
                  '-scale', '1', '-fsroot', str(r / 'wireframe/build'),
                  '-prg', str(r / 'wireframe/build/c02/CADET.PRG'), '-run'],
                 stdout=stream, stderr=stream,
                 env=dict(os.environ, SDL_AUDIODRIVER='dummy'))
    try:
        window = sp.check_output(['xdotool', 'search', '--sync', '--onlyvisible',
                                  '--name', 'Commander X16'], timeout=10).decode().splitlines()[0]
        sp.run(['xdotool', 'windowfocus', window], check=True)
        time.sleep(3)
        def key(kind, name):
            sp.run(['xdotool', kind, '--window', window, name], check=True)
        def shot(name):
            path = o / name
            sp.run(['import', '-window', window, str(path)], check=True)
            return Image.open(path).resize((320, 240), Image.Resampling.NEAREST).convert('RGB')
        key('key', 'n'); time.sleep(.4)
        initial = shot('score-zero.png').crop((207, 60, 287, 98))
        changed = False
        for attempt in range(8):
            key('keydown', 'space'); time.sleep(1.4); key('keyup', 'space')
            for phase in range(8):
                key('keydown', 'Shift_L' if phase % 2 else 'Shift_R')
                time.sleep(.12)
                key('keyup', 'Shift_L' if phase % 2 else 'Shift_R')
                time.sleep(.12)
            current = shot('score-live.png')
            if ImageChops.difference(initial, current.crop((207, 60, 287, 98))).getbbox():
                changed = True
                break
        assert changed, 'score did not visibly change during keyboard-controlled play'
        print('Normal 65C02 PRG: visible live score advanced during keyboard play PASS')
    finally:
        p.terminate()
        try: p.wait(timeout=5)
        except sp.TimeoutExpired: p.kill(); p.wait()
