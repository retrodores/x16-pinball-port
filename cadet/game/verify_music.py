"""Independent tick/state/key-event comparison of original and compact ZSM."""
from pathlib import Path
import json
r=Path(__file__).resolve().parents[2];o=r/'cadet/play-build'
def decode(path):
 b=path.read_bytes();p=16;tick=0;state={};snapshots={};keys=[]
 while True:
  c=b[p];p+=1
  if c>=128:
   snapshots[tick]=dict(state)
   if c==128:break
   tick+=c&127;continue
  if c<64:seq=[('p',c,b[p])];p+=1
  else:
   assert c!=64
   seq=[('f',b[i],b[i+1])for i in range(p,p+2*(c&63),2)];p+=2*(c&63)
  for typ,reg,value in seq:
   state[typ,reg]=value
   if typ=='f'and reg in (1,8,20):keys.append((tick,reg,value))
 return tick,snapshots,keys
a=decode(r/'cadet/build/THEME.ZSM');b=decode(o/'THEME.ZSM')
assert a[0]==b[0] and a[2]==b[2]
sa={};sb={}
for tick in range(a[0]+1):
 sa=a[1].get(tick,sa);sb=b[1].get(tick,sb)
 assert sa==sb,(tick,sa,sb)
report={'end_ticks':a[0],'side_effect_events':len(a[2]),'all_tick_register_states_match':True,'key_and_control_events_match':True}
(o/'music-equivalence.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
