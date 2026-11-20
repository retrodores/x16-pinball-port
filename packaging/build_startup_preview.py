"""Repackage the checked 512 KB Backbox and 2 MB Cover Balance runtimes."""
import argparse
import json
from pathlib import Path
import zipfile

from build_cover_balance import read_verified
from build_backbox_preview import sha


def build(releases, runtime, out, source, startup_audio):
    archives = {}
    manifests = {}
    for base, ram, program in (('Backbox', '512', 'CADET'),
                               ('Cover-Balance', '2048', 'COVER')):
        folder = releases/(base+'-Preview')
        manifest = json.loads((folder/'PACKAGE-MANIFEST.json').read_text())
        manifests[base] = manifest
        for edition in ('SpaceCadet-X16', 'SpaceCmdr2D'):
            old = f'{edition}-{base}-{ram}KB-Preview.zip'
            files = read_verified(folder, old, manifest)
            for suffix in ('PRG','PHY','RUL'):
                f = f'{program}.{suffix}'
                files[f] = (runtime/f).read_bytes()
            readme = files['README.txt'].decode('ascii')
            readme = readme.replace(base.replace('-', ' ')+' Preview','Startup Preview')
            readme = readme.replace(manifest['engine_source_commit'],source)
            files['README.txt'] = (readme.rstrip()+
                '\n\nThe opening animates the playfield lamps before the first ball is served.\n'
                'F2 starts a new game or skips an active opening.\n').encode('ascii')
            title = 'Startup'
            if startup_audio:
                title = 'Startup-Audio'
                sample = (runtime/'STARTFX.BIN').read_bytes()
                assert len(sample) == 768
                files['STARTFX.BIN'] = sample
                files['RUN-WINDOWS.bat'] = files['RUN-WINDOWS.bat'].replace(
                    b'for %%F in (', b'for %%F in (STARTFX.BIN ', 1)
                files['README.txt'] += b'Original electronic pulses play on cold start and F2.\n'
            path = out/f'{edition}-{title}-{ram}KB-Preview.zip'
            with zipfile.ZipFile(path,'w') as z:
                for name,data in sorted(files.items()):
                    z.writestr(zipfile.ZipInfo(name,(2026,11,20,0,0,0)), data,
                               compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
            with zipfile.ZipFile(path) as z:
                assert z.testzip() is None and set(z.namelist()) == files.keys()
            archives[path.name] = {'sha256':sha(path.read_bytes()),
                                   'files':{f:sha(data) for f,data in sorted(files.items())}}
    spec = manifests['Backbox']['specification_commit']
    assert spec == manifests['Cover-Balance']['specification_commit']
    manifest = {'engine_source_commit':source,'specification_commit':spec,'archives':archives}
    (out/'PACKAGE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'SHA256SUMS').write_text(''.join(f"{a['sha256']}  {n}\n" for n,a in archives.items()))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('releases','runtime','output'):
        p.add_argument(name,type=Path)
    p.add_argument('source')
    p.add_argument('--startup-audio', action='store_true')
    a = p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    build(a.releases,a.runtime,a.output,a.source,a.startup_audio)
