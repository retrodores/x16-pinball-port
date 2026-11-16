%encoding iso
%import physics
%import score
%import video
%import storage
%import sound
%import geometry
%import emudbg
%import tap
%import textio
main {
    sub sample(long x,long y,word vx,word vy) {
        physics.new_game()
        physics.state=2
        physics.x=x*256
        physics.y=y*256
        physics.vx=vx
        physics.vy=vy
    }
    sub start() {
        uword i
        long cycles
        physics.new_game()
        tap.ok(physics.lives==3 and physics.state==0 and physics.x==175*256,"new game serves a ball")
        repeat 64 { physics.frame(4) }
        tap.ok(physics.charge==64 and physics.state==0,"holding plunger charges without launching")
        physics.frame(0)
        tap.ok(physics.state==1 and physics.vy < -320,"release launches charged plunger")
        repeat 200 { physics.frame(0) }
        tap.ok(physics.state!=1,"ball leaves the launch channel")
        sample(100,120,0,0)
        physics.frame(0)
        tap.ok(physics.vy>0 and physics.y>120*256,"gravity accelerates downward")
        sample(10,100,-128,0)
        physics.frame(0)
        tap.ok(physics.vx>0 and physics.x>=35*256,"left rail contains and reflects ball")
        sample(190,100,128,0)
        physics.frame(0)
        tap.ok(physics.vx<0 and physics.x<=165*256,"right rail contains and reflects ball")
        sample(100,22,0,-256)
        physics.frame(0)
        tap.ok(physics.vy>0 and physics.y>=22*256,"roof reflects upward motion")
        sample(100,214,0,300)
        physics.frame(0)
        tap.ok(physics.lives==2 and physics.state==0 and physics.drains==1,"drain consumes one life and serves")
        physics.lives=1
        physics.state=2
        physics.y=215*256
        physics.frame(0)
        tap.ok(physics.lives==0,"last drain ends the game")
        sample(100,120,0,100)
        physics.paused=true
        physics.frame(7)
        tap.ok(physics.y==120*256,"pause freezes simulation")
        physics.new_game()
        repeat 4 { physics.frame(3) }
        tap.ok(physics.left_angle==7 and physics.right_angle==7,"both flippers respond simultaneously")
        repeat 7 { physics.frame(0) }
        tap.ok(physics.left_angle==0 and physics.right_angle==0,"released flippers return")
        sample(99,58,0,200)
        physics.frame(0)
        tap.say("# bumper vy/hits/award: ") txt.print_w(physics.vy) txt.spc() txt.print_uw(physics.hits) txt.spc() txt.print_uw(physics.awarded) txt.nl()
        tap.ok(physics.vy<0 and physics.hits>0 and physics.awarded>=100,"bumper reflects and awards points")
        sample(83,198,0,200)
        physics.frame(0)
        tap.say("# flipper vy/hits/x/y: ") txt.print_w(physics.vy) txt.spc() txt.print_uw(physics.hits) txt.spc() txt.print_l(physics.x) txt.spc() txt.print_l(physics.y) txt.nl()
        tap.ok(physics.hits>0 and physics.vy<0,"resting left flipper reflects ball")
        sample(116,198,0,200)
        physics.frame(0)
        tap.say("# flipper vy/hits/x/y: ") txt.print_w(physics.vy) txt.spc() txt.print_uw(physics.hits) txt.spc() txt.print_l(physics.x) txt.spc() txt.print_l(physics.y) txt.nl()
        tap.ok(physics.hits>0 and physics.vy<0,"resting right flipper reflects ball")
        sample(84,190,0,100)
        repeat 4 { physics.frame(1) }
        tap.ok(physics.vy<0,"moving left flipper transfers impulse")
        physics.new_game()
        bool safe=true
        for i in 0 to 4999 {
            if physics.lives==0 { physics.new_game() }
            if physics.state==0 {
                physics.frame(4)
                physics.frame(0)
            }
            physics.frame((i & 3) as ubyte)
            if physics.x<0 or physics.x>201*256 or physics.y<0 or physics.y>216*256 {
                if safe {
                    tap.say("# first bounds failure frame/x/y/state: ")
                    txt.print_uw(i) txt.spc() txt.print_l(physics.x) txt.spc() txt.print_l(physics.y) txt.spc() txt.print_ub(physics.state) txt.nl()
                }
                safe=false
            }
        }
        tap.ok(safe,"5000-frame deterministic soak stays in bounds")
        sample(99,58,0,200)
        emudbg.reset_cpu_cycles()
        physics.frame(3)
        cycles=emudbg.cpu_cycles()
        tap.say("# physics contact frame cycles: ") txt.print_l(cycles) txt.nl()
        tap.ok(cycles<90000,"contact physics fits 8 MHz frame budget")
        ; End-to-end CPU work including full 39-digit score draw and HUD.
        score.clear()
        sys.memset(&score.total,16,255)
        sample(99,58,0,200)
        emudbg.reset_cpu_cycles()
        physics.frame(3)
        sound.tick()
        video.objects()
        video.counters()
        video.latest_pending=false
        video.remaining=0
        video.present_score()
        cycles=emudbg.cpu_cycles()
        tap.say("# max-score contact and conversion-phase cycles: ") txt.print_l(cycles) txt.nl()
        tap.ok(cycles<133333,"max-score update and scheduled rendering fit a 60 Hz frame")
        video.score_row()
        video.score_row()
        video.score_row()
        tap.ok(video.remaining==0 and video.active_start==40,"all 39 digits rendered across three bounded frames")
        tap.done()
    }
}
