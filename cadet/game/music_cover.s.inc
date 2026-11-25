; Resident 2 MB player for the GTR3QQ export and the Christmas rock arrangement.
; Read commands and PCM directly from resident banks. The caller owns RAM-bank
; and VERA-address preservation. No KERNAL calls or compiler zero page in IRQ.
.globl music_prefetch, cover_triggers

music_prefetch:
 rts

music_reset:
.ifdef CHRISTMAS
 stz christmas_song_tick
 stz christmas_song_tick+1
 lda #CAROL_BANK
.else
 lda #32
.endif
 sta music_bank
.ifdef CHRISTMAS
 lda #<CAROL_COMMAND
 sta cover_command+1
 lda #>CAROL_COMMAND
.else
 stz cover_command+1
 lda #$a0
.endif
 sta cover_command+2
 stz cover_phase
 stz cover_phase+1
 rts

cover_loop:
.ifdef CHRISTMAS
 stz christmas_song_tick
 stz christmas_song_tick+1
.endif
 lda #COVER_LOOP_BANK
 sta music_bank
 lda #<COVER_LOOP_PTR
 sta cover_command+1
 lda #>COVER_LOOP_PTR
 sta cover_command+2
 rts

music_byte:
 lda music_bank
 sta $00
cover_command:
 lda $a000
 inc cover_command+1
 bne 1f
 pha
 inc cover_command+2
 lda cover_command+2
 cmp #$c0
 bne 2f
 lda #$a0
 sta cover_command+2
 inc music_bank
 .ifndef CHRISTMAS
 lda music_bank
 cmp #45
 bne 2f
 lda #COVER_CMD_HIGH
 sta music_bank
 .endif
2:
 pla
1:
 ora #0
 rts

.ifdef CHRISTMAS
 COVER_TICK_NUM = 630    ; 60 ticks/s at 25 MHz / (800*525) VGA frames/s
.else
 COVER_TICK_NUM = 966    ; 92 ticks/s for the R6 cover
.endif
cover_tick:
 clc
 lda cover_phase
 adc #<COVER_TICK_NUM
 sta cover_phase
 lda cover_phase+1
 adc #>COVER_TICK_NUM
 sta cover_phase+1
1:
 sec
 lda cover_phase
 sbc #<625
 tax
 lda cover_phase+1
 sbc #>625
 bcc 2f
 sta cover_phase+1
 stx cover_phase
 .ifdef CHRISTMAS
 lda music_enabled
 beq 1b
 lda music_delay          ; initial command block is song tick zero
 beq 3f
 inc christmas_song_tick
 bne 3f
 inc christmas_song_tick+1
3:
 .endif
 jsr music_service
 bra 1b
2:
 rts

cover_extension:
 jsr music_byte
 tax
 and #$3f
 sta music_count
 beq 3f
 txa
 and #$c0
 bne 2f
1:
 jsr music_byte
 tax
 jsr music_byte
 .ifdef CHRISTMAS
 cpx #0
 bne 8f
 and #15
 tay
 lda #>carol_gain_start
 clc
 adc carol_volume_pages,y
 sta carol_gain_l+2
 sta carol_gain_r+2
 sta carol_gain_direct+2
 bra 4f
8:
 .endif
 cpx #2
 bne 4f
 jsr cover_trigger
4:
 dec music_count
 dec music_count
 bne 1b
 bra 3f
2:
 jsr music_byte
 dec music_count
 bne 2b
3:
 jmp music_command

cover_trigger:
 cmp #COVER_INSTRUMENTS
 bcs 1f
 asl
 tay
 asl
 sta cover_offset
 tya
 clc
 adc cover_offset
 tax
 lda cover_instruments,x
 sta cover_bank
 lda cover_instruments+1,x
 sta cover_position
 lda cover_instruments+2,x
 .ifdef CHRISTMAS
 sta carol_fetch+2
 .else
 sta cover_left+2
 sta cover_right+2
 .endif
 lda cover_instruments+3,x
 sta cover_remaining
 lda cover_instruments+4,x
 sta cover_remaining+1
 lda cover_instruments+5,x
 sta cover_remaining+2
 inc cover_triggers
 bne 1f
 inc cover_triggers+1
