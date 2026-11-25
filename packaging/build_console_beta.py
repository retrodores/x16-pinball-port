"""Package the updated PINBALL.PRG and overlays for both X16 emulator CPUs."""

import argparse
from copy import copy
import json
from zipfile import ZIP_DEFLATED, ZipFile

from build_emulator_beta import ROOT, file_hashes, sha
from build_pinball_beta import OUTPUT as SOURCE

OUTPUT = SOURCE.parent / 'RAM-and-Quit'
PLAYER = ROOT / 'cadet/play-build'
CPUS = {'65C02': b'-c02', '65C816': b'-c816'}


def build(engine_commit, cold_start=False):
    destination = OUTPUT.parent / "Cold-Start" if cold_start else OUTPUT
    source = json.loads((SOURCE / 'PACKAGE-MANIFEST.json').read_text())
    destination.mkdir(exist_ok=True)
    archives = {}
    for name, old in source['archives'].items():
        path = SOURCE / name
        assert sha(path.read_bytes()) == old['sha256']
        with ZipFile(path) as archive:
            records = archive.infolist()
            files = {record.filename: archive.read(record) for record in records}
        assert len(records) == len(files) and file_hashes(files) == old['files']

        memory = '2 MB' if name.endswith('-2MB.zip') else '512 KB'
        stem = 'COVER' if memory == '2 MB' else 'CADET'
        files['PINBALL.PRG'] = (PLAYER / f'{stem}.PRG').read_bytes()
        for extension in ('RUL', 'PHY', 'MEC'):
            overlay = f'{stem}.{extension}'
            files[overlay] = (PLAYER / overlay).read_bytes()
        heading, rest = files['README.txt'].split(b'\n', 1)
        readme = rest.replace(source['engine_source_commit'].encode(), engine_commit.encode())
        readme = readme.replace(b'Exit: Escape.', b'Quit to BASIC: Q or Escape.')
        assert b'Quit to BASIC: Q or Escape.' in readme

        for cpu, flag in CPUS.items():
            runtime = dict(files)
            assert runtime['RUN-WINDOWS.bat'].count(b'-c02') == 1
            runtime['RUN-WINDOWS.bat'] = runtime['RUN-WINDOWS.bat'].replace(b'-c02', flag)
            title = heading.decode().removesuffix(')') + f', {cpu})'
            runtime['README.txt'] = (
                title.encode() + b'\n'
                + readme.replace(b'Run PINBALL.PRG from this folder.',
                    f'Run PINBALL.PRG from this folder. Requires {memory} of banked RAM.'.encode())
            )
            archive_name = name.removesuffix('.zip') + f'-{cpu}.zip'
            output = destination / archive_name
            with ZipFile(output, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
                for record in records:
                    archive.writestr(copy(record), runtime[record.filename], compresslevel=9)

            hashes = file_hashes(runtime)
            with ZipFile(output) as archive:
                assert archive.testzip() is None
                assert file_hashes({key: archive.read(key) for key in archive.namelist()}) == hashes
            archives[archive_name] = {
                'sha256': sha(output.read_bytes()),
                'files': hashes,
                'source_archive': f'../Pinball-PRG/{name}',
                'source_archive_sha256': old['sha256'],
                'cpu': cpu,
                'ram_kb': 2048 if stem == 'COVER' else 512,
                'release': {
                    'title': title,
                    'tag': old['release']['tag'].removesuffix('-pinball-prg') + f'-{cpu.lower()}-' + ('cold-start' if cold_start else 'ram-quit'),
                },
            }

    assert len(archives) == 8
    (destination / 'PACKAGE-MANIFEST.json').write_text(json.dumps({
        'engine_source_commit': engine_commit,
        'specification_commit': source['specification_commit'],
        'archives': archives,
    }, indent=2) + '\n')
    (destination / 'SHA256SUMS').write_text(''.join(
        f"{metadata['sha256']}  {name}\n" for name, metadata in archives.items()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('engine_commit', help='Source commit used to build all runtime binaries')
    parser.add_argument('--cold-start', action='store_true', help='Stage the cold-start follow-up alongside RAM-and-Quit')
    args = parser.parse_args()
    build(args.engine_commit, args.cold_start)
