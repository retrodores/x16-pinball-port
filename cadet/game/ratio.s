; Exact floor(4096*n/d), modulo uint16, for the rebound scale.
; A/X=n, rc2/3=d; returns A/X. Caller-saved registers only.
.zeropage __rc2,__rc3,__rc4,__rc5,__rc6,__rc7,__rc8,__rc9
.section .text.ratio12,"ax",@progbits
.globl ratio12
ratio12:
 sta __rc4
 stx __rc5
 stz __rc6
 stz __rc7
 stz __rc8
 lda __rc2
 ora __rc3
 bne whole_loop
 lda #0
 tax
 rts
whole_loop:
 lda __rc5
 cmp __rc3
 bcc fractional
 bne subtract_whole
 lda __rc4
 cmp __rc2
 bcc fractional
subtract_whole:
 sec
 lda __rc4
 sbc __rc2
 sta __rc4
 lda __rc5
 sbc __rc3
 sta __rc5
 clc
 lda __rc8
 adc #16
 sta __rc8
 bra whole_loop
fractional:
 ldy #12
1:
 asl __rc4
 rol __rc5
 asl __rc6
 rol __rc7
 lda __rc5
 cmp __rc3
 bcc 3f
 bne 2f
 lda __rc4
 cmp __rc2
 bcc 3f
2:
 sec
 lda __rc4
 sbc __rc2
 sta __rc4
 lda __rc5
 sbc __rc3
 sta __rc5
 inc __rc6
3:
 dey
 bne 1b
 lda __rc7
 ora __rc8
 tax
 lda __rc6
 rts
; floor(256*n/d), saturated at 256. Used with 0<d<2^31, n<=d.
; n A/X/rc2/3; d rc4..7; output A/X.
.section .text.fraction32,"ax",@progbits
.globl fraction32
fraction32:
 sta __rc8
 stx __rc9
 lda __rc3
 cmp __rc7
 bcc fraction_begin
 bne fraction_full
 lda __rc2
 cmp __rc6
 bcc fraction_begin
 bne fraction_full
 lda __rc9
 cmp __rc5
 bcc fraction_begin
 bne fraction_full
 lda __rc8
 cmp __rc4
 bcc fraction_begin
fraction_full:
 lda #0
 ldx #1
 rts
fraction_begin:
 ldx #0
 ldy #8
1:
 asl __rc8
 rol __rc9
 rol __rc2
 rol __rc3
 txa
 asl
 tax
 lda __rc3
 cmp __rc7
 bcc 3f
 bne 2f
 lda __rc2
 cmp __rc6
 bcc 3f
 bne 2f
 lda __rc9
 cmp __rc5
 bcc 3f
 bne 2f
 lda __rc8
 cmp __rc4
 bcc 3f
2:
 sec
 lda __rc8
 sbc __rc4
 sta __rc8
 lda __rc9
 sbc __rc5
 sta __rc9
 lda __rc2
 sbc __rc6
 sta __rc2
 lda __rc3
 sbc __rc7
 sta __rc3
 inx
3:
 dey
 bne 1b
 txa
 ldx #0
 rts
