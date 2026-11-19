; Exact PackBits depth span. x=A/X, y=rc2/3, depth=rc4, result=A/X.
; Each 64-pixel row block is independently indexed in bank10; data17,18,45..50.
; Input x0..349,y0..469; returns16 visibility bits and restores RAM bank.
.zeropage __rc2,__rc3,__rc4,__rc5,__rc6,__rc7,__rc8,__rc9
.zeropage __rc10,__rc11,__rc12,__rc13,__rc14,__rc15
.section .text.depth_decode,"ax",@progbits
.globl depth_decode
depth_decode:
 sta __rc6
 stx __rc7
 lda __rc4
 inc
 sta __rc13
 bne 1f
 lda #0
 tax
 rts
1:
 lda $00
 pha
 ; y*12 + (x/64)*2 is the block index byte offset.
 lda __rc2
 sta __rc14
 lda __rc3
 sta __rc15
 asl __rc14
 rol __rc15
 clc
 lda __rc14
 adc __rc2
 sta __rc14
 lda __rc15
 adc __rc3
 sta __rc15
 asl __rc14
 rol __rc15
 asl __rc14
 rol __rc15
 lda __rc6
 and #$c0
 lsr
 lsr
 lsr
 lsr
 lsr
 sta __rc5
 lda __rc7
 asl
 asl
 asl
 ora __rc5
 clc
 adc __rc14
 sta __rc14
 lda __rc15
 adc #$a0
 sta __rc15
 lda __rc6
 and #63
 sta __rc12
 lda #64
 sec
 sbc __rc12
 sta __rc11
 lda #16
 sta __rc10
 stz __rc8
 stz __rc9
 jsr depth_getblock
depth_token:
 lda (__rc6),y
 sta __rc5
 bmi depth_repeat
 iny
 ; Literal run: skip irrelevant prefix without reading individual pixels.
 lda __rc12
 cmp __rc5
 bcc depth_literal_partial
 sec
 sbc __rc5
 sta __rc12
 tya
 clc
 adc __rc5
 tay
 jmp depth_token
depth_literal_partial:
 lda __rc5
 sec
 sbc __rc12
 sta __rc5
 tya
 clc
 adc __rc12
 tay
 stz __rc12
depth_literal_emit:
 lda (__rc6),y
 cmp __rc13
 ror __rc9
 ror __rc8
 dec __rc10
 beq depth_done
 dec __rc11
 beq depth_nextblock
 iny
 dec __rc5
 bne depth_literal_emit
 jmp depth_token
depth_repeat:
 and #127
 sta __rc5
 iny
 lda (__rc6),y
 sta __rc2
 iny
 lda __rc12
 cmp __rc5
 bcc depth_repeat_partial
 sec
 sbc __rc5
 sta __rc12
 jmp depth_token
depth_repeat_partial:
 lda __rc5
 sec
 sbc __rc12
 sta __rc5
 stz __rc12
depth_repeat_emit:
 lda __rc2
 cmp __rc13
 ror __rc9
 ror __rc8
 dec __rc10
 beq depth_done
 dec __rc11
 beq depth_nextblock
 dec __rc5
 bne depth_repeat_emit
 jmp depth_token
depth_nextblock:
 clc
 lda __rc14
 adc #2
 sta __rc14
 bcc 1f
 inc __rc15
1:
 lda #64
 sta __rc11
 jsr depth_getblock
 jmp depth_token
depth_done:
 pla
 sta $00
 lda __rc8
 ldx __rc9
 rts
depth_getblock:
 lda #10
 sta $00
 ldy #0
 lda (__rc14),y
 sta __rc6
 iny
 lda (__rc14),y
 pha
 and #$1f
 ora #$a0
 sta __rc7
 pla
 lsr
 lsr
 lsr
 lsr
 lsr
 tax
 lda depth_banks,x
 sta $00
 ldy #0
 rts
.section .rodata.depth_banks,"a",@progbits
depth_banks: .byte 17,18,45,46,47,48,49,50

; Rectangle wrapper uses private scratch: only foreground rendering calls it.
; x=A/X,y=rc2/3,d=rc4,dest=rc6/7,width=rc5,height=rc8.
.section .text.depth_masks,"ax",@progbits
.globl depth_masks
depth_masks:
 sta rect_x
 stx rect_x+1
 lda __rc2
 sta rect_y
 lda __rc3
 sta rect_y+1
 lda __rc4
 sta rect_depth
 lda __rc5
 sta rect_width
 lda __rc6
 sta rect_dest
 lda __rc7
 sta rect_dest+1
 lda __rc8
 sta rect_height
 bne rect_row
 rts
rect_row:
 lda rect_y
 sta __rc2
 lda rect_y+1
 sta __rc3
 lda rect_depth
 sta __rc4
 lda rect_x
 ldx rect_x+1
 jsr depth_decode
 sta __rc2
 stx __rc3
 ldy rect_width
 and rect_bits_low,y
 sta __rc2
 txa
 and rect_bits_high,y
 sta __rc3
 lda rect_dest
 sta __rc6
 lda rect_dest+1
 sta __rc7
 ldy #0
 lda __rc2
 sta (__rc6),y
 iny
 lda __rc3
 sta (__rc6),y
 clc
 lda rect_dest
 adc #2
 sta rect_dest
 bcc 1f
 inc rect_dest+1
1:
 inc rect_y
 bne 2f
 inc rect_y+1
2:
 dec rect_height
 bne rect_row
 rts
.section .rodata.rect_bits,"a",@progbits
rect_bits_low: .byte 0,1,3,7,15,31,63,127,255,255,255,255,255,255,255,255,255
rect_bits_high: .byte 0,0,0,0,0,0,0,0,0,1,3,7,15,31,63,127,255
.section .bss.depthrect,"aw",@nobits
rect_x: .space 2
rect_y: .space 2
rect_dest: .space 2
rect_depth: .space 1
rect_width: .space 1
rect_height: .space 1
