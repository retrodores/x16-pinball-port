; Standalone Commander X16 music audition. The ZSMKit v3 library owns banks
; 1 and 2. The song is resident from bank 3 upward. No pinball files needed.
.setcpu "65C02"
.macpack longbranch
.segment "CODE"
.word $0801
.word basic_end
.word 10
.byte $9e,"2061",0
basic_end: .word 0
start:
 lda $00
 pha
 ldx #0
: lda banner,x
 beq :+
 jsr $ffd2
 inx
 bra :-
:
 lda #1
 sta $00
 lda #libend-lib
 ldx #<lib
 ldy #>lib
 jsr load_binary
 jcs failure
 lda #3
 sta $00
 lda #songend-song
 ldx #<song
 ldy #>song
 jsr load_binary
 jcs failure
 lda #3
 sta $00
 lda $a000
 cmp #'z'
 jne failure
 lda #1
 sta $00
 lda $a000
 cmp #$4c
 jne failure
 ldx #<workspace
 ldy #>workspace
 jsr $a000
 lda #59
 ldy #134
 jsr $a03f
 ldx #0
 lda #3
 jsr $a01b
 ldx #0
 lda #0
 ldy #$a0
 jsr $a01e
 ldx #0
 jsr $a02a
 beq failure
 jsr install_irq
 ldx #0
 jsr $a006
 ldx #0
: lda playing,x
 beq :+
 jsr $ffd2
 inx
 bra :-
:
wait:
 wai
 jsr $ffe4
 cmp #'Q'
 beq finish
 cmp #'q'
 beq finish
 cmp #27
 beq finish
 lda #1
 sta $00
 ldx #0
 jsr $a02a
 bcs wait
finish:
 lda #1
 sta $00
 ldx #0
 jsr $a009
 jsr remove_irq
 ldx #0
 jsr $a00f
 ldx #0
: lda done,x
 beq restore
 jsr $ffd2
 inx
 bra :-
failure:
 ldx #0
: lda error,x
 beq restore
 jsr $ffd2
 inx
 bra :-
restore:
 pla
 sta $00
 rts
install_irq:
 php
 sei
 lda $0314
 sta old_irq
 lda $0315
 sta old_irq+1
 lda #<on_irq
 sta $0314
 lda #>on_irq
 sta $0315
 plp
 rts
remove_irq:
 php
 sei
 lda old_irq
 sta $0314
 lda old_irq+1
 sta $0315
 plp
 rts
on_irq:
 lda $9f27
 and #1
 beq chain_irq
 lda $00
 pha
 lda #1
 sta $00
 lda #0
 jsr $a003
 pla
 sta $00
chain_irq:
 jmp (old_irq)
old_irq: .word 0
load_binary:
 jsr $ffbd
 lda #1
 ldx #8
 ldy #2
 jsr $ffba
 lda #0
 ldx #0
 ldy #$a0
 jmp $ffd5
lib: .byte "ZSMKIT.BIN"
libend:
song: .byte "CAROL.ZSM"
songend:
banner: .byte 13,"CAROL OF THE BELLS - X16 ROCK AUDITION",13,"LOADING MUSIC...",13,0
playing: .byte "# PLAY",13,"Q TO RETURN TO BASIC.",13,0
done: .byte "# DONE",13,0
error: .byte "CHECK CAROL.ZSM AND ZSMKIT.BIN IN THIS FOLDER.",13,0
workspace: .res 256
