#!/usr/bin/env python3
from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
j=json.loads((r/'data/table.json').read_text())
def number(v):
 s=format(v,'.9g')
 if '.' not in s and 'e' not in s:s+='.0'
 return s+'f'
parts=['// Exported original TFlipperEdge state; compact offset/value initializer.','#pragma once','#include <stddef.h>','#include <string.h>','struct FlipperSetting {uint16_t offset;float value;};','static const FlipperSetting flipper_settings[]={']
assert len(j['flippers'])==2
for i,f in enumerate(j['flippers']):
 for k,v in f.items():
  if k=='CollisionGroup':
   assert v==1
   continue
  if isinstance(v,list):
   for component,value in zip(['X','Y'],v):parts.append(' {%d*sizeof(TFlipperEdge)+offsetof(TFlipperEdge,%s)+offsetof(vector2,%s),%s},'%(i,k,component,number(value)))
  else:parts.append(' {%d*sizeof(TFlipperEdge)+offsetof(TFlipperEdge,%s),%s},'%(i,k,number(v)))
parts+=['};','static void initialize_flippers(TFlipperEdge* edges) {',' for(const auto& setting:flipper_settings)memcpy((char*)edges+setting.offset,&setting.value,sizeof(float));','}']
(r/'src/flipper_params.h').write_text('\n'.join(parts)+'\n')
parts=['// Original initialized TPlunger constructor parameters.','#pragma once','static void initialize_plunger(TPlunger& p) {']
for k,v in j['plunger_params'].items():
 if k=='bitmap_count':parts.append(' p.bitmaps.count=%d;'%v)
 else:parts.append(' p.%s=%s;'%(k,number(v)))
parts.append('}')
parts.append('constexpr float serve_y=%s;'%number(j['plunger'][1]))
(r/'src/plunger_params.h').write_text('\n'.join(parts)+'\n')
