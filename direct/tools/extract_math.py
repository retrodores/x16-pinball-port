#!/usr/bin/env python3
"""Extract original method bodies verbatim; the original source remains vendored."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[1]
source=root/'vendor/SpaceCadetPinball/maths.cpp'
s=source.read_text()
names=['ray_intersect_circle','normalize_2d','line_init','ray_intersect_line','cross','vector_sub','vector_add','vector_mul','basic_collision','DotProduct','Distance_Squared','Distance','magnitudeSq']
parts=[]
for m in re.finditer(r'^(?:float|void|vector2|vector3|int) maths::(\w+)\(',s,re.M):
 if m[1] not in names:continue
 start=s.index('{',m.start());depth=1;end=start+1
 while depth:
  if s[end]=='{':depth+=1
  if s[end]=='}':depth-=1
  end+=1
 parts.append(s[m.start():end])
(root/'src/maths.h').write_bytes((root/'vendor/SpaceCadetPinball/maths.h').read_bytes())
(root/'src/original_math.cpp').write_text('// Generated verbatim from vendored maths.cpp. See vendor/LICENSE.\n#include "port_types.h"\n\n'+'\n\n'.join(parts)+'\n')
(root/'src/provenance.json').write_text(json.dumps({'upstream':'https://github.com/k4zmu2a/SpaceCadetPinball','revision':'cb9b7b886244a27773f66b0b19fdc2998392565e','maths_cpp_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method_bodies':'verbatim','methods':names},indent=2)+'\n')
