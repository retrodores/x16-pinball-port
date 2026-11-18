#!/usr/bin/env python3
"""Original-resolution 16x16/4bpp VERA tiles with 16 local color palettes."""
from pathlib import Path
import json,struct,math,sys
import numpy as np
from scipy.cluster.vq import kmeans2
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];O=Path(sys.argv[1]) if len(sys.argv)>1 else R/'cadet/build';O.mkdir(exist_ok=True)
J=json.loads(Path('/opt/spacecadet-x16-analysis/evidence/inventory.json').read_text())
D=Path('/opt/spacecadet-x16-analysis/input/game/PINBALL.DAT').read_bytes()
pe=next(e for g in J['groups']for e in g['entries']if e['type']==5)
rgb=np.array([(r,g,b)for b,g,r,a in struct.iter_unpack('BBBB',D[pe['offset']:pe['offset']+1024])],dtype=np.uint8)
rgb[:10]=[(0,0,0),(128,0,0),(0,128,0),(128,128,0),(0,0,128),(128,0,128),(0,128,128),(192,192,192),(192,220,192),(166,202,240)]
rgb[246:255]=0;rgb[255]=255
def bitmap(gid):
 b=next(b for b in J['bitmaps']if b['group']==gid);stride=(b['width']+3)&~3
 raw=b''.join(D[b['offset']+y*stride:b['offset']+y*stride+b['width']]for y in reversed(range(b['height'])))
 return np.frombuffer(raw,np.uint8).reshape(b['height'],b['width']),b
screen=np.zeros((480,640),np.uint8)
def paste(a,x,y,transparent=False):
 h,w=a.shape;dest=screen[y:y+h,x:x+w]
 if transparent:dest[a!=0]=a[a!=0]
 else:dest[:]=a
table,tm=bitmap(107);paste(table,8,5)
back,bm=bitmap(2);paste(back,386,12)
for gid in ([372,380,388,396,405,413,421] if len(sys.argv)>1 else [355,363,372,380,388,396,405,413,421,473]):
 a,b=bitmap(gid);paste(a,b['x']-tm['x']+8,b['y']-tm['y']+5,True)
source=Image.fromarray(rgb[screen],'RGB')
# A bounded audition screen; no suggestion that this is already a playable port.
d=ImageDraw.Draw(source);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',10)
labels=[(410,'CMDRX CADET - TABLE TEST 0.2'),(423,'Z / SHIFT: LEFT   /: RIGHT'),(436,'SPACE: PLUNGER   F2: NEW GAME'),(449,'M: MUSIC   ESC: EXIT   8 MHZ')] if len(sys.argv)>1 else [(410,'X16 FIDELITY LAB - NOT GAMEPLAY'),(423,'LEFT/RIGHT: SELECT  SPACE: PLAY'),(436,'M: ORIGINAL THEME  S: STOP'),(449,'ESC: EXIT   65C02 / 8 MHZ')]
for y,s in labels:d.text((386,y),s,font=f,fill=(187,187,221))
source.save(O/'original-layout.png')
# Reduce only colors to VERA 12-bit; retain every spatial pixel.
pixels=np.asarray(source).astype(np.float64)
hw=(np.rint(pixels/17)*17).astype(np.uint8)
colors,ids=np.unique(hw.reshape(-1,3),axis=0,return_inverse=True)
ids=ids.reshape(480,640);n=len(colors);black=int(np.where((colors==0).all(axis=1))[0][0])
tiles=np.array([ids[y:y+16,x:x+16]for y in range(0,480,16)for x in range(0,640,16)])
hist=np.array([np.bincount(t.ravel(),minlength=n)for t in tiles],dtype=np.float64)
dist=((colors[:,None,:].astype(float)-colors[None,:,:])**2).sum(axis=2)
_,labels=kmeans2(np.sqrt(hist/256),16,iter=25,minit='++',seed=42)
def fit(weights):
 selected=[black];error=dist[:,black].copy()
 for _ in range(15):
  benefit=(np.maximum(error[:,None]-dist,0)*weights[:,None]).sum(axis=0)
  benefit[selected]=-1;idx=int(np.argmax(benefit));selected.append(idx);error=np.minimum(error,dist[:,idx])
 return np.array(selected)
for iteration in range(8):
 palettes=np.array([fit(hist[labels==k].sum(axis=0))for k in range(16)])
 errors=np.array([dist[:,p].min(axis=1)for p in palettes])
 new=np.argmin(hist@errors.T,axis=1)
 if np.array_equal(labels,new):break
 labels=new
lookup=np.array([np.argmin(dist[:,p],axis=1)for p in palettes])
mapping=bytearray(64*32*2);patterns=[];cache={};reconstructed=np.zeros((480,640,3),np.uint8)
for i,t in enumerate(tiles):
 bank=int(labels[i]);q=lookup[bank,t].astype(np.uint8)
 variants=[(q,0),(q[:,::-1],4),(q[::-1,:],8),(q[::-1,::-1],12)]
 packed=[((a[:,::2]<<4)|a[:,1::2]).tobytes()for a,_ in variants]
 canonical=min(range(4),key=lambda k:packed[k]);data=packed[canonical];flip=variants[canonical][1]
 if data not in cache:cache[data]=len(patterns);patterns.append(data)
 index=cache[data];off=((i//40)*64+i%40)*2;mapping[off]=index&255;mapping[off+1]=(index>>8)|flip|(bank<<4)
 reconstructed[(i//40)*16:(i//40+1)*16,(i%40)*16:(i%40+1)*16]=colors[palettes[bank,q]]
assert len(patterns)<=928,('tiles exceed VRAM plan',len(patterns))
raw=b''.join(patterns);(O/'TILES.BIN').write_bytes(raw);(O/'MAP.BIN').write_bytes(mapping)
pal=colors[palettes].reshape(-1,3)
(O/'PAL.BIN').write_bytes(bytes(v for r,g,b in pal for v in [(int(g)//17)*16+int(b)//17,int(r)//17]))
Image.fromarray(reconstructed).save(O/'x16-layout.png')
error=(reconstructed.astype(float)-pixels)**2
nonblack=(pixels!=0).any(axis=2)
report={'resolution':[640,480],'original_table_pixels':[365,470],'tile_size':[16,16],'bpp':4,'palette_banks':16,
 'tiles':len(patterns),'tile_bytes':len(raw),'map_bytes':len(mapping),'tile_base':4096,'tile_end':4096+len(raw),
 'sprite_reserve_start':122880,'palette_base':129536,'spatial_resampling':False,
 'psnr_all_db':float(10*np.log10(255**2/error.mean())),
 'psnr_nonblack_db':float(10*np.log10(255**2/error[nonblack].mean())),
 'identical_rgb_fraction':float(np.mean(np.all(reconstructed==pixels,axis=2))),
 'source':'PINBALL.DAT groups 107,2,355,363,372,380,388,396,405,413,421,473'}
(O/'graphics.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
