#!/usr/bin/env python3
"""Offline asset conversion; no runtime Python dependency."""
from pathlib import Path
import argparse,json,struct,math,subprocess
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('dat',type=Path)
ap.add_argument('--inventory',type=Path,required=True)
args=ap.parse_args()
j=json.loads(args.inventory.read_text());data=args.dat.read_bytes()
groups=j['groups']
pale=next(e for g in groups for e in g['entries'] if e['type']==5)
rgb=[(r,g,b) for b,g,r,a in struct.iter_unpack('BBBB',data[pale['offset']:pale['offset']+1024])]
rgb[:10]=[(0,0,0),(128,0,0),(0,128,0),(128,128,0),(0,0,128),(128,0,128),(0,128,128),(192,192,192),(192,220,192),(166,202,240)]
rgb[246:255]=[(17,17,34),(34,34,51),(68,221,221),(255,204,68),(136,153,187),(255,102,119),(85,221,153),(51,68,85),(68,85,102)];rgb[255]=(255,255,255)
rgb=[tuple(round(v/17)*17 for v in c) for c in rgb]
palette=[v for c in rgb for v in c]
def bitmap(gid):
 b=next(b for b in j['bitmaps'] if b['group']==gid)
 stride=(b['width']+3)&~3
 p=b''.join(data[b['offset']+y*stride:b['offset']+y*stride+b['width']] for y in reversed(range(b['height'])))
 im=Image.frombytes('P',(b['width'],b['height']),p);im.putpalette(palette)
 return im,b
def attr(gid,n):
 return next(e['values'][1:] for e in groups[gid]['entries'] if e['type']==11 and int(e['values'][0])==n)
camera=next(e['values'] for e in groups[3]['entries'] if e['type']==11)
def project(x,y,z=0):
 rx=camera[0]*x+camera[1]*y+camera[2]*z+camera[3]
 ry=camera[4]*x+camera[5]*y+camera[6]*z+camera[7]
 rz=camera[8]*x+camera[9]*y+camera[10]*z+camera[11]
 return (8+(rx*camera[12]/rz+183)/2,2+(ry*camera[12]/rz+238)/2)
table,_=bitmap(107)
bg=Image.new('P',(320,240));bg.putpalette(palette)
bg.paste(table.resize((183,235),Image.Resampling.NEAREST),(8,2))
draw=ImageDraw.Draw(bg)
draw.rounded_rectangle((197,2,318,237),radius=5,fill=246,outline=253)
draw.rectangle((201,6,314,32),fill=247)
draw.line((204,34,311,34),fill=248)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',9)
title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',13)
draw.text((211,10),'CMDRX CADET',font=title,fill=249)
for x,y,t,color in [(204,38,'SCORE',250),(204,88,'PERSONAL BEST',250),(204,135,'BALLS   CHARGE',250),(204,208,'Z / SHIFT   /',250),(204,221,'L LISTEN N PLAY',250)]:
 draw.text((x,y),t,font=font,fill=color)
for box in [(202,49,312,82),(202,100,312,132),(202,147,312,162),(202,166,312,204)]:
 draw.rounded_rectangle(box,radius=2,fill=247)
