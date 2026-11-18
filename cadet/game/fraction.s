; floor(256*n/d), saturated at 256. d<32768 for unsaturated calls.
.zeropage __rc2,__rc3,__rc4,__rc5,__rc6
.section .text.fraction8,"ax",@progbits
.globl fraction8
fraction8:
 sta __rc4
 stx __rc5
 txa
 cmp __rc3
 bcc begin
 bne full
 lda __rc4
 cmp __rc2
 bcc begin
full:
 lda #0
 ldx #1
 rts
begin:
 stz __rc6
 ldy #8
1:
 asl __rc4
 rol __rc5
 asl __rc6
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
 lda __rc6
 ldx #0
 rts
