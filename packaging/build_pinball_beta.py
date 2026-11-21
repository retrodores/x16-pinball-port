"""Rename the entry point in each verified 1.0 Beta emulator ZIP."""

import json
from copy import copy
from tempfile import TemporaryDirectory
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from build_emulator_beta import OUTPUT as SOURCE, file_hashes, sha

OUTPUT = SOURCE / 'Pinball-PRG'


def build():
    manifest = json.loads((SOURCE / 'PACKAGE-MANIFEST.json').read_text())
    assert len(manifest['archives']) == 4
    validation = json.loads((SOURCE / 'VALIDATION.json').read_text())
    OUTPUT.mkdir(exist_ok=True)
    for name, metadata in manifest['archives'].items():
        ram = validation['source_runtime_checks'][name]['ram_kb']
        old_program = {512: 'CADET.PRG', 2048: 'COVER.PRG'}[ram]
        source = SOURCE / name
        assert sha(source.read_bytes()) == metadata['sha256']
        with ZipFile(source) as archive:
            assert archive.testzip() is None
            entries = archive.infolist()
            files = {entry.filename: archive.read(entry) for entry in entries}
        assert len(files) == len(entries) and file_hashes(files) == metadata['files']
        assert {key for key in files if key.endswith('.PRG')} == {old_program}
        launcher = files['RUN-WINDOWS.bat']
        assert launcher.count(old_program.encode()) == 2
        assert f'-ram {ram} -fsroot . -prg {old_program} -run -scale 2'.encode() in launcher
        files['RUN-WINDOWS.bat'] = launcher.replace(old_program.encode(), b'PINBALL.PRG')
        heading, remainder = files['README.txt'].split(b'\n', 1)
        files['README.txt'] = (
            heading + b'\n\n'
            b'Run PINBALL.PRG from this folder. The embedded specifications document\n'
            b'the original build names. The package launcher uses the filename above.\n'
            + remainder
        )
        files['PINBALL.PRG'] = files.pop(old_program)
        output = OUTPUT / name
        with ZipFile(output, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
            for original in entries:
                entry = copy(original)
                if entry.filename == old_program:
                    entry.filename = 'PINBALL.PRG'
                archive.writestr(entry, files[entry.filename], compresslevel=9)
        expected = file_hashes(files)
        original_hashes = metadata['files']
        assert expected['PINBALL.PRG'] == original_hashes[old_program]
        assert set(expected) == set(original_hashes) - {old_program} | {'PINBALL.PRG'}
        assert all(expected[key] == original_hashes[key] for key in expected
                   if key not in {'PINBALL.PRG', 'RUN-WINDOWS.bat', 'README.txt'})
        with ZipFile(output) as archive, TemporaryDirectory() as folder:
            assert archive.testzip() is None
            assert set(archive.namelist()) == set(expected) and len(archive.namelist()) == len(expected)
            archive.extractall(folder)
            assert file_hashes({key: (Path(folder) / key).read_bytes() for key in expected}) == expected
        metadata['source_archive'] = f'../{name}'
        metadata['source_archive_sha256'] = metadata['sha256']
        metadata['sha256'] = sha(output.read_bytes())
        metadata['files'] = expected
        metadata['release']['tag'] += '-pinball-prg'

    (OUTPUT / 'PACKAGE-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (OUTPUT / 'SHA256SUMS').write_text(''.join(
        f"{meta['sha256']}  {name}\n" for name, meta in manifest['archives'].items()))


if __name__ == '__main__':
    build()
