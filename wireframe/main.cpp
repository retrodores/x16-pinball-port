#include "engine.h"
#include "video.h"
#include <cbm.h>
#include <cx16.h>
#include <stdint.h>
extern "C" {void audio_install();void audio_uninstall();void audio_stop();void audio_toggle();
__attribute__((used)) volatile uint8_t keys[128],commands;
__attribute__((naked,used)) void keyboard(){asm volatile("phx\npha\nand #127\ntax\npla\nbmi 1f\nlda keys,x\nbne 3f\ncpx #$2c\nbeq 4f\ncpx #$2e\nbeq 4f\ncpx #$37\nbeq 5f\ncpx #$39\nbeq 5f\ncpx #$33\nbeq 6f\ncpx #$20\nbeq 7f\ncpx #$1a\nbeq 8f\ncpx #$6e\nbeq 9f\ncpx #$53\nbeq 10f\nbra 3f\n4: lda #16\nbra 11f\n5: lda #32\nbra 11f\n6: lda #1\nbra 11f\n7: lda #8\nbra 11f\n8: lda #2\nbra 11f\n9: lda #4\nbra 11f\n10: lda #64\n11: ora commands\nsta commands\n3: lda #1\nbra 2f\n1: lda #0\n2: sta keys,x\nplx\nlda #0\nrts");}
__attribute__((naked)) void screen(){asm volatile("jmp $ff81");}
}
static volatile uint8_t*const vera=(volatile uint8_t*)0x9f20;
static void print(const char*s){while(*s)cbm_k_bsout(*s++);}
static bool load(const char*n,uint8_t mode,uint16_t addr){cbm_k_setnam(n);cbm_k_setlfs(1,8,2);return (uintptr_t)cbm_k_load(mode,(void*)addr)>255;}
static void address(uint32_t a){vera[0]=a;vera[1]=a>>8;vera[2]=0x10|(a>>16);}
static void word(uint16_t v){vera[3]=v;vera[3]=v>>8;}
static void sprite(uint8_t i,uint16_t addr,uint16_t x,uint16_t y,uint8_t size,bool visible){address(0x1fc00UL+i*8);word(addr);word(x);word(y);vera[3]=visible?12:0;vera[3]=size;}
__attribute__((noinline)) static void glyph(uint16_t x,uint8_t y,uint8_t c,uint8_t color){if(c<32||c>95)c='?';const uint8_t*g=glyphs+(c-32)*8;uint16_t a=(uint16_t)y*320+x;for(uint8_t row=0;row<8;++row){address(a);uint8_t bits=*g++;for(uint8_t k=0;k<6;++k){vera[3]=(bits&32)?color:0;bits<<=1;}a+=320;}}
static void line(uint16_t x,uint8_t y,const char*s,uint8_t c=8){while(*s){glyph(x,y,*s++,c);x+=6;}}
static void video_init(){vera[5]=0;vera[9]=0x51;vera[10]=64;vera[11]=64;vera[12]=0;vera[13]=7;vera[14]=0;vera[15]=0;vera[16]=0;vera[17]=0;vera[18]=0;vera[19]=0;for(uint8_t i=0;i<128;++i)sprite(i,0,1000,0,0,false);for(uint8_t i=0;i<sizeof(markers)/sizeof(markers[0]);++i){const auto&m=markers[i];sprite(i+3,m.addr,m.x,m.y,0,false);}for(uint8_t i=0;i<sizeof(mechanisms)/sizeof(mechanisms[0]);++i){const auto&m=mechanisms[i];sprite(i+3+sizeof(markers)/sizeof(markers[0]),m.addr,m.x,m.y,0xa0,true);}}
static uint8_t mechanism_cache[sizeof(mechanisms)/sizeof(mechanisms[0])];
static uint8_t marker_cache[sizeof(markers)/sizeof(markers[0])],phase_cache[2]={255,255};
static char status_cache[16];static uint8_t status_cursor=0;
static uint8_t score_cache[40],laststate=255,lastballs=255,lastmask=255,lastcharge=255;static bool paused=false;
__attribute__((noinline)) static void display(){auto&g=pin::game;
 int16_t px=g.x;if(px>2800)px=2800;if(px< -2800)px=-2800;
 uint16_t x=109-(px*11)/256,y=113+(g.y*7)/256;
 sprite(0,ball_addr,x-4,y-4,0,g.state>=pin::Serving&&g.state<=pin::Captured);
 for(uint8_t i=0;i<2;++i)if(phase_cache[i]!=g.phase[i]){sprite(i+1,paddle_addr[i][g.phase[i]],paddle_x[i],paddle_y[i],0xa0,true);phase_cache[i]=g.phase[i];}
 for(uint8_t i=0;i<sizeof(markers)/sizeof(markers[0]);++i){const auto&m=markers[i];uint8_t visible=g.flash[m.group]!=0||g.lamps[m.group];if(marker_cache[i]!=visible){address(0x1fc06UL+(i+3)*8);vera[3]=visible?12:0;marker_cache[i]=visible;}}
 for(uint8_t i=0;i<sizeof(mechanisms)/sizeof(mechanisms[0]);++i){const auto&m=mechanisms[i];uint8_t hidden=g.disabled[m.group]!=0;if(mechanism_cache[i]!=hidden){address(0x1fc06UL+(i+3+sizeof(markers)/sizeof(markers[0]))*8);vera[3]=hidden?0:12;mechanism_cache[i]=hidden;}}
 uint8_t state=paused?6:g.state;if(state!=laststate){status_cursor=0;laststate=state;}
 const char*labels[]={"N: START A GAME  ","HOLD SPACE      ","BALL IN PLAY    ","CAPTURE / RETURN","NEXT BALL...    ","GAME OVER: N    ","PAUSED: P       "};
 uint8_t text_budget=2;while(status_cursor<16&&text_budget){char c=labels[state][status_cursor];if(status_cache[status_cursor]!=c){glyph(207+status_cursor*6,37,c,3);status_cache[status_cursor]=c;--text_budget;}++status_cursor;}

 if(g.balls!=lastballs){glyph(260,113,'0'+g.balls,8);lastballs=g.balls;}
 if(g.mask!=lastmask){glyph(260,129,'0'+g.mask,6);lastmask=g.mask;}
 if(g.charge!=lastcharge){address(156UL*320+207);for(uint8_t i=0;i<100;++i)vera[3]=i<g.charge?2:10;lastcharge=g.charge;}
 // At most two changed digits per display frame; all 128 bits remain visible.
 uint8_t budget=2;uint8_t significant=0;for(int i=39;i>=0;--i){if(g.digits[i]||i==0)significant=1;uint8_t c=significant?'0'+g.digits[i]:' ';if(c!=score_cache[i]&&budget){uint8_t place=39-i;glyph(207+(place%10)*6,60+(place/10)*10,c,8);score_cache[i]=c;--budget;}}
 if(g.overflow)line(207,100,"SCORE OVERFLOW",4);
}
#ifdef PIN_AUTOPLAY
static void log(const char*s){while(*s)*(volatile uint8_t*)0x9fbb=*s++;}
static void hex(uint32_t n){for(int8_t i=7;i>=0;--i)*(volatile uint8_t*)0x9fbb="0123456789abcdef"[(n>>(i*4))&15];}
#endif
int main(){print("\x93" "CMDRX WIREFRAME\rLOADING...\r");if(!pin::load()){print("MODEL LOAD FAILED\r");return 1;}
 vera[5]=0;vera[9]=1;
 if(!load("TABLE.BIN",2,0)||!load("PALETTE.BIN",3,0xfa00)||!load("SPRITES.BIN",3,0x3000)){screen();print("ASSET LOAD FAILED\r");return 1;}
 *(volatile uint8_t*)0=56;bool ok=load("SFXA.BIN",0,0xa000);*(volatile uint8_t*)0=2;ok=load("SFXB.BIN",0,0xa000)&&ok;*(volatile uint8_t*)0=0;
 if(!ok){screen();print("SOUND LOAD FAILED\r");return 1;}audio_install();video_init();
 uint16_t old=*(volatile uint16_t*)0x032e;asm volatile("sei");*(volatile uint16_t*)0x032e=(uint16_t)(uintptr_t)keyboard;asm volatile("cli");
#ifdef PIN_AUTOPLAY
 pin::start();uint32_t maximum=0,total=0;uint16_t over=0,frames=0,game_frame=0,total_drains=0,total_returns=0;uint8_t game_index=0;log("# START\n");
#endif
 for(;;){waitvsync();asm volatile("sei":::"memory");uint8_t cmd=commands;commands=0;asm volatile("cli":::"memory");if(cmd&4)break;
#ifdef PIN_AUTOPLAY
 *(volatile uint8_t*)0x9fb8=0;
#endif
 if(cmd&1){audio_stop();pin::start();paused=false;}if(cmd&2){paused=!paused;if(paused)audio_stop();}if(cmd&8)audio_toggle();
 if(!paused){
#ifdef PIN_AUTOPLAY
 const uint8_t charge[3]={80,73,78},left_period[3]={53,50,96},right_period[3]={67,56,102};
 bool pull=pin::game.state==pin::Serving&&pin::game.charge<charge[game_index];
 pin::frame(game_frame%left_period[game_index]<12,game_frame%right_period[game_index]<12,pull);
#else
 pin::frame(keys[0x2c]||keys[0x2e]||(cmd&16),keys[0x37]||keys[0x39]||(cmd&32),keys[0x3d],cmd&64);
#endif
 }
 #ifdef PIN_AUTOPLAY
 uint32_t physics_cycles=*(volatile uint32_t*)0x9fb8;
#endif
 display();
#ifdef PIN_AUTOPLAY
 uint32_t elapsed=*(volatile uint32_t*)0x9fb8;total+=elapsed;if(elapsed>maximum){maximum=elapsed;log("# WORST ");hex(frames);log(" ");hex(elapsed);log(" ");hex(pin::game.x);log(" ");hex(pin::game.y);log(" ");hex(pin::game.contacts);log(" ");hex(physics_cycles);log("\n");}if(elapsed>133333)++over;
 if(frames%120==0){log("# PLAY ");hex(frames);log(" ");hex(pin::game.x);log(" ");hex(pin::game.y);log(" ");hex(pin::game.state);log(" ");hex(pin::game.drains);log("\n");}
 if(frames==240||frames==1000||frames==1800)*(volatile uint8_t*)0x9fb5=1;
 ++frames;++game_frame;bool ended=false;if(pin::game.state==pin::GameOver){total_drains+=pin::game.drains;total_returns+=pin::game.returns;if(++game_index==3)ended=true;else{pin::start();game_frame=0;}}
 if(frames>=18000||ended){log("# RESULT ");hex(frames);log(" ");hex(maximum);log(" ");hex(total/frames);log(" ");hex(over);log(" ");hex(total_drains);log(" ");hex(total_returns);log("\n");break;}
#endif
 }
 audio_uninstall();asm volatile("sei");*(volatile uint16_t*)0x032e=old;asm volatile("cli");screen();print("WIREFRAME ENDED\r");
#ifdef PIN_AUTOPLAY
 log("# DONE\n");
#endif
 return 0;
}
