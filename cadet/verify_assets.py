#!/usr/bin/env python3
"""Decode the emitted format independently, then compare with the note ledger."""
from pathlib import Path
import json,csv,hashlib,collections
r=Path(__file__).resolve().parent/'build';b=(r/'THEME.ZSM').read_bytes()
assert b[:3]==b'zm\x01'and int.from_bytes(b[3:6],'little')==16
assert int.from_bytes(b[12:14],'little')==60
assert b==b''.join(p.read_bytes()for p in sorted(r.glob('MUSIC[0-9].BIN')))
p=16;t=0;fm=0;psg=0;attacks=[];drums=[];registers={}
while True:
 command=b[p];p+=1
 if command==128:break
 if command>128:t+=command&127;continue
 if command<64:
  value=b[p];p+=1;psg+=1
  if command%4==3:drums.append((t,command//4))
 else:
  assert command!=64,'unexpected extension'
  for _ in range(command&63):
   reg,val=b[p:p+2];p+=2;fm+=1;registers[reg]=val
   if reg==8 and val&120:
    voice=val&7;kc=registers[0x28+voice];kf=registers[0x30+voice]
    semitone={0:1,1:2,2:3,4:4,5:5,6:6,8:7,9:8,10:9,12:10,13:11,14:12}[kc&15]
    attacks.append((t,voice,12*((kc>>4)+1)+semitone+(kf>>2)/64))
assert p==len(b)
ledger=list(csv.DictReader((r/'music-notes.csv').open()))
expected_fm=[(int(x['tick']),int(x['voice']))for x in ledger if x['device']=='YM2151']
expected_psg=[(int(x['tick']),int(x['voice']))for x in ledger if x['device']=='PSG percussion']
assert [(t,v)for t,v,n in attacks]==expected_fm
assert drums==expected_psg
assert len(attacks)+len(drums)==14139
assert abs(t/60-json.loads((r/'music.json').read_text())['zsm_seconds'])<1e-9
# Native complete-loop register counts must agree with independent stream decode.
for ram in (512,2048):
 pth=r/f'MUSIC_TEST-{ram}.json'
 if pth.exists():
  j=json.loads(pth.read_text());assert j['fm_writes']==fm and j['psg_writes']==psg
catalog=json.loads((r/'audio-catalog.json').read_text())
for a in catalog['assets']:
 data=(r/'PCM'/a['pcm']).read_bytes()
 assert len(data)==a['bytes']and hashlib.sha256(data).hexdigest()==a['pcm_sha256']
report={'zsm_end_ticks':t,'fm_register_writes':fm,'psg_register_writes':psg,'decoded_melodic_attacks':len(attacks),
 'decoded_percussion_onsets':len(drums),'ledger_order_and_tick_match':True,'pcm_sha256_checked':len(catalog['assets'])}
(r/'format-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
