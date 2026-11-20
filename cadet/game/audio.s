; Three original-rate PCM voices + standard ZSM v1 player. No compiler/KERNAL zero page.
; Compressed music: banks 32..44; dictionary/read-ahead: bank 31 A000..AFFF.
; Resident PCM effects: banks 19..30 then 51..57. Decompression runs in bounded main-thread batches.
.section .text.lab,"ax",@progbits
.globl lab_install,lab_uninstall,pcm_start,pcm_flipper_start,pcm_plunger_start,pcm_stop,music_start,music_stop,lab_clock
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
 stz pcm_underruns
 stz pcm_underruns+1
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
 stz pcm_flipper_remaining
 stz pcm_flipper_remaining+1
 stz pcm_plunger_remaining
 stz pcm_plunger_remaining+1
 stz pcm_started
 stz pcm_fresh
 plp
 rts
; Independent table, flipper and plunger voices. Starting one never resets
; the shared FIFO or touches another voice's read cursor.
pcm_start:
 php
 sei
 ldy #0
 bra pcm_voice_start
pcm_flipper_start:
 php
 sei
 ldy #6
 bra pcm_voice_start
pcm_plunger_start:
 php
 sei
 ldy #12
pcm_voice_start:
 sta pcm_new_length
 stx pcm_new_length+1
 lda pcm_remaining
 ora pcm_remaining+1
 ora pcm_flipper_remaining
 ora pcm_flipper_remaining+1
 ora pcm_plunger_remaining
 ora pcm_plunger_remaining+1
 bne 1f
 ; A finished source may still have a FIFO tail. Preserve normal pacing
 ; when that tail survives; an already-empty idle transition is not starvation.
 lda #1
 sta pcm_fresh
1:
 lda pcm_new_length
 sta pcm_voices,y
 lda pcm_new_length+1
 sta pcm_voices+1,y
 lda pcm_select_bank
 sta pcm_voices+2,y
 lda pcm_select_ptr
 sta pcm_voices+3,y
 lda pcm_select_ptr+1
 sta pcm_voices+4,y
 plp
 rts
music_start:
 php
 sei
 jsr music_stop
 jsr music_reset
 stz music_delay
 stz music_phase
 ; State 2 requests bounded main-thread priming. Do not decode 2048 bytes
 ; while IRQs are masked: that froze physics/input on every M-key restart.
 lda #2
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
 ora pcm_flipper_remaining
 ora pcm_flipper_remaining+1
 ora pcm_plunger_remaining
 ora pcm_plunger_remaining+1
 bne pcm_pending
 lda $9f3b
 and #$40
 beq pcm_done
 stz $9f3c
 lda #$80
 sta $9f3b ; Mute the held final sample while idle.
 stz pcm_started
pcm_done:
 rts
pcm_pending:
 lda pcm_started
 beq pcm_prime
 lda $9f3b
 and #$40
 beq pcm_regular
 lda pcm_fresh
 bne pcm_prime
 jsr pcm_count_underrun
pcm_prime:
 ; Initial 256-byte lead is 23.14 ms, not the old ~1024-byte AFLOW lead.
 stz pcm_quota
 lda #1
 sta pcm_quota+1
 sta pcm_started
 stz pcm_phase
 stz pcm_phase+1
 lda #$05
 sta $9f3b ; Lower effects volume for the music-forward mix; preserve format and FIFO.
 bra pcm_fill
pcm_regular:
 ; rate29 * 800 * 525 / 65536 = 185 + 55840/65536 samples per VGA VBL.
 ; Carry schedules 185/186 samples and preserves a short, bounded lead.
 clc
 lda pcm_phase
 adc #$20
 sta pcm_phase
 lda pcm_phase+1
 adc #$da
 sta pcm_phase+1
 lda #185
 adc #0
 sta pcm_quota
 stz pcm_quota+1
pcm_fill:
 stz pcm_fresh
 jsr pcm_render
 ; Also catch starvation during mixing, not just before it. Initial priming
 ; intentionally begins empty and is excluded by quota's high byte.
 lda pcm_quota+1
 bne pcm_fifo_write
 lda $9f3b
 and #$40
 beq pcm_fifo_write
 jsr pcm_count_underrun
pcm_fifo_write:
 ldx #0
1:
 lda pcm_buffer,x
 sta $9f3d
 inx
 cpx pcm_quota
 bne 1b
 lda #29
 sta $9f3c
 rts
pcm_count_underrun:
 inc pcm_underruns
 bne 1f
 inc pcm_underruns+1
 bne 1f
 dec pcm_underruns
 dec pcm_underruns+1 ; Saturate rather than hide overflow.
1:
 rts
