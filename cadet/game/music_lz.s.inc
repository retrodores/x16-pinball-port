; Lossless LZSS reader. Entirely self-modifying/BSS state: no compiler zero page.
; Preserves X/Y. Each call returns one original ZSM command-stream byte in A.
.globl music_reset,music_byte,lz_byte,music_prefetch,music_buffered
music_reset:
 stz lz_write+1
 stz music_consume+1
 lda #$a0
 sta lz_write+2
 sta music_consume+2
 stz music_buffered
 stz music_buffered+1
lz_restart:
 lda #32
 sta music_bank
 stz music_read+1
 lda #$a0
 sta music_read+2
 stz lz_left
 stz lz_run
 lda #$df
 sta lz_remaining
 lda #$44
 sta lz_remaining+1
 lda #3
 sta lz_remaining+2
 rts
lz_byte:
 lda lz_remaining
 ora lz_remaining+1
 ora lz_remaining+2
 bne 1f
 jsr lz_restart
1:
 lda lz_run
 bne lz_match
 lda lz_left
 bne lz_flag
 jsr music_raw
 sta lz_flags
 lda #8
 sta lz_left
lz_flag:
 lsr lz_flags
 dec lz_left
 bcs lz_token
 jsr music_raw
 bra lz_emit
lz_token:
 jsr music_raw
 sta lz_low
 jsr music_raw
 sta lz_high
 lsr
 lsr
 lsr
 lsr
 clc
 adc #3
 sta lz_run
 lda lz_high
 and #15
 sta lz_high
 clc
 lda lz_write+1
 sbc lz_low
 sta lz_read+1
 lda lz_write+2
 sbc lz_high
 and #15
 ora #$a0
 sta lz_read+2
lz_match:
 dec lz_run
 lda #31
 sta $00
lz_read:
 lda $a000
 inc lz_read+1
 bne lz_emit
 pha
 inc lz_read+2
 lda lz_read+2
 and #15
 ora #$a0
 sta lz_read+2
 pla
lz_emit:
 pha
 lda #31
 sta $00
 pla
lz_write:
 sta $a000
 inc lz_write+1
 bne lz_done
 pha
 inc lz_write+2
 lda lz_write+2
 and #15
 ora #$a0
 sta lz_write+2
 pla
lz_done:
 pha
 lda lz_remaining
 bne 1f
 lda lz_remaining+1
 bne 2f
 dec lz_remaining+2
2:
 dec lz_remaining+1
1:
 dec lz_remaining
 pla
 ora #0
 rts
music_raw:
 lda music_bank
 sta $00
music_read:
 lda $a000
 inc music_read+1
 bne raw_done
 pha
 inc music_read+2
 lda music_read+2
 cmp #$c0
 bne raw_restore
 lda #$a0
 sta music_read+2
 inc music_bank
 lda music_bank
 cmp #45
 bcc 1f
 inc music_error
1:
 sta $00
raw_restore:
 pla
raw_done:
 ora #0
 rts

; Main-thread producer: at most 64 bytes, target 2048 bytes ahead. IRQ only reads.
music_prefetch:
 lda music_enabled
 beq prefetch_return
 lda $00
 pha
 ldx #64
prefetch_next:
 lda music_buffered+1
 cmp #8
 bcs prefetch_done
 jsr lz_byte
 php
 sei
 inc music_buffered
 bne 1f
 inc music_buffered+1
1:
 plp
 dex
 bne prefetch_next
prefetch_done:
 pla
 sta $00
prefetch_return:
 rts
; IRQ consumer. music_service selects bank 31 before parsing commands.
music_byte:
 lda music_buffered
 ora music_buffered+1
 bne 1f
 inc music_error
 lda #$80
 rts
1:
 lda music_buffered
 bne 2f
 dec music_buffered+1
2:
 dec music_buffered
music_consume:
 lda $a000
 inc music_consume+1
 bne consumer_done
 pha
 inc music_consume+2
 lda music_consume+2
 and #15
 ora #$a0
 sta music_consume+2
 pla
consumer_done:
 ora #0
 rts
