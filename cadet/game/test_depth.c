#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <cbm.h>
extern uint16_t depth_mask(int16_t,int16_t,uint8_t);
extern void depth_masks(uint16_t,uint16_t,uint8_t,uint16_t*,uint8_t,uint8_t);
typedef struct __attribute__((packed)){int16_t x,y;uint8_t depth,pad;uint16_t mask[16];} Case;
static bool load(const char*n,uint8_t bank){*(volatile uint8_t*)0=bank;cbm_k_setnam(n);cbm_k_setlfs(1,8,2);return(uintptr_t)cbm_k_load(0,(void*)0xa000)>255;}
static void text(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint16_t n){for(uint8_t i=0;i<4;++i){*(volatile uint8_t*)0x9fbb="0123456789abcdef"[n>>12];n<<=4;}}
static uint32_t clock_cycles(void){uint8_t a=*(volatile uint8_t*)0x9fb8,b=*(volatile uint8_t*)0x9fb9,c=*(volatile uint8_t*)0x9fba,d=*(volatile uint8_t*)0x9fbb;return(uint32_t)a|((uint32_t)b<<8)|((uint32_t)c<<16)|((uint32_t)d<<24);}
int main(void){
 uint32_t worst=0,total=0;uint16_t rectangles=0;
 if(!load("UI.BIN",11))goto fail;
 for(uint8_t i=0;i<9;++i){char n[]="DEPTH00.BIN";n[5]+=i/10;n[6]+=i%10;if(!load(n,i==0?10:i<3?16+i:i+42))goto fail;}
 if(!load("DEPCA0.BIN",12)||!load("DEPCA1.BIN",13))goto fail;
 for(uint16_t i=0;i<384;++i){
  uint8_t bank=12+i/192;*(volatile uint8_t*)0=bank;
  Case c;memcpy(&c,(const void*)(0xa000+(i%192)*sizeof(Case)),sizeof c);
  uint16_t masks[16];
  if(c.x>=0&&c.x<=349&&c.y>=0&&c.y<=454){
   uint32_t before=clock_cycles();depth_masks(c.x,c.y,c.depth,masks,16,16);uint32_t elapsed=clock_cycles()-before;
   total+=elapsed;if(elapsed>worst)worst=elapsed;++rectangles;
   if(memcmp(masks,c.mask,32)){text("# RECT FAIL ");hex(i);text("\n");for(uint8_t j=0;j<16;++j){hex(masks[j]);text(" ");hex(c.mask[j]);text(" ");hex(depth_mask(c.x,c.y+j,c.depth));text("\n");}goto fail;}
  }
  if(c.x>=0&&c.x<=349&&c.y>=0&&c.y<=454){
   uint8_t width=9+i%7,height=9+(i/7)%7;memset(masks,0x55,sizeof masks);
   depth_masks(c.x,c.y,c.depth,masks,width,height);
   for(uint8_t y=0;y<16;++y)if(masks[y]!=(y<height?(c.mask[y]&((1u<<width)-1)):0x5555)){text("# SIZE FAIL\n");goto fail;}
  }
  for(uint8_t y=0;y<16;++y){
   if(depth_mask(c.x,c.y+y,c.depth)!=c.mask[y]){text("# ROW FAIL ");hex(i);text(" ");hex(y);text("\n");goto fail;}
  }
  if(*(volatile uint8_t*)0!=bank){text("# BANK FAIL\n");goto fail;}
 }
 text("# DEPTH CYCLES ");hex(worst>>16);hex(worst);text(" ");uint32_t mean=total/rectangles;hex(mean>>16);hex(mean);text("\n");
 text("# DEPTH PASS 384 rectangles, 6144 rows\n# DONE\n");goto done;
fail:text("# FAIL\n# DONE\n");
done:*(volatile uint8_t*)0x9fb4=0;__asm__ volatile("jmp $ffff");return 0;
}
