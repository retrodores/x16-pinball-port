%encoding iso
%import syslib
%import sprites
%import glyphs
video {
    bool error=false
    sub load(str filename,ubyte length,ubyte bank,uword address) {
        cbm.SETNAM(length,filename)
        cbm.SETLFS(1,8,2)
        void cbm.LOAD(bank+2,address)
        if_cs { error=true }
    }
    sub init() {
        ubyte i
        cbm.SETMSG(0)
        cx16.VERA_DC_VIDEO=1
        error=false
        load("TABLE.BIN",9,0,0)
        if error { return }
        load("PALETTE.BIN",11,1,$fa00)
        if error { return }
        load("SPRITES.BIN",11,1,$3000)
        if error { return }
        sys.set_irqd()
        cx16.VERA_CTRL=0
        cx16.VERA_DC_HSCALE=64
        cx16.VERA_DC_VSCALE=64
        cx16.VERA_DC_BORDER=0
        cx16.VERA_L0_CONFIG=7
        cx16.VERA_L0_MAPBASE=0
        cx16.VERA_L0_TILEBASE=0
        cx16.VERA_L0_HSCROLL=0
        cx16.VERA_L0_VSCROLL=0
        sprites.reset(0,128)
        sprites.init(0,geometry.BALL_BANK as ubyte,geometry.BALL_ADDR,0,0,128,0)
        sprites.init(1,1,$3000,2,2,128,0)
        sprites.init(2,1,$5000,2,2,128,0)
        for i in 0 to 6 {
            sprites.init(i+3,1,$7000+(i as uword)*2048,2,2,128,0)
            sprites.pos(i+3,geometry.bax[i] as word,geometry.bay[i] as word)
        }
        sprites.pos(1,geometry.lax as word,geometry.lay as word)
        sprites.pos(2,geometry.rax as word,geometry.ray as word)
        cx16.VERA_DC_VIDEO=$51
        sys.clear_irqd()
    }
    sub objects() {
        ubyte i
        sys.set_irqd()
        if physics.lives!=0 {
            sprites.pos(0,((physics.x>>8) as word)-2,((physics.y>>8) as word)-2)
        } else { sprites.pos(0,-16,-16) }
        sprites.data(1,1,$3000+(physics.left_angle as uword)*1024)
        sprites.data(2,1,$5000+(physics.right_angle as uword)*1024)
        for i in 0 to 6 {
            uword address=$7000+(i as uword)*2048
            if physics.bumper_flash!=0 and physics.hit_bumper==i { address+=1024 }
            sprites.data(i+3,1,address)
        }
        sys.clear_irqd()
    }
    uword @shared glyph_address
    ubyte @shared glyph_number,glyph_index,glyph_bits,glyph_count
    sub digit(ubyte number,uword x,ubyte y) {
        glyph_address=((y as uword)*320)+x
        glyph_number=number
        blit(&glyphs.rows)
    }
    asmsub blit(pointer font @R0) clobbers(A,X,Y) {
        %asm {{
            lda p8b_video.p8v_glyph_number
            asl a
            asl a
            asl a
            sec
            sbc p8b_video.p8v_glyph_number
            sta p8b_video.p8v_glyph_index
            lda #7
            sta p8b_video.p8v_glyph_count
_row:
            stz $9f25
            lda #$10
            sta $9f22
            lda p8b_video.p8v_glyph_address
            sta $9f20
            lda p8b_video.p8v_glyph_address+1
            sta $9f21
            lda p8b_video.p8v_glyph_number
            cmp #10
            bcs _blank
            ldy p8b_video.p8v_glyph_index
            lda (cx16.r0),y
            bra _got
_blank:
            lda #0
_got:
            asl a
            asl a
            asl a
            sta p8b_video.p8v_glyph_bits
            asl p8b_video.p8v_glyph_bits
            lda #0
            bcc +
            lda #255
+           sta $9f23
            asl p8b_video.p8v_glyph_bits
            lda #0
            bcc +
            lda #255
+           sta $9f23
            asl p8b_video.p8v_glyph_bits
            lda #0
            bcc +
            lda #255
+           sta $9f23
            asl p8b_video.p8v_glyph_bits
            lda #0
            bcc +
            lda #255
+           sta $9f23
            asl p8b_video.p8v_glyph_bits
            lda #0
            bcc +
            lda #255
+           sta $9f23
            stz $9f23
            clc
            lda p8b_video.p8v_glyph_address
            adc #64
            sta p8b_video.p8v_glyph_address
            lda p8b_video.p8v_glyph_address+1
            adc #1
            sta p8b_video.p8v_glyph_address+1
            inc p8b_video.p8v_glyph_index
            dec p8b_video.p8v_glyph_count
            beq _done
            jmp _row
_done:
            rts
        }}
    }
    sub decimal(ubyte y) {
        ubyte start=0
        ubyte col,row,c
        while start<39 and score.text[start]=='0' { start++ }
        sys.set_irqd()
        for row in 0 to 2 {
            for col in 0 to 12 {
                c=10
                if start<40 { c=score.text[start]-48 start++ }
                digit(c,204+(col as uword)*6,y+row*9)
            }
        }
        sys.clear_irqd()
    }
    str latest="0000000000000000000000000000000000000000"
    str active="0000000000000000000000000000000000000000"
    bool latest_pending=false
    ubyte remaining=0
    ubyte active_start=0
    ubyte active_row=0
    sub request_score() {
        sys.memcopy(score.text,latest,40)
        latest_pending=true
    }
    sub score_row() {
        ubyte col,c
        if remaining==0 {
            if not latest_pending { return }
            sys.memcopy(latest,active,40)
            active_start=0
            while active_start<39 and active[active_start]=='0' { active_start++ }
            remaining=3
            active_row=0
            latest_pending=false
        }
        sys.set_irqd()
        for col in 0 to 12 {
            c=10
            if active_start<40 { c=active[active_start]-48 active_start++ }
            digit(c,204+(col as uword)*6,44+active_row*9)
        }
        sys.clear_irqd()
        active_row++
        remaining--
    }
    ; Conversion and pixel drawing occupy separate simulation frames. A pending
    ; presentation is immutable; new score events queue the next complete value.
    sub present_score() {
        if score.dirty and remaining==0 and not latest_pending {
            score.format()
            request_score()
        } else {
            score_row()
        }
    }
    sub counters() {
        sys.set_irqd()
        digit(physics.lives,204,133)
        if physics.paused { digit(1,228,133) } else { digit(10,228,133) }
        digit(physics.charge/10,246,133)
        digit(physics.charge % 10,252,133)
        sys.clear_irqd()
    }
}
