#!/usr/bin/env python3
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
dst=root/'build/reference'
shutil.copytree(root/'vendor',dst,dirs_exist_ok=True)
p=dst/'SpaceCadetPinball/pb.cpp'
s=p.read_text().replace('#include "translations.h"','#include "translations.h"\n#include "TLine.h"\n#include "TCircle.h"\n#include "TPlunger.h"\n#include <typeinfo>\n#include "TFlipper.h"\n#include "TFlipperEdge.h"')
code=r'''
 if (getenv("CMDRX_EXPORT")) {
  FILE* f=fopen(getenv("CMDRX_EXPORT"),"w");
  auto b=MainTable->BallList[0];
  fprintf(f,"{\"radius\":%.9g,\"max_speed\":%.9g,\"plunger\":[%.9g,%.9g],\"edges\":[",b->Radius,b->Radius*200.0f,MainTable->PlungerPosition.X,MainTable->PlungerPosition.Y);
  bool first=true;
  for(auto component:MainTable->ComponentList) {
   auto c=dynamic_cast<TCollisionComponent*>(component);
   if(!c)continue;
   for(auto e:c->EdgeList) {
    auto l=dynamic_cast<TLine*>(e);auto circle=dynamic_cast<TCircle*>(e);
    if(!l&&!circle)continue;
    if(!first)fprintf(f,",");first=false;
    fprintf(f,"{\"component\":%d,\"class\":\"%s\",\"mask\":%u,\"active\":%d,\"elasticity\":%.9g,\"smoothness\":%.9g,\"threshold\":%.9g,\"boost\":%.9g,",
      c->GroupIndex,typeid(*c).name(),e->CollisionGroup,*e->ActiveFlagPtr,c->Elasticity,c->Smoothness,c->Threshold,c->Boost);
    if(l)fprintf(f,"\"line\":[%.9g,%.9g,%.9g,%.9g]}",l->X0,l->Y0,l->X1,l->Y1);
    else fprintf(f,"\"circle\":[%.9g,%.9g,%.9g]}",circle->Circle.Center.X,circle->Circle.Center.Y,circle->Circle.RadiusSq);
   }
  }
  fprintf(f,"],\"gravity\":[");
  for(auto component:MainTable->ComponentList) {
   auto t=dynamic_cast<TTableLayer*>(component);
   if(t)fprintf(f,"%.9g,%.9g,%.9g",t->GraityDirX,t->GraityDirY,t->GraityMult);
  }
  fprintf(f,"]");
  fprintf(f,",\"flippers\":[");
  first=true;
  for(auto component:MainTable->FlipperList) {
   auto e=component->FlipperEdge;
   if(!first)fprintf(f,",");first=false;
   fprintf(f,"{\"CollisionGroup\":%u,",e->CollisionGroup);
   fprintf(f,"\"Elasticity\":%.9g",e->Elasticity);
   fprintf(f,",\"Smoothness\":%.9g",e->Smoothness);
   fprintf(f,",\"CirclebaseRadius\":%.9g",e->CirclebaseRadius);
   fprintf(f,",\"CircleT1Radius\":%.9g",e->CircleT1Radius);
   fprintf(f,",\"CirclebaseRadiusSq\":%.9g",e->CirclebaseRadiusSq);
   fprintf(f,",\"CircleT1RadiusSq\":%.9g",e->CircleT1RadiusSq);
   fprintf(f,",\"CirclebaseRadiusMSq\":%.9g",e->CirclebaseRadiusMSq);
   fprintf(f,",\"CircleT1RadiusMSq\":%.9g",e->CircleT1RadiusMSq);
   fprintf(f,",\"AngleMax\":%.9g",e->AngleMax);
   fprintf(f,",\"CollisionMult\":%.9g",e->CollisionMult);
   fprintf(f,",\"DistanceDiv\":%.9g",e->DistanceDiv);
   fprintf(f,",\"DistanceDivSq\":%.9g",e->DistanceDivSq);
   fprintf(f,",\"ExtendSpeed\":%.9g",e->ExtendSpeed);
   fprintf(f,",\"RetractSpeed\":%.9g",e->RetractSpeed);
   fprintf(f,",\"InvT1Radius\":%.9g",e->InvT1Radius);
   fprintf(f,",\"YMin\":%.9g",e->YMin);
   fprintf(f,",\"YMax\":%.9g",e->YMax);
   fprintf(f,",\"XMin\":%.9g",e->XMin);
   fprintf(f,",\"XMax\":%.9g",e->XMax);
   fprintf(f,",\"RotOrigin\":[%.9g,%.9g]",e->RotOrigin.X,e->RotOrigin.Y);
   fprintf(f,",\"A1Src\":[%.9g,%.9g]",e->A1Src.X,e->A1Src.Y);
   fprintf(f,",\"A2Src\":[%.9g,%.9g]",e->A2Src.X,e->A2Src.Y);
   fprintf(f,",\"B1Src\":[%.9g,%.9g]",e->B1Src.X,e->B1Src.Y);
   fprintf(f,",\"B2Src\":[%.9g,%.9g]",e->B2Src.X,e->B2Src.Y);
   fprintf(f,",\"T1Src\":[%.9g,%.9g]",e->T1Src.X,e->T1Src.Y);
   fprintf(f,",\"T2Src\":[%.9g,%.9g]",e->T2Src.X,e->T2Src.Y);
   fprintf(f,"}");
  }
  fprintf(f,"]");
  fprintf(f,",\"plunger_params\":{");
  for(auto component:MainTable->ComponentList) {
   auto p=dynamic_cast<TPlunger*>(component);if(!p)continue;
   fprintf(f,"\"MaxPullback\":%.9g,\"PullbackIncrement\":%.9g,\"PullbackDelay\":%.9g,\"Elasticity\":%.9g,\"Smoothness\":%.9g,\"bitmap_count\":%zu",p->MaxPullback,p->PullbackIncrement,p->PullbackDelay,p->Elasticity,p->Smoothness,p->ListBitmap->size());
  }
  fprintf(f,"}}\n");fclose(f);exit(0);
 }
'''
s=s.replace('MainTable = new TPinballTable();','MainTable = new TPinballTable();'+code)
p.write_text(s)
