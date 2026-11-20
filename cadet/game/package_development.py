#!/usr/bin/env python3
"""Audit and package a committed CmdrX Cadet 0.3.1 development build.

Run --audit-only while integrating. Final packaging requires root's recorded
validation JSON (tested_commit, native_results for both RAM sizes, changes,
known_issues, functional_checks). No emulator/compiler binary is redistributed.
"""
from pathlib import Path, PurePosixPath
import argparse, datetime, hashlib, io, json, os, re, subprocess as sp, zipfile

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'cadet/play-build'
VERSION='0.3.1-dev'
RUNTIME=('CADET.PRG','CADET.RUL','CADET.PHY','MAP.BIN','TILES.BIN','PAL.BIN','SPRITES.BIN',
         'FONT.BIN','UI.BIN',*[f'GEOM{i}.BIN' for i in range(3)],
         *[f'MUSIC{i}.BIN' for i in range(2)],*[f'PCM{i}.BIN' for i in range(3)],
         *[f'DEPTH{i:02}.BIN' for i in range(9)],*[f'DYN{i}.BIN' for i in range(4)],'RINGS.BIN','MSGFONT.BIN','STARTFX.BIN')
# Geometry loader temporarily writes padding/obsolete bounds in10,11,17,18.
# The later UI/depth loads intentionally overwrite those locations.
LIVE_BANKS={
 'geometry':[1,2,3,4,5,6,7,8,9,12,13,14,15,16],
 'depth_index':[10], 'ui':[11], 'depth_data':[17,18,45,46,47,48,49,50],
 'pcm':list(range(19,31))+list(range(51,58)), 'music_buffer':[31],
 'music':list(range(32,45)), 'dynamic':[58,59,60,63], 'rules':[61], 'physics':[62],
}
BANK_LOADS={'UI.BIN':11,'CADET.RUL':61,'CADET.PHY':62,
 **{f'MUSIC{i}.BIN':b for i,b in enumerate((32,40))},
 **{f'PCM{i}.BIN':b for i,b in enumerate((19,27,51))},
 **{f'DEPTH{i:02}.BIN':b for i,b in enumerate((10,17,18,45,46,47,48,49,50))},
 **{f'DYN{i}.BIN':b for i,b in enumerate((58,59,60,63))}}
GENERATED=('MODEL.BIN','THEME.ZSM','MUSIC.LZ','UI-SPR.BIN','DEPTHROW.BIN',
 'model.json','music-pack.json','sprites.json','depth.json','dynamic.json',
 'graphics.json','resident-audio.json','dynamic-rest.png','dynamic-active.png',
 'dynamic-comparison.png','x16-layout.png','original-layout.png')
WINDOWS=r'''@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  "..\x16emu.exe" -rom "..\rom.bin" -c02 -mhz 8 -ram 512 -fsroot . -prg CADET.PRG -run -scale 2
) else (
  "%~1" -rom "%~dp1rom.bin" -c02 -mhz 8 -ram 512 -fsroot . -prg CADET.PRG -run -scale 2
)
if errorlevel 1 (
  echo.
  echo Expected x16emu.exe and its matching rom.bin in the parent folder.
  echo Or drag x16emu.exe onto this BAT, or pass its full path.
  pause
)
endlocal
'''
LINUX='''#!/bin/sh
set -eu
game_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ "$#" -gt 0 ]; then
  emu=$1
  case "$emu" in /*) ;; *) emu="$PWD/$emu";; esac
else
  emu="$game_dir/../x16emu"
fi
rom="$(dirname -- "$emu")/rom.bin"
cd "$game_dir"
exec "$emu" -rom "$rom" -c02 -mhz 8 -ram 512 -fsroot . -prg CADET.PRG -run -scale 2
'''
def sha(data): return hashlib.sha256(data).hexdigest()
def git(*args): return sp.check_output(['git',*args],cwd=ROOT)
def safe_source(name):
    p=PurePosixPath(name)
    return not(p.is_absolute() or '..' in p.parts or p.name.lower()=='rom.bin'
               or p.suffix.lower() in ('.exe','.dll','.mp4','.wav','.gif')
               or any(x in p.parts for x in ('.git','__pycache__')))
