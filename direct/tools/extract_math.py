#!/usr/bin/env python3
"""Extract original method bodies verbatim; the original source remains vendored."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[1]
source=root/'vendor/SpaceCadetPinball/maths.cpp'
s=source.read_text()
names=['ray_intersect_circle','normalize_2d','line_init','ray_intersect_line','cross','vector_sub','vector_add','vector_mul','basic_collision','DotProduct','Distance_Squared','Distance','magnitudeSq','SinCos','RotatePt','distance_to_flipper']
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
(root/'src/original_math.cpp').write_text('// Generated verbatim from vendored maths.cpp. See vendor/LICENSE.\n#include "port_types.h"\n#include "flipper.h"\n\n'+'\n\n'.join(parts)+'\n')
(root/'src/provenance.json').write_text(json.dumps({'upstream':'https://github.com/k4zmu2a/SpaceCadetPinball','revision':'cb9b7b886244a27773f66b0b19fdc2998392565e','maths_cpp_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method_bodies':'verbatim','methods':names},indent=2)+'\n')

flipper_source=root/'vendor/SpaceCadetPinball/TFlipperEdge.cpp'
flipper_text=flipper_source.read_text()
flipper_names=['FindCollisionDistance','EdgeCollision','set_control_points','flipper_angle_delta','SetMotion']
flipper_parts=[]
for m in re.finditer(r'^(?:float|void|int) TFlipperEdge::(\w+)\(',flipper_text,re.M):
 if m[1] not in flipper_names:continue
 start=flipper_text.index('{',m.start());depth=1;end=start+1
 while depth:
  if flipper_text[end]=='{':depth+=1
  if flipper_text[end]=='}':depth-=1
  end+=1
 flipper_parts.append(flipper_text[m.start():end])
(root/'src/original_flipper.cpp').write_text('// Generated verbatim from vendored TFlipperEdge.cpp. See vendor/LICENSE.\n#include "flipper.h"\n\n'+'\n\n'.join(flipper_parts)+'\n')
(root/'src/flipper_provenance.json').write_text(json.dumps({'upstream':'https://github.com/k4zmu2a/SpaceCadetPinball','revision':'cb9b7b886244a27773f66b0b19fdc2998392565e','source_sha256':hashlib.sha256(flipper_source.read_bytes()).hexdigest(),'method_bodies':'verbatim','methods':flipper_names},indent=2)+'\n')

control_source=root/'vendor/SpaceCadetPinball/TFlipper.cpp'
control_text=control_source.read_text()
control_parts=[]
for m in re.finditer(r'^(?:void|int) TFlipper::(GetFlipperStepAngle|FlipperCollision)\(',control_text,re.M):
 start=control_text.index('{',m.start());depth=1;end=start+1
 while depth:
  if control_text[end]=='{':depth+=1
  if control_text[end]=='}':depth-=1
  end+=1
 control_parts.append(control_text[m.start():end])
(root/'src/original_flipper_control.cpp').write_text('// Generated verbatim from vendored TFlipper.cpp. See vendor/LICENSE.\n#include "flipper.h"\n\n'+'\n\n'.join(control_parts)+'\n')

plunger_source=root/'vendor/SpaceCadetPinball/TPlunger.cpp'
plunger_text=plunger_source.read_text()
plunger_parts=[]
plunger_names=['Collision','Message','BallFeedTimer','PullbackTimer','ReleasedTimer']
for m in re.finditer(r'^(?:void|int) TPlunger::(\w+)\(',plunger_text,re.M):
 if m[1] not in plunger_names:continue
 start=plunger_text.index('{',m.start());depth=1;end=start+1
 while depth:
  if plunger_text[end]=='{':depth+=1
  if plunger_text[end]=='}':depth-=1
  end+=1
 plunger_parts.append(plunger_text[m.start():end])
(root/'src/original_plunger.cpp').write_text('// Generated verbatim from vendored TPlunger.cpp. See vendor/LICENSE.\n#include "plunger.h"\n\n'+'\n\n'.join(plunger_parts)+'\n')
(root/'src/plunger_provenance.json').write_text(json.dumps({'upstream':'https://github.com/k4zmu2a/SpaceCadetPinball','revision':'cb9b7b886244a27773f66b0b19fdc2998392565e','source_sha256':hashlib.sha256(plunger_source.read_bytes()).hexdigest(),'method_bodies':'verbatim','methods':plunger_names},indent=2)+'\n')

(root/'src/flipper_control_provenance.json').write_text(json.dumps({'upstream':'https://github.com/k4zmu2a/SpaceCadetPinball','revision':'cb9b7b886244a27773f66b0b19fdc2998392565e','source_sha256':hashlib.sha256(control_source.read_bytes()).hexdigest(),'method_bodies':'verbatim','methods':['GetFlipperStepAngle','FlipperCollision']},indent=2)+'\n')
