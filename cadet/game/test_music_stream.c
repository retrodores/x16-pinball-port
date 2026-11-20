/* Feasibility test for ZSM drum streaming at VERA rate 73, 8-bit stereo.
 * STREAM.PCM is a synthetic sequential drum stem. Effects are game assets.
 * r49 cycle-counter and HostFS/SD emulation are used by the test harness.
 */
#include <cbm.h>
#include <cx16.h>
#include <stdbool.h>
#include <stdint.h>
#include "audio.h"
#ifndef STREAM_FRAMES
#define STREAM_FRAMES 3500
#endif

extern void lab_install(void), lab_uninstall(void);
extern void pcm_start(uint16_t), pcm_flipper_start(uint16_t), pcm_plunger_start(uint16_t);
extern void pcm_render(void);
extern uint16_t lab_clock(void);
extern volatile uint16_t pcm_quota, pcm_select_ptr;
extern volatile uint8_t pcm_select_bank, pcm_buffer[256];

static volatile uint8_t *const vera = (volatile uint8_t *)0x9f20;
static uint8_t sector[512];
static uint16_t pos, end;
uint8_t effect_phase, stream_effect, stream_bytes;
int8_t held_effect;
const uint8_t *stream_source;
extern void stream_mix(void);
static uint32_t max_read, bytes_read, samples_out;

static __attribute__((noinline)) uint32_t cycles(void) {
    __asm__ volatile("php\nsei":::"memory");
    volatile uint8_t *p = (volatile uint8_t *)0x9fb8;
    uint8_t a=p[0], b=p[1], c=p[2], d=p[3];
    __asm__ volatile("plp":::"memory");
    return a | (uint32_t)b<<8 | (uint32_t)c<<16 | (uint32_t)d<<24;
}

static void report(const char *label, uint32_t value) {
    volatile uint8_t *out = (volatile uint8_t *)0x9fbb;
    while (*label) *out = *label++;
    for (uint8_t n=8; n; --n, value<<=4) *out = "0123456789abcdef"[value>>28];
    *out = '\n';
}

static bool open_stem(void) {
    cbm_k_setnam("STREAM.PCM");
    cbm_k_setlfs(2,8,2);
    return !cbm_k_open() && !cbm_k_chkin(2);
}

static bool refill(void) {
    uint32_t start = cycles();
    long count = cx16_k_macptr(0,0,sector);
    uint32_t cost = cycles() - start;
    if (cost>max_read) max_read=cost;
    if (count<=0 || count>sizeof(sector) || (count&1)) return false;
    pos=0;
    end=(uint16_t)count;
    bytes_read+=end;
    return true;
}

static void start_effect(uint8_t id, void (*start)(uint16_t)) {
    const Effect *e=effects+id;
    pcm_select_bank=e->bank;
    pcm_select_ptr=e->ptr;
    start(e->length);
}

static bool mix_block(uint16_t samples) {
    uint16_t advance=(uint16_t)(samples*29u)+effect_phase;
    pcm_quota=advance/73;
    pcm_render();
    stream_effect=0;
    uint16_t remaining=samples;
    while (remaining) {
        if (pos==end && !refill()) return false;
        uint16_t n=(end-pos)/2;
        if (n>remaining) n=remaining;
        if (n>128) n=128;
        remaining-=n;
        stream_source=sector+pos;
        stream_bytes=(uint8_t)(2*n);
        stream_mix();
        pos+=2*n;
    }
    samples_out+=samples;
    return true;
}

/* Keep the existing IRQ clock. The bench owns the FIFO and uses pcm_render
 * directly, so remove the IRQ's PCM FIFO service for this fixture. */
int main(void) {
    uint32_t worst=0, total=0;
    uint16_t overruns=0, gaps=0, empty=0, full=0, frames=0;
    uint8_t error=0;
    for (uint8_t i=0;i<PCM_PARTS;++i) {
        char name[]="PCM0.BIN";
        name[3]+=i;
        *(volatile uint8_t *)0=pcm_load_banks[i];
        cbm_k_setnam(name);
        cbm_k_setlfs(1,8,2);
        if ((uintptr_t)cbm_k_load(0,(void *)0xa000)<=255) {
            report("# LOAD ERROR ",i);
            return 1;
        }
    }
    if (!open_stem()) {report("# OPEN ERROR ",cbm_k_readst());return 1;}
    lab_install();
    report("# STREAM READY ",0);
    vera[27]=0x9a;
    for (uint8_t i=0;i<7 && !error;++i) if (!mix_block(128)) error=1;
    uint16_t frame=lab_clock();
    vera[28]=73;
    for (; !error && frames<STREAM_FRAMES; ++frames) {
        uint16_t now;
        do {now=lab_clock();} while (now==frame);
        if ((uint16_t)(now-frame)>1) ++gaps;
        frame=now;
        uint32_t start=cycles();
        if (vera[27]&0x40) ++empty;
        if (frames%31==0) start_effect(SOUND104,pcm_flipper_start);
        if (frames%53==0) start_effect(SOUND22,pcm_plunger_start);
        if (frames%97==0) start_effect(SOUND43,pcm_start);
        /* Use VERA's FIFO low-water flag for pacing. Limit work in a
         * single game interval even if SD stalls for multiple intervals. */
        for (uint8_t refill_block=0; refill_block<6 && (vera[7]&8); ++refill_block) {
            if (!mix_block(128)) {error=2;break;}
        }
        if (vera[27]&0x80) ++full;
        uint32_t cost=cycles()-start;
        total+=cost;
        if (cost>worst) worst=cost;
        if (cost>133333UL) ++overruns;
    }
    report("# CTRL ",vera[27]);
    report("# RATE ",vera[28]);
    report("# CLOCK ",lab_clock());
    vera[28]=0;
    lab_uninstall();
    cbm_k_clrch();
    cbm_k_close(2);
    report("# FRAMES ",frames);
    report("# BYTES ",bytes_read);
    report("# SAMPLES ",samples_out);
    report("# READ MAX ",max_read);
    report("# WORK MAX ",worst);
    report("# WORK MEAN ",frames?total/frames:0);
    report("# OVER ",overruns);
    report("# GAPS ",gaps);
    report("# EMPTY ",empty);
    report("# FULL ",full);
    report("# DONE ",error);
    return error;
}