def audit(build=BUILD):
    missing=[n for n in RUNTIME if not (build/n).is_file()]
    assert not missing, f'Missing runtime assets: {missing}'
    data={n:(build/n).read_bytes() for n in RUNTIME}
    assert len(data['CADET.PRG'])==2+0x96ff, 'main PRG region must end before I/O'
    assert data['CADET.PRG'][:2]==b'\x01\x08', 'wrong PRG load address'
    assert len(data['CADET.RUL'])==8192, 'incomplete rules overlay'
    assert len(data['CADET.PHY'])==8192, 'incomplete physics overlay'
    assert data['CADET.RUL']!=data['CADET.PHY'], 'rules/physics overlays are duplicated'
    seen={}
    for owner,banks in LIVE_BANKS.items():
        for bank in banks:
            assert 0<=bank<64,(owner,bank)
            assert bank not in seen, f'Live RAM bank overlap: {owner}/{seen.get(bank)} bank{bank}'
            seen[bank]=owner
    for name,start in BANK_LOADS.items():
        n=len(data[name]); assert n>0,name
        last=start+(n-1)//8192
        owner='depth_index' if name=='DEPTH00.BIN' else (
            'depth_data' if name.startswith('DEPTH') else 'dynamic' if name.startswith('DYN')
            else 'pcm' if name.startswith('PCM') else 'music' if name.startswith('MUSIC')
            else 'rules' if name=='CADET.RUL' else 'physics' if name=='CADET.PHY' else 'ui')
        assert all(b in LIVE_BANKS[owner] for b in range(start,last+1)),(name,start,last,owner)
    assert [len(data[f'GEOM{i}.BIN']) for i in range(3)]==[65536,65536,16384]
    model=build/'MODEL.BIN'
    if model.exists(): assert model.read_bytes()==b''.join(data[f'GEOM{i}.BIN'] for i in range(3))
    assert len(data['DEPTH00.BIN'])==470*6*2
    assert len(data['MAP.BIN'])==4096 and len(data['PAL.BIN'])==512
    assert len(data['FONT.BIN'])==2048
    sprites=json.loads((build/'sprites.json').read_text())
    assert sprites['base']==4096+len(data['TILES.BIN'])
    assert sprites['bytes']==len(data['SPRITES.BIN'])
    assert sprites['end']==sprites['base']+sprites['bytes']
    assert sprites['end']+len(data['FONT.BIN'])+128<=0x1f9c0, 'sprite/font/ball scratch overlaps PSG'
    audio=json.loads((build/'resident-audio.json').read_text())
    assert audio['bytes']==sum(len(data[f'PCM{i}.BIN']) for i in range(3))
    assert audio['banks']==LIVE_BANKS['pcm']
    assert audio['load_banks']==[19,27,51]
    depth=json.loads((build/'depth.json').read_text())
    assert depth['codec']=='packbits64-deduplicated'
    assert depth['codec_exact_pixels']==365*470
    assert depth['data_bytes']==sum(len(data[f'DEPTH{i:02}.BIN']) for i in range(1,9))
    dynamic=json.loads((build/'dynamic.json').read_text())
    assert dynamic['bytes']<=4*8192
    for i in range(4): assert len(data[f'DYN{i}.BIN'])==8192
    assert 0<len(data['MSGFONT.BIN'])<=0x1900
    assert len(data['STARTFX.BIN'])==0x300
    assert len(data['PCM2.BIN'])<=6*8192+0x400
    assert 0<len(data['RINGS.BIN'])<=4096
    assert dynamic['ring_tail_bytes']==len(data['RINGS.BIN'])
    return {'runtime_files':len(data),'runtime_bytes':sum(map(len,data.values())),
            'live_banks':LIVE_BANKS,'free_banks':[b for b in range(1,64)if b not in seen],
            'sha256':{n:sha(b)for n,b in sorted(data.items())}}