1:
 rts

.ifdef CHRISTMAS
.include "cadet/game/music_carol_mix.s.inc"
.else
cover_pcm_service:
 lda pcm_started
 bne 1f
 lda #$9a
 sta $9f3b
 lda #4
 sta cover_blocks
2:
 jsr cover_mix_block
 dec cover_blocks
 bne 2b
 lda #73
 sta $9f3c
 inc pcm_started
 rts
1:
 lda $9f3b
 and #$40
 beq 3f
 jsr pcm_count_underrun
3:
 lda #5
 sta cover_blocks
4:
 lda $9f27
 and #8
 beq 5f
 jsr cover_mix_block
 dec cover_blocks
 bne 4b
5:
 rts

cover_mix_block:
 ; Exactly 128 frames at rate 73. Render the needed 50 or 51 mono
 ; effect frames at rate 29, retaining the last sample across blocks.
 lda cover_effect_phase
 cmp #11
 lda #50
 adc #0
 sta pcm_quota
 stz pcm_quota+1
 jsr pcm_render
 lda #128
 sta cover_frames
 lda cover_remaining+1
 ora cover_remaining+2
 bne 1f
 lda cover_remaining
 cmp #128
 bcc 2f
1:
 lda #128
2:
 sta cover_drum_frames
 sec
 lda cover_remaining
 sbc cover_drum_frames
 sta cover_remaining
 lda cover_remaining+1
 sbc #0
 sta cover_remaining+1
 lda cover_remaining+2
 sbc #0
 sta cover_remaining+2
 lda $00
 pha
 lda cover_bank
 sta $00
 ldx #0
 ldy cover_position
3:
 lda cover_effect_phase
 clc
 adc #29
 cmp #73
 bcc 4f
 sbc #73
 pha
 lda pcm_buffer,x
 ; Mix effects at 5/8 scale (1/2 + 1/8), leaving headroom for 1/4 drums.
 cmp #$80
 ror
 sta cover_held_effect
 cmp #$80
 ror
 cmp #$80
 ror
 clc
 adc cover_held_effect
 sta cover_held_effect
 inx
 pla
4:
 sta cover_effect_phase
 lda cover_drum_frames
 beq 6f
 dec cover_drum_frames
cover_left:
 lda $a000,y
 cmp #$80
 ror
 cmp #$80
 ror
 clc
 adc cover_held_effect
 sta $9f3d
 iny
cover_right:
 lda $a000,y
 cmp #$80
 ror
 cmp #$80
 ror
 clc
 adc cover_held_effect
 sta $9f3d
 iny
 bne 7f
 inc cover_left+2
 lda cover_left+2
 cmp #$c0
 bne 5f
 lda #$a0
 sta cover_left+2
 inc cover_bank
 ldy cover_bank
 sty $00
 ldy #0
5:
 sta cover_right+2
 bra 7f
6:
 lda cover_held_effect
 sta $9f3d
 sta $9f3d
7:
 dec cover_frames
 bne 3b
 sty cover_position
 pla
 sta $00
 rts

.endif

.ifdef CHRISTMAS
.include "cadet/play-build/carol_audio.inc"
.else
.include "cadet/play-build/music_cover_data.inc"
.endif

.section .bss.lab,"aw",@nobits
cover_phase: .zero 2
cover_offset: .zero 1
cover_bank: .zero 1
cover_position: .zero 1
cover_remaining: .zero 3
.ifdef CHRISTMAS
.globl christmas_song_tick
christmas_song_tick: .zero 2

.endif
cover_blocks: .zero 1
cover_frames: .zero 1
cover_drum_frames: .zero 1
cover_effect_phase: .zero 1
cover_held_effect: .zero 1
cover_triggers: .zero 2
.section .text.lab,"ax",@progbits
