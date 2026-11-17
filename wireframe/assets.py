#!/usr/bin/env python3
from pathlib import Path
import json,math,struct
from PIL import Image,ImageDraw,ImageFont
r=Path(__file__).resolve().parent;o=r/'build';j=json.loads((r/'table.json').read_text());manifest=json.loads((o/'model.json').read_text());ids=manifest['component_ids'];src=[e for e in j['edges'] if e['class'] not in ('5TDemo','8TBlocker')]
palette=[(5,9,17),(44,90,98),(110,214,222),(255,220,90),(255,112,132),(94,246,170),(101,158,255),(223,128,255),(255,255,255),(90,108,128),(20,34,49),(255,168,79)]+[(0,0,0)]*244
pal=[]
for R,G,B in palette:pal.extend([((G//17)<<4)|(B//17),R//17])
(o/'PALETTE.BIN').write_bytes(bytes(pal))
def pt(x,y):return (round(109-x*11),round(113+y*7))
colors={'7TBumper':3,'11TSoloTarget':4,'12TPopupTarget':4,'5TRamp':6,'7TOneway':5,'5TSink':7,'8TKickout':7,'5THole':7,'9TRollover':5,'14TLightRollover':5,'9TTripwire':5,'12TFlagSpinner':11,'5TGate':11,'9TKickback':11}
im=Image.new('P',(320,240),0);im.putpalette([v for rgb in palette for v in rgb]);draw=ImageDraw.Draw(im)
for e in src:
 col=colors.get(e['class'],2);mask=e['mask']
 if e['class'] in ('12TPopupTarget','5TGate'):continue
 if 'line'in e:
  x,y,ex,ey=e['line']
  if e['class'] in ('5TWall','11TTableLayer','11TSoloTarget','12TPopupTarget','5TGate','9TKickback','8TPlunger'):
   length=math.hypot(ex-x,ey-y);nx=(ey-y)/length;ny=(x-ex)/length;x-=nx*.3;y-=ny*.3;ex-=nx*.3;ey-=ny*.3
  draw.line([pt(x,y),pt(ex,ey)],fill=col,width=1)
 else:
  x,y,r2=e['circle'];radius=math.sqrt(r2)
  if e['class']=='7TBumper':radius=max(.05,radius-.3)
  if e['class'] in ('5TWall','11TSoloTarget','12TPopupTarget'):continue
  a=pt(x+radius,y-radius);b=pt(x-radius,y+radius);draw.ellipse([a,b],outline=col)
draw.rectangle((200,0,319,239),fill=0);draw.line((199,4,199,235),fill=9)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',9)
bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',12)
def text(x,y,s,c=8,f=font):draw.text((x,y),s,fill=c,font=f)
text(207,8,'CMDRX CADET',2,bold);text(207,25,'WIREFRAME',3)
text(207,48,'SCORE',9);text(207,112,'BALLS',9);text(207,128,'LAYER',9);text(207,145,'CHARGE',9)
for y,t in [(173,'N   NEW GAME'),(185,'SPACE  LAUNCH'),(197,'SHIFT  FLIPPERS'),(209,'UP  NUDGE / P PAUSE'),(221,'S SOUND / ESC EXIT')]:text(205,y,t)
(o/'TABLE.BIN').write_bytes(im.tobytes());im.save(o/'wireframe.png')
sprites=bytearray();positions=[]
def add(sprite):
 addr=0x13000+len(sprites);sprites.extend(sprite.tobytes());return addr
ball=Image.new('P',(8,8),0);d=ImageDraw.Draw(ball);d.ellipse((1,2,7,6),fill=8);balladdr=add(ball)
# Pad to 1 KB so every 32x32 paddle pattern is naturally aligned.
sprites.extend(bytes(1024-len(sprites)));flippers=[]
for side,f in enumerate(j['flippers']):
 ox,oy=f['RotOrigin'];tx,ty=f['T1Src'];coords=[]
 for k in range(13):
  a=f['AngleMax']*k/12;c,s=math.cos(a),math.sin(a);coords.append((ox+(tx-ox)*c-(ty-oy)*s,oy+(tx-ox)*s+(ty-oy)*c))
 pts=[pt(ox,oy)]+[pt(*v) for v in coords];x0=min(p[0] for p in pts)-7;y0=min(p[1] for p in pts)-7
 addresses=[]
 for k,(x,y) in enumerate(coords):
  sprite=Image.new('P',(32,32),0);sd=ImageDraw.Draw(sprite);p=pt(ox,oy);t=pt(x,y);p=(p[0]-x0,p[1]-y0);t=(t[0]-x0,t[1]-y0)
  # Draw the physical capsule; the solver envelope additionally includes the ball radius.
  sd.line([p,t],fill=2,width=4);sd.ellipse((p[0]-3,p[1]-2,p[0]+3,p[1]+2),outline=8);sd.ellipse((t[0]-2,t[1]-1,t[0]+2,t[1]+1),outline=8);sd.line([p,t],fill=8,width=1)
  addresses.append(add(sprite))
 flippers.append({'x':x0,'y':y0,'addresses':addresses})
markers=[];dots={}
for col in (3,4,5,7,11):
 sp=Image.new('P',(8,8),0);sd=ImageDraw.Draw(sp);sd.ellipse((1,1,6,6),outline=col);sd.line((2,4,5,4),fill=8);dots[col]=add(sp)
for group,c in enumerate(ids):
 edges=[e for e in src if e['component']==c];e=edges[0];cls=e['class']
 if cls not in colors or cls in ('5TRamp','7TOneway'):continue
 if 'circle'in e:x,y,_=e['circle']
 else:
  xy=[v for t in edges if 'line'in t for v in [t['line'][:2],t['line'][2:]]];x=sum(v[0]for v in xy)/len(xy);y=sum(v[1]for v in xy)/len(xy)
 px,py=pt(x,y);markers.append((group,px-4,py-4,dots.get(colors[cls],dots[5])))
mechanisms=[]
for e in src:
 if e['class'] not in ('12TPopupTarget','5TGate'):continue
 x,y,ex,ey=e['line'];length=math.hypot(ex-x,ey-y);nx=(ey-y)/length*.3;ny=(x-ex)/length*.3
 a=pt(x-nx,y-ny);b=pt(ex-nx,ey-ny);x0=min(a[0],b[0])-2;y0=min(a[1],b[1])-2
 sp=Image.new('P',(32,32),0);sd=ImageDraw.Draw(sp);sd.line([(a[0]-x0,a[1]-y0),(b[0]-x0,b[1]-y0)],fill=colors[e['class']])
 mechanisms.append((ids.index(e['component']),x0,y0,add(sp)))
assert len(markers)+len(mechanisms)+3<128 and len(sprites)<0xc000
(o/'SPRITES.BIN').write_bytes(sprites)
# Glyphs for runtime score/status updates, one byte per 6-pixel row.
glyph=[]
for code in range(32,96):
 tile=Image.new('1',(6,8));ImageDraw.Draw(tile).text((0,-2),chr(code),font=font,fill=1)
 for y in range(8):glyph.append(sum((1<<(5-x))for x in range(6)if tile.getpixel((x,y))))
h=['#pragma once','static const uint8_t glyphs[]={'+','.join(map(str,glyph))+'};','struct Marker{uint8_t group;uint16_t x,y,addr;};','static const Marker markers[]={'+','.join('{%d,%d,%d,%d}'%(g,x,y,(a>>5)|0x8000) for g,x,y,a in markers)+'};','static const uint16_t paddle_x[2]={%d,%d},paddle_y[2]={%d,%d};'%(flippers[0]['x'],flippers[1]['x'],flippers[0]['y'],flippers[1]['y']),'static const uint16_t paddle_addr[2][13]={'+','.join('{'+','.join(str((a>>5)|0x8000)for a in f['addresses'])+'}'for f in flippers)+'};',f'constexpr uint16_t ball_addr={(balladdr>>5)|0x8000};']
h.append('static const Marker mechanisms[]={'+','.join('{%d,%d,%d,%d}'%(g,x,y,(a>>5)|0x8000)for g,x,y,a in mechanisms)+'};')
(o/'video.h').write_text('\n'.join(h)+'\n')
print('sprites',len(sprites),'markers',len(markers))
# The proven PCM driver uses upper banks for the new compact world model.
sfx=(r.parent/'assets/SFX.BIN').read_bytes();(o/'SFXA.BIN').write_bytes(sfx[:65536]);(o/'SFXB.BIN').write_bytes(sfx[65536:])
lengths=[790,1329,3020,6579,11895,40219,5449];pos=0;banks=[];lo=[];hi=[]
for n in lengths:
 bank=56+pos//8192;banks.append(2 if bank==64 else bank);a=0xa000+pos%8192;lo.append(a&255);hi.append(a>>8);pos+=n
arrays={'audio_banks':banks,'audio_low':lo,'audio_high':hi,'audio_length_low':[n&255 for n in lengths],'audio_length_high':[n>>8 for n in lengths],'audio_priorities':[2,1,4,3,1,5,0]}
(o/'audio-assets.inc').write_text('\n'.join(k+': .byte '+','.join(map(str,v))for k,v in arrays.items())+'\n')
s=(r.parent/'direct/integer/audio.s').read_text().replace('cmp #32','cmp #64').replace('direct/build/integer/audio-assets.inc','wireframe/build/audio-assets.inc');(o/'audio.s').write_text(s)
