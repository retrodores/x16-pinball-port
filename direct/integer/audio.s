; IRQ-fed original PCM. No compiler/KERNAL zero-page locations are touched.
; IRQ is chained through the normal ROM handler, including its 65816 bridge.
.section .text.audio,"ax",@progbits
.globl audio_install,audio_uninstall,audio_effect,audio_stop,audio_toggle
audio_install:
 php
 sei
 lda $0314
 sta audio_old_irq
 lda $0315
 sta audio_old_irq+1
 lda #<audio_irq
 sta $0314
 lda #>audio_irq
 sta $0315
 lda #1
 sta audio_enabled
 jsr audio_stop
 plp
 rts
audio_uninstall:
 php
 sei
 jsr audio_stop
 lda audio_old_irq
 sta $0314
 lda audio_old_irq+1
 sta $0315
 plp
 rts
audio_toggle:
 php
 sei
 lda audio_enabled
 eor #1
 sta audio_enabled
 jsr audio_stop
 plp
 rts
audio_stop:
 php
 sei
 stz $9f3c
 lda #$8c
 sta $9f3b
 stz audio_remaining
 stz audio_remaining+1
 stz audio_priority
 plp
 rts
audio_effect:
 php
 sei
 cmp #7
 bcs audio_effect_done
 tax
 lda audio_enabled
 beq audio_effect_done
 lda audio_remaining
 ora audio_remaining+1
 beq audio_start
 lda audio_priorities,x
 cmp audio_priority
 bcc audio_effect_done
audio_start:
 lda audio_priorities,x
 sta audio_priority
 lda audio_banks,x
 sta audio_bank
 lda audio_low,x
 sta audio_read+1
 lda audio_high,x
 sta audio_read+2
 lda audio_length_low,x
 sta audio_remaining
 lda audio_length_high,x
 sta audio_remaining+1
 stz $9f3c
 lda #$8c
 sta $9f3b
 jsr audio_service
 lda #21
 sta $9f3c
audio_effect_done:
 plp
 rts
audio_irq:
 pha
 phx
 phy
 jsr audio_service
 ply
 plx
 pla
 jmp (audio_old_irq)
audio_service:
 lda audio_remaining
 ora audio_remaining+1
 bne audio_pending
 lda $9f3b
 and #$40
 beq audio_done
 stz $9f3c
audio_done:
 rts
audio_pending:
 lda $9f27
 and #8
 beq audio_done
 lda $00
 pha
 lda audio_bank
 sta $00
 lda audio_remaining+1
 beq audio_partial
 dec audio_remaining+1
 ldx #0
 bra audio_loop
audio_partial:
 ldx audio_remaining
 stz audio_remaining
audio_loop:
audio_read:
 lda $a000
 sta $9f3d
 inc audio_read+1
 bne audio_next
 inc audio_read+2
 lda audio_read+2
 cmp #$c0
 bne audio_next
 lda #$a0
 sta audio_read+2
 inc audio_bank
 lda audio_bank
 cmp #32
 bne audio_select
 lda #2
 sta audio_bank
audio_select:
 sta $00
audio_next:
 dex
 bne audio_loop
 pla
 sta $00
 rts
.section .rodata.audio,"a",@progbits
.include "direct/build/integer/audio-assets.inc"
.section .bss.audio,"aw",@nobits
.globl audio_enabled,audio_remaining
audio_enabled: .zero 1
audio_old_irq: .zero 2
audio_remaining: .zero 2
audio_bank: .zero 1
audio_priority: .zero 1
