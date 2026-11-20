; Rate-73 stereo fixture mixer. Effects are rendered at rate 29 and held
; between source samples. Both drum channels stay independent.
.section .text.stream_mix,"ax",@progbits
.globl stream_mix
stream_mix:
 lda stream_source
 sta left+1
 clc
 adc #1
 sta right+1
 lda stream_source+1
 sta left+2
 adc #0
 sta right+2
 ldx stream_effect
 ldy #0
sample:
 lda effect_phase
 clc
 adc #29
 cmp #73
 bcc phase
 sbc #73
 pha
 lda pcm_buffer,x
 cmp #$80
 ror
 cmp #$80
 ror
 sta held_effect
 inx
 pla
phase:
 sta effect_phase
left:
 lda $ffff,y
 cmp #$80
 ror
 clc
 adc held_effect
 sta $9f3d
right:
 lda $ffff,y
 cmp #$80
 ror
 clc
 adc held_effect
 sta $9f3d
 iny
 iny
 cpy stream_bytes
 bne sample
 stx stream_effect
 rts