def zip_bytes(files,stamp,executable=()):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            assert not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
            info=zipfile.ZipInfo(name,stamp)
            info.compress_type=zipfile.ZIP_DEFLATED
            info.create_system=3
            info.external_attr=((0o755 if name in executable else 0o644)|0o100000)<<16
            z.writestr(info,data)
    return buf.getvalue()

def source_files(commit):
    names=git('ls-files','-z').decode().split('\0')[:-1]
    files={}
    for name in names:
        if name.startswith('cadet/play-build/') or not safe_source(name):continue
        p=ROOT/name
        assert p.is_file() and not p.is_symlink(),f'Missing/nonregular tracked source: {name}'
        files['source/'+name]=p.read_bytes()
    for name in RUNTIME+GENERATED:
        p=BUILD/name
        if p.is_file():files['source/cadet/play-build/'+name]=p.read_bytes()
    for p in sorted(BUILD.glob('*.h')):
        files['source/cadet/play-build/'+p.name]=p.read_bytes()
    for name in ('audio-catalog.json','THEME.ZSM'):
        p=ROOT/'cadet/build'/name
        assert p.is_file(),name
        files['source/cadet/build/'+name]=p.read_bytes()
    for p in sorted((ROOT/'cadet/build/PCM').glob('*.PCM')):
        files['source/cadet/build/PCM/'+p.name]=p.read_bytes()
    files['source/BUILD.json']=(json.dumps({'version':VERSION,'status':'DEVELOPMENT',
        'commit':commit,'cpu':'65C02','ram_kb':512,'mhz':8,
        'asset_regeneration':'Requires separately supplied original DAT and inventory; see cadet/RESUME.md.'},
        indent=2)+'\n').encode()
    return files

def read_validation(path,commit):
    v=json.loads(path.read_text())
    assert v['tested_commit']==commit,'Validation and packaged commit differ'
    rows=v['native_results']
    assert {r['ram'] for r in rows}=={512,2048},'Need both RAM configurations'
    assert all(r['frames']>6000 for r in rows),'Need extended integrated runs'
    assert isinstance(v['changes'],list) and isinstance(v['known_issues'],list)
    assert isinstance(v['functional_checks'],list)
    return v

def readme(v,commit):
    rows='\n'.join(f"| {r['ram']} KB | {r['frames']} | {r['max_cycles']} | {r['over_budget']} |"
                  for r in v['native_results'])
    changes='\n'.join('- '+s for s in v['changes'])
    gaps='\n'.join('- '+s for s in v['known_issues'])
    checks='\n'.join('- '+s for s in v['functional_checks'])
    budget=all(r['max_cycles']<=133333 and r['over_budget']==0 for r in v['native_results'])
    performance=('The recorded workloads passed the frame budget; this is not a universal worst-case guarantee.'
        if budget else 'The strict 133333-cycle frame budget still FAILS. This build does not claim sustained 60 FPS.')
    return f'''# CmdrX Cadet {VERSION} — development playtest

This is a playable development build, not the completed Space Cadet port.
The accepted Original Table 0.2 and Wireframe 0.2 remain preserved.
Source commit: {commit}

## Run

Extract every file into one game folder. Keep x16emu.exe (or x16emu on Linux)
and its matching rom.bin in the parent folder. Double-click RUN-WINDOWS.bat.
You can also drag x16emu.exe onto that BAT. On Linux, run sh RUN-LINUX.sh.
Both launchers keep the game folder current and use stock 65C02, 8 MHz,
512 KB RAM and scale 2. The archive has no enclosing wrapper directory.

Do not copy CADET.PRG alone: CADET.RUL, CADET.PHY and all BIN assets are required.
No emulator, ROM or original Windows executable is included.

## Controls

- Space: hold to pull the main plunger; release to launch.
- Z or left Shift: left flipper.
- / or right Shift: right flipper.
- F2: new three-ball game.
- M: toggle theme music.
- Escape: exit to BASIC.

## Changes in this build

{changes}

## Validation

{checks}

| RAM | Tested frames | Worst cycles | Frames over 133333 |
| --- | ---: | ---: | ---: |
{rows}

{performance}
8 MHz is recommended. No new 2 MHz performance guarantee is made.
See VALIDATION.json for the recorded test results.

## Known issues

{gaps}

## Source and credits

SOURCE.zip contains committed source, tests, recovered table data, generated
headers and the matching converted runtime assets. To rebuild the PRG using
those assets, run sh cadet/game/build.sh in its source/ directory. Full asset
regeneration additionally needs the original DAT/inventory and dependencies
documented in cadet/RESUME.md. The compiler is LLVM-MOS SDK 23.4.0.

Original reconstruction: Andrey Muzychenko / k4zmu2a, SpaceCadetPinball,
upstream cb9b7b886244a27773f66b0b19fdc2998392565e. MIT source license included.
Original game/art/audio: Cinematronics and their respective rights holders.
X16 adaptation and validation: Codex, working with Brett Estrade.
'''

