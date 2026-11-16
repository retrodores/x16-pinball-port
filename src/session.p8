%encoding iso
session {
    const ubyte ATTRACT=0
    const ubyte PLAY=1
    const ubyte LISTEN=2
    ubyte mode=ATTRACT
    ubyte previous=ATTRACT
    uword idle=0
    ubyte demo_charge=0
    ubyte demo_blink=0
    ubyte lamp=0
    sub play() {
        mode=PLAY
        idle=0
        score.clear()
        physics.new_game()
        video.remaining=0
        video.latest_pending=false
    }
    sub listen() {
        if mode==LISTEN { mode=previous }
        else { previous=mode mode=LISTEN }
    }
    sub input(ubyte manual) -> ubyte {
        if mode==LISTEN { return 0 }
        if mode==PLAY {
            if manual!=0 { idle=0 }
            else {
                if physics.state==0 or physics.lives==0 { idle++ }
            }
            if idle<1800 { return manual }
            mode=ATTRACT
            score.clear()
            physics.new_game()
        }
        demo_blink++
        if demo_blink>=12 { demo_blink=0 lamp++ if lamp>=7 { lamp=0 } }
        if physics.lives==0 { physics.new_game() score.clear() }
        if physics.state==0 {
            if demo_charge<64 { demo_charge++ return 4 }
            demo_charge=0
            return 0
        }
        demo_charge=0
        ubyte keys=0
        if physics.y>170*256 {
            if physics.x<104*256 { keys|=1 }
            if physics.x>96*256 { keys|=2 }
        }
        return keys
    }
}
