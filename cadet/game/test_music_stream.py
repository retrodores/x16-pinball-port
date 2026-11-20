"""Measure the rate-73 stereo feasibility fixture without redistributing music.

Requires the generated resident effects and r49. Pass --sd-image with a FAT
partition offset of 1 MiB (as in the r49 sample image) to test KERNAL SD reads.
"""
import argparse
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / 'cadet/play-build'
RAM_SIZES = (512, 2048)


def run_fixture(directory, rom, emulator, ram, image):
    command = [emulator, '-rom', rom, '-c02', '-mhz', '8', '-ram', str(ram),
               '-echo', 'raw', '-fsroot', '.', '-prg', 'STREAM.PRG', '-run']
    if image:
        command += ['-sdcard', image]
    log = directory / f'{ram}.log'
    with log.open('w') as output:
        process = subprocess.Popen(command, cwd=directory, stdout=output,
                                   stderr=subprocess.STDOUT,
                                   env=dict(os.environ, SDL_VIDEODRIVER='dummy',
                                            SDL_AUDIODRIVER='dummy'))
        try:
            deadline = time.monotonic() + 180
            while True:
                trace = log.read_text(errors='replace')
                if '# DONE ' in trace or process.poll() is not None:
                    break
                if time.monotonic() >= deadline:
                    raise RuntimeError(f'{ram} KB fixture timed out\n{trace[-2000:]}')
                time.sleep(.25)
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    return {key: int(value, 16) for key, value in
            re.findall(r'^# ([A-Z ]+) ([0-9a-f]{8})$', trace, re.MULTILINE)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frames', type=int, default=3500)
    parser.add_argument('--ram', type=int, choices=RAM_SIZES, action='append')
    parser.add_argument('--sd-image', type=Path)
    parser.add_argument('--mcopy', default='mcopy')
    parser.add_argument('--sdk', type=Path, default=Path('/opt/llvm-mos-sdk-23.4.0/llvm-mos'))
    parser.add_argument('--emulator-dir', type=Path, default=Path('/opt/x16emu-r49'))
    args = parser.parse_args()
    if not 1 <= args.frames <= 12000:
        parser.error('--frames must be between 1 and 12000')
    with tempfile.TemporaryDirectory(prefix='cadet-stream-') as temp:
        directory = Path(temp)
        subprocess.run([args.sdk / 'bin/mos-cx16-clang', '-Os', '-Wa,-defsym,AUDIO_STREAM_FIXTURE=1',
                        f'-DSTREAM_FRAMES={args.frames}', '-Icadet/play-build',
                        'cadet/game/audio.s', 'cadet/game/test_music_stream.c',
                        'cadet/game/test_music_stream_mix.s', '-o', directory / 'STREAM.PRG'],
                       cwd=ROOT, check=True)
        # Distinct waveforms catch stereo routing mistakes. Supply headroom for
        # catch-up after a stalled frame without ending the file prematurely.
        period = bytes(round(92 * math.sin(i * 2 * math.pi / n)) & 255
                       for i in range(443) for n in (443, 443 / 2))
        repetitions = (args.frames * 1536 + 8192) // len(period) + 1
        (directory / 'STREAM.PCM').write_bytes(period * repetitions)
        data = sorted(RUNTIME.glob('PCM?.BIN'))
        if not data:
            raise FileNotFoundError('Generate the resident game effects before running this test')
        for part in data:
            shutil.copyfile(part, directory / part.name)
        image = None
        if args.sd_image:
            image = directory / 'test.img'
            shutil.copyfile(args.sd_image, image)
            subprocess.run([args.mcopy, '-o', '-i', f'{image}@@1048576', 'STREAM.PCM',
                            *(p.name for p in data), '::/'], cwd=directory, check=True)
        ok = True
        for ram in args.ram or RAM_SIZES:
            result = run_fixture(directory, args.emulator_dir / 'rom.bin',
                                 args.emulator_dir / 'x16emu', ram, image)
            print(f'{ram} KB {"SD" if image else "HostFS"} {result}', flush=True)
            ideal = args.frames * 73 * 420000 // 65536
            ok &= (result.get('DONE') == 0 and result.get('FRAMES') == args.frames
                   and result.get('RATE') == 73 and result.get('CTRL') == 0x1a
                   and abs(result.get('SAMPLES', 0) - ideal) < 2048
                   and all(result.get(k) == 0 for k in ('EMPTY', 'FULL', 'GAPS', 'OVER')))
        return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
