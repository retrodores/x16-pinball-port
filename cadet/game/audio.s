; Original PCM + standard ZSM v1 player. No compiler or KERNAL zero page.
; Music: banks 32..58; resident PCM effects: banks 19..31.
.section .text.lab,"ax",@progbits
.globl lab_install,lab_uninstall,pcm_start,pcm_stop,music_start,music_stop,lab_clock
lab_install:
 php
 sei
 lda $0314
 sta old_irq
 lda $0315
 sta old_irq+1
 lda #<lab_irq
 sta $0314
 lda #>lab_irq
 sta $0315
 stz lab_ticks
 stz lab_ticks+1
 stz music_enabled
 stz music_loops
 stz music_error
 stz irq_max
 stz irq_max+1
 stz irq_max+2
 stz irq_max+3
 ldx #3
1:
 stz fm_writes,x
 stz psg_writes,x
 dex
 bpl 1b
 jsr save_address
 lda #$c0
 sta $9f20
 lda #$f9
 sta $9f21
 lda #$11
 sta $9f22
 ldx #0
2:
 lda $9f24
 sta saved_psg,x
 inx
 cpx #64
 bne 2b
 jsr restore_address
 jsr pcm_stop
 plp
 rts
lab_uninstall:
 php
 sei
 jsr music_stop
 jsr pcm_stop
 lda old_irq
 sta $0314
 lda old_irq+1
 sta $0315
 jsr save_address
 lda #$c0
 sta $9f20
 lda #$f9
 sta $9f21
 lda #$11
 sta $9f22
 ldx #0
1:
 lda saved_psg,x
 sta $9f24
 inx
 cpx #64
 bne 1b
 jsr restore_address
 plp
 rts
lab_clock:
 php
 sei
 lda lab_ticks
 ldx lab_ticks+1
 plp
 rts
pcm_stop:
 php
 sei
 stz $9f3c
 lda #$80
 sta $9f3b
 stz pcm_remaining
 stz pcm_remaining+1
 plp
 rts
pcm_start:
 php
 sei
 sta pcm_remaining
 stx pcm_remaining+1
 stz $9f3c
 lda #$8b
 sta $9f3b
 lda pcm_select_bank
 sta pcm_bank
 lda pcm_select_ptr
 sta pcm_read+1
 lda pcm_select_ptr+1
 sta pcm_read+2
 plp
 rts
music_start:
 php
 sei
 jsr music_stop
 lda #32
 sta music_bank
 lda #$10
 sta music_read+1
 lda #$a0
 sta music_read+2
 stz music_delay
 stz music_phase
 lda #1
 sta music_enabled
 plp
 rts
music_stop:
 php
 sei
 stz music_enabled
 ldx #0
1:
 txa
 pha
 lda #8
 sta $9f40
2:
 bit $9f41
 bmi 2b
 pla
 sta $9f41
 inx
 cpx #8
 bne 1b
 jsr save_address
 ldx #4
3:
 txa
 asl
 asl
 ora #$c2
 sta $9f20
 lda #$f9
 sta $9f21
 lda #1
 sta $9f22
 stz $9f24
 inx
 cpx #16
 bne 3b
 jsr restore_address
 plp
 rts
lab_irq:
 pha
 phx
 phy
 lda $9f27
 and #1
 beq irq_end
 ldx #0
1:
 lda $9fb8,x
 sta irq_start,x
 inx
 cpx #4
 bne 1b
 inc lab_ticks
 bne 2f
 inc lab_ticks+1
2:
 jsr pcm_service
 jsr music_service
 ; VGA refresh is 25 MHz / (800 * 525): 60 ticks = 126/125 frames.
 inc music_phase
 lda music_phase
 cmp #125
 bcc 6f
 stz music_phase
 jsr music_service
6:
 sec
 lda $9fb8
 sbc irq_start
 sta irq_elapsed
 lda $9fb9
 sbc irq_start+1
 sta irq_elapsed+1
 lda $9fba
 sbc irq_start+2
 sta irq_elapsed+2
 lda $9fbb
 sbc irq_start+3
 sta irq_elapsed+3
 ldx #3
3:
 lda irq_elapsed,x
 cmp irq_max,x
 bcc irq_end
 bne 4f
 dex
 bpl 3b
 bra irq_end
4:
 ldx #3
5:
 lda irq_elapsed,x
 sta irq_max,x
 dex
 bpl 5b
irq_end:
 ply
 plx
 pla
 jmp (old_irq)
