#!/usr/bin/env python3
"""Build two allowlisted runtime ZIPs from the immutable beta reference.
Usage: python3 build_runtime.py REFERENCE.zip SPEC_DIR OUTPUT_DIR
No source archive or original table/audio is copied into either output.
"""
from pathlib import Path
import sys,zipfile,io,json,hashlib
REF_SHA='7f2984ab9939b5ec8ffa828cdd2423c16c4faa3e3bf2afb3881fb47acf87b72b'
SOURCE='9534fb8ed127092b0e9580ab75bfaf5d010e9b94'
SPEC_COMMIT='898276b21c124afddbb242fb4dba0ff933feb049'
ref,spec,out=map(Path,sys.argv[1:]);out.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(ref.read_bytes())==REF_SHA,'Reference checksum mismatch'
z=zipfile.ZipFile(ref);prefix='SpaceCmdr2D/'
read=lambda n:z.read(prefix+n)
base=zipfile.ZipFile(io.BytesIO(read('CmdrX_Cadet_0.3.1_Development.zip')))
assets=read('COPY-031-FILES.txt').decode().split()
assert len(assets)==26 and len(set(assets))==26
expected={n:sha(base.read(n)) for n in assets}
patch=json.loads(read('2D-PATCH.json'))
for n,p in patch.items():
 assert p['before'].lower()==expected[n]
 b=bytearray(base.read(n))
 for offset,h in p['writes']:b[offset:offset+len(h)//2]=bytes.fromhex(h)
 assert sha(b)==p['after'].lower()==sha(read(n)),n
specnames=['ENGINE-SPEC.md','engine-contract.json','engine-contract.schema.json','reference-data.json']
binary_names=['CADET.PRG','CADET.PHY','CADET.RUL','FONT.BIN']
# The three beta binaries must match the pinned implementation snapshot.
contract=json.loads((spec/'engine-contract.json').read_text())
hashes={Path(i['path']).name:i['sha256'] for i in contract['runtime_files']}
assert all(sha(read(n))==hashes[n] for n in binary_names)
importer=r'''$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$expected = @'
EXPECTED_JSON
'@ | ConvertFrom-Json
$isCmdr = IS_CMDR
$patch = $null
if ($isCmdr) { $patch = Get-Content -LiteralPath '2D-PATCH.json' -Raw | ConvertFrom-Json }
function Digest([byte[]]$bytes) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose() }
}
$repair = @()
foreach ($asset in $expected.PSObject.Properties) {
    $name = $asset.Name
    $ok = $false
    if (Test-Path -LiteralPath $name -PathType Leaf) {
        $hash = (Get-FileHash -LiteralPath $name -Algorithm SHA256).Hash
        $ok = $hash -eq $asset.Value
        if ($isCmdr -and $patch.PSObject.Properties[$name]) { $ok = $ok -or ($hash -eq $patch.$name.after) }
    }
    if (-not $ok) { $repair += $name }
}
if ($repair.Count) {
    $archive = Join-Path $PSScriptRoot 'CmdrX_Cadet_0.3.1_Development.zip'
    if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) { $archive = Join-Path (Split-Path $PSScriptRoot -Parent) 'CmdrX_Cadet_0.3.1_Development.zip' }
    if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) { throw 'First setup or repair needs CmdrX_Cadet_0.3.1_Development.zip in this folder or its parent.' }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($archive)
    $prepared = @{}
    try {
        foreach ($name in $repair) {
            $entries = @($zip.Entries | Where-Object { $_.FullName -ceq $name })
            if ($entries.Count -ne 1) { throw "Missing or duplicate asset: $name" }
            $stream = $entries[0].Open(); $memory = New-Object System.IO.MemoryStream
            try { $stream.CopyTo($memory); $bytes = $memory.ToArray() }
            finally { $stream.Dispose(); $memory.Dispose() }
            if ((Digest $bytes) -ne $expected.$name) { throw "Wrong or damaged asset in ZIP: $name" }
            $prepared[$name] = $bytes
        }
    } finally { $zip.Dispose() }
    foreach ($name in $prepared.Keys) { [System.IO.File]::WriteAllBytes((Join-Path $PSScriptRoot $name), $prepared[$name]) }
}
'''
launcher='''@echo off
setlocal
cd /d "%~dp0" || exit /b 1
if not exist "..\\x16emu.exe" goto emulator
if not exist "..\\rom.bin" goto emulator
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0SCRIPT_NAME"
if errorlevel 1 goto failed
"..\\x16emu.exe" -rom "..\\rom.bin" -c02 -mhz 8 -ram 512 -fsroot . -prg CADET.PRG -run -scale 2
set "RUN_RESULT=%errorlevel%"
if not "%RUN_RESULT%"=="0" pause
exit /b %RUN_RESULT%
:failed
echo Asset setup failed. Read the error above. Keep the 0.3.1 ZIP zipped.
pause
exit /b 1
:emulator
echo Place x16emu.exe and its matching rom.bin in the parent folder.
pause
exit /b 1
'''
results=[]
for cmdr in (False,True):
 name=('SpaceCmdr2D' if cmdr else 'SpaceCadet-X16')+'-1.0-Beta-Runtime.zip'
 title='2D Pinball - Space CmdrX16' if cmdr else 'Space Cadet - original presentation on X16'
 helper='APPLY-2D.ps1' if cmdr else 'IMPORT-ORIGINAL.ps1'
 files={n:read(n) for n in binary_names+['LICENSE','ENGINE-THIRD-PARTY-LICENSE','COPY-031-FILES.txt']}
 script=importer.replace('EXPECTED_JSON',json.dumps(expected,indent=2)).replace('IS_CMDR','$true' if cmdr else '$false')
 if cmdr:script+='\n'+read('APPLY-2D.ps1').decode();files['2D-PATCH.json']=read('2D-PATCH.json')
 files[helper]=script.encode()
 files['RUN-WINDOWS.bat']=launcher.replace('SCRIPT_NAME',helper).replace('\n','\r\n').encode()
 files['README.txt']=f'''{title} -- 1.0 Beta

Extract into its own writable folder. Put x16emu.exe and its matching rom.bin
in the parent folder. Put the unopened CmdrX_Cadet_0.3.1_Development.zip in
the game folder or its parent, then double-click RUN-WINDOWS.bat.
PowerShell 5.1 or newer is required. No compiler or manual asset copying is needed.
The launcher validates assets and imports missing/damaged files automatically.
After successful setup the local ZIP is needed only for repair.
Use separate folders for the two editions; their presentation files differ.

Flippers: Z and /. Plunger: hold/release Space. New game: F2.
Music: M. Exit: Escape.

This is an X16 adaptation, not the Windows executable. Original playfield,
audio, emulator and ROM are not included. Supply the local asset ZIP yourself.
{'The 2D artwork patch is applied automatically.' if cmdr else 'Original presentation is imported without the 2D artwork patch.'}
Engine source commit: {SOURCE}
Specification commit: {SPEC_COMMIT}
Both editions use identical beta PRG and overlay bytes from the verified reference.
Original mode uses that same current engine, not the older 0.3.1 engine binary.

The specs/ folder contains the human and machine engine specifications.
It is documentation; JSON reference data includes geometry and policy excerpts.
No standalone source/build files or nested archives are included.

Known limitations include occasional frame-budget overruns and incomplete rules.
Windows interactive testing has not been performed for this package.
See the adjacent release validation report for exactly what was tested.

Licensing: LICENSE covers new code; ENGINE-THIRD-PARTY-LICENSE credits the
recovered engine. Original Space Cadet artwork/audio belong to their respective
rights holders and are not relicensed here. Microsoft/Maxis/Cinematronics
Space Cadet source reference: https://github.com/k4zmu2a/SpaceCadetPinball
'''.encode()
 # Preserve original license text, correcting only references to absent notice files.
 files['LICENSE']=files['LICENSE'].replace(b'See README.md and REFERENCE-LICENSE.txt for source attribution.',b'See README.txt and ENGINE-THIRD-PARTY-LICENSE for source attribution.')
 for n in specnames:files['specs/'+n]=(spec/n).read_bytes()
 allowed=set(binary_names+['LICENSE','ENGINE-THIRD-PARTY-LICENSE','COPY-031-FILES.txt',helper,'RUN-WINDOWS.bat','README.txt']+(['2D-PATCH.json'] if cmdr else [])+['specs/'+n for n in specnames])
 assert set(files)==allowed
 with zipfile.ZipFile(out/name,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as dest:
  for n in sorted(allowed):
   info=zipfile.ZipInfo(n,(2026,11,19,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
   dest.writestr(info,files[n])
 with zipfile.ZipFile(out/name) as check:
  assert check.testzip() is None and set(check.namelist())==allowed
  assert not any(n.lower().endswith(('.zip','.py','.c','.h','.s','.exe')) for n in check.namelist())
 results.append({'filename':name,'sha256':sha((out/name).read_bytes()),'bytes':(out/name).stat().st_size,'allowlist':sorted(allowed)})
(out/'SHA256SUMS').write_text(''.join(r['sha256']+'  '+r['filename']+'\n' for r in results))
(out/'PACKAGE-MANIFEST.json').write_text(json.dumps({'label':'1.0 Beta','engine_source_commit':SOURCE,'specification_commit':SPEC_COMMIT,'reference_sha256':REF_SHA,'archives':results,'windows_interactive_tested':False},indent=2)+'\n')
print(json.dumps(results,indent=2))
