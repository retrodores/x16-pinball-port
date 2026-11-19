from pathlib import Path
import subprocess,json
import numpy as np
from scipy.signal import resample,fftconvolve,find_peaks
p=Path('/workspace/scratch/c2e9b03daa2e'); refs=p/'pinball-review/source/cadet/build/PCM'; out={}
for label,name in [('original','2026-11-17 22-59-31(1).mp4'),('x16','2026-11-18 23-02-35.mp4')]:
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p/'upload'/name),'-vn','-ac','1','-ar','11025','-f','f32le','-'])
 a=np.frombuffer(raw,'<f4').astype(float);row={}
 for sound in ['SOUND43','SOUND17','SOUND12','SOUND57','SOUND104']:
  b=np.frombuffer((refs/(sound+'.PCM')).read_bytes(),np.int8).astype(float)
  b=resample(b,round(len(b)*11025/11062.6220703125));b-=b.mean();n=len(b)
  corr=fftconvolve(a,b[::-1],mode='valid');cs=np.r_[0,np.cumsum(a*a)];power=cs[n:]-cs[:-n]
  corr=np.abs(corr)/np.sqrt(np.maximum(power,1e-20)*np.dot(b,b))
  peaks,_=find_peaks(corr,height=.08,distance=11025)
  peaks=sorted(peaks,key=lambda t:corr[t],reverse=True)[:8]
  row[sound]=[{'seconds':round(float(t)/11025,3),'normalized_correlation':round(float(corr[t]),4)} for t in peaks]
 out[label]=row
(p/'video-review/audio-matches.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
