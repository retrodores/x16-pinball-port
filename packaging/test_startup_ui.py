"""Check the startup, new-game and skip transitions in an extracted runtime."""
import json
import os
from pathlib import Path
import subprocess as sp
import sys
import time

from PIL import Image, ImageChops

ram, stem = sys.argv[1:]
player = (430, 260, 610, 306)
message = (430, 333, 610, 430)
table = (85, 75, 295, 360)
log = Path('startup.log')


def changed(a, b, roi):
    return ImageChops.difference(a.crop(roi), b.crop(roi)).getbbox() is not None


def lit(img, roi):
    return img.crop(roi).getbbox() is not None


with log.open('w') as output:
    p = sp.Popen(['/opt/x16emu-r49/x16emu', '-rom', '/opt/x16emu-r49/rom.bin',
                  '-c02', '-mhz', '8', '-ram', ram, '-echo', 'raw', '-fsroot',
                  '.', '-prg', stem+'.PRG', '-run'],
                 stdout=output, stderr=output, env=dict(os.environ, SDL_AUDIODRIVER='dummy'))
    try:
        deadline = time.monotonic()+30
        while '# PLAY READY' not in log.read_text(errors='replace'):
            assert p.poll() is None and time.monotonic()<deadline
            time.sleep(.03)
        win = sp.check_output(['xdotool','search','--onlyvisible','--name',
                               'Commander X16'],text=True).splitlines()[0]
        sp.run(['xdotool','windowfocus',win],check=True)
        def snap():
            data = sp.check_output(['import','-window',win,'ppm:-'])
            from io import BytesIO
            return Image.open(BytesIO(data)).convert('RGB')

        def key(value):
            sp.run(['xdotool','key','--window',win,value],check=True)

        def until(test, seconds=24):
            stop = time.monotonic()+seconds
            while time.monotonic() < stop:
                frame = snap()
                if test(frame):
                    return frame
                time.sleep(.1)
            raise AssertionError('Expected startup stage was not shown')

        start = snap()
        assert not lit(start,player) and not lit(start,message)
        until(lambda f: changed(f,start,table) and not lit(f,player))
        until(lambda f: lit(f,player) and not lit(f,message))
        ready = until(lambda f: lit(f,player) and lit(f,message))
        key('F2')
        until(lambda f: not lit(f,player) and not lit(f,message),5)
        # F2 during the show advances directly to the ready prompt.
        key('F2')
        until(lambda f: lit(f,player) and not changed(f,ready,message),5)
        key('F2')
        until(lambda f: not lit(f,player) and not lit(f,message),5)
        key('F3')
        until(lambda f: lit(f,player) and changed(f,ready,message),5)
        key('Escape')
        deadline=time.monotonic()+5
        while '# DONE' not in log.read_text(errors='replace'):
            assert time.monotonic()<deadline
            time.sleep(.1)
    finally:
        if p.poll() is None:
            p.terminate()
            try: p.wait(5)
            except sp.TimeoutExpired: p.kill();p.wait()
print(json.dumps({'ram_kb':int(ram),'cold_start':True,'changing_lamps':True,
                  'player_before_prompt':True,'f2_restart_and_skip':True,
                  'f3_enters_demo_during_show':True,'exit':True}))
