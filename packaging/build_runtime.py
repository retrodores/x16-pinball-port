#!/usr/bin/env python3
"""Package complete runtimes. No first-run import or patching.
Usage: python3 packaging/build_runtime.py ORIGINAL_DIR CMDR_2D_DIR SPEC_DIR OUT_DIR [--attract-preview | --message-preview]
Inputs must be prepared, tested runtime directories; only allowlisted files ship.
"""
from pathlib import Path
import argparse,json,hashlib,zipfile
parser=argparse.ArgumentParser(description=__doc__)
for name in ('original','cmdr','spec','out'):
 parser.add_argument(name,type=Path)
mode=parser.add_mutually_exclusive_group()
mode.add_argument('--attract-preview',action='store_true')
mode.add_argument('--message-preview',action='store_true')
args=parser.parse_args()
original,cmdr,spec,out=args.original,args.cmdr,args.spec,args.out
out.mkdir(parents=True,exist_ok=True)
runtime=['CADET.PRG','CADET.PHY','CADET.RUL','FONT.BIN','MAP.BIN','TILES.BIN','PAL.BIN','SPRITES.BIN','UI.BIN']
runtime += [f'{prefix}{i}.BIN' for prefix,n in [('GEOM',3),('MUSIC',2),('PCM',3),('DYN',4)] for i in range(n)]
runtime += [f'DEPTH{i:02}.BIN' for i in range(9)]
assert len(runtime)==30
specnames=['ENGINE-SPEC.md','engine-contract.json','engine-contract.schema.json','reference-data.json']
sha=lambda b:hashlib.sha256(b).hexdigest()
source='116ee4cc6d7b85c55313c54f404c4ce3f676c3fe'
runtime_pinned={
 'CADET.PRG':'78d8896c00ad765e21a32f26defc2a0ab30603668954a313e12c327d7bee2126',
 'CADET.PHY':'a01cd22e5ba27deb5c94a1bfc1eed510d21ed89baffa5effa985f2ebe775ee36',
 'CADET.RUL':'57a362ff3722fbbbaa5898210e8d37adc77fa94fb4140ea2b6badfbfd2da3fe5',
 'MUSIC0.BIN':'235d0956bff4a8fbb6bc979e2663eb55f5b50b27fa8b9593faa1338f70b831ec',
 'MUSIC1.BIN':'dcb3b3501b76b87f2790ae79945a6641d2fc2496b81cd4e806ce38924ee3b5b4',
}
label='1.0 Beta'
archive_label='1.0-Beta'
notes=('Music: M. Exit: Escape. This refresh puts the music ahead of sound effects\n'
       'and uses purple for live status text.')
if args.attract_preview:
 label='Attract Preview 1'
 archive_label='Attract-Preview-1'
 source='bc67ff64f550ad08503d528d5b263884a7855fb7'
 notes=('Music: M. Exit: Escape. Press F3 or idle for about 15 seconds for the demo.\n'
        'F2 starts a fresh game. A play control also takes over from the demo.\n'
        'This preview uses an effects-forward mix.\n\n'
        'Known timing limit: 70 of 12000 benchmark frames exceeded the cycle budget\n'
        'at each tested RAM size. See the release validation report.')
 runtime_pinned={
  'CADET.PRG':'f39633133da4a03608d9a9471747dc25464375fc1aa8127f5000876356204346',
  'CADET.PHY':'5c0e7f1da75e8050edfc709990ce96e4b9789e4d34d58bcd85bc0a34aebba492',
  'CADET.RUL':'2a3143a442b4711a6b9e039bb053e3fb4ea9342196660fac203a111af2e0bf4b',
  'MUSIC0.BIN':'d73e67d4a41a3946c697171b6c77ef77e842c01ab55a9afa8fcece772b9e00b5',
  'MUSIC1.BIN':'771273719e81d71c90271664b10f5effb5938b94ec0f719fa0c98d9be2cf224d',
 }
if args.message_preview:
 label='Attract Preview 2'
 archive_label='Attract-Preview-2'
 source='25fb5f99aaaf50d459555cec07555d59cfd232a7'
 notes=('Music: M. Exit: Escape. Press F3 or idle for about 15 seconds for the demo.\n'
        'F2 starts a fresh game. A play control also takes over from the demo.\n'
        'This build restores the music-forward mix and adds large purple messages.\n'
        'See the release validation report for timing measurements.')
 runtime_pinned={
  'CADET.PRG':'02ce0d607f43a682420843f77d6607f22a6f993c551a1fe5268d5e5cae4ca00f',
  'CADET.PHY':'c973ecafcef07e4c9547259d69135d7b8f83d15f4c63fa210620063637af9586',
  'CADET.RUL':'8c5dc5e09647cf9b22f03e5562f0a4f03ef315c6dfc635e189769f25719c30ae',
  'MUSIC0.BIN':'235d0956bff4a8fbb6bc979e2663eb55f5b50b27fa8b9593faa1338f70b831ec',
  'MUSIC1.BIN':'dcb3b3501b76b87f2790ae79945a6641d2fc2496b81cd4e806ce38924ee3b5b4',
 }
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
manifest={'label':label,'packaging':'complete runtime with all 30 game files; no asset import',
'engine_source_commit':source,'music_source_commit':('317af0be667eadd846b5cd9adc213f3e49714bb9' if args.message_preview else source),'specification_commit':spec_commit,
'reference_sha256':'7f2984ab9939b5ec8ffa828cdd2423c16c4faa3e3bf2afb3881fb47acf87b72b',
'windows_interactive_tested':False,'archives':[]}
for title,folder,stem in [('Space Cadet - original presentation on X16',original,'SpaceCadet-X16'),
                         ('2D Pinball - Space CmdrX16',cmdr,'SpaceCmdr2D')]:
 files={n:(folder/n).read_bytes() for n in runtime}
 assert sha(files['FONT.BIN'])==pinned['FONT.BIN'],'FONT.BIN'
 for n,digest in runtime_pinned.items():assert sha(files[n])==digest,n
 for n in ['LICENSE','ENGINE-THIRD-PARTY-LICENSE']:files[n]=(folder/n).read_bytes()
 files['RUN-WINDOWS.bat']=launcher.replace('FILES',' '.join(runtime)).replace('\n','\r\n').encode()
 files['README.txt']=f'''{title} -- {label}

ALL GAME ASSETS ARE INCLUDED AND READY.
Extract this ZIP into its own folder and double-click RUN-WINDOWS.bat.
Put x16emu.exe and its matching rom.bin in the parent folder.
No other asset ZIP, import, patch, PowerShell or build tools are needed.
The emulator and ROM are the only external prerequisites.

Use separate folders for the two editions.
Flippers: Z and /. Plunger: hold/release Space. New game: F2.
{notes}

Engine source commit: {source}
Specification commit: {spec_commit}
Human and machine-readable engine specifications are in specs/. They document
the reference snapshot. See the release's PACKAGE-MANIFEST.json for current
runtime file hashes.
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
 name=f'{stem}-{archive_label}-Runtime.zip'
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
