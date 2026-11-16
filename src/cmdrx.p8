%encoding iso
%zeropage basicsafe
%import syslib
%import textio
%import score
%import geometry
%import physics
%import video
%import storage
%import controls
%import sound
%import session
main {
    bool was_new=false
    bool was_pause=false
    bool was_sound=false
    bool was_music=false
    bool was_listen=false
    bool stop=false
    bool status_dirty=true
    ubyte last_mode=255
    sub start() {
        ubyte keys
        video.init()
        if video.error {
            cbm.CINT()
            txt.print("CmdrX Cadet: missing or unreadable game assets.\n")
            return
        }
        sound.init()
        storage.load()
        show_best()
        score.clear()
        physics.new_game()
        session.mode=session.ATTRACT
        controls.install()
        while not stop {
            sys.waitvsync()
            stop=controls.raw[$6e]!=0
            keys=controls.state()
            if controls.raw[$33]!=0 and not was_new or session.mode==session.ATTRACT and keys & 4 !=0 {
                if session.mode==session.PLAY { storage.observe() storage.save() }
                session.play()
                show_best()
                status_dirty=true
            }
            was_new=controls.raw[$33]!=0
            if controls.raw[$27]!=0 and not was_listen {
                session.listen()
                if session.mode==session.LISTEN { sound.fx_remaining=0 sound.music_on=true }
                status_dirty=true
            }
            was_listen=controls.raw[$27]!=0
            if controls.raw[$20]!=0 and not was_sound {
                sound.effects_on=not sound.effects_on
                status_dirty=true
            }
            was_sound=controls.raw[$20]!=0
            if controls.raw[$34]!=0 and not was_music {
                sound.music_on=not sound.music_on
                status_dirty=true
            }
            was_music=controls.raw[$34]!=0
            if controls.raw[$1a]!=0 and not was_pause { physics.paused=not physics.paused }
            was_pause=controls.raw[$1a]!=0
            keys=session.input(keys)
            if session.mode!=session.LISTEN {
                physics.frame(keys)
                sound.tick()
                if physics.awarded!=0 {
                    score.add16(physics.awarded)
                    if session.mode==session.PLAY { storage.observe() }
                }
            } else { sound.service() }
            video.objects()
            video.counters()
            video.present_score()
            if session.mode!=last_mode { status_dirty=true last_mode=session.mode }
            if status_dirty { video.status(session.mode,sound.music_on,sound.effects_on) status_dirty=false }
            if physics.lives==0 and session.mode==session.PLAY { storage.save() }
        }
        if session.mode==session.PLAY or session.mode==session.LISTEN and session.previous==session.PLAY { storage.observe() }
        storage.save()
        controls.remove()
        sound.quiet()
        cbm.CINT()
        txt.print("CmdrX Cadet 0.2\n")
        if storage.failed { txt.print("High score could not be saved.\n") }
    }
    sub show_best() {
        ubyte[16] saved
        ubyte i
        for i in 0 to 15 { saved[i]=score.total[i] score.total[i]=storage.best[i] }
        score.format()
        video.decimal(104)
        for i in 0 to 15 { score.total[i]=saved[i] }
        score.dirty=true
    }
}
