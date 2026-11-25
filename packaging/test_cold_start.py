"""Linux r49 integration check for cold-start sample loading, F2 and demo skip.

Run under xvfb-run with an extracted runtime as the working directory.
"""
import argparse
import os
from pathlib import Path
import re
import subprocess as sp
import tempfile
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('cpu', choices=['c02', 'c816'])
parser.add_argument('ram', choices=[512, 2048], type=int)
parser.add_argument('--early-demo', action='store_true')
args = parser.parse_args()


def wait(condition, label):
    until = time.monotonic() + 50
    while time.monotonic() < until:
        if condition():
            return
        if process.poll() is not None:
            break
        time.sleep(.025)
    raise RuntimeError(label + '\n' + log.read_bytes().decode('ascii', 'replace')[-800:])


def loads():
    # HostFS opens the asset itself with O_RDONLY. Directory searches, stats
    # and reads of the emulator binary are irrelevant to the game load order.
    return re.findall(r'openat\([^\n]*?"(?:[^"]*/)?(STARTFX\.BIN|PCM0\.BIN)", O_RDONLY[^\n]*?= \d+', trace.read_text())


def key(name):
    sp.run(['xdotool', 'key', '--window', window, name], check=True)


with tempfile.TemporaryDirectory() as temp:
    log, trace = (Path(temp) / name for name in ('game.log', 'opens.log'))
    with log.open('wb') as out:
        process = sp.Popen(['strace', '-f', '-s', '300', '-e', 'trace=openat', '-o', str(trace),
                            '/opt/x16emu-r49/x16emu', '-' + args.cpu, '-mhz', '8',
                            '-ram', str(args.ram), '-rom', '/opt/x16emu-r49/rom.bin',
                            '-scale', '1', '-fsroot', '.', '-echo', 'raw', '-prg', 'PINBALL.PRG', '-run'],
                           stdout=out, stderr=out, start_new_session=True,
                           env=dict(os.environ, SDL_AUDIODRIVER='dummy'))
        try:
            wait(lambda: b'# PLAY READY' in log.read_bytes(), 'play never started')
            assert loads() == ['STARTFX.BIN'], loads()
            window = sp.check_output(['xdotool', 'search', '--onlyvisible', '--name', 'Commander X16'],
                                     text=True).splitlines()[0]
            sp.run(['xdotool', 'windowfocus', window], check=True)
            if args.early_demo:
                key('F3')
            wait(lambda: len(loads()) >= 2, 'gameplay samples not loaded')
            assert loads() == ['STARTFX.BIN', 'PCM0.BIN'], loads()
            if args.early_demo:
                key('z')  # Take over from the demo before requesting a fresh opening.
                time.sleep(.35)
            key('F2')
            wait(lambda: len(loads()) >= 4, 'F2 did not restore both sample sets')
            assert loads() == ['STARTFX.BIN', 'PCM0.BIN'] * 2, loads()
            key('q')
            wait(lambda: b'READY.' in log.read_bytes().partition(b'# DONE')[2], 'Q did not return to BASIC')
            result = log.read_bytes().split(b'# RESULT ')[1].splitlines()[0].split()
            assert int(result[6], 16) == 0, result
            print(args.cpu, args.ram, 'early-demo' if args.early_demo else 'natural opening',
                  loads(), 'frames', int(result[0], 16), 'over', int(result[3], 16),
                  'peak', int(result[1], 16), flush=True)
        finally:
            import signal
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=4)
            except (ProcessLookupError, sp.TimeoutExpired):
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