(root/'assets/TABLE.BIN').write_bytes(bg.tobytes())
(root/'assets/PALETTE.BIN').write_bytes(bytes(v for r,g,b in rgb for v in ((g//17)*16+b//17,r//17)))
patterns=bytearray();anchors=[];tips=[];pivots=[]
for base in (355,363):
 ims=[bitmap(base+k) for k in range(8)]
 ax=min(round((b['x']-137)/2+8) for im,b in ims)
 ay=min(round((b['y']-2)/2+2) for im,b in ims)
 anchors.append((ax,ay))
 for im,b in ims:
  frame=Image.new('P',(32,32))
  w=max(1,round(im.width/2));h=max(1,round(im.height/2))
  frame.paste(im.resize((w,h),Image.Resampling.NEAREST),(round((b['x']-137)/2+8)-ax,round((b['y']-2)/2+2)-ay))
  patterns.extend(frame.tobytes())
 origin=attr(base,800);rest=attr(base,801);up=attr(base,802)
 pivots.append(tuple(round(v) for v in project(*origin[:3])))
 a0=math.atan2(rest[1]-origin[1],rest[0]-origin[0]);a1=math.atan2(up[1]-origin[1],up[0]-origin[0])
 delta=(a1-a0+math.pi)%(2*math.pi)-math.pi
 radius=math.hypot(rest[0]-origin[0],rest[1]-origin[1])
 tips.append([tuple(round(v) for v in project(origin[0]+radius*math.cos(a0+delta*k/7),origin[1]+radius*math.sin(a0+delta*k/7),rest[2])) for k in range(8)])
bumperids=[372,380,388,396,405,413,421]
banchors=[];centers=[]
for base in bumperids:
 im,b=bitmap(base)
 ax=round((b['x']-137)/2+8);ay=round((b['y']-2)/2+2)
 banchors.append((ax,ay))
 for state in (0,1):
  im,meta=bitmap(base+state)
  frame=Image.new('P',(32,32))
  frame.paste(im.resize((max(1,round(im.width/2)),max(1,round(im.height/2))),Image.Resampling.NEAREST),(round((meta['x']-137)/2+8)-ax,round((meta['y']-2)/2+2)-ay))
  patterns.extend(frame.tobytes())
 try:
  v=attr(base,600);centers.append(tuple(round(n) for n in project(v[1],v[2])))
 except StopIteration:centers.append((ax+round(b['width']/4),ay+round(b['height']/4)))
balladdr=0x13000+len(patterns)
im,b=bitmap(108);ball=Image.new('P',(8,8));ball.paste(im.resize((7,7),Image.Resampling.NEAREST),(0,0));patterns.extend(ball.tobytes())
(root/'assets/SPRITES.BIN').write_bytes(patterns)
plunger=bytearray()
for gid in range(473,481):
 im,meta=bitmap(gid)
 frame=Image.new('P',(8,64))
 frame.paste(im.resize((max(1,round(im.width/2)),max(1,round(im.height/2))),Image.Resampling.NEAREST),(round((meta['x']-137)/2+8)-170,round((meta['y']-2)/2+2)-192))
 plunger.extend(frame.tobytes())
(root/'assets/PLUNGER.BIN').write_bytes(plunger)
lines=['%encoding iso','geometry {']
def const(name,value):lines.append(f'    const uword {name}={value}')
def arr(name,values):lines.append('    ubyte['+str(len(values))+'] '+name+'=['+','.join(map(str,values))+']')
for k,side in enumerate(('l','r')):
 const(side+'ax',anchors[k][0]);const(side+'ay',anchors[k][1])
 const(side+'px',pivots[k][0]);const(side+'py',pivots[k][1])
 arr(side+'tx',[p[0] for p in tips[k]]);arr(side+'ty',[p[1] for p in tips[k]])
arr('bx',[p[0] for p in centers]);arr('by',[p[1] for p in centers])
arr('bax',[p[0] for p in banchors]);arr('bay',[p[1] for p in banchors])
const('BALL_BANK',balladdr>>16);const('BALL_ADDR',balladdr&65535)
const('BALL_DIAMETER',7)
for k in range(2):
 lines.append('    uword[256] invlen'+str(k)+'=['+','.join(map(str,[0 if i==0 else round(4096/math.sqrt(i)) for i in range(k*256,(k+1)*256)]))+']')
lines+=['}']
(root/'src/geometry.p8').write_text('\n'.join(lines)+'\n')
# Small fixed-width decimal font, one byte per row, bits 4..0 left to right.
fontrows=['01110100011000110001100011000101110','00100011000010000100001000010001110','01110100010000100010001000100011111','11110000010000101110000010000111110','00010001100101010010111110001000010','11111100001000011110000010000111110','01110100001000011110100011000101110','11111000010001000100010000100001000','01110100011000101110100011000101110','01110100011000101111000010000101110']
rows=[int(s[i:i+5],2) for s in fontrows for i in range(0,35,5)]
(root/'src/glyphs.p8').write_text('%encoding iso\nglyphs {\n    ubyte[70] @shared rows=['+','.join(map(str,rows))+']\n}\n')
bg.resize((1280,960),Image.Resampling.NEAREST).save(root/'evidence/table-at-scale2.png')
(root/'evidence/assets.json').write_text(json.dumps({'flipper_anchors':anchors,'flipper_pivots':pivots,'flipper_tips':tips,'bumper_centers':centers,'sprite_bytes':len(patterns),'ball_address':balladdr,'palette':'original indexed rounded to 12-bit'},indent=2))
print('sprites',len(patterns),'bytes; flipper pivots',pivots,'bumpers',centers)

font={'A': [14, 17, 17, 31, 17, 17, 17], 'B': [30, 17, 17, 30, 17, 17, 30], 'C': [14, 17, 16, 16, 16, 17, 14], 'D': [30, 17, 17, 17, 17, 17, 30], 'E': [31, 16, 16, 30, 16, 16, 31], 'F': [31, 16, 16, 30, 16, 16, 16], 'G': [14, 17, 16, 23, 17, 17, 15], 'H': [17, 17, 17, 31, 17, 17, 17], 'I': [14, 4, 4, 4, 4, 4, 14], 'J': [7, 2, 2, 2, 18, 18, 12], 'K': [17, 18, 20, 24, 20, 18, 17], 'L': [16, 16, 16, 16, 16, 16, 31], 'M': [17, 27, 21, 21, 17, 17, 17], 'N': [17, 25, 21, 19, 17, 17, 17], 'O': [14, 17, 17, 17, 17, 17, 14], 'P': [30, 17, 17, 30, 16, 16, 16], 'Q': [14, 17, 17, 17, 21, 18, 13], 'R': [30, 17, 17, 30, 20, 18, 17], 'S': [15, 16, 16, 14, 1, 1, 30], 'T': [31, 4, 4, 4, 4, 4, 4], 'U': [17, 17, 17, 17, 17, 17, 14], 'V': [17, 17, 17, 17, 17, 10, 4], 'W': [17, 17, 17, 21, 21, 21, 10], 'X': [17, 17, 10, 4, 10, 17, 17], 'Y': [17, 17, 10, 4, 4, 4, 4], 'Z': [31, 1, 2, 4, 8, 16, 31], ':': [0, 4, 4, 0, 4, 4, 0], ' ': [0, 0, 0, 0, 0, 0, 0]}
labelrows=[]
for ch in range(32,96):labelrows.extend(font.get(chr(ch),[0]*7))
parts=[]
for k in range(2):
 parts.append('    ubyte[224] label'+str(k)+'=['+','.join(map(str,labelrows[k*224:(k+1)*224]))+']')
p=root/'src/glyphs.p8';s=p.read_text().replace('\n}', '\n'+'\n'.join(parts)+'\n}');p.write_text(s)
