; Direct 16-pixel depth rows, masked to requested width/height (1..16).
; x A/X, y rc2/3, depth rc4, dest rc6/7, width rc5, height rc8.
; Input rectangle must fit within the 365x470 table. Saves/restores RAM bank.
.zeropage __rc2,__rc3,__rc4,__rc5,__rc6,__rc7,__rc8,__rc9
.zeropage __rc10,__rc11,__rc12,__rc13,__rc14,__rc15
.section .text.depth_masks,"ax",@progbits
.globl depth_masks
depth_masks:
 sta __rc14
 stx __rc15
 lda __rc8
 sta __rc12
 lda __rc4
 inc
 sta __rc13
 ldx __rc5
 lda depth_bits_low,x
 sta __rc8
 lda depth_bits_high,x
 sta __rc9
 lda __rc2
 sta __rc10
 lda __rc3
 sta __rc11
 asl __rc10
 rol __rc11
 clc
 lda __rc10
 adc __rc2
 sta __rc10
 lda __rc11
 adc __rc3
 clc
 adc #$b4
 sta __rc11
 lda $00
 pha
depth_row:
 lda __rc13
 bne 4f
 jmp depth_blank
4:
 lda #11
 sta $00
 ldy #0
 clc
 lda (__rc10),y
 adc __rc14
 sta __rc4
 iny
 lda (__rc10),y
 adc __rc15
 sta __rc5
 iny
 lda (__rc10),y
 sta $00
 ldy #0
 .rept 8
 lda (__rc4),y
 cmp __rc13
 ror __rc2
 iny
 .endr
 .rept 8
 lda (__rc4),y
 cmp __rc13
 ror __rc3
 iny
 .endr
 jmp depth_store
depth_blank:
 stz __rc2
 stz __rc3
depth_store:
 ldy #0
 lda __rc2
 and __rc8
 sta (__rc6),y
 iny
 lda __rc3
 and __rc9
 sta (__rc6),y
 clc
 lda __rc6
 adc #2
 sta __rc6
 bcc 1f
 inc __rc7
1:
 clc
 lda __rc10
 adc #3
 sta __rc10
 bcc 2f
 inc __rc11
2:
 dec __rc12
 beq 3f
 jmp depth_row
3:
 pla
 sta $00
 rts
.section .rodata.depth_bits,"a",@progbits
depth_bits_low: .byte 0,1,3,7,15,31,63,127,255,255,255,255,255,255,255,255,255
depth_bits_high: .byte 0,0,0,0,0,0,0,0,0,1,3,7,15,31,63,127,255
