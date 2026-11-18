from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
r=Path(__file__).resolve().parents[1];o=r/'cadet/build'
pal=(o/'PAL.BIN').read_bytes()
colors=np.array([((pal[i+1]&15)*17,(pal[i]>>4)*17,(pal[i]&15)*17)for i in range(0,512,2)])
i=int(np.argmin(((colors-255)**2).sum(axis=1)));bank,pen=divmod(i,16)
assert pen
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',9)
data=bytearray(32)
for code in range(33,128):
 a=Image.new('1',(8,8));ImageDraw.Draw(a).text((0,-2),chr(code),fill=1,font=font)
 p=np.asarray(a,dtype=np.uint8)*pen;data.extend(((p[:,::2]<<4)|p[:,1::2]).tobytes())
(o/'FONT.BIN').write_bytes(data)
catalog=json.loads((o/'audio-catalog.json').read_text())['assets']
(o/'lab-assets.h').write_text('#define FONT_PALETTE '+str(bank)+'\n#define EFFECT_COUNT '+str(len(catalog))+
 '\nstatic const char*const effect_files[]={'+','.join('"PCM/'+x['pcm']+'"'for x in catalog)+'};\n'+
 'static const unsigned short effect_lengths[]={'+','.join(str(x['bytes'])for x in catalog)+'};\n')
print('lab assets ready')
