/* Original mechanism poses: masked background patches, plus instant tilemap
 * swaps for the original 100 ms slingshot rubber/glow composite. The latter
 * uses private tile patterns after FONT and the masked-ball buffer. */
#include "dynamic.h"
#include "engine.h"
extern uint8_t game_lamp(uint16_t),game_pose(uint16_t);
static volatile uint8_t *const dv=(volatile uint8_t*)0x9f20;
static uint8_t shown[DYNAMIC_COUNT],active=255,target,next_component,shown_epoch,fast_epoch;
static uint8_t cross_shown,spinner_epoch;
static uint8_t runs_left,run_left,address_bank;
static uint16_t address;
static const uint8_t *run_ptr,*mask_ptr,*value_ptr;
static void bank(uint8_t b){__asm__ volatile("":::"memory");*(volatile uint8_t*)0=b;__asm__ volatile("":::"memory");}
static uint16_t u16(const uint8_t*p){return(uint16_t)p[0]|((uint16_t)p[1]<<8);}
static void write_address(uint32_t a){dv[5]=0;dv[0]=a;dv[1]=a>>8;dv[2]=0x10|(a>>16);}
static void addresses(void){
 dv[5]=0;dv[0]=address;dv[1]=address>>8;dv[2]=0x10|address_bank;
 dv[5]=1;dv[0]=address;dv[1]=address>>8;dv[2]=0x10|address_bank;dv[5]=0;
}
static bool fast_update(void){
 bool changed=false;
 for(uint8_t i=0;i<DYNAMIC_FAST_COUNT;++i){
  const DynamicDesc*d=dynamic_desc+i;uint8_t pose=game_pose(d->group)!=0;
  if(shown[i]==pose)continue;
  bank(d->bank);const uint8_t*p=(const uint8_t*)(uintptr_t)d->ptr;
  uint8_t count=*p;p+=4;
  while(count--){uint16_t map=u16(p),value=u16(p+2+(uint8_t)(pose*2));p+=6;
   dv[5]=0;dv[0]=map;dv[1]=map>>8;dv[2]=0x10;dv[3]=value;dv[3]=value>>8;
  }
  shown[i]=pose;changed=true;
 }
 fast_epoch=game.visual_epoch;return changed;
}
static void cross_update(void){
 uint8_t on=game_lamp(OpeningCrossLamp);
 if(on==cross_shown)return;
 cross_shown=on;
 /* Sprite 127 stays behind the ball and doesn't own slingshot tiles. */
 write_address(0x1fffeUL);
 dv[3]=on?12:0;
}
bool dynamic_update(uint8_t budget){
 if(game.state==Ready||cross_shown)cross_update();
 uint8_t saved=*(volatile uint8_t*)0;
 if(fast_epoch!=game.visual_epoch){bool changed=fast_update();bank(saved);if(changed)return true;}
 if(!budget)return false;
 bool changed=false;
again:
 if(active==255){
  if(spinner_epoch!=game.spinner_epoch){
   for(uint8_t i=FLAG_DESCRIPTOR;i<FLAG_DESCRIPTOR+2;++i){
    uint8_t pose=game_pose(dynamic_desc[i].group);
    if(shown[i]!=pose){active=i;target=pose;break;}
   }
   if(active==255)spinner_epoch=game.spinner_epoch;
  }
  if(active==255&&shown_epoch==game.visual_epoch)goto done;
  uint8_t checked=0;
  while(active==255&&checked++<DYNAMIC_COUNT-DYNAMIC_FAST_COUNT){
   uint8_t i=next_component;if(++next_component==DYNAMIC_COUNT)next_component=DYNAMIC_FAST_COUNT;
   const DynamicDesc*d=&dynamic_desc[i];
   uint8_t pose=d->lamp==3?game_ring_lamp(d->group):d->lamp?game_lamp(d->group):game_pose(d->group);
   if(shown[i]!=pose){active=i;target=pose;break;}
  }
  if(active==255){shown_epoch=game.visual_epoch;goto done;}
  const DynamicDesc*d=&dynamic_desc[active];bank(d->bank);
  const uint8_t*p=(const uint8_t*)(uintptr_t)d->ptr;
  runs_left=p[0];if(target>=p[1])target=0;
  uint16_t count=u16(p+2);run_ptr=p+4;
  mask_ptr=run_ptr+(uint16_t)runs_left*4;value_ptr=mask_ptr+count+(uint16_t)target*count;
  run_left=0;
 }else bank(dynamic_desc[active].bank);
 changed=true;
 while(budget){
  if(!run_left){
   if(!runs_left){shown[active]=target;active=255;break;}
   address=u16(run_ptr);address_bank=run_ptr[2];run_left=run_ptr[3];run_ptr+=4;--runs_left;
  }
  addresses();
  uint8_t n=run_left<budget?run_left:budget;budget-=n;run_left-=n;address+=n;
  while(n--){uint8_t mask=*mask_ptr++,value=*value_ptr++;uint8_t old=dv[3];dv[4]=(old&~mask)|(value&mask);}
 }
 if(!run_left&&!runs_left&&active!=255){shown[active]=target;active=255;}
 if(budget&&active==255)goto again;
done:
 bank(saved);dv[5]=0;return changed;
}
void dynamic_init(void){
 uint8_t saved=*(volatile uint8_t*)0;
 active=255;next_component=DYNAMIC_FAST_COUNT;shown_epoch=fast_epoch=game.visual_epoch-1;
 for(uint8_t i=0;i<DYNAMIC_COUNT;++i)shown[i]=255;
 /* Upload the independent insert sprite into reserved pattern memory. */
 bank(63);
 const uint8_t*cross=(const uint8_t*)(uintptr_t)CROSS_PATTERN_PTR;
 write_address(CROSS_PATTERN_VRAM);
 for(uint8_t i=0;i<128;++i)dv[3]=*cross++;
 write_address(0x1fff8UL);
 dv[3]=(uint8_t)(CROSS_PATTERN_VRAM/32);dv[3]=CROSS_PATTERN_VRAM/8192;
 dv[3]=CROSS_X;dv[3]=0;dv[3]=CROSS_Y&255;dv[3]=CROSS_Y>>8;
 dv[3]=0;dv[3]=CROSS_ATTR;cross_shown=0;spinner_epoch=game.spinner_epoch;
 /* Load both permanent-rest and alternate-fire private patterns once. */
 for(uint8_t i=0;i<DYNAMIC_FAST_COUNT;++i){
  const DynamicDesc*d=dynamic_desc+i;bank(d->bank);
  const uint8_t*p=(const uint8_t*)(uintptr_t)d->ptr;uint8_t count=p[0];
  const uint8_t*meta=p+4,*source=meta+(uint16_t)count*6;
  for(uint8_t pose=0;pose<2;++pose){
   const uint8_t*q=meta;
   for(uint8_t t=0;t<count;++t){
    uint16_t pattern=u16(q+2+(uint8_t)(pose*2))&1023;q+=6;
    write_address(4096UL+(uint32_t)pattern*128);
    for(uint8_t k=0;k<128;++k)dv[3]=*source++;
   }
  }
 }
 bank(saved);
 /* Initial stable poses are drawn during loading, before the gameplay clock. */
 while(dynamic_update(255)){}
}
