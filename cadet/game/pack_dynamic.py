"""Measure/pack original mechanism poses as writes into the existing tile patterns."""
from pathlib import Path
import json,struct
import numpy as np
from collections import defaultdict
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
j=json.loads(Path('/opt/spacecadet-x16-analysis/evidence/inventory.json').read_text())
d=Path('/opt/spacecadet-x16-analysis/input/game/PINBALL.DAT').read_bytes()
pe=next(e for g in j['groups'] for e in g['entries'] if e['type']==5)
rgb=np.array([(r,g,b)for b,g,r,a in struct.iter_unpack('BBBB',d[pe['offset']:pe['offset']+1024])],dtype=np.int32)
rgb[:10]=[(0,0,0),(128,0,0),(0,128,0),(128,128,0),(0,0,128),(128,0,128),(0,128,128),(192,192,192),(192,220,192),(166,202,240)]
rgb[246:255]=0;rgb[255]=255
pal=(o/'PAL.BIN').read_bytes()
colors=np.array([((pal[i+1]&15)*17,(pal[i]>>4)*17,(pal[i]&15)*17)for i in range(0,512,2)]).reshape(16,16,3)
lookup=(((rgb[None,:,None,:]-colors[:,None,:,:])**2).sum(axis=3)).argmin(axis=2)
mapping=bytearray((o/'MAP.BIN').read_bytes());base=(o/'TILES.BIN').read_bytes()
def bitmap(gid):
 b=next(b for b in j['bitmaps']if b['group']==gid);stride=(b['width']+3)&~3
 raw=b''.join(d[b['offset']+y*stride:b['offset']+y*stride+b['width']]for y in reversed(range(b['height'])))
 return np.frombuffer(raw,np.uint8).reshape(b['height'],b['width']),b
