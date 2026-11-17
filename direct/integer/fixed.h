#pragma once
#include <stdint.h>
#include <type_traits>
#ifdef PROFILE_INTEGER
extern uint32_t profile_cycles[4],profile_calls[4];
struct ProfileScope {uint32_t start;uint8_t slot;ProfileScope(uint8_t i):start(*(volatile uint32_t*)0x9fb8),slot(i){++profile_calls[i];}~ProfileScope(){profile_cycles[slot]+=*(volatile uint32_t*)0x9fb8-start;}};
#define PROFILE_SCOPE(i) ProfileScope scope(i)
#else
#define PROFILE_SCOPE(i)
#endif
// Q20.12: all runtime arithmetic is integer. Floating literals are converted
// at compile time; the linked executable is checked for soft-float helpers.
uint32_t fixed_multiply(uint32_t a,uint32_t b);
uint32_t fixed_divide(uint32_t x,uint32_t y);
struct Fixed {
 int32_t raw;
 static constexpr int32_t scale=4096;
 Fixed()=default;
 template<class T,typename std::enable_if<std::is_integral<T>::value,int>::type=0>
 constexpr Fixed(T n):raw((int32_t)n*scale){}
 constexpr Fixed(double n):raw(n>=524287?INT32_MAX:n<=-524287?-INT32_MAX:(int32_t)(n*scale+(n<0?-.5:.5))){}
 static constexpr Fixed bits(int32_t n){return Fixed(n,0);}
 template<class T> explicit operator T()const{return (T)(raw/scale);}
 constexpr Fixed operator-()const{return bits(-raw);}
 Fixed& operator+=(Fixed b){raw+=b.raw;return *this;}
 Fixed& operator-=(Fixed b){raw-=b.raw;return *this;}
 Fixed& operator*=(Fixed b){return *this=*this*b;}
 Fixed& operator/=(Fixed b){return *this=*this/b;}
 friend Fixed operator+(Fixed a,Fixed b){return bits(a.raw+b.raw);}
 friend Fixed operator-(Fixed a,Fixed b){return bits(a.raw-b.raw);}
 friend __attribute__((noinline)) Fixed operator*(Fixed a,Fixed b){PROFILE_SCOPE(0);
  uint32_t x=a.raw<0?-a.raw:a.raw,y=b.raw<0?-b.raw:b.raw;
  uint32_t q=fixed_multiply(x,y);return bits((a.raw<0)!=(b.raw<0)?-(int32_t)q:(int32_t)q);
 }
 friend __attribute__((noinline)) Fixed operator/(Fixed a,Fixed b){PROFILE_SCOPE(1);
  if(!b.raw)return bits(a.raw<0?-INT32_MAX:INT32_MAX);
  uint32_t x=a.raw<0?-a.raw:a.raw,y=b.raw<0?-b.raw:b.raw;
  uint32_t q=fixed_divide(x,y);
  return bits((a.raw<0)!=(b.raw<0)?-(int32_t)q:(int32_t)q);
 }
 friend bool operator<(Fixed a,Fixed b){return a.raw<b.raw;}
 friend bool operator>(Fixed a,Fixed b){return a.raw>b.raw;}
 friend bool operator<=(Fixed a,Fixed b){return a.raw<=b.raw;}
 friend bool operator>=(Fixed a,Fixed b){return a.raw>=b.raw;}
 friend bool operator==(Fixed a,Fixed b){return a.raw==b.raw;}
 friend bool operator!=(Fixed a,Fixed b){return a.raw!=b.raw;}
private:constexpr Fixed(int32_t n,int):raw(n){}
};
static_assert(sizeof(Fixed)==4,"banked record ABI");
#ifdef __CX16__
extern "C" uint32_t fastmul16(uint16_t,uint16_t);
inline uint32_t mul16(uint16_t a,uint16_t b){return fastmul16(a,b);}
#else
inline uint32_t mul16(uint16_t a,uint16_t b){return (uint32_t)a*b;}
#endif
__attribute__((noinline)) inline uint32_t fixed_multiply(uint32_t a,uint32_t b){
 if(!a||!b)return 0;
 if(a==4096)return b;if(b==4096)return a;
 if((a|b)<65536UL)return mul16(a,b)>>12;
 uint16_t ah=a>>12,bh=b>>12,al=a&4095,bl=b&4095;
 return (ah&&bh?(mul16(ah,bh)<<12):0)+(ah?mul16(ah,bl):0)+(bh?mul16(al,bh):0)+(mul16(al,bl)>>12);
}
__attribute__((noinline)) inline uint32_t fixed_divide(uint32_t x,uint32_t y){
 if(x<1048576UL)return (x<<12)/y;
 uint32_t q=x/y,r=x%y;
 for(uint8_t i=0;i<12;++i){r<<=1;q<<=1;if(r>=y){r-=y;++q;}}
 return q;
}
inline uint16_t integer_sqrt(uint32_t n){
 uint32_t result=0,bit=1UL<<30;
 while(bit>n)bit>>=2;
 while(bit){if(n>=result+bit){n-=result+bit;result=(result>>1)+bit;}else result>>=1;bit>>=2;}
 return (uint16_t)result;
}
inline Fixed sqrt(Fixed n){
 if(n.raw<=0)return Fixed(0);
 uint32_t v=n.raw;uint8_t shift=0;
 while(v>=1048576UL){v>>=2;++shift;}
 return Fixed::bits((uint32_t)integer_sqrt(v<<12)<<shift);
}
inline Fixed fixed_hypot(Fixed x,Fixed y){PROFILE_SCOPE(2);
 uint32_t a=x.raw<0?-x.raw:x.raw,b=y.raw<0?-y.raw:y.raw;uint8_t shift=0;
 while((a|b)>32767){a>>=1;b>>=1;++shift;}
 return Fixed::bits((uint32_t)integer_sqrt(mul16(a,a)+mul16(b,b))<<shift);
}
inline Fixed floor(Fixed x){return Fixed::bits(x.raw&~4095L);}
inline Fixed sin(Fixed x){Fixed z=x*x;return x*(1+z*(-1.0/6+z*(1.0/120-z/5040)));}
inline Fixed cos(Fixed x){Fixed z=x*x;return 1+z*(-1.0/2+z*(1.0/24-z/720));}
namespace std {
template<class T>T min(T a,T b){return a<b?a:b;}
template<class T>T max(T a,T b){return a>b?a:b;}
inline Fixed abs(Fixed a){return a<0?-a:a;}
inline Fixed fabs(Fixed a){return abs(a);}
inline Fixed sqrt(Fixed a){return ::sqrt(a);}
inline Fixed ceil(Fixed a){return Fixed::bits((a.raw+4095)&~4095L);}
}

// Exact rational frame intervals avoid quantizing 1/60 and 1/120 to Q12.
__attribute__((noinline)) inline Fixed time_product(Fixed value,Fixed dt){
 if(dt.raw==34)return Fixed::bits(value.raw/120);
 if(dt.raw==68)return Fixed::bits(value.raw/60);
 if(dt.raw==41)return Fixed::bits(value.raw/100);
 return value*dt;
}
