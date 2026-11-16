%encoding iso
%import syslib
sound {
    ubyte timer=0
    ubyte last_state=0
    ubyte last_lives=3
    uword frequency=0
    sub quiet() {
        timer=0
        cx16.vpoke(1,$f9c2,0)
    }
    sub tick() {
        if physics.awarded!=0 { frequency=2600 timer=6 }
        if last_state==0 and physics.state==1 { frequency=1600 timer=8 }
        if physics.lives<last_lives { frequency=500 timer=16 }
        last_state=physics.state
        last_lives=physics.lives
        sys.set_irqd()
        if timer!=0 {
            timer--
            cx16.vpoke(1,$f9c0,lsb(frequency))
            cx16.vpoke(1,$f9c1,msb(frequency))
            cx16.vpoke(1,$f9c2,192+timer*2)
            cx16.vpoke(1,$f9c3,128)
        } else {
            cx16.vpoke(1,$f9c2,0)
        }
        sys.clear_irqd()
    }
}
