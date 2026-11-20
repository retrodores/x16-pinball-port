"""Update verified Quick Reset archives with the matching spinner runtime."""

import argparse
import json
from pathlib import Path
from shutil import unpack_archive
import tempfile
import zipfile

from build_backbox_preview import sha
from build_cover_balance import read_verified


def build(previous, runtime, output, source, revision=1):
    baseline = json.loads((previous / 'PACKAGE-MANIFEST.json').read_text())
    output.mkdir(parents=True, exist_ok=True)
    dynamic = json.loads((runtime / 'dynamic.json').read_text())
    first_flag = next(record['offset'] for record in dynamic['records'] if record['group'] == 481)
    assert 2 * 8192 < first_flag < 3 * 8192
    boundary = first_flag - 2 * 8192
    title = 'Spinner Preview' if revision == 1 else f'Spinner Preview {revision}'
    name_part = 'Spinner' if revision == 1 else f'Spinner-{revision}'
    archives = {}
    for original in baseline['archives']:
        program = 'COVER' if '2048KB' in original else 'CADET'
        files = read_verified(previous, original, baseline)
        assert {name: sha(data) for name, data in files.items()} == baseline['archives'][original]['files']
        updated = [f'{program}.{ext}' for ext in ('PRG', 'PHY', 'RUL', 'MEC')]
        updated += [f'{stem}{i}.BIN' for stem, count in (('DYN', 4), ('GEOM', 3)) for i in range(count)]
        updated += ['RINGS.BIN', 'RINGS2.BIN']
        if revision == 3:
            replacement = (runtime / 'UI.BIN').read_bytes()
            assert len(files['UI.BIN']) == len(replacement)
            assert files['UI.BIN'][:0x500] == replacement[:0x500]
            assert files['UI.BIN'][0x800:] == replacement[0x800:]
            updated.append('UI.BIN')
        for name in updated:
            data = (runtime / name).read_bytes()
            if name in ('DYN0.BIN', 'DYN1.BIN'):
                assert files[name] == data
            if name == 'DYN2.BIN':
                # The 2D artwork masks around the kickbacks are already in
                # this prefix. The new spinners and relocated rings follow it.
                if original.startswith('SpaceCadet-X16'):
                    assert files[name][:boundary] == data[:boundary]
                data = files[name][:boundary] + data[boundary:]
            files[name] = data
        assert len(files[f'{program}.MEC']) == 0x9f8
        assert 0 < len(files['RINGS2.BIN']) <= 0x600
        assert len(files['UI.BIN']) <= 0x1a00
        batch_prefix = b'for %%F in ('
        required = f'{program}.MEC RINGS2.BIN '.encode('ascii')
        batch = files['RUN-WINDOWS.bat']
        assert batch.count(batch_prefix) == 1
        files['RUN-WINDOWS.bat'] = batch.replace(batch_prefix, batch_prefix + required)
        readme = files['README.txt'].decode('ascii').replace('Quick Reset Preview', title)
        readme = readme.replace(baseline['engine_source_commit'], source).rstrip()
        readme += ('\n\nBoth flag spinners react to a passing ball. The red X flashes during the opening.\n'
                   'The larger Time Warp mission is still pending.\n')
        if revision == 3:
            readme += ('\nUse Up Arrow to nudge. Three close nudges trigger tilt. Clear the first three drop targets for a four-second spinner boost.\n'
                       'The upper status panel reports tilt, boost, and wormhole visits.\n')
        files['README.txt'] = readme.encode('ascii')
        path = output / original.replace('Quick-Reset', name_part)
        with zipfile.ZipFile(path, 'w') as archive:
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(name, (2026, 11, 20, 0, 0, 0))
                archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        digests = {name: sha(data) for name, data in sorted(files.items())}
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None and set(archive.namelist()) == set(digests)
        with tempfile.TemporaryDirectory() as tmp:
            unpack_archive(path, tmp)
            assert {name: sha((Path(tmp) / name).read_bytes()) for name in digests} == digests
        archives[path.name] = {'sha256': sha(path.read_bytes()), 'files': digests}
    result = {'engine_source_commit': source,
              'specification_commit': baseline['specification_commit'], 'archives': archives}
    (output / 'PACKAGE-MANIFEST.json').write_text(json.dumps(result, indent=2) + '\n')
    (output / 'SHA256SUMS').write_text(''.join(f"{a['sha256']}  {n}\n" for n, a in archives.items()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('previous', 'runtime', 'output'):
        parser.add_argument(name, type=Path)
    parser.add_argument('source')
    parser.add_argument('--revision', type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args()
    build(args.previous, args.runtime, args.output, args.source, args.revision)
