"""Verify that BASIC can LOAD and execute another PRG after Pinball exits."""

import argparse
import os
from pathlib import Path
import subprocess as sp
import time
import tkinter as tk

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('cpu', choices=('c02', 'c816'))
parser.add_argument('ram', type=int)
parser.add_argument('--required-ram', type=int, choices=(512, 2048))
parser.add_argument('--quit-key', default='q', choices=('q', 'Escape'))
args = parser.parse_args()
log = Path('console-return.log')
fixture = Path('NEXT.PRG')
# Load at $1000. Emit a marker through the KERNAL, then return to BASIC.
marker = b'NEXT PROGRAM OK'
program = b''.join(bytes((0xA9, char, 0x20, 0xD2, 0xFF)) for char in b'\r' + marker + b'\r')
with fixture.open('xb') as f:
    f.write(b'\x00\x10' + program + b'\x60')


def wait_for(predicate):
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        clipboard.update()
        output = log.read_bytes()
        if predicate(output):
            return output
        assert emulator.poll() is None, output
        time.sleep(.04)
    raise AssertionError(log.read_bytes())


clipboard = tk.Tk()
clipboard.withdraw()
try:
    with log.open('wb') as output:
        emulator = sp.Popen(
            ['/opt/x16emu-r49/x16emu', '-rom', '/opt/x16emu-r49/rom.bin',
             '-' + args.cpu, '-mhz', '8', '-ram', str(args.ram), '-fsroot', '.',
             '-echo', 'raw', '-prg', 'PINBALL.PRG', '-run', '-scale', '2'],
            stdout=output, stderr=output, env=dict(os.environ, SDL_AUDIODRIVER='dummy'))
        try:
            if args.required_ram:
                required = {512: b'512 KB', 2048: b'2 MB'}[args.required_ram]
                again = b'PINBALL NEEDS ' + required + b' OF BANKED RAM.'
                result = wait_for(lambda text: b'READY.' in text.partition(again)[2])
                assert b'# PLAY READY' not in result and b'LOADING...' not in result, result
                if args.required_ram == 2048:
                    assert b'TRY THE 512 KB EDITION INSTEAD.' in result, result
            else:
                wait_for(lambda text: b'# PLAY READY' in text)

            window = sp.check_output(['xdotool', 'search', '--onlyvisible', '--name',
                                      'Commander X16'], text=True).splitlines()[0]
            sp.run(['xdotool', 'windowfocus', window], check=True)
            if not args.required_ram:
                sp.run(['xdotool', 'key', args.quit_key], check=True)
                wait_for(lambda text: b'READY.' in text.partition(b'# DONE')[2])

            def basic(command):
                clipboard.clipboard_clear()
                clipboard.clipboard_append(command + '\r')
                clipboard.update()
                sp.run(['xdotool', 'key', '--window', window, 'Control_L+v'], check=True)

            offset = log.stat().st_size
            basic('LOAD"NEXT.PRG",8,1')
            wait_for(lambda text: b'READY.' in text[offset:] and b'LOADING' in text[offset:])
            offset = log.stat().st_size
            basic('SYS4096')
            wait_for(lambda text: marker in text[offset:] and b'READY.' in text[offset:])
        finally:
            if emulator.poll() is None:
                emulator.terminate()
                try:
                    emulator.wait(5)
                except sp.TimeoutExpired:
                    emulator.kill()
                    emulator.wait()
finally:
    clipboard.destroy()
    fixture.unlink()

print(f'{args.cpu} {args.ram} KB: BASIC loaded and ran NEXT.PRG')
