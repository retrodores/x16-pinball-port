"""Directly readable original z-buffer, quantized to 8 bits; 22 rows per bank."""
from pathlib import Path
import json,struct
import numpy as np
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
j=json.loads(Path('/opt/spacecadet-x16-analysis/evidence/inventory.json').read_text())
d=Path('/opt/spacecadet-x16-analysis/input/game/PINBALL.DAT').read_bytes()
e=next(e for e in j['groups'][107]['entries']if e['type']==12)
z=np.frombuffer(d[e['offset']+14:e['offset']+e['bytes']],'<u2').reshape(470,368)[::-1,:365]
q=(z>>8).astype('B');banks=[10,17,18]+list(range(45,64));blob=bytearray();rows=bytearray()
for y in range(470):
 page=y//22;offset=(y%22)*365
 rows.extend(struct.pack('<HB',0xa000+offset,banks[page]))
 while len(blob)<page*8192+offset:blob.append(0)
 blob.extend(q[y].tobytes())
assert len(blob)<=22*8192
for y in range(470):
 address,bank=struct.unpack_from('<HB',rows,y*3);offset=banks.index(bank)*8192+address-0xa000
 assert blob[offset:offset+365]==q[y].tobytes()
for f in o.glob('DEPTH[0-9]*.BIN'):f.unlink()
for i,offset in enumerate(range(0,len(blob),8192)):(o/f'DEPTH{i:02}.BIN').write_bytes(blob[offset:offset+8192])
(o/'DEPTH.BIN').write_bytes(blob);(o/'DEPTHROW.BIN').write_bytes(rows)
report={'source_group':107,'width':365,'height':470,'depth_bits':8,'bytes':len(blob),'index_bytes':len(rows),'banks':banks,'codec_exact_pixels':365*470,'depth_quantum_world':256/4303.9697265625}
(o/'depth.json').write_text(json.dumps(report,indent=2)+'\n')
print('Direct depth map:',len(blob),'bytes, all',365*470,'quantized pixels verified')
