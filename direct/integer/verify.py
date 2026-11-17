#!/usr/bin/env python3
from pathlib import Path
import os,re,struct,subprocess as sp,json
root=Path(__file__).resolve().parents[2];os.chdir(root)
out=root/'evidence/integer-preview';out.mkdir(exist_ok=True,parents=True)
def rows(text):return re.findall(r'^# (?:WORLD|MECHANISMS|FLIPPER) .+$',text,re.M)
for ram in (512,2048):
 for kind in ('world','mechanisms','flipper','arithmetic'):
  result=sp.run(['perl','t/run_x16.pl',f'direct/build/integer/{kind}.prg','direct/build/integer'],env=dict(os.environ,X16_RAM_KB=str(ram)),capture_output=True,text=True,timeout=90)
  (out/f'{kind}-{ram}.tap').write_text(result.stdout+result.stderr)
  assert result.returncode==0 and not re.search(r'^not ok',result.stdout,re.M),(kind,ram,result.stdout[-2000:])
  if kind!='arithmetic':
   host=Path(f'direct/build/integer/{kind}-host.tap').read_text()
   assert rows(host)==rows(result.stdout),(kind,ram,'native/host mismatch')
  print(f'{kind}: native PASS, {ram} KB',flush=True)
# These are separate, explicit fixed-point error bounds; the existing float
# tests retain their original 2e-5 tolerance and bit-exact world requirement.
original=re.findall(r'^# FLIPPER (.+)$',Path('direct/build/flipper-host.tap').read_text(),re.M)
integer=re.findall(r'^# FLIPPER (.+)$',Path('direct/build/integer/flipper-host.tap').read_text(),re.M)
assert len(original)==len(integer)==96
maximum=[0.0]*9
for a,b in zip(original,integer):
 aa,bb=a.split(),b.split();assert aa[0]==bb[0]
 for i,(x,y) in enumerate(zip(aa[1:],bb[1:])):
  ref=struct.unpack('>f',bytes.fromhex(x))[0];n=int(y,16);value=(n if n<2**31 else n-2**32)/4096
  error=abs(ref-value);maximum[i]=max(maximum[i],error)
  limit=.004 if i<2 else .012 if i<6 else .01 if i<8 else .05+.01*abs(ref)
  assert error<=limit,('flipper differential',aa[0],i,ref,value,limit)
assert '# CONTACTS 00000028' in Path('direct/build/integer/flipper-host.tap').read_text()
(out/'differential.json').write_text(json.dumps({'flipper_records':96,'contacts':40,'maximum_absolute_error':maximum,'precision_units':1/4096},indent=2)+'\n')
print('96 flipper differential records / 40 contacts PASS',flush=True)
for kind in ('normal','test'):
 symbols=sp.check_output(['/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/llvm-nm',f'direct/build/integer/preview/{kind}.prg.elf'],text=True)
 assert not re.search(r'__\w*(?:sf3|df3|sf2|df2|floatsi|fixsf|fixdf|extendsf|truncdf)',symbols),'floating-point helper linked'
print('normal and test PRGs contain no runtime floating-point helpers',flush=True)
