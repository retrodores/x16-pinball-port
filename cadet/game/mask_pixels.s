; Mask 128 4bpp ball bytes from VERA DATA1 to DATA0.
; Both address ports have increment 1, set by the caller. Input A/X is the
; address of 16 visibility words. Zero bits clear the matching sprite nibble.
.zeropage __rc2,__rc3,__rc4
.section .text.mask_pixels,"ax",@progbits
.globl mask_pixels
mask_pixels:
 sta __rc2
 stx __rc3
 ldy #0
1:
 lda (__rc2),y
 sta __rc4
 .rept 4
 lda __rc4
 and #3
 tax
 lda $9f24
 and pixel_keep,x
 sta $9f23
 lsr __rc4
 lsr __rc4
 .endr
 iny
 cpy #32
 bne 1b
 rts
.section .rodata.pixel_keep,"a",@progbits
pixel_keep: .byte 0,240,15,255
