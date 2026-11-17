; LLVM-MOS ABI: a=A/X, b=rc2/rc3; return=A/X/rc2/rc3.
; Uses only caller-saved imaginary registers. IRQ does no arithmetic here.
.zeropage __rc2,__rc3,__rc4,__rc5,__rc6,__rc7,__rc8,__rc9
.zeropage __rc10,__rc11,__rc12,__rc13,__rc14,__rc15
.section .text.fastmul16,"ax",@progbits
.globl fastmul16
fastmul16:
 sta __rc4
 stx __rc5
 lda __rc2
 sta __rc6
 lda __rc3
 sta __rc7
 lda __rc4
 ldx __rc6
 jsr fm_byte
 sta __rc8
 stx __rc9
 stz __rc15
 lda __rc5
 ldx __rc6
 jsr fm_byte
 clc
 adc __rc9
 sta __rc9
 txa
 adc #0
 sta __rc14
 lda __rc4
 ldx __rc7
 jsr fm_byte
 clc
 adc __rc9
 sta __rc9
 txa
 adc __rc14
 sta __rc14
 bcc 1f
 inc __rc15
1:
 lda __rc5
 ldx __rc7
 jsr fm_byte
 clc
 adc __rc14
 sta __rc2
 txa
 adc __rc15
 sta __rc3
 lda __rc8
 ldx __rc9
 rts
fm_byte:
 cmp #0
 beq fm_zero
 cpx #0
 beq fm_zero
 sta __rc10
 stx __rc11
 clc
 adc __rc11
 tax
 bcs fm_high
 lda fm_sqlo,x
 sta __rc12
 lda fm_sqhi,x
 bra fm_diff
fm_high:
 lda fm_sqlo+256,x
 sta __rc12
 lda fm_sqhi+256,x
fm_diff:
 sta __rc13
 sec
 lda __rc10
 sbc __rc11
 bcs fm_positive
 eor #255
 inc
fm_positive:
 tax
 sec
 lda __rc12
 sbc fm_sqlo,x
 sta __rc12
 lda __rc13
 sbc fm_sqhi,x
 tax
 lda __rc12
 rts
fm_zero:
 lda #0
 tax
 rts
.section .rodata.fastmul,"a",@progbits
.p2align 8
.globl fm_sqlo
fm_sqlo:
.include "direct/integer/squares-lo.inc"
.globl fm_sqhi
fm_sqhi:
.include "direct/integer/squares-hi.inc"
