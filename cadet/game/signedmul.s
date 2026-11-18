; Signed 16x16 -> 32, exact two's complement. LLVM-MOS caller-saved registers only.
.zeropage __rc2,__rc3,__rc4,__rc5
.section .text.signedmul,"ax",@progbits
.globl signedmul
signedmul:
 sta __rc4
 stx __rc5
 txa
 eor __rc3
 pha
 txa
 bpl 1f
 sec
 lda #0
 sbc __rc4
 sta __rc4
 lda #0
 sbc __rc5
 sta __rc5
1:
 lda __rc3
 bpl 2f
 sec
 lda #0
 sbc __rc2
 sta __rc2
 lda #0
 sbc __rc3
 sta __rc3
2:
 lda __rc3
 beq narrow
 lda __rc5
 beq swap
 lda __rc4
 ldx __rc5
 jsr fastmul16
 bra sign
swap:
 lda __rc2
 ldx __rc3
 ldy __rc4
 sty __rc2
 jsr fastmul8
 bra sign
narrow:
 lda __rc4
 ldx __rc5
 jsr fastmul8
sign:
 sta __rc4
 pla
 bpl positive
 sec
 lda #0
 sbc __rc4
 sta __rc4
 stx __rc5
 lda #0
 sbc __rc5
 tax
 lda #0
 sbc __rc2
 sta __rc2
 lda #0
 sbc __rc3
 sta __rc3
positive:
 lda __rc4
 rts
