"""Repackage the pinned Attract Fidelity preview with the shared backbox."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from backbox import replace_backbox

COVER_BANKS = ('COVER.CMD', 'COVER.HI', 'COVER.PCM')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pack(base, audio, output, source):
    old = json.loads((base/'PACKAGE-MANIFEST.json').read_text())
    archives = {}
    for name, manifest in old['archives'].items():
        payload = (base/name).read_bytes()
        if sha(payload) != manifest['sha256']:
            raise ValueError(f'Unexpected base runtime {name}')
        with zipfile.ZipFile(base/name) as archive:
            files = {f: archive.read(f) for f in archive.namelist()}
        cmdr = name.startswith('SpaceCmdr2D')
        original_name = name.replace('SpaceCmdr2D', 'SpaceCadet-X16')
        if cmdr:
            with zipfile.ZipFile(base/original_name) as archive:
                reference = {f: archive.read(f) for f in ('MAP.BIN','TILES.BIN','PAL.BIN')}
        else:
            reference = files
        replace_backbox(files, reference, cmdr)
        cover = '2048KB' in name
        if cover:
            for bank in COVER_BANKS:
                data = (audio/bank).read_bytes()
                if len(data) != len(files[bank]):
                    raise ValueError(f'Bank layout changed for {bank}')
                files[bank] = data
            files['MUSIC-CREDITS.txt'] += (
                b'The backbox preview applies another 4 dB target cut to the cover banks.\n'
            )
        files['README.txt'] = files['README.txt'].replace(
            b'Attract Fidelity Preview', b'Backbox Preview', 1)
        if cover:
            files['README.txt'] += b'\nThe native stereo cover is roughly 4 dB lower than the Attract Fidelity preview.\n'
        out = output/name.replace('Attract-Fidelity', 'Backbox')
        with zipfile.ZipFile(out, 'w') as archive:
            for f, data in sorted(files.items()):
                archive.writestr(zipfile.ZipInfo(f, (2026,11,20,0,0,0)), data,
                                 compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(out) as archive:
            assert archive.testzip() is None
        digests = {f: sha(data) for f,data in sorted(files.items())}
        allowed = {'MAP.BIN', 'TILES.BIN', 'README.txt'}
        if cover:
            allowed.update((*COVER_BANKS, 'MUSIC-CREDITS.txt'))
        assert {f for f in files if digests[f] != manifest['files'][f]} == allowed
        archives[out.name] = {'sha256': sha(out.read_bytes()), 'files': digests,
                              'baseline_archive_sha256': manifest['sha256']}
    data = {'packaging_source_commit': source, 'engine_source_commit': old['source_commit'],
            'specification_commit': old['specification_commit'], 'archives': archives}
    (output/'PACKAGE-MANIFEST.json').write_text(json.dumps(data, indent=2)+'\n')
    (output/'SHA256SUMS').write_text(''.join(f"{a['sha256']}  {name}\n" for name,a in archives.items()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', type=Path)
    parser.add_argument('cover_banks', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('packaging_source')
    a = parser.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    pack(a.base, a.cover_banks, a.output, a.packaging_source)
