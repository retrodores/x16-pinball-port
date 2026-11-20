"""Build the two 2 MB previews with restored cover banks and new effect gain."""
import argparse
import json
from pathlib import Path
import zipfile

from build_backbox_preview import COVER_BANKS, sha

PLAYER = ('COVER.PRG', 'COVER.PHY', 'COVER.RUL')


def read_verified(folder, name, manifest):
    assert sha((folder/name).read_bytes()) == manifest['archives'][name]['sha256']
    with zipfile.ZipFile(folder/name) as z:
        return {f: z.read(f) for f in z.namelist()}


def build(backbox, attract, runtime, output, source):
    current = json.loads((backbox/'PACKAGE-MANIFEST.json').read_text())
    previous = json.loads((attract/'PACKAGE-MANIFEST.json').read_text())
    archives = {}
    for name in current['archives']:
        if '2048KB' not in name:
            continue
        files = read_verified(backbox, name, current)
        old_name = name.replace('Backbox', 'Attract-Fidelity')
        old = read_verified(attract, old_name, previous)
        for f in COVER_BANKS:
            assert (runtime/f).read_bytes() == old[f]
            files[f] = old[f]
        for f in PLAYER:
            files[f] = (runtime/f).read_bytes()
        files['MUSIC-CREDITS.txt'] = old['MUSIC-CREDITS.txt']
        readme = files['README.txt'].decode('ascii').splitlines()
        readme = [s for s in readme if 'cover is roughly' not in s and
                  'cover build reduces music gain' not in s]
        readme[0] = readme[0].replace('Backbox Preview', 'Cover Balance Preview')
        files['README.txt'] = ('\n'.join(readme).replace(current['engine_source_commit'], source)
                               .rstrip()+'\n\nCover music gain restored. Live PCM effects are raised by about 2 dB.\n').encode('ascii')
        out = output/name.replace('Backbox', 'Cover-Balance')
        with zipfile.ZipFile(out,'w') as z:
            for f,data in sorted(files.items()):
                z.writestr(zipfile.ZipInfo(f,(2026,11,20,0,0,0)),data,
                           compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        with zipfile.ZipFile(out) as z:
            assert z.testzip() is None and set(z.namelist()) == files.keys()
        archives[out.name] = {'sha256':sha(out.read_bytes()),
                              'files':{f:sha(data) for f,data in sorted(files.items())}}
    index = {'engine_source_commit':source,'specification_commit':current['specification_commit'],
             'archives':archives}
    (output/'PACKAGE-MANIFEST.json').write_text(json.dumps(index,indent=2)+'\n')
    (output/'SHA256SUMS').write_text(''.join(f"{a['sha256']}  {n}\n" for n,a in archives.items()))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('backbox','attract','runtime','output'):
        p.add_argument(name,type=Path)
    p.add_argument('source')
    a = p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    build(a.backbox,a.attract,a.runtime,a.output,a.source)
