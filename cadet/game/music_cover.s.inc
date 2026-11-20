; Optional 2 MB player for the verified GTR3QQ R6 export.
; Read commands and PCM directly from resident banks. The caller owns RAM-bank
; and VERA-address preservation. No KERNAL calls or compiler zero page in IRQ.
.globl music_prefetch, cover_triggers, cover_pcm_frames

music_prefetch:
 rts

music_reset:
 lda #32
 sta music_bank
 stz cover_command+1
 lda #$a0
 sta cover_command+2
 stz cover_phase
 stz cover_phase+1
 rts

cover_loop:
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
 lda music_bank
 cmp #45
 bne 2f
 lda #COVER_CMD_HIGH
 sta music_bank
2:
 pla
1:
 ora #0
 rts

cover_tick:
 ; 92 ZSM ticks/s at 25 MHz / (800 * 525) VGA frames/s = 966/625.
 clc
 lda cover_phase
 adc #<966
 sta cover_phase
 lda cover_phase+1
 adc #>966
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
 sta cover_left+2
 sta cover_right+2
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
 ; Give effects half-scale headroom, equal to each stereo drum channel.
 cmp #$80
 ror
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
 clc
 adc cover_held_effect
 sta $9f3d
 iny
cover_right:
 lda $a000,y
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
 clc
 lda cover_pcm_frames
 adc #128
 sta cover_pcm_frames
 bcc 8f
 inc cover_pcm_frames+1
 bne 8f
 inc cover_pcm_frames+2
8:
 rts

.include "cadet/play-build/music_cover_data.inc"

.section .bss.lab,"aw",@nobits
cover_phase: .zero 2
cover_offset: .zero 1
cover_bank: .zero 1
cover_position: .zero 1
cover_remaining: .zero 3
cover_blocks: .zero 1
cover_frames: .zero 1
cover_drum_frames: .zero 1
cover_effect_phase: .zero 1
cover_held_effect: .zero 1
cover_triggers: .zero 2
cover_pcm_frames: .zero 3
.section .text.lab,"ax",@progbits
