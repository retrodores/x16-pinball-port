"""Independent LLVM-tool check of emitted PRG and same-address bank overlays.

Run after a normal build: python3 cadet/game/test_build_native.py CADET TEST
TIP is the default fixture. Both named overlays must be live and distinct.
"""
from pathlib import Path
import subprocess as sp,tempfile,re,sys,json
from build_native import OUT,CC,MAIN_BYTES
toolbin=Path(CC).parent
reports=[]
for name in sys.argv[1:] or ['TIP']:
 elf=OUT/(name+'.image.elf')
 listing=sp.check_output([str(toolbin/'llvm-readelf'),'-SW',str(elf)],text=True)
 sections={n:(int(a,16),int(sz,16))for n,a,sz in re.findall(
  r'\[\s*\d+\]\s+(\S+)\s+PROGBITS\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)',listing)}
 assert all(n in sections and sections[n][1]>0 for n in ('.rules','.physics'))
 assert sections['.rules'][0]==sections['.physics'][0]==0xa000
 wanted=[n for n,(addr,size)in sections.items()if size and (0x801<=addr<0x9f00 or n in ('.rules','.physics'))]
 with tempfile.TemporaryDirectory(prefix='cadet-elf-')as temp:
  tmp=Path(temp)
  args=[str(toolbin/'llvm-objcopy')]
  for n in wanted:args+=['--dump-section',n+'='+str(tmp/n[1:])]
  sp.run([*args,str(elf),str(tmp/'copy.elf')],check=True)
  prg=(OUT/(name+'.PRG')).read_bytes()
  assert len(prg)==MAIN_BYTES and prg[:2]==b'\x01\x08'
  overlays=[]
  for n in wanted:
   body=(tmp/n[1:]).read_bytes();addr,size=sections[n];assert len(body)==size
   if n in ('.rules','.physics'):
    ext='.RUL'if n=='.rules'else'.PHY';got=(OUT/(name+ext)).read_bytes()
    assert size<=8192 and len(got)==8192
    assert got==body.ljust(8192,b'\0'),(name,n,'wrong named overlay')
    overlays.append(got)
   else:
    offset=2+addr-0x801
    assert prg[offset:offset+size]==body,(name,n,'main PRG mismatch')
  assert overlays[0]!=overlays[1],(name,'overlays duplicated')
 row={'program':name,'checked_sections':wanted,'overlays_distinct':True,'llvm_extract_matches':True}
 reports.append(row);print(row,flush=True)
(OUT/'build-native-results.json').write_text(json.dumps(reports,indent=2)+'\n')
