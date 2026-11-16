%encoding iso
%import syslib
boundaries {
    bool ready=false
    byte[16] nx=[2,2,1,1,0,-1,-1,-2,-2,-2,-1,-1,0,1,1,2]
    byte[16] ny=[0,1,1,2,2,2,1,1,0,-1,-1,-2,-2,-2,-1,-1]
    sub load() {
        ubyte saved=@($00)
        ready=false
        cbm.SETNAM(9,"WALLS.BIN")
        cbm.SETLFS(1,8,2)
        @($00)=8
        void cbm.LOAD(0,$a000)
        if_cc { ready=true }
        @($00)=saved
    }
    sub at(word x,word y) -> ubyte {
        if not ready or x<0 or x>=192 or y<0 or y>=224 { return 0 }
        return fetch(((y as uword)*192)+(x as uword))
    }
    asmsub fetch(uword offset @R0) clobbers(X,Y) -> ubyte @A {
        %asm {{
            php
            sei
            lda $00
            pha
            lda cx16.r0+1
            lsr a
            lsr a
            lsr a
            lsr a
            lsr a
            clc
            adc #8
            sta $00
            lda cx16.r0+1
            and #31
            ora #$a0
            sta cx16.r0+1
            ldy #0
            lda (cx16.r0),y
            tax
            pla
            sta $00
            txa
            plp
            rts
        }}
    }
}
