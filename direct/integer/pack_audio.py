#!/usr/bin/env python3
"""Rebank the existing original effects without trimming/resampling them again."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
out=root/'build/integer';out.mkdir(exist_ok=True,parents=True)
data=(root.parent/'assets/SFX.BIN').read_bytes()
names=['SOUND104.WAV','SOUND105.WAV','SOUND12.WAV','SOUND21.WAV','SOUND4.WAV','SOUND1.WAV','SOUND108.WAV']
lengths=[790,1329,3020,6579,11895,40219,5449]
assert len(data)==sum(lengths)==69281
(out/'SFXA.BIN').write_bytes(data[:65536]);(out/'SFXB.BIN').write_bytes(data[65536:])
banks=[];lo=[];hi=[];pos=0
for length in lengths:
 bank=24+pos//8192;banks.append(2 if bank==32 else bank)
 address=0xa000+pos%8192;lo.append(address&255);hi.append(address>>8);pos+=length
arrays={'audio_banks':banks,'audio_low':lo,'audio_high':hi,'audio_length_low':[n&255 for n in lengths],'audio_length_high':[n>>8 for n in lengths],'audio_priorities':[2,1,4,3,1,5,0]}
(out/'audio-assets.inc').write_text('\n'.join(n+': .byte '+','.join(map(str,v)) for n,v in arrays.items())+'\n')
(out/'audio-manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(data).hexdigest(),'files':names,'lengths':lengths,'format':'signed 8-bit mono','rate_register':21,'sample_rate':8011,'banks':'24..31, then 2','music':False},indent=2)+'\n')