def verify_archive(path):
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        assert len(names)==len(set(names)) and z.testzip()is None
        assert all('/' not in n for n in names),'Runtime archive is not flat'
        assert set(RUNTIME)<=set(names)
        assert all(safe_source(n) for n in names)
        hashes=z.read('SHA256SUMS').decode().splitlines()
        for line in hashes:
            digest,name=line.split('  ',1);assert sha(z.read(name))==digest,name
        manifest=json.loads(z.read('MANIFEST.json'))
        for n,digest in manifest['sha256'].items():assert sha(z.read(n))==digest,n
        with zipfile.ZipFile(io.BytesIO(z.read('SOURCE.zip'))) as s:
            assert s.testzip()is None
            assert len(s.namelist())==len(set(s.namelist()))
            assert all(n.startswith('source/') and safe_source(n)for n in s.namelist())
            for n in RUNTIME:assert s.read('source/cadet/play-build/'+n)==z.read(n),n
    return {'archive_bytes':path.stat().st_size,'archive_sha256':sha(path.read_bytes()),
            'runtime_files':len(RUNTIME),'source_matches_runtime':True}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--audit-only',action='store_true')
    p.add_argument('--validation',type=Path)
    p.add_argument('--output',type=Path,default=ROOT/'cadet/releases/CmdrX_Cadet_0.3.1_Development.zip')
    args=p.parse_args()
    report=audit()
    if args.audit_only:
        print(json.dumps(report,indent=2));return
    assert args.validation,'Supply --validation with final recorded test results'
    assert not git('status','--porcelain').strip(),'Commit intended source changes before packaging'
    commit=git('rev-parse','HEAD').decode().strip()
    v=read_validation(args.validation,commit)
    epoch=int(git('show','-s','--format=%ct',commit))
    stamp=tuple(datetime.datetime.fromtimestamp(max(epoch,315532800),datetime.timezone.utc).timetuple()[:6])
    files={n:(BUILD/n).read_bytes() for n in RUNTIME}
    files['SOURCE.zip']=zip_bytes(source_files(commit),stamp)
    files['README.md']=readme(v,commit).encode()
    files['RUN-WINDOWS.bat']=WINDOWS.replace('\n','\r\n').encode('ascii')
    files['RUN-LINUX.sh']=LINUX.encode('ascii')
    files['VALIDATION.json']=(json.dumps(v,indent=2)+'\n').encode()
    manifest={'version':VERSION,'status':'DEVELOPMENT','commit':commit,**report}
    files['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    files['SHA256SUMS']=(''.join(sha(b)+'  '+n+'\n'for n,b in sorted(files.items()))).encode()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    assert not args.output.exists(),f'Refusing to replace existing package: {args.output}'
    args.output.write_bytes(zip_bytes(files,stamp,('RUN-LINUX.sh',)))
    print(json.dumps({'output':str(args.output),**verify_archive(args.output)},indent=2))
if __name__=='__main__':main()
