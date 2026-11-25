"""Linux r49 integration check for cold-start sample loading, F2 and demo skip.

Run under xvfb-run with an extracted runtime as the working directory.
"""
import argparse
import ctypes
import os
from pathlib import Path
import signal
import struct
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


# Observe HostFS opens without tracing every emulated byte read.
libc = ctypes.CDLL(None, use_errno=True)
watch_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
if watch_fd < 0:
    raise OSError(ctypes.get_errno(), 'inotify_init1')
watched = {}
for filename in ('STARTFX.BIN', 'PCM0.BIN'):
    wd = libc.inotify_add_watch(watch_fd, os.fsencode(filename), 0x20)  # IN_OPEN
    if wd < 0:
        raise OSError(ctypes.get_errno(), filename)
    watched[wd] = filename
observed = []


def loads():
    try:
        while True:
            for wd, mask, _, _ in struct.iter_unpack('iIII', os.read(watch_fd, 4096)):
                if mask & 0x20:
                    observed.append(watched[wd])
    except BlockingIOError:
        return observed


def key(name):
    sp.run(['xdotool', 'key', '--window', window, name], check=True)


with tempfile.TemporaryDirectory() as temp:
    log = Path(temp) / 'game.log'
    with log.open('wb') as out:
        process = sp.Popen(['/opt/x16emu-r49/x16emu', '-' + args.cpu, '-mhz', '8',
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
            os.close(watch_fd)
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=4)
            except (ProcessLookupError, sp.TimeoutExpired):
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
