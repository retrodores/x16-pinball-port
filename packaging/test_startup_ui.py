"""Check the startup, new-game and skip transitions in an extracted runtime."""
import json
import os
from pathlib import Path
import subprocess as sp
import sys
import time

from PIL import ImageChops, ImageGrab

ram, stem, *flags = sys.argv[1:]
audio = "--audio" in flags
show_frames = "--show-frames" in flags
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
                  '.', '-prg', stem+'.PRG', '-run']+(['-wav','startup.wav'] if audio else []),
                 stdout=output, stderr=output, env=dict(os.environ, SDL_AUDIODRIVER='dummy'))
    try:
        deadline = time.monotonic()+30
        while '# PLAY READY' not in log.read_text(errors='replace'):
            assert p.poll() is None and time.monotonic()<deadline
            time.sleep(.03)
        win = sp.check_output(['xdotool','search','--onlyvisible','--name',
                               'Commander X16'],text=True).splitlines()[0]
        sp.run(['xdotool','windowfocus',win],check=True)
        geometry=sp.check_output(['xdotool','getwindowgeometry','--shell',win],text=True)
        bounds={k:int(v) for k,v in (line.split('=',1) for line in geometry.splitlines())
                if k in ('X','Y','WIDTH','HEIGHT')}
        x,y=bounds['X'],bounds['Y']
        rectangle=(x,y,x+bounds['WIDTH'],y+bounds['HEIGHT'])

        def snap():
            return ImageGrab.grab(bbox=rectangle).convert('RGB')

        def key(value):
            sp.run(['xdotool','key','--window',win,value],check=True)

        def until(test, seconds=24):
            stop = time.monotonic()+seconds
            while time.monotonic() < stop:
                frame = snap()
                if test(frame):
                    return frame
                time.sleep(.1)
            frame.save('startup-failure.png')
            raise AssertionError('Expected startup stage was not shown')

        start = snap()
        assert not lit(start,player) and not lit(start,message)
        until(lambda f: changed(f,start,table) and not lit(f,player))
        if show_frames:
            reference = Path('lamp-frames')
            reference.mkdir(exist_ok=True)
            for i in range(12):
                frame = snap()
                assert not lit(frame,player)
                frame.save(reference/f'{i:02d}.png')
                time.sleep(.11)
        until(lambda f: lit(f,player) and not lit(f,message))
        until(lambda f: lit(f,player) and lit(f,message))
        time.sleep(1.5)
        ready = snap()
        if show_frames:
            ready.save(reference/'ready.png')
        for action in ('keydown','keyup'):
            sp.run(['xdotool',action,'--window',win,'space'],check=True)
            time.sleep(.5)
        until(lambda f: lit(f,message) and changed(f,ready,message),5)
        if audio:
            key('m')
            time.sleep(.5)
        key('F2')
        until(lambda f: not lit(f,player) and not lit(f,message),5)
        # Allow a few reset cues in the audio capture before testing skip.
        if audio:
            time.sleep(1.4)
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
                  'player_before_prompt':True,'plunger_after_serve':True,'f2_restart_and_skip':True,
                  'f3_enters_demo_during_show':True,'exit':True}))
