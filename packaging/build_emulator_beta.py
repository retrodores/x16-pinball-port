"""Relabel four verified runtime ZIPs for the 1.0 Beta emulator drafts."""

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'releases/Spinner-Preview-3'
OUTPUT = ROOT / 'releases/1.0-Beta/Emulator'
EDITIONS = (
    ('SpaceCadet-X16', 'SpaceCadet-X16', 'Space Cadet X16'),
    ('SpaceCmdr2D', 'SpaceCmdrX16', 'Space CmdrX16'),
)
MEMORY = ((512, '512KB', '512 KB'), (2048, '2MB', '2 MB'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_hashes(files):
    return {name: sha(data) for name, data in sorted(files.items())}


def build():
    source = json.loads((SOURCE / 'PACKAGE-MANIFEST.json').read_text())
    previous = json.loads((SOURCE / 'VALIDATION.json').read_text())
    assert len(source['archives']) == 4
    assert source['engine_source_commit'] == previous['engine_source_commit']
    OUTPUT.mkdir(parents=True, exist_ok=True)
    archives = {}
    inherited_checks = {}
    for original, stem, label in EDITIONS:
        for ram, suffix, memory in MEMORY:
            old = f'{original}-Spinner-3-{ram}KB-Preview.zip'
            new = f'{stem}-1.0-Beta-{suffix}.zip'
            meta = source['archives'][old]
            assert sha((SOURCE / old).read_bytes()) == meta['sha256']
            with ZipFile(SOURCE / old) as archive:
                assert archive.testzip() is None
                files = {item.filename: archive.read(item) for item in archive.infolist()}
                assert len(files) == len(archive.infolist())
            old_files = file_hashes(files)
            assert old_files == meta['files']
            assert ('MUSIC-CREDITS.txt' in files) == (ram == 2048)
            title = f'{label} 1.0 Beta ({memory})'
            heading, rest = files['README.txt'].split(b'\n', 1)
            assert b'Spinner Preview 3' in heading
            files['README.txt'] = title.encode('ascii') + b'\n' + rest
            path = OUTPUT / new
            with ZipFile(path, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
                # Preserve the source entry metadata and fixed timestamps.
                with ZipFile(SOURCE / old) as original_zip:
                    for entry in original_zip.infolist():
                        archive.writestr(entry, files[entry.filename], compresslevel=9)
            expected = file_hashes(files)
            assert {name for name in expected if expected[name] != old_files[name]} == {'README.txt'}
            with ZipFile(path) as archive, TemporaryDirectory() as folder:
                assert archive.testzip() is None
                assert len(archive.namelist()) == len(expected) and set(archive.namelist()) == set(expected)
                archive.extractall(folder)
                assert {name: sha((Path(folder) / name).read_bytes()) for name in expected} == expected
            archives[new] = {
                'sha256': sha(path.read_bytes()), 'files': expected, 'source_archive': old,
                'release': {'title': title, 'tag': f'v1.0-beta-{stem.lower()}-{suffix.lower()}-emulator'},
            }
            inherited_checks[new] = previous['fresh_zip_checks'][old]
    (OUTPUT / 'PACKAGE-MANIFEST.json').write_text(json.dumps({
        'engine_source_commit': source['engine_source_commit'],
        'specification_commit': source['specification_commit'],
        'archives': archives,
    }, indent=2) + '\n')
    (OUTPUT / 'SHA256SUMS').write_text(''.join(
        f"{meta['sha256']}  {name}\n" for name, meta in archives.items()))
    (OUTPUT / 'VALIDATION.json').write_text(json.dumps({
        'source': '../../Spinner-Preview-3/VALIDATION.json',
        'verified_in_this_package': 'All fresh extractions match the input ZIPs outside the README title line.',
        'emulator_baseline': previous['emulator'],
        'source_runtime_checks': inherited_checks,
        'windows_launcher_tested': False,
        'physical_hardware_tested': False,
        'extended_gameplay': previous['extended_gameplay'],
    }, indent=2) + '\n')


if __name__ == '__main__':
    build()
