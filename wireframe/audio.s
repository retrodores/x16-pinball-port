; Low-cost VERA PSG music/effects. No compiler zero-page or RAM bank is touched.
; ADDR1 and CTRL are saved around writes; interrupted DATA0 rendering is safe.
.section .text.audio,"ax",@progbits
.globl audio_install,audio_uninstall,audio_effect,audio_stop,audio_toggle
.globl audio_music_toggle,audio_pause,audio_clock

audio_install:
 php
 sei
 lda $0314
 sta audio_old_irq
 lda $0315
 sta audio_old_irq+1
 lda #<audio_irq
 sta $0314
 lda #>audio_irq
 sta $0315
 lda #1
 sta audio_enabled
 sta music_enabled
 stz audio_paused
 stz audio_ticks
 stz audio_ticks+1
 stz music_step
 stz music_tick
 stz fx_count
 stz fx_count+4
 stz audio_remaining
 stz audio_remaining+1
 ldx #15
1:
 stz audio_regs,x
 dex
 bpl 1b
 jsr audio_save_address
 ldx #0
2:
 lda $9f24
 sta saved_psg,x
 inx
 cpx #16
 bne 2b
 jsr audio_restore_address
 jsr audio_flush
 plp
 rts

audio_uninstall:
 php
 sei
 lda audio_old_irq
 sta $0314
 lda audio_old_irq+1
 sta $0315
 ldx #15
1:
 lda saved_psg,x
 sta audio_regs,x
 dex
 bpl 1b
 jsr audio_flush
 plp
 rts

audio_clock:
 php
 sei
 lda audio_ticks
 ldx audio_ticks+1
 plp
 rts

audio_pause:
 php
 sei
 sta audio_paused
 beq 1f
 jsr audio_silence
1:
 plp
 rts

audio_toggle:
 php
 sei
 lda audio_enabled
 eor #1
 sta audio_enabled
 bne 1f
 jsr audio_silence
1:
 plp
 rts

audio_music_toggle:
 php
 sei
 lda music_enabled
 eor #1
 sta music_enabled
 bne 1f
 stz audio_regs+2
 stz audio_regs+6
 jsr audio_flush
1:
 plp
 rts

audio_silence:
 stz audio_regs+2
 stz audio_regs+6
 stz audio_regs+10
 stz audio_regs+14
 jsr audio_clear_fx
 jmp audio_flush

audio_clear_fx:
 stz fx_count
 stz fx_count+4
 stz audio_remaining
 stz audio_remaining+1
 stz audio_regs+10
 stz audio_regs+14
 rts

audio_stop:
 php
 sei
 jsr audio_clear_fx
 jsr audio_flush
 plp
 rts

audio_effect:
 php
 sei
 cmp #7
 bcs effect_done
 tay
 lda audio_enabled
 beq effect_done
 lda audio_paused
 bne effect_done
 ldx #0
 cpy #2
 bcs 1f
 ldx #4
1:
 lda fx_count,x
 beq effect_start
 lda sfx_priorities,y
 cmp fx_priority,x
 bcc effect_done
effect_start:
 tya
 sta fx_id,x
 lda sfx_ticks,y
 sta fx_count,x
 lda sfx_priorities,y
 sta fx_priority,x
 stz fx_pos,x
 lda #1
 sta audio_remaining
 stz audio_remaining+1
effect_done:
 plp
 rts

audio_irq:
 pha
 phx
 phy
 lda $9f27
 and #1
 beq 1f
 inc audio_ticks
 bne 2f
 inc audio_ticks+1
2:
 jsr audio_service
1:
 ply
 plx
 pla
 jmp (audio_old_irq)

audio_service:
 lda audio_enabled
 beq service_done
 lda audio_paused
 bne service_done
 jsr music_service
 ldx #0
voice_loop:
 lda fx_count,x
 beq voice_off
 lda fx_id,x
 asl
 tay
 lda sfx_addresses,y
 sta sound_read+1
 lda sfx_addresses+1,y
 sta sound_read+2
 ldy fx_pos,x
 jsr sound_read
 sta audio_regs+8,x
 iny
 jsr sound_read
 sta audio_regs+9,x
 iny
 jsr sound_read
 sta audio_regs+10,x
 iny
 jsr sound_read
 sta audio_regs+11,x
 iny
 tya
 sta fx_pos,x
 dec fx_count,x
 bra voice_next
voice_off:
 stz audio_regs+10,x
voice_next:
 cpx #0
 bne voices_done
 ldx #4
 bra voice_loop
voices_done:
 lda fx_count
 ora fx_count+4
 sta audio_remaining
 jmp audio_flush
service_done:
 rts
sound_read:
 lda $ffff,y
 rts

music_service:
 lda music_enabled
 beq music_done
 ldy music_step
 lda melody_lo,y
 sta audio_regs
 lda melody_hi,y
 sta audio_regs+1
 ldy music_tick
 lda melody_env,y
 sta audio_regs+2
 lda music_step
 and #3
 asl
 asl
 asl
 asl
 clc
 adc music_tick
 tay
 lda bass_env,y
 sta audio_regs+6
 lda music_step
 lsr
 lsr
 tay
 lda bass_lo,y
 sta audio_regs+4
 lda bass_hi,y
 sta audio_regs+5
 lda #128
 sta audio_regs+3
 sta audio_regs+7
 inc music_tick
 lda music_tick
 cmp #16
 bne music_done
 stz music_tick
 inc music_step
 lda music_step
 and #63
 sta music_step
music_done:
 rts

; The address-save routine cannot leave values on the stack across RTS.
audio_save_address:
 lda $9f25
 sta vera_ctrl_saved
 ora #1
 sta $9f25
 lda $9f20
 sta vera_lo_saved
 lda $9f21
 sta vera_mid_saved
 lda $9f22
 sta vera_hi_saved
 lda #$c0
 sta $9f20
 lda #$f9
 sta $9f21
 lda #$11
 sta $9f22
 rts
audio_restore_address:
 lda vera_lo_saved
 sta $9f20
 lda vera_mid_saved
 sta $9f21
 lda vera_hi_saved
 sta $9f22
 lda vera_ctrl_saved
 sta $9f25
 rts
audio_flush:
 jsr audio_save_address
 ldx #0
1:
 lda audio_regs,x
 sta $9f24
 inx
 cpx #16
 bne 1b
 jmp audio_restore_address

.section .rodata.audio,"a",@progbits
.include "wireframe/build/sound-data.inc"
.section .bss.audio,"aw",@nobits
.globl audio_enabled,audio_remaining,music_enabled,audio_ticks
audio_enabled: .zero 1
music_enabled: .zero 1
audio_paused: .zero 1
audio_ticks: .zero 2
audio_old_irq: .zero 2
audio_remaining: .zero 2
music_step: .zero 1
music_tick: .zero 1
fx_count: .zero 8
fx_id: .zero 8
fx_pos: .zero 8
fx_priority: .zero 8
audio_regs: .zero 16
saved_psg: .zero 16
vera_ctrl_saved: .zero 1
vera_lo_saved: .zero 1
vera_mid_saved: .zero 1
vera_hi_saved: .zero 1
