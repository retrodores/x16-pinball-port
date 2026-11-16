#include "world.h"
#include "flipper.h"
#include "plunger.h"
#include <cbm.h>
#include <cx16.h>
#include <stddef.h>
#include <stdint.h>

// Presentation lives in RAM bank 1; the collision model occupies banks 32..55.
struct PreviewState {uint16_t x,y;uint8_t left,right,plunger,status,charge;};
extern "C" {
__attribute__((used)) volatile PreviewState ui_state;
volatile uint8_t raw_keys[128];
volatile uint8_t command_keys;
__attribute__((naked)) void key_handler(){
 asm volatile("phx\npha\nand #127\ntax\npla\nbmi 1f\nlda raw_keys,x\nbne 3f\ncpx #$33\nbeq 4f\ncpx #$1a\nbeq 5f\ncpx #$6e\nbeq 6f\nbra 3f\n4: lda #1\nbra 7f\n5: lda #2\nbra 7f\n6: lda #4\n7: ora command_keys\nsta command_keys\n3: lda #1\nbra 2f\n1: lda #0\n2: sta raw_keys,x\nplx\nlda #0\nrts");
}
__attribute__((naked)) void restore_screen(){asm volatile("jmp $ff81");}
}
static_assert(offsetof(PreviewState,charge)==8,"banked UI ABI");
// Latch commands in the IRQ: a short tap may begin and end during a slow
// floating-point frame. Held flipper/plunger keys remain level-sensitive.
static uint8_t commands(){asm volatile("sei":::"memory");uint8_t c=command_keys;command_keys=0;asm volatile("cli":::"memory");return c;}
static void print(const char*s){while(*s)cbm_k_bsout(*s++);}
static bool load(const char*name,uint8_t mode,uint16_t address){
 cbm_k_setnam(name);cbm_k_setlfs(1,8,2);
 return (uintptr_t)cbm_k_load(mode,(void*)address)>255;
}
static void ui(bool init){
 uint8_t saved=*(volatile uint8_t*)0;*(volatile uint8_t*)0=1;
 if(init)((void(*)())0xa000)();else ((void(*)())0xa003)();
 *(volatile uint8_t*)0=saved;
}
static uint8_t frame(const TFlipperEdge&e){return (uint8_t)(e.CurrentAngle/e.AngleMax*7+.5f);}
static void project(){
 ui_state.x=1000;ui_state.y=0;
 if(world::ball.ActiveFlag&&!world::drained){
  float y=world::ball.Position.Y;
  float z=24.675402f-.406737f*y-.913545f*ball_radius;
  float scale=200.00035f/z;
  ui_state.x=(uint16_t)(96.5f-world::ball.Position.X*scale);
  ui_state.y=(uint16_t)(118.f-(-.913545f*y+.406737f*ball_radius+3.791398f)*scale);
 }
 ui_state.left=frame(flippers::edges[0]);ui_state.right=frame(flippers::edges[1]);
 ui_state.plunger=plunger::instance.sprite;
 ui_state.charge=(uint8_t)plunger::instance.Boost;
}
#ifdef PREVIEW_TEST
static void log(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void inject(uint8_t code){
 // Exercise the installed KERNAL callback, including release-bit handling.
 asm volatile("lda %0\njsr key_handler"::"r"(code):"a","x");
}
#endif
int main(){
 print("\x93" "CMDRX CADET - DIRECT ENGINE\rLOADING TABLE AND MECHANICS...\r");
 if(!world::load()){print("WORLD.BIN MISSING\r");return 1;}
 *(volatile uint8_t*)0=1;
 if(!load("UI.BIN",0,0xa000)){print("UI.BIN MISSING\r");return 1;}
 *(volatile uint8_t*)0=0;
 *(volatile uint8_t*)0x9f25=0;*(volatile uint8_t*)0x9f29=1;
 if(!load("TABLE.BIN",2,0)||!load("PALETTE.BIN",3,0xfa00)||!load("SPRITES.BIN",3,0x3000)||!load("PLUNGER.BIN",3,0xc000)){
  restore_screen();print("ASSET LOAD FAILED\r");return 1;
 }
 flippers::reset();plunger::reset(world::ball);world::ball.ActiveFlag=false;
 ui_state.status=0;project();ui(true);ui(false);
 uint16_t old=*(volatile uint16_t*)0x032e;
 asm volatile("sei");*(volatile uint16_t*)0x032e=(uint16_t)(uintptr_t)key_handler;asm volatile("cli");
 bool started=false,paused=false,launched=false,prev_pull=false;
#ifdef PREVIEW_TEST
 unsigned test_frame=0;bool cleared=false,left_seen=false,right_seen=false;
 log("# BOOT\n");
#endif
 for(;;){
  waitvsync();
#ifdef PREVIEW_TEST
  if(test_frame==30)inject(0x33);
  if(test_frame==31)inject(0xb3);
  if(test_frame==200)inject(0x3d);
  if(test_frame==420)inject(0xbd);
  if(test_frame==450){inject(0x2e);inject(0x37);}
  if(test_frame==480){inject(0xae);inject(0xb7);}
  if(test_frame==500){inject(0x1a);inject(0x9a);}
  if(test_frame==501)inject(0x9a);
  if(test_frame==520)inject(0x1a);
  if(test_frame==521)inject(0x9a);
#endif
  uint8_t cmd=commands();if(cmd&4)break;
  if(cmd&1){world::start();started=true;paused=false;launched=false;prev_pull=false;}
  if((cmd&2)&&started)paused=!paused;
  if(started&&!paused){
   bool pull=raw_keys[0x3d];
   world::input(raw_keys[0x2c]||raw_keys[0x2e],raw_keys[0x39]||raw_keys[0x37],pull);
   if(prev_pull&&!pull)launched=true;
   prev_pull=pull;world::preview_tick();
  }
  project();
  ui_state.status=!started?0:paused?4:world::drained?5:!world::ball.ActiveFlag?1:launched?3:2;
  ui(false);
#ifdef PREVIEW_TEST
  if(test_frame==29||test_frame==199||test_frame==419||test_frame==460||test_frame==510||test_frame==620)*(volatile uint8_t*)0x9fb5=1;
  if(world::ball.Position.X>4&&world::ball.Position.Y<-5)cleared=true;
  if(ui_state.left)left_seen=true;if(ui_state.right)right_seen=true;
  if(test_frame==419)log(ui_state.charge==100?"# CHARGE+\n":"# CHARGE-\n");
  if(test_frame==510)log(paused?"# PAUSE+\n":"# PAUSE-\n");
  if(++test_frame==760){
   log(cleared?"# CHUTE+\n":"# CHUTE-\n");
   log(left_seen&&right_seen?"# FLIPPERS+\n":"# FLIPPERS-\n");
   log(!raw_keys[0x3d]&&!raw_keys[0x2e]&&!raw_keys[0x37]?"# RELEASE+\n":"# RELEASE-\n");
   break;
  }
#endif
 }
 asm volatile("sei");*(volatile uint16_t*)0x032e=old;asm volatile("cli");
 restore_screen();print("CMDRX CADET PREVIEW ENDED\r");
#ifdef PREVIEW_TEST
 log("# EXIT\n");*(volatile uint8_t*)0x9fb4=0;
#endif
 return 0;
}
