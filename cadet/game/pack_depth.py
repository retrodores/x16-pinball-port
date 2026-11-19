"""Exact quantized original z-buffer: deduplicated 64-pixel PackBits blocks.
Index is bank 10; block data is banks 17,18,45..50. Blocks never cross banks.
"""
from pathlib import Path
import os
import json,struct
import numpy as np
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
j=json.loads(Path(os.environ.get('CADET_INVENTORY', '/opt/spacecadet-x16-analysis/evidence/inventory.json')).read_text())
d=Path(os.environ.get('CADET_DAT', '/opt/spacecadet-x16-analysis/input/game/PINBALL.DAT')).read_bytes()
e=next(e for e in j['groups'][107]['entries']if e['type']==12)
z=np.frombuffer(d[e['offset']+14:e['offset']+e['bytes']],'<u2').reshape(470,368)[::-1,:365]
q=(z>>8).astype('B')
def pack(b):
 out=bytearray();i=0
 while i<len(b):
  j=i+1
  while j<len(b) and b[j]==b[i] and j-i<127:j+=1
  if j-i>=3:out+=bytes([128|(j-i),b[i]]);i=j
  else:
   j=i+1
   while j<len(b) and j-i<127 and not(j+2<len(b) and b[j]==b[j+1]==b[j+2]):j+=1
   out+=bytes([j-i])+b[i:j];i=j
 return bytes(out)
def unpack(b,pos):
 out=bytearray()
 while len(out)<64:
  tag=b[pos];pos+=1
  if tag&128:out+=bytes([b[pos]])*(tag&127);pos+=1
  else:out+=b[pos:pos+tag];pos+=tag
 assert len(out)==64
 return bytes(out)
index=bytearray();data=bytearray();shared={}
for row in q:
 b=row.tobytes()+bytes([255])*19
 for x in range(0,384,64):
  raw=b[x:x+64];p=pack(raw)
  if p not in shared:
   if len(data)%8192+len(p)>8192:data.extend(bytes(8192-len(data)%8192))
   shared[p]=len(data);data.extend(p)
  index.extend(struct.pack('<H',shared[p]))
assert len(index)==5640 and len(data)<=65536,(len(index),len(data))
for y in range(470):
 decoded=b''.join(unpack(data,struct.unpack_from('<H',index,(y*6+x)*2)[0]) for x in range(6))
 assert decoded[:365]==q[y].tobytes()
for f in o.glob('DEPTH[0-9]*.BIN'):f.unlink()
(o/'DEPTH00.BIN').write_bytes(index)
for i in range(8):(o/f'DEPTH{i+1:02}.BIN').write_bytes(data[i*8192:(i+1)*8192] or bytes(1))
(o/'DEPTH.BIN').write_bytes(bytes(index)+bytes(8192-len(index))+data)
# Retain the previous UI field size; the block decoder uses DEPTH00 instead.
(o/'DEPTHROW.BIN').write_bytes(bytes(1410))
report={'source_group':107,'width':365,'height':470,'depth_bits':8,'codec':'packbits64-deduplicated','index_bytes':len(index),'data_bytes':len(data),'unique_blocks':len(shared),'banks':[10,17,18,45,46,47,48,49,50],'codec_exact_pixels':365*470,'depth_quantum_world':256/4303.9697265625}
(o/'depth.json').write_text(json.dumps(report,indent=2)+'\n')
print('Depth PackBits:',len(index)+len(data),'bytes; all',365*470,'quantized pixels verified')