table,tm=bitmap(107)
defs=[(g,0,list(range(g,g+8)))for g in [372,380,388,396,405,413,421]]
defs += [(g,1,[None,g]) for g in [128,129,130,214,215,216,185,186,187,188,189,190,148,147,228,227,125,126,127,168,191]]
defs += [(g,1,[None,g,g+1,g+2]) for g in [116,119,122]]
defs += [(501,0,[501,None]),(502,0,[502,None]),(505,0,[505,506]),(507,0,[507,508])]
report=[];used=defaultdict(list)
for i in range(40*30):
 off=(i//40*64+i%40)*2;t=mapping[off]|((mapping[off+1]&3)<<8);used[t].append(i)
total=0;alltiles=set();records=[]
for gid,kind,poses in defs:
 bitmaps=[bitmap(g)if g is not None else None for g in poses]
 px=set()
 for item in bitmaps:
  if item:
   a,b=item
   px.update((int(x)+b['x']-tm['x']+8,int(y)+b['y']-tm['y']+5)for y,x in zip(*np.nonzero(a)))
 positions=defaultdict(int)
 for x,y in px:
  off=(y//16*64+x//16)*2;t=mapping[off]|((mapping[off+1]&3)<<8);attr=mapping[off+1];xx=x%16;yy=y%16
  if attr&4:xx=15-xx
  if attr&8:yy=15-yy
  addr=4096+t*128+yy*8+xx//2;mask=15 if xx&1 else 240
  positions[addr]|=mask;alltiles.add(t)
 data=[]
 for item in bitmaps:
  a=table.copy()
  # Composite each original sprite onto the unbaked table, preserving its transparent mask.
  if item:
   frame,b=item;x=b['x']-tm['x'];y=b['y']-tm['y'];h,w=frame.shape
   dest=a[y:y+h,x:x+w];dest[frame!=0]=frame[frame!=0]
  writes={addr:base[addr-4096]for addr in positions}
  for x,y in px:
   off=(y//16*64+x//16)*2;t=mapping[off]|((mapping[off+1]&3)<<8);attr=mapping[off+1];xx=x%16;yy=y%16
   if attr&4:xx=15-xx
   if attr&8:yy=15-yy
   addr=4096+t*128+yy*8+xx//2;shift=0 if xx&1 else 4;mask=15<<shift
   value=int(lookup[attr>>4,a[y-5,x-8]])<<shift
   writes[addr]=(writes[addr]&~mask)|value
  data.append(writes)
 # Every addressed byte must be written on every pose to restore old pixels.
 # Pack ascending runs within one 64 KB VERA bank, at most 255 bytes each.
 addresses=sorted(positions);runs=[]
 for addr in addresses:
  if runs and addr==runs[-1][-1]+1 and len(runs[-1])<255 and addr>>16==runs[-1][0]>>16:runs[-1].append(addr)
  else:runs.append([addr])
 size=1+sum(4+len(run)*2 for run in runs) # destination masks + per-pose data later
 fixed=1+sum(4+len(run)for run in runs)
 variable=len(addresses)*len(poses)
 total+=fixed+variable
 report.append({'group':gid,'kind':kind,'pixels':len(px),'bytes':len(addresses),'runs':len(runs),'poses':len(poses),'fixed':fixed,'variable':variable})
 records.append((gid,kind,positions,runs,data))
assert not any(len(used[t])>1 for t in alltiles),'Dynamic tile patterns must not alias other screen cells'
blob=bytearray();descs=[];packed_records=[]
for gid,kind,positions,runs,data in records:
 addresses=[addr for run in runs for addr in run];n=len(addresses)
 raw=bytearray(struct.pack('<BBH',len(runs),len(data),n))
 for run in runs:raw.extend(struct.pack('<HBB',run[0]&65535,run[0]>>16,len(run)))
 raw.extend(positions[addr]for addr in addresses)
 for writes in data:raw.extend(writes[addr]for addr in addresses)
 assert len(raw)<=8192
 if len(blob)%8192+len(raw)>8192:blob.extend(bytes(8192-len(blob)%8192))
 offset=len(blob);descs.append((gid,58+offset//8192,0xa000+offset%8192,kind));blob.extend(raw)
 packed_records.append({'group':gid,'offset':offset,'length':len(raw),'positions':addresses,'masks':[positions[a]for a in addresses],'poses':[[values[a]for a in addresses]for values in data]})
assert len(blob)<=3*8192,('dynamic bank budget exceeded',len(blob))
used_bytes=len(blob);blob.extend(bytes(3*8192-len(blob)))
for i in range(3):(o/f'DYN{i}.BIN').write_bytes(blob[i*8192:(i+1)*8192])
h=['#ifndef CADET_DYNAMIC_H','#define CADET_DYNAMIC_H','#include <stdint.h>','#include <stdbool.h>',
 '#define DYNAMIC_COUNT '+str(len(descs)),
 'typedef struct {uint16_t group;uint8_t bank;uint16_t ptr;uint8_t lamp;} DynamicDesc;',
 'static const DynamicDesc dynamic_desc[]={'+','.join('{%d,%d,%d,%d}'%v for v in descs)+'};',
 'void dynamic_init(void);bool dynamic_update(uint8_t);','#endif']
(o/'dynamic.h').write_text('\n'.join(h)+'\n')
manifest={'bytes':used_bytes,'banks':[58,59,60],'affected_tiles':len(alltiles),'components':report,'records':packed_records}
(o/'dynamic.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Validate every pose and every transparent nibble against the packed source.
for record,desc in zip(packed_records,descs):
 at=record['offset'];nr,nposes,n=struct.unpack_from('<BBH',blob,at);at+=4
 runs=[]
 for _ in range(nr):
  lo,hi,count=struct.unpack_from('<HBB',blob,at);at+=4;runs.extend(range(lo+(hi<<16),lo+(hi<<16)+count))
 masks=blob[at:at+n];at+=n
 assert runs==record['positions'] and list(masks)==record['masks']
 for pose in range(nposes):
  values=blob[at+pose*n:at+(pose+1)*n];assert list(values)==record['poses'][pose]
  for address,mask,value in zip(runs,masks,values):
   for old in (0,85,170,255):assert (((old&(~mask&255))|(value&mask))&(~mask&255))==(old&(~mask&255))
print(json.dumps({k:v for k,v in manifest.items()if k!='records'},indent=2))

# Mechanisms own disjoint pixel nibbles, so asynchronous updates cannot erase a
# neighbour's light when two components occupy the same tile or byte.
owned={}
for record in packed_records:
 for address,mask in zip(record['positions'],record['masks']):
  assert not (owned.get(address,0)&mask),('overlapping dynamic pixels',record['group'],address)
  owned[address]=owned.get(address,0)|mask

def preview(active):
 pixels=bytearray(base)
 for record in packed_records:
  pose=(3 if record['group']in (372,380,388,396,405,413,421)else 1)if active else 0
  if not active and record['group']in (501,502,147,148,227,228):pose=1
  for address,mask,value in zip(record['positions'],record['masks'],record['poses'][pose]):
   pixels[address-4096]=(pixels[address-4096]&~mask)|(value&mask)
 image=np.zeros((480,640,3),np.uint8)
 for y in range(30):
  for x in range(40):
   at=(y*64+x)*2;t=mapping[at]|((mapping[at+1]&3)<<8);attr=mapping[at+1]
   b=np.frombuffer(pixels[t*128:(t+1)*128],np.uint8).reshape(16,8);q=np.empty((16,16),np.uint8)
   q[:,::2]=b>>4;q[:,1::2]=b&15
   if attr&4:q=q[:,::-1]
   if attr&8:q=q[::-1,:]
   image[y*16:(y+1)*16,x*16:(x+1)*16]=colors[attr>>4,q]
 return Image.fromarray(image)
rest=preview(False);active=preview(True)
rest.save(o/'dynamic-rest.png');active.save(o/'dynamic-active.png')
sheet=Image.new('RGB',(730,490));sheet.paste(rest.crop((8,5,373,475)),(0,20));sheet.paste(active.crop((8,5,373,475)),(365,20))
label=ImageDraw.Draw(sheet);label.text((10,3),'Initial game state',fill='white');label.text((375,3),'Original active poses (fixture)',fill='white');sheet.save(o/'dynamic-comparison.png')
