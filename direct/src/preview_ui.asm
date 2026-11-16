; Bank 1 presentation. No compiler zero page registers are touched.
.cpu "65c02"
.include "../build/preview/ui-address.inc"
* = $a000
jmp init
jmp draw
init:
 php
 sei
 stz $9f25
 stz $9f20
 lda #$fc
 sta $9f21
 lda #$11
 sta $9f22
 ldx #4
 ldy #0
 lda #0
clear:
 sta $9f23
 iny
 bne clear
 dex
 bne clear
 stz $9f20
 lda #$fc
 sta $9f21
 lda #$11
 sta $9f22
 ldx #0
copy:
 lda sprites,x
 sta $9f23
 inx
 cpx #88
 bne copy
 lda #64
 sta $9f2a
 sta $9f2b
 stz $9f2c
 lda #7
 sta $9f2d
 stz $9f2e
 stz $9f2f
 stz $9f30
 stz $9f31
 stz $9f32
 stz $9f33
 lda #$51
 sta $9f29
 lda #255
 sta last_status
 sta last_charge
 plp
 rts
draw:
 php
 sei
 stz $9f25
 lda #2
 sta $9f20
 lda #$fc
 sta $9f21
 lda #$11
 sta $9f22
 ldx #0
ball:
 lda ui_state,x
 sta $9f23
 inx
 cpx #4
 bne ball
 lda #8
 sta $9f20
 lda ui_state+4
 asl
 asl
 asl
 asl
 asl
 clc
 adc #$80
 sta $9f23
 lda #$89
 adc #0
 sta $9f23
 lda #16
 sta $9f20
 lda ui_state+5
 asl
 asl
 asl
 asl
 asl
 clc
 adc #$80
 sta $9f23
 lda #$8a
 adc #0
 sta $9f23
 lda #80
 sta $9f20
 lda ui_state+6
 asl
 asl
 asl
 asl
 sta $9f23
 lda #$8e
 sta $9f23
 lda ui_state+7
 cmp last_status
 beq charge
 sta last_status
 tax
 lda status_lo,x
 sta read_pixel+1
 lda status_hi,x
 sta read_pixel+2
 lda #<(84*320+204)
 sta screen_lo
 lda #>(84*320+204)
 sta screen_hi
 lda #10
 sta rows
status_row:
 lda screen_lo
 sta $9f20
 lda screen_hi
 sta $9f21
 lda #$10
 sta $9f22
 ldx #0
read_pixel:
 lda status,x
 sta $9f23
 inx
 cpx #108
 bne read_pixel
 clc
 lda read_pixel+1
 adc #108
 sta read_pixel+1
 bcc no_carry
 inc read_pixel+2
no_carry:
 jsr next_row
 dec rows
 bne status_row
charge:
 lda ui_state+8
 cmp last_charge
 beq done
 sta last_charge
 lda #<(112*320+204)
 sta screen_lo
 lda #>(112*320+204)
 sta screen_hi
 lda #4
 sta rows
charge_row:
 lda screen_lo
 sta $9f20
 lda screen_hi
 sta $9f21
 lda #$10
 sta $9f22
 ldx #0
bar:
 lda #248
 cpx last_charge
 bcc colored
 lda #247
colored:
 sta $9f23
 inx
 cpx #100
 bne bar
 jsr next_row
 dec rows
 bne charge_row
done:
 plp
 rts
next_row:
 clc
 lda screen_lo
 adc #$40
 sta screen_lo
 lda screen_hi
 adc #1
 sta screen_hi
 rts
screen_lo: .byte 0
screen_hi: .byte 0
rows: .byte 0
last_status: .byte 255
last_charge: .byte 255
sprites: .binary "../build/preview/sprites-init.bin"
status_lo: .byte <status,<(status+1080),<(status+2160),<(status+3240),<(status+4320),<(status+5400)
status_hi: .byte >status,>(status+1080),>(status+2160),>(status+3240),>(status+4320),>(status+5400)
status: .binary "../build/preview/status.bin"
.cerror * > $c000, "UI exceeds one RAM bank"
