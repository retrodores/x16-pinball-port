; Exact signed AABB rejection against the original Edge record.
; Input A/X edge id; output rc2/rc3 bank-window pointer, or zero if rejected.
; bound_query = xmin,xmax,ymin,ymax, already expanded by five Q8 units.
; Leaves the edge's bank selected, matching edge() in engine.c.
.zeropage __rc2,__rc3,__rc4,__rc5
.section .text.bounded_edge,"ax",@progbits
.globl bounded_edge
bounded_edge:
 sta __rc2
 and #7
 asl
 asl
 asl
 asl
 asl
 sta __rc4
 lda __rc2
 lsr
 lsr
 lsr
 ora #$a0
 sta __rc5
 txa
 clc
 adc #12
 sta $00
 ; query xmax >= edge xmin
 ldy #14
 lda bound_query+2
 cmp (__rc4),y
 iny
 lda bound_query+3
 sbc (__rc4),y
 bvc 1f
 eor #$80
1:
 bmi rejected
 ; query ymax >= edge ymin
 iny
 lda bound_query+6
 cmp (__rc4),y
 iny
 lda bound_query+7
 sbc (__rc4),y
 bvc 2f
 eor #$80
2:
 bmi rejected
 ; edge xmax >= query xmin
 iny
 lda (__rc4),y
 cmp bound_query
 iny
 lda (__rc4),y
 sbc bound_query+1
 bvc 3f
 eor #$80
3:
 bmi rejected
 ; edge ymax >= query ymin
 iny
 lda (__rc4),y
 cmp bound_query+4
 iny
 lda (__rc4),y
 sbc bound_query+5
 bvc 4f
 eor #$80
4:
 bmi rejected
 lda __rc4
 sta __rc2
 lda __rc5
 sta __rc3
 rts
rejected:
 stz __rc2
 stz __rc3
 rts
