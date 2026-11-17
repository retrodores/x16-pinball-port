; Narrow unsigned 16x8 multiply, LLVM-MOS ABI: A/X, rc2; 32-bit result.
.zeropage __rc2,__rc3,__rc4,__rc5,__rc6,__rc7,__rc8,__rc9
.zeropage __rc10,__rc11,__rc12,__rc13,__rc14,__rc15
.section .text.fastmul8,"ax",@progbits
.globl fastmul8
fastmul8:
 sta __rc4
 stx __rc5
 lda __rc2
 sta __rc6
 lda __rc4
 ldx __rc6
 jsr nm_byte
 sta __rc8
 stx __rc9
 lda __rc5
 beq 1f
 ldx __rc6
 jsr nm_byte
 clc
 adc __rc9
 sta __rc10
 txa
 adc #0
 sta __rc2
 stz __rc3
 lda __rc8
 ldx __rc10
 rts
1:
 stz __rc2
 stz __rc3
 lda __rc8
 ldx __rc9
 rts
nm_byte:
 cmp #0
 beq nm_zero
 cpx #0
 beq nm_zero
 sta __rc10
 stx __rc11
 clc
 adc __rc11
 tax
 bcs nm_high
 lda nm_sqlo,x
 sta __rc12
 lda nm_sqhi,x
 bra nm_diff
nm_high:
 lda nm_sqlo+256,x
 sta __rc12
 lda nm_sqhi+256,x
nm_diff:
 sta __rc13
 sec
 lda __rc10
 sbc __rc11
 bcs nm_positive
 eor #255
 inc
nm_positive:
 tax
 sec
 lda __rc12
 sbc nm_sqlo,x
 sta __rc12
 lda __rc13
 sbc nm_sqhi,x
 tax
 lda __rc12
 rts
nm_zero:
 lda #0
 tax
 rts
.section .rodata.fastmul,"a",@progbits
.p2align 8
nm_sqlo:
.include "direct/integer/squares-lo.inc"
nm_sqhi:
.include "direct/integer/squares-hi.inc"
