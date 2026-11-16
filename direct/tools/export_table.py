#!/usr/bin/env python3
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
dst=root/'build/reference'
shutil.copytree(root/'vendor',dst,dirs_exist_ok=True)
p=dst/'SpaceCadetPinball/pb.cpp'
s=p.read_text().replace('#include "translations.h"','#include "translations.h"\n#include "TLine.h"\n#include "TCircle.h"\n#include "TPlunger.h"\n#include <typeinfo>')
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
  fprintf(f,"]}\n");fclose(f);exit(0);
 }
'''
s=s.replace('MainTable = new TPinballTable();','MainTable = new TPinballTable();'+code)
p.write_text(s)
