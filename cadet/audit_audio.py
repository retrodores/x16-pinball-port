#!/usr/bin/env python3
"""Recover sound references, convert all source effects, and match the OBS audio."""
from pathlib import Path
import json, wave, hashlib, math, csv, collections, re, zlib
from fractions import Fraction
import numpy as np
from scipy.signal import resample_poly, correlate, find_peaks, butter, sosfiltfilt
ROOT=Path(__file__).resolve().parents[1]
SRC=Path('/opt/spacecadet-x16-analysis/input/game')
OUT=ROOT/'cadet/build';OUT.mkdir(exist_ok=True)
PCM=OUT/'PCM';PCM.mkdir(exist_ok=True)
j=json.loads(Path('/opt/spacecadet-x16-analysis/evidence/inventory.json').read_text())
groups=j['groups']
sounds={}
for g in groups:
 if any(e['type']==0 and e.get('values')==[202] for e in g['entries']):
  sounds[g['id']]=next(e['text'].upper() for e in g['entries'] if e['type']==9)
assert sounds
# loader::query_visual/material/kicker field semantics, preserving field provenance.
references=[]
def resolve(gid,visited=()):
 if gid in visited:return {}
 g=groups[gid];v={}
 for e in g['entries']:
  if e['type']==10:
   a=e['values'];k=0
   while k+1<len(a):
    code,ref=a[k:k+2];k+=9 if code==1500 else 2
    if code in (300,400):v.update(resolve(ref,visited+(gid,)))
    if code in (304,406,1100,1101):
     v[{304:'soft_hit',406:'hard_hit',1100:'sound4',1101:'sound3'}[code]]={'group':ref,'wav':sounds[ref],'source_group':gid,'field':code}
  if e['type']==11 and e['values'][0] in (301,302,304,401,402,403,404,405,406):
   a=e['values'];k=0
   while k+1<len(a):
    code=int(a[k]);ref=a[k+1];k+=4 if code==404 else 2
    if code in (304,406):v[{304:'soft_hit',406:'hard_hit'}[code]]={'group':int(ref),'wav':sounds[int(ref)],'source_group':gid,'field':code}
 return v
for g in groups:
 if g['name'] and any(e['type']==0 and e.get('values')==[200] for e in g['entries']):
  v=resolve(g['id'])
  if v:references.append({'component_group':g['id'],'name':g['name'],'sounds':v})
# Preserve original relative loudness. Never normalize each effect independently.
# Closest hardware rate to source 11025 Hz: VERA register 29 = 11062.6220703125 Hz.
clock=25_000_000;rate_reg=29;target=clock*rate_reg/65536
catalog=[];templates={}
for p in sorted(SRC.glob('*.WAV'),key=lambda p:(int(re.search(r'\d+',p.stem)[0]),p.name)):
 with wave.open(str(p))as w:
  assert w.getsampwidth()==1 and w.getnchannels()==1
  rate=w.getframerate();raw=w.readframes(w.getnframes())
 x=np.frombuffer(raw,np.uint8).astype(np.float64)-128
 ratio=Fraction(clock*rate_reg,65536*rate).limit_denominator(4096)
 # Rational resampling at the actual hardware rate avoids pitch/duration drift.
 y=resample_poly(x,ratio.numerator,ratio.denominator)
 y=y[:round(len(x)*target/rate)]
 y=np.rint(np.clip(y,-128,127)).astype(np.int8)
 path=PCM/(p.stem+'.PCM');path.write_bytes(y.tobytes())
 templates[p.name]=resample_poly(x,11025,rate)
 catalog.append({'name':p.name,'source_rate':rate,'source_frames':len(x),'source_seconds':len(x)/rate,
                 'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pcm':path.name,'bytes':len(y),
                 'pcm_sha256':hashlib.sha256(y.tobytes()).hexdigest(),'rate_register':rate_reg,
                 'actual_rate':target,'pcm_seconds':len(y)/target,'peak':int(np.abs(y.astype(np.int16)).max()),
                 'referenced_groups':[g for g,n in sounds.items()if n==p.name]})
assert len(catalog)==len(list(SRC.glob("*.WAV")))
(OUT/'audio-catalog.json').write_text(json.dumps({'format':'signed 8-bit mono, no header','rate_register':rate_reg,
 'actual_rate':target,'resource_sounds':len(sounds),'wav_files':len(catalog),'assets':catalog,
 'component_references':references},indent=2)+'\n')
with (OUT/'component-sounds.csv').open('w',newline='')as f:
 c=csv.writer(f);c.writerow(['component_group','component','role','WAV','resource_group','attribute_group','attribute'])
 for row in references:
  for role,a in row['sounds'].items():c.writerow([row['component_group'],row['name'],role,a['wav'],a['group'],a['source_group'],a['field']])
capture_path=ROOT/'cadet/capture/obs-audio.s8'
capture_bytes=capture_path.read_bytes() if capture_path.exists() else zlib.decompress(capture_path.with_suffix('.s8.zlib').read_bytes())
capture=np.frombuffer(capture_bytes,np.int8).astype(np.float64)
# Bandpass suppresses music bass/DC while retaining sample signatures.
band=butter(4,[250,2200],btype='bandpass',fs=11025,output='sos')
capture=sosfiltfilt(band,capture);matches=[];best=[]
for name,x in templates.items():
 x=sosfiltfilt(band,x);x=x[:min(len(x),int(.25*11025))]
 if len(x)<32 or np.linalg.norm(x)==0:continue
 x=x-x.mean()
 num=correlate(capture,x,mode='valid',method='fft')
 cs=np.concatenate(([0.],np.cumsum(capture*capture)))
 energy=cs[len(x):]-cs[:-len(x)]
 den=np.sqrt(np.maximum(energy,1)*np.dot(x,x));corr=num/den
 idx=int(np.argmax(corr));best.append({'wav':name,'correlation':float(corr[idx]),'seconds':idx/11025})
 peaks,_=find_peaks(corr,height=.5,distance=max(1,int(.08*11025)))
 for i in peaks:matches.append({'wav':name,'seconds':round(float(i)/11025,5),'correlation':round(float(corr[i]),5),
 'template_seconds':round(len(x)/11025,5),'confidence':'strong waveform match' if corr[i]>=.7 else 'candidate waveform match'})
matches.sort(key=lambda a:(a['seconds'],-a['correlation']))
# Keep ambiguous candidates, rather than silently choosing between similar effects.
(OUT/'obs-sound-matches.json').write_text(json.dumps({'method':'normalized correlation after 250–2200 Hz bandpass; first up to 0.25 s of each source WAV',
 'threshold':.5,'capture_seconds':len(capture)/11025,'matches':matches,'best_per_asset':sorted(best,key=lambda x:-x['correlation'])},indent=2)+'\n')
with (OUT/'obs-sound-matches.csv').open('w',newline='')as f:
 c=csv.DictWriter(f,fieldnames=['seconds','wav','correlation','template_seconds','confidence']);c.writeheader();c.writerows(matches)
print(json.dumps({'wav_files':len(catalog),'resource_sounds':len(sounds),'component_references':len(references),
 'pcm_bytes':sum(x['bytes']for x in catalog),'OBS_matches':len(matches),'top_matches':sorted(best,key=lambda x:-x['correlation'])[:12]},indent=2),flush=True)
