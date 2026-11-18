"""Original movable bitmaps, spatially unchanged, using VERA's local palettes."""
from pathlib import Path
import json,struct
import numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
j=json.loads(Path('/opt/spacecadet-x16-analysis/evidence/inventory.json').read_text())
d=Path('/opt/spacecadet-x16-analysis/input/game/PINBALL.DAT').read_bytes()
pe=next(e for g in j['groups'] for e in g['entries'] if e['type']==5)
rgb=np.array([(r,g,b)for b,g,r,a in struct.iter_unpack('BBBB',d[pe['offset']:pe['offset']+1024])],dtype=np.int32)
rgb[:10]=[(0,0,0),(128,0,0),(0,128,0),(128,128,0),(0,0,128),(128,0,128),(0,128,128),(192,192,192),(192,220,192),(166,202,240)]
rgb[246:255]=0;rgb[255]=255
pal=(o/'PAL.BIN').read_bytes()
colors=np.array([((pal[i+1]&15)*17,(pal[i]>>4)*17,(pal[i]&15)*17)for i in range(0,512,2)]).reshape(16,16,3)
dist=((rgb[None,:,None,:]-colors[:,None,:,:])**2).sum(axis=3)
# Pen zero is sprite transparency. Preserve the source bitmap's zero mask.
dist[:,:,0]=10**9
lookup=dist.argmin(axis=2);error=dist.min(axis=2)
patterns=[];cache={};frames=[];pattern_bytes=0
def bitmap(gid):
 b=next(b for b in j['bitmaps']if b['group']==gid);stride=(b['width']+3)&~3
 raw=b''.join(d[b['offset']+y*stride:b['offset']+y*stride+b['width']]for y in reversed(range(b['height'])))
 return np.frombuffer(raw,np.uint8).reshape(b['height'],b['width']),b
def frame(gid,screen=True,digit=False):
 global pattern_bytes
 a,b=bitmap(gid);h,w=a.shape;tiles=[]
 tile_h=32 if 5<=gid<=14 else 16
 for y in range(0,h,tile_h):
  for x in range(0,w,16):
   t=np.zeros((tile_h,16),np.uint8);sub=a[y:y+tile_h,x:x+16];t[:sub.shape[0],:sub.shape[1]]=sub
   hist=np.bincount(t.ravel(),minlength=256);hist[0]=0
   bank=int(np.argmin(error@hist));q=lookup[bank,t].astype(np.uint8);q[t==0]=0
   packed=((q[:,::2]<<4)|q[:,1::2]).tobytes()
   if packed not in cache:cache[packed]=pattern_bytes;patterns.append(packed);pattern_bytes+=len(packed)
   tiles.append((cache[packed],x,y,bank,0x90 if tile_h==32 else 0x50))
 return {'group':gid,'x':b['x']-137+8 if screen else 0,'y':b['y']-2+5 if screen else 0,'width':w,'height':h,'tiles':tiles}
for gid in list(range(355,371))+list(range(473,481))+list(range(108,115))+list(range(5,15)):frames.append(frame(gid,gid>=355))
base=(4096+len((o/'TILES.BIN').read_bytes())+127)&~127
data=b''.join(patterns);assert base+len(data)<=0x1f9c0,(base,len(data),hex(base+len(data)))
(o/'SPRITES.BIN').write_bytes(data)
h=['#ifndef CADET_SPRITES_H','#define CADET_SPRITES_H','#include <stdint.h>',f'#define SPRITE_BASE {base}UL',
 'typedef struct __attribute__((packed)) {uint16_t address;uint8_t x,y,palette,size;} SpriteTile;',
 'typedef struct __attribute__((packed)) {int16_t x,y;uint8_t width,height,count;const SpriteTile* tiles;} SpriteFrame;',
 '#define sprites ((const SpriteFrame*)0xa000)','#endif']
ui=bytearray(len(frames)*9)
for i,f in enumerate(frames):
 ptr=0xa000+len(ui)
 struct.pack_into('<hhBBBH',ui,i*9,f['x'],f['y'],f['width'],f['height'],len(f['tiles']),ptr)
 for off,x,y,p,size in f['tiles']:ui.extend(struct.pack('<HBBBB',(base+off)//32,x,y,p,size))
assert len(ui)<=2048,len(ui)
(o/'UI-SPR.BIN').write_bytes(ui)
(o/'sprites.h').write_text('\n'.join(h)+'\n')
report={'unique_tiles':len(patterns),'bytes':len(data),'base':base,'end':base+len(data),'frames':frames}
(o/'sprites.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:v for k,v in report.items()if k!='frames'})