pcm_service:
 lda pcm_remaining
 ora pcm_remaining+1
 bne pcm_pending
 lda $9f3b
 and #$40
 beq pcm_done
 stz $9f3c
 lda #$80
 sta $9f3b ; Mute the held final sample while idle.
pcm_done:
 rts
pcm_pending:
 lda $9f27
 and #8
 beq pcm_done
 lda $00
 pha
 lda pcm_bank
 sta $00
 lda pcm_remaining+1
 beq pcm_partial
 dec pcm_remaining+1
 ldx #0
 bra pcm_loop
pcm_partial:
 ldx pcm_remaining
 stz pcm_remaining
pcm_loop:
pcm_read:
 lda $a000
 sta $9f3d
 inc pcm_read+1
 bne pcm_next
 inc pcm_read+2
 lda pcm_read+2
 cmp #$c0
 bne pcm_next
 lda #$a0
 sta pcm_read+2
 inc pcm_bank
 lda pcm_bank
 sta $00
pcm_next:
 dex
 bne pcm_loop
 lda #29
 sta $9f3c
 pla
 sta $00
 rts
save_address:
 lda $9f25
 sta saved_ctrl
 ora #1
 sta $9f25
 lda $9f20
 sta saved_addr
 lda $9f21
 sta saved_addr+1
 lda $9f22
 sta saved_addr+2
 rts
restore_address:
 lda saved_addr
 sta $9f20
 lda saved_addr+1
 sta $9f21
 lda saved_addr+2
 sta $9f22
 lda saved_ctrl
 sta $9f25
 rts
music_service:
 lda music_enabled
 bne 1f
 rts
1:
 lda music_delay
 beq 2f
 dec music_delay
 beq 2f
 rts
2:
 lda $00
 pha
 lda music_bank
 sta $00
 jsr save_address
music_command:
 jsr music_byte
 bmi music_wait
 cmp #$40
 bcs music_fm
 ; PSG offset 0..63
 ora #$c0
 sta $9f20
 lda #$f9
 sta $9f21
 lda #1
 sta $9f22
 jsr music_byte
 sta $9f24
 inc psg_writes
 bne music_command
 inc psg_writes+1
 bne music_command
 inc psg_writes+2
 bra music_command
music_fm:
 and #$3f
 sta music_count
 beq music_extension
music_fm_loop:
 jsr music_byte
 sta music_reg
 jsr music_byte
 pha
 lda music_reg
 sta $9f40
3:
 bit $9f41
 bmi 3b
 pla
 sta $9f41
 inc fm_writes
 bne 4f
 inc fm_writes+1
 bne 4f
 inc fm_writes+2
4:
 dec music_count
 bne music_fm_loop
 bra music_command
music_extension:
 ; Extensions are structurally skipped. Generated theme uses none.
 jsr music_byte
 and #$3f
 sta music_count
 beq music_command
5:
 jsr music_byte
 dec music_count
 bne 5b
 bra music_command
music_wait:
 and #$7f
 beq music_eof
 sta music_delay
 bra music_return
music_eof:
 inc music_loops
 lda #32
 sta music_bank
 lda #$10
 sta music_read+1
 lda #$a0
 sta music_read+2
 ; Start the next loop on the next video tick.
 lda #1
 sta music_delay
music_return:
 jsr restore_address
 pla
 sta $00
 rts
music_byte:
music_read:
 lda $a010
 inc music_read+1
 bne byte_done
 pha
 inc music_read+2
 lda music_read+2
 cmp #$c0
 bne byte_restore
 lda #$a0
 sta music_read+2
 inc music_bank
 lda music_bank
 cmp #64
 bcc 1f
 inc music_error
1:
 sta $00
byte_restore:
 pla
byte_done:
 ora #0
 rts
.section .bss.lab,"aw",@nobits
.globl pcm_remaining,music_enabled,music_loops,lab_ticks,music_error,irq_max,fm_writes,psg_writes
old_irq: .zero 2
lab_ticks: .zero 2
saved_ctrl: .zero 1
saved_addr: .zero 3
saved_psg: .zero 64
pcm_remaining: .zero 2
pcm_bank: .zero 1
music_enabled: .zero 1
music_bank: .zero 1
music_delay: .zero 1
music_phase: .zero 1
music_count: .zero 1
music_reg: .zero 1
music_loops: .zero 1
music_error: .zero 1
irq_start: .zero 4
irq_elapsed: .zero 4
irq_max: .zero 4
fm_writes: .zero 4
psg_writes: .zero 4

.globl pcm_select_bank,pcm_select_ptr
pcm_select_bank: .zero 1
pcm_select_ptr: .zero 2

.globl irq_start,irq_elapsed
