%encoding iso
%import syslib
; Binary 128-bit unsigned score. Decimal text has 40 digits plus NUL.
; Overflow saturates, never wraps. All byte arrays are little endian.
score {
    ubyte[16] total
    ubyte[16] award
    ubyte[16] temp
    ubyte[20] bcd
    str text = "0000000000000000000000000000000000000000"
    bool saturated = false
    bool dirty = true
    ubyte bits,budget
    bool busy=false
    sub clear() {
        ubyte i
        for i in 0 to 15 { total[i]=0 award[i]=0 }
        saturated=false
        dirty=true
    }
    sub add16(uword points) {
        ubyte i
        for i in 0 to 15 { award[i]=0 }
        award[0]=lsb(points)
        award[1]=msb(points)
        add()
    }
    asmsub add() clobbers(A,X,Y) {
        %asm {{
            php
            cld
            clc
            ldx #0
            ldy #16
_loop:
            lda p8b_score.p8v_total,x
            adc p8b_score.p8v_award,x
            sta p8b_score.p8v_total,x
            inx
            dey
            bne _loop
            bcc _done
            lda #1
            sta p8b_score.p8v_saturated
            lda #255
            ldx #15
_sat:
            sta p8b_score.p8v_total,x
            dex
            bpl _sat
_done:
            lda #1
            sta p8b_score.p8v_dirty
            plp
            rts
        }}
    }
    ; Binary-to-packed-BCD via decimal carry. Each decimal section is atomic;
    ; no generic compiler runtime executes while the decimal flag is set.
    sub format() {
        begin_format()
        while busy { format_step() }
    }
    asmsub begin_format() clobbers(A,X,Y) {
        %asm {{
            php
            sei
            cld
            ldx #15
_copy:
            lda p8b_score.p8v_total,x
            sta p8b_score.p8v_temp,x
            dex
            bpl _copy
            ldx #19
            lda #0
_zero:
            sta p8b_score.p8v_bcd,x
            dex
            bpl _zero
            lda #128
            sta p8b_score.p8v_bits
            lda #1
            sta p8b_score.p8v_busy
            stz p8b_score.p8v_dirty
            plp
            rts
        }}
    }
    asmsub format_step() clobbers(A,X,Y) {
        %asm {{
            php
            sei
            cld
            lda #64
            sta p8b_score.p8v_budget

_bit:
            asl p8b_score.p8v_temp
            rol p8b_score.p8v_temp+1
            rol p8b_score.p8v_temp+2
            rol p8b_score.p8v_temp+3
            rol p8b_score.p8v_temp+4
            rol p8b_score.p8v_temp+5
            rol p8b_score.p8v_temp+6
            rol p8b_score.p8v_temp+7
            rol p8b_score.p8v_temp+8
            rol p8b_score.p8v_temp+9
            rol p8b_score.p8v_temp+10
            rol p8b_score.p8v_temp+11
            rol p8b_score.p8v_temp+12
            rol p8b_score.p8v_temp+13
            rol p8b_score.p8v_temp+14
            rol p8b_score.p8v_temp+15
            sed
            lda p8b_score.p8v_bcd+0
            adc p8b_score.p8v_bcd+0
            sta p8b_score.p8v_bcd+0
            lda p8b_score.p8v_bcd+1
            adc p8b_score.p8v_bcd+1
            sta p8b_score.p8v_bcd+1
            lda p8b_score.p8v_bcd+2
            adc p8b_score.p8v_bcd+2
            sta p8b_score.p8v_bcd+2
            lda p8b_score.p8v_bcd+3
            adc p8b_score.p8v_bcd+3
            sta p8b_score.p8v_bcd+3
            lda p8b_score.p8v_bcd+4
            adc p8b_score.p8v_bcd+4
            sta p8b_score.p8v_bcd+4
            lda p8b_score.p8v_bcd+5
            adc p8b_score.p8v_bcd+5
            sta p8b_score.p8v_bcd+5
            lda p8b_score.p8v_bcd+6
            adc p8b_score.p8v_bcd+6
            sta p8b_score.p8v_bcd+6
            lda p8b_score.p8v_bcd+7
            adc p8b_score.p8v_bcd+7
            sta p8b_score.p8v_bcd+7
            lda p8b_score.p8v_bcd+8
            adc p8b_score.p8v_bcd+8
            sta p8b_score.p8v_bcd+8
            lda p8b_score.p8v_bcd+9
            adc p8b_score.p8v_bcd+9
            sta p8b_score.p8v_bcd+9
            lda p8b_score.p8v_bcd+10
            adc p8b_score.p8v_bcd+10
            sta p8b_score.p8v_bcd+10
            lda p8b_score.p8v_bcd+11
            adc p8b_score.p8v_bcd+11
            sta p8b_score.p8v_bcd+11
            lda p8b_score.p8v_bcd+12
            adc p8b_score.p8v_bcd+12
            sta p8b_score.p8v_bcd+12
            lda p8b_score.p8v_bcd+13
            adc p8b_score.p8v_bcd+13
            sta p8b_score.p8v_bcd+13
            lda p8b_score.p8v_bcd+14
            adc p8b_score.p8v_bcd+14
            sta p8b_score.p8v_bcd+14
            lda p8b_score.p8v_bcd+15
            adc p8b_score.p8v_bcd+15
            sta p8b_score.p8v_bcd+15
            lda p8b_score.p8v_bcd+16
            adc p8b_score.p8v_bcd+16
            sta p8b_score.p8v_bcd+16
            lda p8b_score.p8v_bcd+17
            adc p8b_score.p8v_bcd+17
            sta p8b_score.p8v_bcd+17
            lda p8b_score.p8v_bcd+18
            adc p8b_score.p8v_bcd+18
            sta p8b_score.p8v_bcd+18
            lda p8b_score.p8v_bcd+19
            adc p8b_score.p8v_bcd+19
            sta p8b_score.p8v_bcd+19
            cld
            dec p8b_score.p8v_bits
            beq _converted
            dec p8b_score.p8v_budget
            bne +
            plp
            rts
+           jmp _bit
_converted:
            ldy #19
            ldx #0
_digits:
            lda p8b_score.p8v_bcd,y
            pha
            lsr a
            lsr a
            lsr a
            lsr a
            ora #48
            sta p8b_score.p8v_text,x
            inx
            pla
            and #15
            ora #48
            sta p8b_score.p8v_text,x
            inx
            dey
            bpl _digits
            stz p8b_score.p8v_text+40
            stz p8b_score.p8v_busy
            plp
            rts
        }}
    }
    sub greater(pointer other) -> bool {
        ubyte i
        for i in 15 downto 0 {
            if total[i] > other[i] { return true }
            if total[i] < other[i] { return false }
        }
        return false
    }
}
