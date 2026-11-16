%encoding iso
%import syslib
controls {
    ubyte[128] @shared raw
    uword saved_handler
    sub install() {
        ubyte i
        for i in 0 to 127 { raw[i]=0 }
        sys.set_irqd()
        saved_handler=cx16.KEYHDL
        cx16.KEYHDL=&key
        sys.clear_irqd()
    }
    sub remove() {
        sys.set_irqd()
        cx16.KEYHDL=saved_handler
        sys.clear_irqd()
    }
    sub state() -> ubyte {
        ubyte bits=0
        if raw[$2c]!=0 or raw[$2e]!=0 { bits|=1 }
        if raw[$39]!=0 or raw[$37]!=0 { bits|=2 }
        if raw[$3d]!=0 { bits|=4 }
        return bits
    }
    ; IRQ callback: only absolute array writes, no compiler temporaries or I/O.
    asmsub key(ubyte code @A) clobbers(X) -> ubyte @A {
        %asm {{
            phx
            pha
            and #127
            tax
            pla
            bmi _up
            lda #1
            bra _store
_up:
            lda #0
_store:
            sta p8b_controls.p8v_raw,x
            plx
            lda #0
            rts
        }}
    }
}
