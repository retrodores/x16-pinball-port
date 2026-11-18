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
report={'source_bytes':len(src),'bytes':len(b),'original_writes':writes,'retained_writes':kept,'end_ticks':t,'first_bank':32,'last_bank':32+(len(b)-1)//8192}
(out/'music-pack.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
assert len(b)<=27*8192

# LZSS: flags LSB-first, 12-bit backward distance, lengths 3..18.
# Decode with a 4096-byte dictionary in bank 31. Retain every compact ZSM byte.
from collections import defaultdict,deque
import struct
source=bytes(b[16:]);assert len(source)==214239, "Update native stream-length counter and fixtures for a new theme"
chains=defaultdict(lambda:deque(maxlen=64));packed=bytearray();p=0;bit=8
while p<len(source):
 if bit==8:flagpos=len(packed);packed.append(0);bit=0
 best=0;distance=0
 if p+2<len(source):
  for prior in reversed(chains[source[p:p+3]]):
   if p-prior>4096:break
   n=3
   while n<18 and p+n<len(source)and source[prior+n]==source[p+n]:n+=1
   if n>best:best=n;distance=p-prior
 if best>=3:
  packed[flagpos]|=1<<bit;packed.extend(struct.pack('<H',((best-3)<<12)|(distance-1)));n=best
 else:packed.append(source[p]);n=1
 for at in range(p,p+n):chains[source[at:at+3]].append(at)
 p+=n;bit+=1
p=0;decoded=bytearray()
while len(decoded)<len(source):
 flags=packed[p];p+=1
 for bit in range(8):
  if len(decoded)==len(source):break
  if flags&(1<<bit):
   token=packed[p]|(packed[p+1]<<8);p+=2;distance=(token&4095)+1
   for _ in range((token>>12)+3):decoded.append(decoded[-distance])
  else:decoded.append(packed[p]);p+=1
assert bytes(decoded)==source and p==len(packed)
assert len(packed)<=13*8192
for f in out.glob('MUSIC[0-9].BIN'):f.unlink()
for i,offset in enumerate(range(0,len(packed),65536)):(out/f'MUSIC{i}.BIN').write_bytes(packed[offset:offset+65536])
(out/'MUSIC.LZ').write_bytes(packed)
report.update(compressed_bytes=len(packed),compressed_last_bank=32+(len(packed)-1)//8192,dictionary_bank=31,dictionary_bytes=4096,byte_exact_decompression=True)
(out/'music-pack.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
