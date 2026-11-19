"""Reproduce the four review crops from the user-supplied original OBS files."""
from pathlib import Path
import argparse,subprocess as sp,json,hashlib
p=argparse.ArgumentParser()
p.add_argument('video_root',type=Path)
p.add_argument('--out',type=Path,default=Path(__file__).parent)
a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
port=a.video_root/'2026-11-19 00-37-20.mp4'
original=a.video_root/'2026-11-17 22-59-31(1).mp4'
specs=[
 (port,41.85,.4,'200:210:700:610',None,'6x4','slingshot-41.85.jpg'),
 (port,37.4,.6,'210:260:430:580',None,'6x6','slingshot-left37.4.jpg'),
 (port,7.8,.8,'160:260:900:750',None,'8x6','plunger-7.8-detail.jpg'),
 (original,12.8,.5,'500:220:470:700','375:165','6x5','original-slingshots12.8.jpg'),
]
for source,start,duration,crop,scale,tile,name in specs:
 filters=['crop='+crop]
 if scale:filters+=['scale='+scale]
 filters+=['setpts=PTS+'+str(start)+'/TB',
  "drawtext=text='%{pts\\:hms}':fontsize=14:fontcolor=yellow:box=1:boxcolor=black",'tile='+tile]
 sp.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(start),'-t',str(duration),'-i',str(source),
  '-vf',','.join(filters),'-frames:v','1',str(a.out/name)],check=True)
report={f.name:{'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in (port,original)}
(a.out/'inputs.json').write_text(json.dumps(report,indent=2)+'\n')
