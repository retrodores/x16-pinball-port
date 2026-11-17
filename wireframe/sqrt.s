; Exact unsigned 32-bit integer square root. LLVM-MOS C ABI.
; Input A/X/rc2/rc3; output A/X. Caller-saved rc4..rc15 only.
.zeropage __rc2,__rc3,__rc4,__rc5,__rc6,__rc7,__rc8,__rc9
.zeropage __rc10,__rc11,__rc12,__rc13,__rc14,__rc15
.section .text.fastsqrt,"ax",@progbits
.globl fastsqrt
fastsqrt:
 sta __rc4
 stx __rc5
 lda __rc2
 sta __rc6
 lda __rc3
 sta __rc7
 stz __rc8
 stz __rc9
 stz __rc10
 stz __rc11
 stz __rc12
 ldx #16
1:
 asl __rc11
 rol __rc12
 asl __rc4
 rol __rc5
 rol __rc6
 rol __rc7
 rol __rc8
 rol __rc9
 rol __rc10
 asl __rc4
 rol __rc5
 rol __rc6
 rol __rc7
 rol __rc8
 rol __rc9
 rol __rc10
 lda __rc11
 asl
 sta __rc13
 lda __rc12
 rol
 sta __rc14
 lda #0
 rol
 sta __rc15
 inc __rc13
 lda __rc10
 cmp __rc15
 bcc 3f
 bne 2f
 lda __rc9
 cmp __rc14
 bcc 3f
 bne 2f
 lda __rc8
 cmp __rc13
 bcc 3f
2:
 sec
 lda __rc8
 sbc __rc13
 sta __rc8
 lda __rc9
 sbc __rc14
 sta __rc9
 lda __rc10
 sbc __rc15
 sta __rc10
 inc __rc11
 bne 3f
 inc __rc12
3:
 dex
 bne 1b
 lda __rc11
 ldx __rc12
 rts
