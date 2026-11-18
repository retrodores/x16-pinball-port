"""Remove only redundant state-register writes; retain YM key/control side effects."""
from pathlib import Path
import json
r=Path(__file__).resolve().parents[2];src=(r/'cadet/build/THEME.ZSM').read_bytes();out=r/'cadet/play-build'
p=16;t=0;events={};state={};writes=0;kept=0
while True:
 c=src[p];p+=1
 if c==128:break
 if c>128:t+=c&127;continue
 if c<64:seq=[('p',c,src[p])];p+=1
 else:
  assert c!=64
  seq=[('f',src[p+i*2],src[p+i*2+1])for i in range(c&63)];p+=(c&63)*2
 for typ,reg,val in seq:
  writes+=1;key=(typ,reg)
  if state.get(key)!=val or(typ=='f'and reg in (1,8,20)):
   events.setdefault(t,[]).append((typ,reg,val));kept+=1
  state[key]=val
b=bytearray(src[:16]);last=0
for tick,seq in sorted(events.items()):
 delay=tick-last
 while delay:q=min(127,delay);b.append(128|q);delay-=q
 last=tick;i=0
 while i<len(seq):
  typ,reg,val=seq[i]
  if typ=='p':b.extend([reg,val]);i+=1
  else:
   batch=[]
   while i<len(seq)and seq[i][0]=='f'and len(batch)<63:batch.append(seq[i][1:]);i+=1
   b.append(64|len(batch))
   for reg,val in batch:b.extend([reg,val])
delay=t-last
while delay:q=min(127,delay);b.append(128|q);delay-=q
b.append(128);(out/'THEME.ZSM').write_bytes(b)
for p in out.glob('MUSIC*.BIN'):p.unlink()
for i,off in enumerate(range(0,len(b),65536)):(out/f'MUSIC{i}.BIN').write_bytes(b[off:off+65536])
report={'source_bytes':len(src),'bytes':len(b),'original_writes':writes,'retained_writes':kept,'end_ticks':t,'first_bank':32,'last_bank':32+(len(b)-1)//8192}
(out/'music-pack.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
assert len(b)<=27*8192
