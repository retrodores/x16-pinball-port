/* Atomic original hyperspace award at the exact unsigned 128-bit boundary.
 * Calls the real capture wrapper, including RAM-bank selection on 65C02. */
#include "engine.c"
#include <stdio.h>
static unsigned checks,failures;
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("# FAIL %u\n",(unsigned)__LINE__);}}while(0)
static void near_max(uint32_t subtract){
 static const char max[]="340282366920938463463374607431768211455";
 uint32_t n=subtract;for(uint8_t i=0;i<16;++i){game.score[i]=255-(n&255);n>>=8;}
 for(uint8_t i=0;i<39;++i)game.digits[i]=max[38-i]-'0';game.digits[39]=0;
 n=subtract;for(uint8_t i=0;n;++i){int16_t d=game.digits[i]-(n%10);n/=10;if(d<0){d+=10;++n;}game.digits[i]=d;}
}
static void award(void){
 Edge e={0};for(uint16_t i=0;i<edge_count;++i){e=*edge(i);if(e.group==GROUP_512)break;}
 game.state=InPlay;rules.hyper_count=4;
#ifdef __CX16__
 uint8_t previous=*(volatile uint8_t*)0;
#endif
 event(&e);
#ifdef __CX16__
 CHECK(*(volatile uint8_t*)0==previous);
#endif
 CHECK(game.sound_value==4&&game.state==Captured);
}
int main(void){
 if(!game_load()){puts("# LOAD FAIL\n# DONE");return 1;}
 uint8_t binary[16],decimal[40];
 const uint32_t values[2]={100000,149999};
 for(uint8_t c=0;c<2;++c){game_start();near_max(values[c]);memcpy(binary,game.score,16);memcpy(decimal,game.digits,40);award();
  CHECK(game.overflow);CHECK(!memcmp(binary,game.score,16));CHECK(!memcmp(decimal,game.digits,40));
  add_score(1);CHECK(!memcmp(binary,game.score,16)&&!memcmp(decimal,game.digits,40));
 }
 game_start();near_max(0);memcpy(decimal,game.digits,40);near_max(150000);award();CHECK(!game.overflow);
 for(uint8_t i=0;i<16;++i)CHECK(game.score[i]==255);CHECK(!memcmp(decimal,game.digits,40));
 puts(failures?"# LARGE AWARD FAIL":"# LARGE AWARD PASS");printf("# CHECKS %u %u\n",checks,failures);puts("# DONE");return failures!=0;
}
