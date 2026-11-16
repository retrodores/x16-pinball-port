%encoding iso
%import score
%import boundaries
%import physics
%import video
%import storage
%import sound
%import emudbg
%import tap
%import textio
main {
    sub bench(word x,word y,word vx,word vy,ubyte keys,str name) {
        physics.new_game()
        physics.state=2
        physics.x=(x as long)*256
        physics.y=(y as long)*256
        physics.vx=vx
        physics.vy=vy
        video.remaining=0
        video.latest_pending=false
        score.clear()
        score.busy=false
        sys.memset(&score.total,16,255)
        cx16.VERA_AUDIO_CTRL=$8c
        sound.music_pos=512
        emudbg.reset_cpu_cycles()
        physics.frame(keys)
        if physics.awarded!=0 {
            score.add16(physics.awarded)
            storage.observe()
        }
        sound.tick()
        video.objects()
        video.counters()
        video.present_score()
        long cycles=emudbg.cpu_cycles()
        tap.say("# ") tap.say(name) tap.say(" cycles: ") txt.print_l(cycles) txt.nl()
        tap.ok(cycles<133333,name)
        ; Same physical setup, but finish the second conversion slice this frame.
        physics.new_game()
        physics.state=2
        physics.x=(x as long)*256
        physics.y=(y as long)*256
        physics.vx=vx
        physics.vy=vy
        cx16.VERA_AUDIO_CTRL=$8c
        sound.music_pos=512
        emudbg.reset_cpu_cycles()
        physics.frame(keys)
        if physics.awarded!=0 { score.add16(physics.awarded) storage.observe() }
        sound.tick()
        video.objects()
        video.counters()
        video.present_score()
        cycles=emudbg.cpu_cycles()
        tap.say("# second-conversion-phase ") tap.say(name) tap.say(" cycles: ") txt.print_l(cycles) txt.nl()
        tap.ok(cycles<133333,"queued presentation step and physics fit the next frame")
    }
    sub start() {
        boundaries.load()
        sound.init()
        sound.open_music()
        bench(99,58,0,200,3,"bumper contact plus maximum score")
        bench(83,198,0,200,0,"left flipper contact plus maximum score")
        bench(116,198,0,200,0,"right flipper contact plus maximum score")
        bench(84,190,0,100,1,"moving left flipper plus maximum score")
        bench(115,190,0,100,2,"moving right flipper plus maximum score")
        bench(100,150,384,448,3,"fast free flight plus maximum score")
        tap.done()
    }
}
