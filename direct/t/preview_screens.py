#!/usr/bin/env python3
"""Validate captures from actual SDL key input against the rendered status art."""
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[2]
palette=(root/'assets/PALETTE.BIN').read_bytes();rgb=[]
for a,b in zip(palette[::2],palette[1::2]):rgb.extend(((b&15)*17,(a>>4)*17,(a&15)*17))
data=(root/'direct/build/preview/status.bin').read_bytes();statuses=[]
for i in range(6):
 im=Image.frombytes('P',(108,10),data[i*1080:(i+1)*1080]);im.putpalette(rgb);statuses.append(im.convert('RGB'))
for ram in (512,2048):
 images={}
 for name,expected in [('start',0),('fed',2),('charged',2),('launched',3),('flippers',3),('paused',4)]:
  im=Image.open(root/f'evidence/direct-preview/{name}-{ram}.png').resize((320,240),Image.Resampling.NEAREST).convert('RGB');images[name]=im
  assert ImageChops.difference(im.crop((204,84,312,94)),statuses[expected]).getbbox() is None,(ram,name)
 assert all(images['charged'].getpixel((x,113))==tuple(rgb[248*3:249*3]) for x in range(204,304)),(ram,'charge bar')
 for x in (70,104):
  box=(x,180,x+32,212)
  assert ImageChops.difference(images['start'].crop(box),images['flippers'].crop(box)).getbbox(),(ram,'flipper sprite')
 print(f'captured status, full charge bar and both moving sprites PASS on {ram} KB')
