#!/usr/bin/env python3
"""Package complete runtimes. No first-run import or patching.
Usage: python3 packaging/build_runtime.py ORIGINAL_DIR CMDR_2D_DIR SPEC_DIR OUT_DIR
Inputs must be prepared, tested runtime directories; only allowlisted files ship.
"""
from pathlib import Path
import sys,json,hashlib,zipfile
original,cmdr,spec,out=map(Path,sys.argv[1:])
out.mkdir(parents=True,exist_ok=True)
runtime=['CADET.PRG','CADET.PHY','CADET.RUL','FONT.BIN','MAP.BIN','TILES.BIN','PAL.BIN','SPRITES.BIN','UI.BIN']
runtime += [f'{prefix}{i}.BIN' for prefix,n in [('GEOM',3),('MUSIC',2),('PCM',3),('DYN',4)] for i in range(n)]
runtime += [f'DEPTH{i:02}.BIN' for i in range(9)]
assert len(runtime)==30
specnames=['ENGINE-SPEC.md','engine-contract.json','engine-contract.schema.json','reference-data.json']
sha=lambda b:hashlib.sha256(b).hexdigest()
source='9534fb8ed127092b0e9580ab75bfaf5d010e9b94'
spec_commit='898276b21c124afddbb242fb4dba0ff933feb049'
contract=json.loads((spec/'engine-contract.json').read_text())
pinned={Path(x['path']).name:x['sha256'] for x in contract['runtime_files']}
launcher='''@echo off
setlocal
cd /d "%~dp0" || exit /b 1
if not exist "..\\x16emu.exe" goto emulator
if not exist "..\\rom.bin" goto emulator
for %%F in (FILES) do if not exist "%%F" goto missing
"..\\x16emu.exe" -rom "..\\rom.bin" -c02 -mhz 8 -ram 512 -fsroot . -prg CADET.PRG -run -scale 2
set "RUN_RESULT=%errorlevel%"
if not "%RUN_RESULT%"=="0" pause
exit /b %RUN_RESULT%
:missing
echo A required game file is missing. Extract the complete runtime ZIP again.
pause
exit /b 1
:emulator
echo Place x16emu.exe and its matching rom.bin in the parent folder.
pause
exit /b 1
'''
manifest={'label':'1.0 Beta','packaging':'complete runtime with all 30 game files; no asset import',
'engine_source_commit':source,'specification_commit':spec_commit,
'reference_sha256':'7f2984ab9939b5ec8ffa828cdd2423c16c4faa3e3bf2afb3881fb47acf87b72b',
'windows_interactive_tested':False,'archives':[]}
for title,folder,stem in [('Space Cadet - original presentation on X16',original,'SpaceCadet-X16'),
                         ('2D Pinball - Space CmdrX16',cmdr,'SpaceCmdr2D')]:
 files={n:(folder/n).read_bytes() for n in runtime}
 for n in ['CADET.PRG','CADET.PHY','CADET.RUL','FONT.BIN']:
  assert sha(files[n])==pinned[n],n
 for n in ['LICENSE','ENGINE-THIRD-PARTY-LICENSE']:files[n]=(folder/n).read_bytes()
 files['RUN-WINDOWS.bat']=launcher.replace('FILES',' '.join(runtime)).replace('\n','\r\n').encode()
 files['README.txt']=f'''{title} -- 1.0 Beta

ALL GAME ASSETS ARE INCLUDED AND READY.
Extract this ZIP into its own folder and double-click RUN-WINDOWS.bat.
Put x16emu.exe and its matching rom.bin in the parent folder.
No other asset ZIP, import, patch, PowerShell or build tools are needed.
The emulator and ROM are the only external prerequisites.

Use separate folders for the two editions.
Flippers: Z and /. Plunger: hold/release Space. New game: F2.
Music: M. Exit: Escape.

Engine source commit: {source}
Specification commit: {spec_commit}
Human and machine-readable engine specifications are in specs/.
This package contains the complete game runtime, not standalone game/build source.
The machine reference documentation includes geometry and policy excerpts.

Linux emulator smoke tests passed at 512 KB and 2048 KB with these game bytes.
Windows interactive testing has not been performed. Occasional frame-budget
overruns and incomplete rules remain; see the release validation report.

LICENSE covers new code. ENGINE-THIRD-PARTY-LICENSE credits the recovered engine.
Original Space Cadet artwork/audio belong to their respective rights holders
and are not relicensed under the engine's MIT notice.
Source reference: https://github.com/k4zmu2a/SpaceCadetPinball
'''.encode()
 for n in specnames:files['specs/'+n]=(spec/n).read_bytes()
 name=stem+'-1.0-Beta-Runtime.zip'
 with zipfile.ZipFile(out/name,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for n,data in sorted(files.items()):
   info=zipfile.ZipInfo(n,(2026,11,19,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
   z.writestr(info,data)
 with zipfile.ZipFile(out/name) as z:
  assert z.testzip() is None and set(z.namelist())==set(files)
  for n in runtime:assert z.read(n)==(folder/n).read_bytes()
  assert not any(n.lower().endswith(('.zip','.ps1','.py','.c','.h','.s','.exe')) for n in z.namelist())
 manifest['archives'].append({'filename':name,'sha256':sha((out/name).read_bytes()),'bytes':(out/name).stat().st_size,
 'allowlist':sorted(files),'runtime_files_sha256':{n:sha(files[n]) for n in runtime}})
(out/'PACKAGE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'SHA256SUMS').write_text(''.join(x['sha256']+'  '+x['filename']+'\n' for x in manifest['archives']))
print((out/'SHA256SUMS').read_text())
