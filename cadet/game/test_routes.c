/* Original recovered gateway/rail fixtures, exercising production engine internals.
 * Fixed IDs are checked against original component, mask, kind and ramp action.
 * Checks topology/collision layers; visual occlusion is tested separately. */
#include "engine.c"
#ifndef __CX16__
#include <stdio.h>
#endif
static uint16_t checks,failures;
static void check(bool ok){++checks;if(!ok)++failures;}
static void text(const char*s){
#ifdef __CX16__
 while(*s)*(volatile uint8_t*)0x9fbb=*s++;
#else
 fputs(s,stdout);
#endif
}
static void hex(uint16_t x){
 for(uint8_t i=0;i<4;++i){char s[2]={"0123456789abcdef"[x>>12],0};text(s);x<<=4;}
}
static void prepare(const Edge*e,uint8_t mask,int16_t*dx,int16_t*dy){
 int16_t mx=(e->x+e->ex)/2,my=(e->y+e->ey)/2;
 *dx=-e->nx/16;*dy=-e->ny/16;
 game_start();game_place(mx+e->nx/32,my+e->ny/32,*dx*60,*dy*60,mask);
}
static void gateway(uint16_t id,uint16_t group,uint8_t source,uint8_t target,uint8_t action){
 Edge e=*edge(id);check(e.kind==Ramp);check(original_groups[e.group]==group);
 check(e.mask==source);check(metadata[e.param].action==action);check(metadata[e.param].mask==target);
 for(uint8_t layer=1;layer<=4;layer*=2){
  int16_t dx,dy;prepare(&e,layer,&dx,&dy);Hit h;bool found=nearest(dx,dy,&h);
  if(layer==source)check(found&&h.id==id);else check(!found||h.id!=id);
  move(dx,dy,1);check(game.mask==(layer==source?target:layer));check(game.state==InPlay);
  check(game.layer_changes==(layer==source&&source!=target?1:0));
  if(layer==source)check(game.ramp==(action==1));
 }
}
static void rail(uint16_t id,uint16_t group,uint8_t source){
 Edge e=*edge(id);check(e.kind==Wall);check(original_groups[e.group]==group);check(e.mask==source);
 for(uint8_t layer=1;layer<=4;layer*=2){
  int16_t dx,dy;prepare(&e,layer,&dx,&dy);Hit h;bool found=nearest(dx,dy,&h);
  if(layer==source)check(found&&h.id==id);else check(!found||h.id!=id);
  move(dx,dy,1);int16_t dist=dot(game.x-(e.x+e.ex)/2,game.y-(e.y+e.ey)/2,e.nx,e.ny);
  check(layer==source?dist>=0:dist<0);check(game.mask==layer);check(game.state==InPlay);
  if(layer==source)check(dot(game.vx,game.vy,e.nx,e.ny)>0);
 }
}
int main(void){
 if(!game_load()){text("# LOAD FAILED\n# DONE\n");return 1;}
 gateway(1152,101,2,1,2);gateway(1153,101,2,4,3);gateway(1158,101,4,2,1);
 gateway(1205,101,1,2,1);gateway(1210,105,2,1,3);gateway(1211,105,1,2,1);
 /* A triangle boundary on the purple ramp must not lift a floor-layer ball. */
 gateway(1203,101,2,2,1);
 rail(697,106,2);rail(698,106,2);rail(699,106,2);rail(700,106,2);
 rail(521,306,4);rail(523,306,4);rail(525,306,4);rail(527,306,4);
 text("# ROUTES ");hex(checks);text(" ");hex(failures);text(failures?" FAIL\n":" PASS\n");text("# DONE\n");
#ifdef __CX16__
 *(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");
#endif
 return failures!=0;
}
