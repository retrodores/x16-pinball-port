%encoding iso
%import syslib
%import audio_assets
sound {
    bool effects_on=true
    bool music_on=true
    bool ready=false
    bool music_open=false
    bool failed=false
    bool slow_io=false
    ubyte last_state=0
    ubyte last_lives=3
    ubyte fx_bank=16
    uword fx_pointer=$a000
    uword fx_remaining=0
    uword music_pos=512
    uword read_count=0
    pointer music_buffer=memory("music-buffer",512,256)
    sub init() {
        ubyte saved=@($00)
        cbm.SETNAM(7,"SFX.BIN")
        cbm.SETLFS(1,8,2)
        @($00)=16
        void cbm.LOAD(0,$a000)
        ready=true
        if_cs { ready=false }
        @($00)=saved
        cx16.VERA_AUDIO_RATE=0
        cx16.VERA_AUDIO_CTRL=$8c
        music_pos=512
        failed=false
    }
    sub quiet() {
        cx16.VERA_AUDIO_RATE=0
        cx16.VERA_AUDIO_CTRL=$8c
        fx_remaining=0
        close_music()
    }
    sub close_music() {
        if music_open { cbm.CLRCHN() cbm.CLOSE(3) music_open=false }
        music_pos=512
    }
    sub effect(ubyte number) {
        if not effects_on or not ready { return }
        fx_bank=audio_assets.bank[number]
        fx_pointer=audio_assets.address[number]
        fx_remaining=audio_assets.length[number]
    }
    sub open_music() {
        cbm.SETNAM(9,"MUSIC.PCM")
        cbm.SETLFS(3,8,2)
        void cbm.OPEN()
        if_cs { failed=true cbm.CLOSE(3) return }
        music_open=true
        music_pos=512
    }
    asmsub readblock(ubyte count @A,pointer buffer @XY) clobbers(A) -> uword @XY {
        %asm {{
            clc
            jsr $ff44
            bcc _done
            lda #1
            sta p8b_sound.p8v_slow_io
            ldx #0
            ldy #0
_done:
            rts
        }}
    }
    sub refill() {
        uword i
        sys.memset(music_buffer,512,0)
        if not music_on { music_pos=0 return }
        if not music_open { open_music() }
        if not music_open { music_pos=0 return }
        void cbm.CHKIN(3)
        read_count=0
        while read_count<512 {
            uword left=512-read_count
            ubyte request=255
            if left<255 { request=left as ubyte }
            uword received=readblock(request,music_buffer+read_count)
            if slow_io {
                if cbm.READST()!=0 { break }
                @(music_buffer+read_count)=cbm.CHRIN()
                received=1
            }
            read_count+=received
            if received==0 or cbm.READST()!=0 { break }
        }
        ubyte status=cbm.READST()
        cbm.CLRCHN()
        if status!=0 or read_count==0 {
            cbm.CLOSE(3)
            music_open=false
        }
        music_pos=0
    }
    sub tick() {
        if not effects_on { fx_remaining=0 }
        if effects_on {
            if physics.left_angle>0 and physics.prior_left==0 or physics.right_angle>0 and physics.prior_right==0 { effect(0) }
            if physics.left_angle<7 and physics.prior_left==7 or physics.right_angle<7 and physics.prior_right==7 { effect(1) }
            if physics.wall_events!=0 and fx_remaining==0 { effect(6) }
            if physics.awarded>=100 { effect(2) }
            if physics.charge==1 and physics.state==0 { effect(4) }
            if last_state==0 and physics.state==1 { effect(3) }
            if physics.lives<last_lives { effect(5) }
        }
        last_state=physics.state
        last_lives=physics.lives
        service()
    }
    sub service() {
        if not effects_on { fx_remaining=0 }
        if not music_on and music_open { close_music() }
        if not music_on and fx_remaining==0 {
            cx16.VERA_AUDIO_RATE=0
            cx16.VERA_AUDIO_CTRL=$8c
            return
        }
        ; AFLOW reports less than 1024 bytes queued. Feed 256 per service.
        if cx16.VERA_ISR & 8 == 0 { return }
        if music_pos>=512 { refill() }
        pump(music_buffer+music_pos)
        music_pos+=256
        cx16.VERA_AUDIO_RATE=21
    }
    asmsub pump(pointer music @R0) clobbers(A,X,Y) {
        %asm {{
            php
            sei
            lda $00
            pha
            lda p8b_sound.p8v_fx_bank
            sta $00
            lda p8b_sound.p8v_fx_pointer
            sta cx16.r1
            lda p8b_sound.p8v_fx_pointer+1
            sta cx16.r1+1
            ldy #0
            ldx #0
_loop:
            lda #0
            sta cx16.r2L
            lda p8b_sound.p8v_music_on
            beq _fx
            lda (cx16.r0),y
            sta cx16.r2L
_fx:
            lda p8b_sound.p8v_fx_remaining
            ora p8b_sound.p8v_fx_remaining+1
            beq _music
            lda (cx16.r1),y
            sta cx16.r2H
            lda p8b_sound.p8v_music_on
            beq _fxalone
            lda cx16.r2L
            eor #128
            sta cx16.r2L
            lda cx16.r2H
            eor #128
            clc
            adc cx16.r2L
            ror a
            eor #128
            bra _writefx
_fxalone:
            lda cx16.r2H
_writefx:
            sta $9f3d
            lda p8b_sound.p8v_fx_remaining
            bne +
            dec p8b_sound.p8v_fx_remaining+1
+           dec p8b_sound.p8v_fx_remaining
            inc cx16.r1
            bne +
            inc cx16.r1+1
            lda cx16.r1+1
            cmp #$c0
            bne +
            lda #$a0
            sta cx16.r1+1
            inc $00
+           bra _next
_music:
            lda cx16.r2L
            sta $9f3d
_next:
            inc cx16.r0
            bne +
            inc cx16.r0+1
+           inx
            beq _done
            jmp _loop
_done:
            lda cx16.r1
            sta p8b_sound.p8v_fx_pointer
            lda cx16.r1+1
            sta p8b_sound.p8v_fx_pointer+1
            lda $00
            sta p8b_sound.p8v_fx_bank
            pla
            sta $00
            plp
            rts
        }}
    }
}
