#!/usr/bin/env python3
"""Extend the disposable upstream export; leave vendor and base-plane data intact."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
runpy.run_path(str(root/'tools/export_table.py'),run_name='__main__')
p=root/'build/reference/SpaceCadetPinball/pb.cpp'
s=p.read_text().replace('#include "TFlipperEdge.h"','#include "TFlipperEdge.h"\n#include "TRamp.h"')
anchor='    if(l)fprintf(f,'
insert=r'''
    auto ramp=dynamic_cast<TRamp*>(c);
    if(ramp) {
     auto plane=static_cast<ramp_plane_type*>(e->WallValue);
     int action=plane?1:e==ramp->Line1?0:e==ramp->Line2?2:3;
     fprintf(f,"\"ramp\":{\"action\":%d,\"mask\":%d,\"zflag\":%d,\"z\":%.9g,\"drag\":%.9g,\"plane\":[%.9g,%.9g,%.9g],\"force\":[%.9g,%.9g]},",
      action,plane?ramp->CollisionGroup:action==2?ramp->Wall1CollisionGroup:ramp->Wall2CollisionGroup,
      ramp->BallZOffsetFlag,action==2?ramp->Wall1BallOffset:ramp->Wall2BallOffset,ramp->BallFieldMult,
      plane?plane->BallCollisionOffset.X:0,plane?plane->BallCollisionOffset.Y:0,plane?plane->BallCollisionOffset.Z:0,
      plane?plane->FieldForce.X:0,plane?plane->FieldForce.Y:0);
    }
'''
assert anchor in s;s=s.replace(anchor,insert+anchor)
p.write_text(s)
