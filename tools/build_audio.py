#!/usr/bin/env python3
from pathlib import Path
import numpy as np
from scipy.signal import resample_poly
import wave,json
root=Path(__file__).resolve().parents[1]
source=Path('/opt/spacecadet-x16-analysis/input/game')
effects=['SOUND104.WAV','SOUND105.WAV','SOUND12.WAV','SOUND21.WAV','SOUND4.WAV','SOUND1.WAV','SOUND108.WAV']
pack=bytearray();banks=[];addresses=[];lengths=[]
for name in effects:
 with wave.open(str(source/name)) as w:
  a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.uint8).astype(float)-128
  rate=w.getframerate()
  a=resample_poly(a,8011,rate)
  a=np.rint(np.clip(a,-127,127)).astype(np.int8)
 off=len(pack);banks.append(16+off//8192);addresses.append(0xa000+(off%8192));lengths.append(len(a));pack.extend(a.tobytes())
(root/'assets/SFX.BIN').write_bytes(pack)
lines=['%encoding iso','audio_assets {']
for typ,name,values in [('ubyte','bank',banks),('uword','address',addresses),('uword','length',lengths)]:
 lines.append('    '+typ+'[7] '+name+'=['+','.join(map(str,values))+']')
lines.append('}')
(root/'src/audio_assets.p8').write_text('\n'.join(lines)+'\n')
tracks=[]
for n in [0]:
 p=root/f'evidence/music{n}.wav'
 with wave.open(str(p)) as w:
  a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.int32).reshape(-1,2).mean(axis=1)
  rate=w.getframerate()
 # Keep the entire original sequence. No looping/trimming of musical sections.
 a=np.rint(np.clip(a/256,-127,127)).astype(np.int8)
 (root/'assets/MUSIC.PCM').write_bytes(a.tobytes())
 tracks.append({'file':'MUSIC.PCM','rate':rate,'seconds':len(a)/rate,'bytes':len(a)})
(root/'evidence/audio-assets.json').write_text(json.dumps({'effects':effects,'sfx_bytes':len(pack),'music':tracks,'render_soundfont':'TimGM6mb.sf2','pcm_format':'8011 Hz mono signed 8-bit; VERA rate 21'},indent=2))
print('Effects:',len(pack),'Music:',tracks)
