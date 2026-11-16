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
main {
    bool was_new=false
    bool was_pause=false
    bool stop=false
    sub start() {
        ubyte keys
        video.init()
        if video.error {
            cbm.CINT()
            txt.print("CmdrX Cadet: missing TABLE.BIN, PALETTE.BIN or SPRITES.BIN.\n")
            return
        }
        sound.quiet()
        storage.load()
        show_best()
        score.clear()
        score.format()
        video.decimal(44)
        physics.new_game()
        controls.install()
        while not stop {
            sys.waitvsync()
            stop=controls.raw[$6e]!=0
            if controls.raw[$33]!=0 and not was_new {
                storage.observe()
                storage.save()
                score.clear()
                physics.new_game()
                show_best()
            }
            was_new=controls.raw[$33]!=0
            if controls.raw[$1a]!=0 and not was_pause { physics.paused=not physics.paused }
            was_pause=controls.raw[$1a]!=0
            keys=controls.state()
            physics.frame(keys)
            sound.tick()
            if physics.awarded!=0 {
                score.add16(physics.awarded)
                storage.observe()
            }
            video.objects()
            video.counters()
            video.present_score()
            if physics.lives==0 { storage.save() }
        }
        storage.observe()
        storage.save()
        controls.remove()
        sound.quiet()
        cbm.CINT()
        txt.print("CmdrX Cadet prototype 0.1\n")
        if storage.failed { txt.print("High score could not be saved.\n") }
    }
    sub show_best() {
        ubyte[16] saved
        ubyte i
        for i in 0 to 15 { saved[i]=score.total[i] score.total[i]=storage.best[i] }
        score.format()
        video.decimal(88)
        for i in 0 to 15 { score.total[i]=saved[i] }
        score.dirty=true
    }
}
