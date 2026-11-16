#!/usr/bin/env python3
"""Presentation adaptation only. Original table/sprite pixels are retained."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re, struct

root=Path(__file__).resolve().parents[2]
out=root/'direct/build/preview';out.mkdir(parents=True,exist_ok=True)
assets=root/'assets'
palette=(assets/'PALETTE.BIN').read_bytes()
rgb=[]
for a,b in zip(palette[::2],palette[1::2]):rgb.extend(((b&15)*17,(a>>4)*17,(a&15)*17))
table=Image.frombytes('P',(320,240),(assets/'TABLE.BIN').read_bytes());table.putpalette(rgb)
d=ImageDraw.Draw(table)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',9)
bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',13)
d.rectangle((197,0,319,239),fill=246)
d.line((197,2,197,237),fill=253)
def text(x,y,s,fill=255,f=font):d.text((x,y),s,fill=fill,font=f)
text(204,9,'CMDRX',248,bold);text(204,25,'CADET',255,bold)
text(204,46,'DIRECT ENGINE',249)
text(204,59,'MECHANICS PREVIEW',250)
d.rectangle((202,79,316,96),fill=247)
text(204,99,'PLUNGER',250)
d.rectangle((204,112,303,115),fill=247)
for y,s in [(129,'N      NEW BALL'),(143,'SPACE  HOLD/RELEASE'),(157,'SHIFT  FLIPPERS'),(169,'  OR Z AND /'),(185,'P      PAUSE'),(199,'ESC    EXIT')]:text(204,y,s)
text(204,218,'UNFINISHED / SILENT',250)
text(204,230,'SLOW AT STOCK CPU',250)
(out/'TABLE.BIN').write_bytes(table.tobytes());table.save(out/'preview-table.png')
for name in ('PALETTE.BIN','SPRITES.BIN','PLUNGER.BIN'):(out/name).write_bytes((assets/name).read_bytes())
(out/'WORLD.BIN').write_bytes((root/'direct/build/WORLD.BIN').read_bytes())
# Status strips keep font rendering out of scarce main memory.
strips=[]
tiny=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',9)
for s in ('PRESS N TO START','FEEDING BALL','HOLD SPACE','BALL IN PLAY','PAUSED: P RESUMES','DRAINED: N AGAIN'):
 im=Image.new('P',(108,10),247);im.putpalette(rgb)
 ImageDraw.Draw(im).text((0,-1),s,font=tiny,fill=255);strips.append(im.tobytes())
(out/'status.bin').write_bytes(b''.join(strips))
data=bytearray()
def sprite(addr,x,y,size):data.extend(struct.pack('<HHHBB',(addr>>5)|0x8000,x,y,0x0c,size))
sprite(0x1a800,1000,0,0);sprite(0x13000,70,180,0xa0);sprite(0x15000,104,180,0xa0)
for i,(x,y) in enumerate(zip([93,104,84,53,46,28,34],[57,40,44,18,109,105,116])):sprite(0x17000+i*2048,x,y,0xa0)
sprite(0x1c000,170,192,0xc0)
(out/'sprites-init.bin').write_bytes(data)
