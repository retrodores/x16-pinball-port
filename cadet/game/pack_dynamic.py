"""Measure/pack original mechanism poses as writes into the existing tile patterns."""
from pathlib import Path
import os
import json,struct
import numpy as np
from collections import defaultdict
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
j=json.loads(Path(os.environ.get('CADET_INVENTORY', '/opt/spacecadet-x16-analysis/evidence/inventory.json')).read_text())
d=Path(os.environ.get('CADET_DAT', '/opt/spacecadet-x16-analysis/input/game/PINBALL.DAT')).read_bytes()
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
# TWall starts hidden; a qualifying rebound exposes bitmap 0 for 0.1 seconds.
# The rest pose restores the original table rather than keeping the firing art.
defs += [(g,0,[None,g]) for g in [471,472]]
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
regular_used=len(blob);blob.extend(bytes(3*8192-len(blob)))
# Lower rebounder rubber and its TLight glow overlap. The original control fires
# both for the same 0.1 seconds; compose their DAT z-maps, then switch private
# tilemap entries. Drawing hundreds of bytes over six frames would erase the flash.
def zmap(gid):
 b=next(b for b in j['bitmaps']if b['group']==gid)
 e=next(e for e in j['groups'][gid]['entries']if e['type']==12)
 stride=(b['width']+3)&~3
 return np.frombuffer(d[e['offset']+14:e['offset']+e['bytes']],'<u2').reshape(b['height'],stride)[::-1,:b['width']]
original_z=zmap(107)
fast_base=(json.loads((o/'sprites.json').read_text())['end']+2048+128+127)&~127
fast_end=fast_base;fast_records=[];fast_descs=[];fast_tiles=set()
regular_tiles={((a-4096)//128) for rec in packed_records for a in rec['positions']}
for gid,lamp in [(469,180),(470,181)]:
 active_table=table.copy();active_z=original_z.copy();px=set()
 # zdrv::paint uses destination depth >= source depth, including equal-depth
 # later sprites. TLight is created before TWall in the original table list.
 for source in (lamp,gid):
  a,b=bitmap(source);z=zmap(source);x=b['x']-tm['x'];y=b['y']-tm['y'];h,w=a.shape
  dest=active_table[y:y+h,x:x+w];dz=active_z[y:y+h,x:x+w];mask=dz>=z
  dest[mask]=a[mask];dz[mask]=z[mask]
  px.update((int(xx)+x+8,int(yy)+y+5)for yy,xx in zip(*np.nonzero((a!=0)|(z!=65535))))
 rest_pixels=bytearray(base);fire_pixels=bytearray(base);tiles=set()
 for x,y in px:
  off=(y//16*64+x//16)*2;t=mapping[off]|((mapping[off+1]&3)<<8);attr=mapping[off+1];xx=x%16;yy=y%16
  if attr&4:xx=15-xx
  if attr&8:yy=15-yy
  at=t*128+yy*8+xx//2;shift=0 if xx&1 else 4;mask=15<<shift;tiles.add(t)
  for pixels,source in [(rest_pixels,table),(fire_pixels,active_table)]:
   value=int(lookup[attr>>4,source[y-5,x-8]])<<shift
   pixels[at]=(pixels[at]&~mask)|value
 assert not tiles&regular_tiles,('fast tile shares another mechanism',gid,tiles&regular_tiles)
 assert not tiles&fast_tiles,('fast tiles overlap each other',gid)
 assert not any(len(used[t])!=1 for t in tiles),('fast tiles alias',gid)
 fast_tiles.update(tiles);meta=[];rest_data=bytearray();fire_data=bytearray()
 for t in sorted(tiles):
  cell=used[t][0];map_address=(cell//40*64+cell%40)*2
  off=mapping[map_address]|(mapping[map_address+1]<<8)
  fire_index=(fast_end-4096)//128;assert fire_index<1024
  on=(off&0xfc00)|fire_index;meta.append((map_address,off,on))
  rest_data.extend(rest_pixels[t*128:(t+1)*128]);fire_data.extend(fire_pixels[t*128:(t+1)*128]);fast_end+=128
 raw=bytearray(struct.pack('<BBH',len(meta),2,len(rest_data)))
 for entry in meta:raw.extend(struct.pack('<HHH',*entry))
 raw.extend(rest_data);raw.extend(fire_data)
 offset=len(blob);assert offset//8192==3 and (offset%8192)+len(raw)<=8192
 fast_descs.append((gid,63,0xa000+offset%8192,2));blob.extend(raw)
 fast_records.append({'group':gid,'lamp_group':lamp,'offset':offset,'length':len(raw),'maps':meta,'rest':list(rest_data),'fire':list(fire_data)})
 report.append({'group':gid,'kind':2,'source_groups':[lamp,gid],'pixels':len(px),'bytes':len(rest_data),'tiles':len(meta),'poses':2})
assert fast_end<=0x1f9c0,('fast patterns overlap palette or sprite attributes',hex(fast_end))
assert fast_base>=json.loads((o/'sprites.json').read_text())['end']+2048+128
used_bytes=len(blob);assert used_bytes<=4*8192
blob.extend(bytes(4*8192-len(blob)))
for i in range(4):(o/f'DYN{i}.BIN').write_bytes(blob[i*8192:(i+1)*8192])
descs=fast_descs+descs
h=['#ifndef CADET_DYNAMIC_H','#define CADET_DYNAMIC_H','#include <stdint.h>','#include <stdbool.h>',
 '#define DYNAMIC_COUNT '+str(len(descs)), '#define DYNAMIC_FAST_COUNT '+str(len(fast_descs)),
 '#define DYNAMIC_BANK_COUNT 4','static const uint8_t dynamic_load_banks[]={58,59,60,63};',
 'typedef struct {uint16_t group;uint8_t bank;uint16_t ptr;uint8_t lamp;} DynamicDesc;',
 'static const DynamicDesc dynamic_desc[]={'+','.join('{%d,%d,%d,%d}'%v for v in descs)+'};',
 'void dynamic_init(void);bool dynamic_update(uint8_t);','#endif']
(o/'dynamic.h').write_text('\n'.join(h)+'\n')
manifest={'bytes':used_bytes,'regular_bytes':regular_used,'banks':[58,59,60,63],'affected_tiles':len(alltiles|fast_tiles),'fast_vram_base':fast_base,'fast_vram_end':fast_end,'components':report,'records':packed_records,'fast_records':fast_records}
(o/'dynamic.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Validate every pose and every transparent nibble against the packed source.
for record in packed_records:
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
print(json.dumps({k:v for k,v in manifest.items()if k not in ('records','fast_records')},indent=2))

# Mechanisms own disjoint pixel nibbles, so asynchronous updates cannot erase a
# neighbour's light when two components occupy the same tile or byte.
owned={}
for record in packed_records:
 for address,mask in zip(record['positions'],record['masks']):
  assert not (owned.get(address,0)&mask),('overlapping dynamic pixels',record['group'],address)
  owned[address]=owned.get(address,0)|mask

def preview(active):
 pixels=bytearray(base)
 for record in fast_records:
  values=record['fire'if active else'rest']
  for i,(_,off,on)in enumerate(record['maps']):
   t=off&1023;pixels[t*128:(t+1)*128]=bytes(values[i*128:(i+1)*128])
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
