; Christmas game mixer. The accepted ZSM and its stereo sample blob stay
; byte-identical in RAM. Play the music at PCM rate 42 and resample only the
; original mono table/flipper/plunger voices, which were recorded for rate 29.
; The single hardware FIFO has one writer. 64 frames require 44 or 45 effect
; samples; pcm_buffer[64..191] stages the drum bytes across the bank switch.
cover_pcm_service:
 lda pcm_started
 bne 1f
 lda #$9e                 ; FIFO reset, stereo 8-bit, volume 14
 sta $9f3b
 lda #6
 sta cover_blocks
2:
 jsr carol_mix_block
 dec cover_blocks
 bne 2b
 lda #42
 sta $9f3c
 inc pcm_started
 rts
1:
 lda $9f3b
 and #$40
 beq 3f
 jsr pcm_count_underrun
3:
 lda #6
 sta cover_blocks
4:
 lda $9f27
 and #8
 beq 5f
 jsr carol_mix_block
 dec cover_blocks
 bne 4b
5:
 rts

carol_mix_block:
 lda pcm_remaining
 ora pcm_remaining+1
 ora pcm_flipper_remaining
 ora pcm_flipper_remaining+1
 ora pcm_plunger_remaining
 ora pcm_plunger_remaining+1
 sta carol_effect_active
 beq 1f
 lda cover_effect_phase
 cmp #34                  ; floor((64*29 + phase)/42)
 lda #44
 adc #0
 sta pcm_quota
 stz pcm_quota+1
 jsr pcm_render
1:
 lda cover_remaining+1
 ora cover_remaining+2
 bne 2f
 lda cover_remaining
 cmp #64
 bcs 2f
 ora #0
 bne 3f
 jmp carol_no_drum
2:
 lda #64
3:
 tax
 sec
 lda cover_remaining
 stx cover_drum_frames
 sbc cover_drum_frames
 sta cover_remaining
 lda cover_remaining+1
 sbc #0
 sta cover_remaining+1
 lda cover_remaining+2
 sbc #0
 sta cover_remaining+2
 txa
 asl
 sta carol_sample_bytes
 lda $00
 pha
 lda cover_bank
 sta $00
 ldx #0
 ldy cover_position
carol_fetch:
 lda $a000,y
 sta pcm_buffer+64,x
 iny
 bne 5f
 inc carol_fetch+2
 lda carol_fetch+2
 cmp #$c0
 bne 5f
 lda #$a0
 sta carol_fetch+2
 inc cover_bank
 lda cover_bank
 sta $00
5:
 inx
 cpx carol_sample_bytes
 bne carol_fetch
 sty cover_position
 lda #0
6:
 cpx #128
 beq 7f
 sta pcm_buffer+64,x
 inx
 bra 6b
7:
 lda #64                   ; holiday overlay contains the signed gain pages
 sta $00
 ldy #0
 lda carol_effect_active
 bne carol_mixed
carol_drum_only:
 ldx pcm_buffer+64,y
carol_gain_direct:
 lda $a000,x
 sta $9f3d
 iny
 bpl carol_drum_only
 bra carol_bank_return
carol_mixed:
 stz carol_effect_pos
8:
 jsr carol_step_effect
 ldx pcm_buffer+64,y
carol_gain_l:
 lda $a000,x
 clc
 adc cover_held_effect
 sta $9f3d
 iny
 ldx pcm_buffer+64,y
carol_gain_r:
 lda $a000,x
 clc
 adc cover_held_effect
 sta $9f3d
 iny
 bpl 8b
carol_bank_return:
 pla
 sta $00
 rts

carol_no_drum:
 ldy #64
 lda carol_effect_active
 beq 2f
 lda $00
 pha
 lda #64
 sta $00
 stz carol_effect_pos
1:
 jsr carol_step_effect
 lda cover_held_effect
 sta $9f3d
 sta $9f3d
 dey
 bne 1b
 bra carol_bank_return
2:
 stz cover_held_effect
3:
 stz $9f3d
 stz $9f3d
 dey
 bne 3b
 rts

carol_step_effect:
 lda cover_effect_phase
 clc
 adc #29
 cmp #42
 bcc 1f
 sbc #42
 sta cover_effect_phase
 ldx carol_effect_pos
 lda pcm_buffer,x
 tax
 lda carol_effect_gain,x    ; 5/16 effect plus drum at max 18/49
 sta cover_held_effect
 inc carol_effect_pos
 rts
1:
 sta cover_effect_phase
 rts

.section .bss.lab,"aw",@nobits
carol_sample_bytes: .zero 1
carol_effect_pos: .zero 1
carol_effect_active: .zero 1
.section .text.lab,"ax",@progbits