; Pure bounded mixer, also exercised directly by native exact-byte fixtures.
; pcm_quota is 1..256. Each original byte is consumed once at the common
; original rate. One voice is exact; two have 6dB headroom, three 12dB.
; Traversing one resident bank stream at a time avoids per-sample bank swaps.
.globl pcm_render,pcm_buffer,pcm_quota,pcm_underruns
pcm_render:
 lda $00
 pha
 ldx #0
 lda #0
1:
 sta pcm_buffer,x
 inx
 cpx pcm_quota
 bne 1b
 stz pcm_voice_index
 stz pcm_active_count
 ldx #0
2:
 lda pcm_voices,x
 ora pcm_voices+1,x
 beq 3f
 inc pcm_active_count
3:
 txa
 clc
 adc #6
 tax
 cpx #18
 bne 2b
 ldx #<pcm_no_shift
 ldy #>pcm_no_shift
 lda pcm_active_count
 cmp #2
 bcc 4f
 cmp #3
 beq 5f
 ldx #<pcm_one_shift
 ldy #>pcm_one_shift
 bra 4f
5:
 ldx #<pcm_two_shift
 ldy #>pcm_two_shift
4:
 stx pcm_gain_jump+1
 sty pcm_gain_jump+2
pcm_next_voice:
 ldy pcm_voice_index
 lda pcm_voices,y
 ora pcm_voices+1,y
 bne 1f
 jmp pcm_voice_done
1:
 ; count=min(remaining,quota), including the 256-byte full batch.
 lda pcm_quota
 sta pcm_count
 lda pcm_quota+1
 sta pcm_count+1
 lda pcm_voices+1,y
 cmp pcm_count+1
 bcc 2f
 bne 3f
 lda pcm_voices,y
 cmp pcm_count
 bcs 3f
2:
 lda pcm_voices,y
 sta pcm_count
 lda pcm_voices+1,y
 sta pcm_count+1
3:
 sec
 lda pcm_voices,y
 sbc pcm_count
 sta pcm_voices,y
 lda pcm_voices+1,y
 sbc pcm_count+1
 sta pcm_voices+1,y
 lda pcm_voices+2,y
 sta pcm_current_bank
 sta $00
 lda pcm_voices+4,y
 sta pcm_read+2
 lda pcm_voices+3,y
 tay
 ldx #0
pcm_read:
 ; Keep the sample offset in Y and patch the page only on wrap.
 lda $a000,y
pcm_gain_jump:
 jmp pcm_no_shift
pcm_two_shift:
 cmp #$80
 ror
pcm_one_shift:
 cmp #$80
 ror
pcm_no_shift:
 clc
 adc pcm_buffer,x
 sta pcm_buffer,x
 iny
 bne pcm_next_sample
 inc pcm_read+2
 lda pcm_read+2
 cmp #$c0
 bne pcm_next_sample
 lda #$a0
 sta pcm_read+2
 inc pcm_current_bank
 lda pcm_current_bank
 cmp #31
 bne 4f
 lda #51
 sta pcm_current_bank
4:
 sta $00
pcm_next_sample:
 inx
 cpx pcm_count
 bne pcm_read
 tya
 ldy pcm_voice_index
 sta pcm_voices+3,y
 lda pcm_current_bank
 sta pcm_voices+2,y
 lda pcm_read+2
 sta pcm_voices+4,y
pcm_voice_done:
 lda pcm_voice_index
 clc
 adc #6
 sta pcm_voice_index
 cmp #18
 beq 1f
 jmp pcm_next_voice
1:
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
 cmp #1
 beq 1f
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
 lda #31
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
 ; Start the next loop on the next video tick.
 lda #1
 sta music_delay
music_return:
 jsr restore_address
 pla
 sta $00
 rts
.include "cadet/game/music_lz.s.inc"
.section .bss.lab,"aw",@nobits
.globl pcm_remaining,music_enabled,music_loops,lab_ticks,music_error,irq_max,fm_writes,psg_writes
old_irq: .zero 2
lab_ticks: .zero 2
saved_ctrl: .zero 1
saved_addr: .zero 3
saved_psg: .zero 64
.globl pcm_flipper_remaining,pcm_plunger_remaining
pcm_voices:
pcm_remaining: .zero 2
.zero 4
pcm_flipper_remaining: .zero 2
.zero 4
pcm_plunger_remaining: .zero 2
.zero 4
pcm_new_length: .zero 2
pcm_count: .zero 2
pcm_current_bank: .zero 1
pcm_voice_index: .zero 1
pcm_active_count: .zero 1
pcm_quota: .zero 2
pcm_phase: .zero 2
pcm_started: .zero 1
pcm_fresh: .zero 1
pcm_underruns: .zero 2
pcm_buffer: .zero 256
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

lz_flags: .zero 1
lz_left: .zero 1
lz_run: .zero 1
lz_low: .zero 1
lz_high: .zero 1
music_buffered: .zero 2
lz_remaining: .zero 3
