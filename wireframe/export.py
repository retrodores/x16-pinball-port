#!/usr/bin/env python3
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
runpy.run_path(str(root/'direct/integer/export_layers.py'),run_name='__main__')
p=root/'direct/build/reference/SpaceCadetPinball/pb.cpp';s=p.read_text()
s=s.replace('#include "TRamp.h"','#include "TRamp.h"\n#include "TSink.h"\n#include "TKickout.h"\n#include "THole.h"\n#include "TOneway.h"')
insert=r'''
    if(auto k=dynamic_cast<TSink*>(c))fprintf(f,"\"capture\":{\"type\":1,\"position\":[%.9g,%.9g],\"direction\":[%.9g,%.9g],\"speed\":%.9g,\"delay\":%.9g},",k->BallPosition.X,k->BallPosition.Y,k->BallThrowDirection.X,k->BallThrowDirection.Y,k->ThrowSpeedMult1,k->TimerTime);
    if(auto k=dynamic_cast<TKickout*>(c))fprintf(f,"\"capture\":{\"type\":2,\"position\":[%.9g,%.9g],\"direction\":[%.9g,%.9g],\"speed\":%.9g,\"delay\":%.9g,\"field_radius_sq\":%.9g},",k->Circle.Center.X,k->Circle.Center.Y,k->BallThrowDirection.X,k->BallThrowDirection.Y,k->ThrowSpeedMult1,k->TimerTime1,k->Circle.RadiusSq);
    if(auto h=dynamic_cast<THole*>(c))fprintf(f,"\"hole\":{\"mask\":%d,\"z\":%.9g,\"pull\":%.9g,\"radius_sq\":%.9g},",h->CollisionMask,h->ZSetValue,h->GravityPull,h->Circle.RadiusSq);
    if(auto o=dynamic_cast<TOneway*>(c))fprintf(f,"\"pass\":%d,",e==o->Line);
'''
s=s.replace('    auto ramp=dynamic_cast<TRamp*>(c);',insert+'    auto ramp=dynamic_cast<TRamp*>(c);');p.write_text(s)
