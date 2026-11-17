; Experimental native 65816 kernel. Entry/exit: emulation mode, D=0, DBR=0,
; DP=0 and page-1 stack, LLVM-MOS caller-saved rc2..rc15. IRQ remains enabled
; as supplied by caller; requires the R47+ native interrupt trampoline.
.zeropage __rc2,__rc3,__rc4,__rc5,__rc6,__rc7,__rc8,__rc9
.zeropage __rc10,__rc11,__rc12,__rc13,__rc14,__rc15
.section .text.fastmul16,"ax",@progbits
.globl fastmul16
fastmul16:
 sta __rc4
 stx __rc5
 php
 clc
 xce
 rep #$30
 lda __rc2
 sta __rc6
 and #mos16($00ff)
 sta __rc8
 lda __rc4
 and #mos16($00ff)
 jsr fm816_byte
 sta __rc14
 lda __rc4
 xba
 and #mos16($00ff)
 jsr fm816_byte
 sta __rc2
 lda __rc6
 xba
 and #mos16($00ff)
 sta __rc8
 lda __rc4
 and #mos16($00ff)
 jsr fm816_byte
 clc
 adc __rc2
 sta __rc2
 lda #mos16(0)
 rol
 pha
 lda __rc4
 xba
 and #mos16($00ff)
 jsr fm816_byte
 sta __rc6
 lda __rc2
 xba
 and #mos16($ff00)
 clc
 adc __rc14
 sta __rc14
 lda __rc2
 xba
 and #mos16($00ff)
 adc __rc6
 sta __rc2
 pla
 xba
 clc
 adc __rc2
 sta __rc2
 sep #$30
 sec
 xce
 plp
 lda __rc14
 ldx __rc15
 rts
fm816_byte:
 cmp #mos16(0)
 beq fm816_zero
 ldx __rc8
 beq fm816_zero
 sta __rc10
 clc
 adc __rc8
 asl
 tax
 lda fm816_sq,x
 sta __rc12
 lda __rc10
 sec
 sbc __rc8
 bcs fm816_positive
 eor #mos16($ffff)
 inc
fm816_positive:
 asl
 tax
 lda __rc12
 sec
 sbc fm816_sq,x
 rts
fm816_zero:
 lda #mos16(0)
 rts
.section .rodata.fastmul,"a",@progbits
.p2align 8
fm816_sq:
.include "direct/integer/cpu816/squares.inc"
