"""Build a flat Space CmdrX16 1.0 or Space Cadet exemplar runtime ZIP."""

import argparse
from copy import copy
import hashlib
import json
import os
from pathlib import Path
from shutil import copy2, copytree, ignore_patterns
import subprocess
import sys
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
BETA = Path('releases/1.0-Beta/Emulator/RAM-and-Quit')
INPUTS = ROOT / 'packaging/release-inputs'
STANDARD_ENGINE = 'e849f19accc583176f5fb9e89e0454cf750996ae'
NAMES = {
    'regular': 'SpaceCmdrX16-2D-Pinball-1.0',
    'christmas': 'SpaceCmdrX16-2D-Pinball-Christmas-1.0',
    'clone': 'SpaceCadet-X16-1.0-Exemplar',
}


def run_python(work, script, *args, **defines):
    env = {
        key: value for key, value in os.environ.items()
        if not key.startswith('CADET_')
    }
    subprocess.run(
        [sys.executable, script, *map(str, args)],
        cwd=work, env={**env, **defines}, check=True,
    )


def stage_sources(work, edition):
    native_sources = ('cadet/game', 'wireframe', 'direct/integer')
    if edition == 'christmas':
        for name in (*native_sources, 'packaging', 'tools/music-auditions/carol-final'):
            copytree(ROOT / name, work / name, ignore=ignore_patterns('__pycache__'))
        return

    # This is the source revision for the approved regular and exemplar
    # executables. Export it without switching the developer's checkout.
    source_tar = work / 'engine.tar'
    subprocess.run(
        ['git', 'archive', '-o', str(source_tar), STANDARD_ENGINE, *native_sources],
        cwd=ROOT, check=True,
    )
    subprocess.run(['tar', '-xf', source_tar, '-C', work], check=True)


def beta_archive(edition, ram):
    series = 'SpaceCadet-X16' if edition == 'clone' else 'SpaceCmdrX16'
    name = f'{series}-1.0-Beta-{ram}-65C02.zip'
    path = ROOT / BETA / name
    metadata = json.loads((path.parent / 'PACKAGE-MANIFEST.json').read_text())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != metadata['archives'][name]['sha256']:
        raise ValueError(f'{path} does not match the archived runtime manifest')
    return path


def write_package(source, destination, edition, binaries):
    with ZipFile(source) as original, ZipFile(
        destination, 'w', ZIP_DEFLATED, compresslevel=9,
    ) as result:
        for info in original.infolist():
            data = original.read(info)
            if info.filename in binaries:
                candidate = binaries[info.filename].read_bytes()
                if data != candidate:
                    raise ValueError(f'{info.filename} differs from the approved runtime')
                data = candidate
            if info.filename == 'README.txt':
                if edition == 'christmas':
                    data = data.replace(b'1.0 Beta', b'1.0', 1)
                    data = data.replace(
                        b'This is a private Christmas playtest. Some frames',
                        b'Some frames',
                        1,
                    )
                elif edition == 'regular':
                    data = data.replace(b'Space CmdrX16 1.0 Beta', b'Space CmdrX16 2D Pinball 1.0', 1)
                    data = data.replace(
                        b'This is a development preview. The broader mission system is incomplete',
                        b'The broader mission system is incomplete',
                        1,
                    )
                else:
                    data = data.replace(b'Space Cadet X16 1.0 Beta', b'Space Cadet X16 1.0 Exemplar', 1)
            result.writestr(copy(info), data, compresslevel=9)


def build(edition, ram, output):
    base = beta_archive(edition, ram)
    output.mkdir(parents=True, exist_ok=True)
    destination = output / f'{NAMES[edition]}-{ram}.zip'
    with TemporaryDirectory(prefix='pinball-release-') as tmp:
        work = Path(tmp)
        stage_sources(work, edition)
        native = work / 'cadet/play-build'
        native.mkdir()
        for pattern in ('*.h', '*.inc'):
            for entry in INPUTS.glob(pattern):
                copy2(entry, native / entry.name)

        defines = {'CADET_BUILD_PLAYER_ONLY': '1'}
        if edition == 'christmas':
            defines['CADET_CHRISTMAS'] = '1'
            pinned_path = work / BETA / base.name
            pinned_path.parent.mkdir(parents=True)
            copy2(base, pinned_path)
            run_python(work, 'tools/music-auditions/carol-final/melody.py', native / 'CAROL.ZSM')
            run_python(
                work, 'packaging/build_christmas_preview.py', 'headers',
                INPUTS / 'christmas-lamp-positions.json',
            )
        elif ram == '2MB':
            defines['CADET_COVER_AUDIO'] = '1'

        run_python(work, 'cadet/game/build_native.py', **defines)
        if edition == 'christmas':
            base = work / 'christmas.zip'
            run_python(work, 'packaging/build_christmas_preview.py', 'package', base)
        stem = 'COVER' if ram == '2MB' else 'CADET'
        binaries = {
            f'{stem}.{ext}': native / f'{stem}.{ext}' for ext in ('RUL', 'PHY', 'MEC')
        }
        binaries['PINBALL.PRG'] = native / f'{stem}.PRG'
        # Write and validate in the output directory so a failed build leaves
        # any existing deliverable intact and the final rename stays atomic.
        with TemporaryDirectory(dir=output) as staging:
            candidate = Path(staging) / destination.name
            write_package(base, candidate, edition, binaries)
            with ZipFile(candidate) as package:
                corrupt = package.testzip()
                if corrupt is not None:
                    raise ValueError(f'Failed ZIP integrity check for {corrupt}')
            candidate.replace(destination)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('edition', choices=NAMES)
    parser.add_argument('--ram', choices=('512KB', '2MB'), default='2MB')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/releases')
    args = parser.parse_args()
    if args.edition == 'christmas' and args.ram != '2MB':
        parser.error('The Christmas edition requires 2 MB of banked RAM')
    path = build(args.edition, args.ram, args.output.resolve())
    print(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path}')


if __name__ == '__main__':
    main()
