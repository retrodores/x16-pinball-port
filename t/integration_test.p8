%encoding iso
%import syslib
%import controls
%import video
%import physics
%import score
%import storage
%import tap
main {
    sub start() {
        uword original=cx16.KEYHDL
        controls.install()
        tap.ok(cx16.KEYHDL==&controls.key,"raw keyboard handler installed")
        void controls.key($2e)
        void controls.key($37)
        tap.ok(controls.state()==3,"both flippers can be held")
        void controls.key($2c)
        void controls.key($ae)
        tap.ok(controls.state()==3,"releasing one alias preserves another held key")
        void controls.key($ac)
        void controls.key($b7)
        tap.ok(controls.state()==0,"release events clear both flippers")
        void controls.key($3d)
        tap.ok(controls.state()==4,"space held is reported")
        void controls.key($bd)
        tap.ok(controls.state()==0,"space release is reported")
        controls.remove()
        tap.ok(cx16.KEYHDL==original,"original keyboard handler restored")
        video.init()
        tap.ok(not video.error,"all native VERA assets load from HostFS")
        tap.ok(cx16.VERA_DC_HSCALE==64 and cx16.VERA_DC_VSCALE==64,"320x240 integer scaling configured")
        tap.ok(cx16.vpeek(1,$fc08)==$80 and cx16.vpeek(1,$fc09)==$89,"left flipper points to converted sprite data")
        tap.ok(cx16.vpeek(1,$3000+322)==57 and cx16.vpeek(1,$3000+323)==191,"sprite data resident in VERA")
        score.clear()
        sys.memset(&score.total,16,255)
        score.format()
        video.request_score()
        repeat 3 { video.score_row() }
        tap.ok(video.active_start==40 and video.remaining==0,"maximum score display consumes every digit")
        tap.done()
    }
}
