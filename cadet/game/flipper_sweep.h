/* Static original tip-circle sweep for outside-to-outside grazing contacts.
 * Include after paddle(). Requires move_time(dx,dy,steps,remaining_time).
 * Caller must only use this after a world sweep with no contacts. This is NOT
 * a moving-flipper sweep: those still require time-dependent face/tip normals.
 */
#ifdef __CX16__
#define TIP_FN __attribute__((section(".physics"),noinline))
#else
#define TIP_FN
#endif
static uint16_t tip_remaining;
static TIP_FN bool paddle_static_tip_core(uint8_t side,uint8_t old,int16_t sx,int16_t sy){
 if(game.state!=InPlay||game.mask!=1||game.phase[side]!=old)return false;
 const Vec*t=&tips[side][old];const uint16_t radius=126,r2=15876;
 int16_t ex=game.x,ey=game.y;
 if((sx<t->x-(int16_t)radius&&ex<t->x-(int16_t)radius)||(sx>t->x+(int16_t)radius&&ex>t->x+(int16_t)radius)||
    (sy<t->y-(int16_t)radius&&ey<t->y-(int16_t)radius)||(sy>t->y+(int16_t)radius&&ey>t->y+(int16_t)radius))return false;
 int16_t rx=sx-t->x,ry=sy-t->y,dx=ex-sx,dy=ey-sy,erx=ex-t->x,ery=ey-t->y;
 if(mul(rx,rx)+mul(ry,ry)<r2||mul(erx,erx)+mul(ery,ery)<r2)return false;
 uint32_t a=mul(dx,dx)+mul(dy,dy);if(!a)return false;
 int32_t projection=-(mul(rx,dx)+mul(ry,dy));if(projection<=0)return false;
 int32_t cross=mul(rx,dy)-mul(ry,dx);if(cross>65535||cross< -65535)return false;
 uint16_t c=cross<0?-cross:cross;
 uint32_t ar=wide_mul(a,r2),c2=umul(c,c);if(c2>=ar)return false;
 int32_t numerator=projection-isqrt(ar-c2);if(numerator<0||(uint32_t)numerator>a)return false;
 uint16_t hit_t=fraction_wide(numerator,a);
 int16_t px=rx+mul(dx,hit_t)/256,py=ry+mul(dy,hit_t)/256;
 uint16_t distance=isqrt(mul(px,px)+mul(py,py));if(!distance)return false;
 int16_t nx=normal(px,distance),ny=normal(py,distance);
 int16_t inward=-dot(game.vx,game.vy,nx,ny);if(inward<=0)return false;
 game.x=t->x+mul(radius+2,nx)/256;game.y=t->y+mul(radius+2,ny)/256;
 rebound(nx,ny,192,128,0,inward);++game.flipper_hits;
 tip_remaining=256-hit_t;
 return true;
}
/* Finish the world sweep only after restoring the caller bank. nearest/edge
 * select geometry banks and must never execute with this overlay on the stack. */
static BANK_TRAMPOLINE bool paddle_static_tip(uint8_t side,uint8_t old,int16_t sx,int16_t sy,uint8_t steps){
#ifdef __CX16__
 uint8_t saved=*(volatile uint8_t*)0;
 *(volatile uint8_t*)0=62;__asm__ volatile("":::"memory");
#endif
 bool hit=paddle_static_tip_core(side,old,sx,sy);
#ifdef __CX16__
 __asm__ volatile("":::"memory");*(volatile uint8_t*)0=saved;
#endif
 if(hit){uint16_t remain=tip_remaining;
  move_time(scaled_step(game.vx,remain,steps),scaled_step(game.vy,remain,steps),steps,remain);
 }
 return hit;
}
#undef TIP_FN
