#!/usr/bin/env python3
"""Build one private CmdrX Cadet runtime from a local reference installation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from package_development import LINUX, RUNTIME, WINDOWS, audit, zip_bytes

ROOT = Path(__file__).resolve().parents[2]
STEPS = (
    'cadet/audit_audio.py', 'cadet/build_music.py', 'cadet/build_graphics.py',
    'cadet/game/pack_model.py', 'cadet/game/pack_music.py',
    'cadet/game/pack_sprites.py', 'cadet/game/pack_depth.py',
    'cadet/game/prepare_runtime.py', 'cadet/game/pack_dynamic.py',
    'cadet/game/make_startup_fx.py', 'cadet/game/build_native.py',
)
SOURCES = STEPS + tuple('cadet/game/' + name for name in (
    'import_local.py', 'message_font.py', 'package_development.py', 'analyze_dat.pl', 'engine.c',
    'engine.h', 'play.c', 'message_display.h', 'attract.c', 'attract.h', 'rules.inc', 'flipper_sweep.h', 'audio_events.h',
    'audio.s', 'music_lz.s.inc', 'depth.c', 'dynamic.c', 'signedmul.s', 'fraction.s',
    'ratio.s', 'bounds.s', 'depth_quant.s', 'mask_pixels.s', 'depth_rect.s',
    'IMPORT.md',
)) + (
    "LICENSE", "direct/vendor/LICENSE",
    'wireframe/widemul.s', 'wireframe/sqrt.s', 'wireframe/narrowmul_shared.s',
    'direct/integer/squares-lo.inc', 'direct/integer/squares-hi.inc',
)
EXPECTED = {
    'PINBALL.EXE': '2bbc8234685fe2f6324040af6ea20123cf00c4a56882ce0d9074f0beefac67bc',
    'PINBALL.DAT': '42defd5d2a339a3953fe643716aff4e35b2cea7a3e54505c82d1e78d5325bc04',
    'PINBALL.MID': 'b030f95b0d3b7b582a8c030ce548e11ab9457e2281f615af1e291401ffb0be41',
}
TABLE = 'wireframe/recovered-table.json'
RULES = 'direct/vendor/SpaceCadetPinball/control.cpp'
REFERENCE_HASHES = {
    TABLE: '174818510b3e94b36cb01884ea6a143315b61f5262028f662dd37a0827bfed35',
    RULES: '7320c196592b62eece8206127645814c4013574430bb1db93b981bf3b564aa16',
}


def source_files():
    return (*SOURCES, *(str(p.relative_to(ROOT)) for p in sorted(
        (ROOT / 'cadet/game/linker').glob('*.ld'))))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package(destination):
    files = {name: (ROOT / name).read_bytes() for name in source_files()}
    with destination.open('xb') as stream:
        stream.write(zip_bytes(files, (2026, 11, 19, 0, 0, 0)))


def convert(args):
    destination = args.output.resolve()
    if destination.exists():
        raise ValueError(f'Output already exists: {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    required_audio = re.findall(r"'(SOUND[^']+\.WAV)'",
                                (ROOT / 'cadet/game/prepare_runtime.py').read_text().split('banks=')[0])
    required = set(EXPECTED) | set(required_audio) | {'SOUND1.WAV'}
    available = {}
    for path in args.install.iterdir():
        name = path.name.upper()
        if path.is_file() and name in required:
            if name in available:
                raise ValueError(f'Ambiguous case-insensitive filename: {name}')
            available[name] = path
    missing = sorted(required - available.keys())
    if missing:
        raise ValueError('Missing installation files: ' + ', '.join(missing))
    hashes = {name: sha(path) for name, path in sorted(available.items())}
    for name, expected in EXPECTED.items():
        if hashes[name] != expected:
            raise ValueError(f'Unsupported {name} revision (SHA-256 {hashes[name]})')
    reference = {TABLE: args.table, RULES: args.rules}
    reference_hashes = {name: sha(path) for name, path in reference.items()}
    for name, digest in reference_hashes.items():
        if digest != REFERENCE_HASHES[name]:
            raise ValueError(f'Unsupported reference input {name} (SHA-256 {digest})')
    compiler = args.compiler.resolve()
    toolchain = subprocess.check_output([str(compiler), '--version'], text=True, timeout=30)
    with tempfile.TemporaryDirectory(prefix='.cadet-import-', dir=destination.parent) as tmp:
        work = Path(tmp)
        install = work / 'installation'
        install.mkdir()
        for name, path in available.items():
            shutil.copyfile(path, install / name)
        for name, path in [(name, ROOT / name) for name in source_files()] + list(reference.items()):
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        (work / 'cadet/build').mkdir()
        build = work / 'cadet/play-build'
        build.mkdir()
        subprocess.run(['perl', 'cadet/game/analyze_dat.pl', str(install / 'PINBALL.DAT'),
                        'cadet/build'], cwd=work, check=True, timeout=60)
        env = dict(os.environ, MOS_CC=str(compiler), CADET_FONT=str(args.font.resolve()),
                   CADET_DAT=str(install / 'PINBALL.DAT'), CADET_MIDI=str(install / 'PINBALL.MID'),
                   CADET_EXE=str(install / 'PINBALL.EXE'), CADET_INSTALL=str(install), CADET_INVENTORY=str(work / 'cadet/build/inventory.json'),
                   CADET_SKIP_CAPTURE='1', CADET_BUILD_PLAYER_ONLY='1')
        for step in STEPS:
            command = [sys.executable, step]
            if step == 'cadet/build_graphics.py':
                command.append(str(build))
            if step == 'cadet/game/make_startup_fx.py':
                command.append(str(build / 'STARTFX.BIN'))
            subprocess.run(command, cwd=work, env=env, check=True, timeout=180)
        manifest = audit(build)
        manifest.update(schema=1, inputs=hashes, font=sha(args.font),
                        references=reference_hashes, toolchain=toolchain.strip(),
                        converter={name: sha(ROOT / name) for name in source_files()})
        output = work / 'output'
        output.mkdir()
        for name in RUNTIME:
            shutil.copyfile(build / name, output / name)
        (output / 'RUN-WINDOWS.bat').write_bytes(WINDOWS.replace('\n', '\r\n').encode())
        launcher = output / 'run-linux.sh'
        launcher.write_bytes(LINUX.encode())
        launcher.chmod(0o755)
        (output / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
        if destination.exists():
            raise ValueError(f'Output appeared during conversion: {destination}')
        output.rename(destination)
    print(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-code', type=Path)
    parser.add_argument('--install', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--table', type=Path, default=ROOT / TABLE)
    parser.add_argument('--rules', type=Path, default=ROOT / RULES)
    parser.add_argument('--font', type=Path)
    parser.add_argument('--compiler', type=Path)
    args = parser.parse_args()
    try:
        if args.package_code:
            package(args.package_code)
        else:
            if any(value is None for value in (args.install, args.output, args.font, args.compiler)):
                parser.error('conversion requires --install, --output, --font and --compiler')
            convert(args)
    except (OSError, ValueError, AssertionError, subprocess.SubprocessError) as error:
        parser.exit(1, f'CmdrX Cadet: {error}\n')


if __name__ == '__main__':
    main()
