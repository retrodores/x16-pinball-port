%encoding iso
%import geometry
%import boundaries
; First mechanics prototype: screen-space fixed point, two substeps per frame.
; This is intentionally a reduced table; ramps and mission collisions are absent.
physics {
    const ubyte LEFT=1
    const ubyte RIGHT=2
    const ubyte PLUNGER=4
    long x,y,oldx,oldy
    word vx,vy
    ubyte left_angle=0
    ubyte right_angle=0
    ubyte prior_left=0
    ubyte prior_right=0
    ubyte charge=0
    ubyte lives=3
    ubyte cooldown=0
    ubyte bumper_flash=0
    ubyte hit_bumper=0
    ubyte plunger_frame=0
    ubyte wall_events=0
    ubyte state=0
    uword awarded=0
    uword hits=0
    uword drains=0
    bool space_was=false
    bool paused=false
    sub new_game() {
        lives=3
        hits=0
        drains=0
        left_angle=0
        right_angle=0
        prior_left=0
        prior_right=0
        paused=false
        space_was=false
        serve()
    }
    sub serve() {
        x=169*256
        y=188*256
        vx=0
        vy=0
        charge=0
        plunger_frame=0
        cooldown=0
        state=0
    }
    sub frame(ubyte keys) {
        ubyte i
        awarded=0
        wall_events=0
        if paused or lives==0 { return }
        prior_left=left_angle
        prior_right=right_angle
        if keys & LEFT != 0 {
            if left_angle<7 { left_angle++ }
            if left_angle<7 { left_angle++ }
        } else {
            if left_angle>0 { left_angle-- }
        }
        if keys & RIGHT != 0 {
            if right_angle<7 { right_angle++ }
            if right_angle<7 { right_angle++ }
        } else {
            if right_angle>0 { right_angle-- }
        }
        if bumper_flash>0 { bumper_flash-- }
        if state!=0 and plunger_frame>0 { plunger_frame-- }
        if state==0 {
            if keys & PLUNGER != 0 {
                if charge<64 { charge++ }
            } else {
                if space_was {
                    state=1
                    vx=0
                    vy=-320-(charge as word)*2
                    charge=0
                }
            }
            if state==0 {
                plunger_frame=charge>>3
                if plunger_frame>7 { plunger_frame=7 }
                x=(169+(charge as long)/32)*256
                y=(188+(charge as long)*3/16)*256
            }
            space_was=keys & PLUNGER != 0
            return
        }
        space_was=keys & PLUNGER != 0
        for i in 0 to 1 {
            step()
            if state==0 or lives==0 { break }
        }
    }
    sub step() {
        word px,py
        ubyte i
        if cooldown>0 { cooldown-- }
        oldx=x
        oldy=y
        if vy<448 { vy++ }
        x+=vx as long
        y+=vy as long
        px=((x>>8) as word)
        py=((y>>8) as word)
        ; Launch uses the same wall collisions as normal play, with no teleport.
        if state==1 and py<160 and px<166 { state=2 }
        if py>214 {
            y=214*256
            vx=0
            vy=0
            if state==1 { serve() return }
            lives--
            drains++
            if lives!=0 { serve() }
            return
        }
        if px<4 { x=4*256 vx=128 }
        if px>190 { x=190*256 vx=-128 }
        if py<4 { y=4*256 vy=128 }
        ubyte normal=boundaries.at(((x>>8) as word),((y>>8) as word))
        if normal!=0 {
            long proposed_x=x
            long proposed_y=y
            normal--
            reflect(boundaries.nx[normal] as word,boundaries.ny[normal] as word,
                (boundaries.nx[normal]*boundaries.nx[normal]+boundaries.ny[normal]*boundaries.ny[normal]) as word,0,0,0)
            x=oldx
            y=oldy
            ; Preserve safe tangential movement along curved rails.
            if boundaries.at(((proposed_x>>8) as word),((oldy>>8) as word))==0 { x=proposed_x }
            if boundaries.at(((x>>8) as word),((proposed_y>>8) as word))==0 { y=proposed_y }
            else {
                long nudge=x
                if boundaries.nx[normal]<0 { nudge-=256 }
                if boundaries.nx[normal]>0 { nudge+=256 }
                if boundaries.at(((nudge>>8) as word),((proposed_y>>8) as word))==0 { x=nudge y=proposed_y }
            }
            wall_events++
        }
        if cooldown==0 {
            for i in 0 to 6 {
                circle(geometry.bx[i] as word,geometry.by[i] as word,9,64,100)
                if cooldown!=0 {
                    hit_bumper=i
                    bumper_flash=6
                    break
                }
            }
        }
        if cooldown==0 {
            line(geometry.lpx as word,geometry.lpy as word,
                geometry.ltx[left_angle] as word,geometry.lty[left_angle] as word,
                left_angle>prior_left,10)
        }
        if cooldown==0 {
            line(geometry.rpx as word,geometry.rpy as word,
                geometry.rtx[right_angle] as word,geometry.rty[right_angle] as word,
                right_angle>prior_right,10)
        }
    }
    sub circle(word cx,word cy,word radius,word kick,uword points) {
        word dx=((x>>8) as word)-cx
        word dy=((y>>8) as word)-cy
        if dx>radius or dx < -radius or dy>radius or dy < -radius { return }
        word d2=(dx*dx+dy*dy) as word
        if d2>radius*radius { return }
        reflect(dx,dy,d2,kick,0,points)
    }
    sub line(word ax,word ay,word bx,word by,bool moving,uword points) {
        word px=((x>>8) as word)
        word py=((y>>8) as word)
        if py<175 or py>211 { return }
        word ex=bx-ax
        word ey=by-ay
        word len2=(ex*ex+ey*ey) as word
        word dot=(px-ax)*ex+(py-ay)*ey
        if dot<0 { dot=0 }
        if dot>len2 { dot=len2 }
        word qx=ax+dot*ex/len2
        word qy=ay+dot*ey/len2
        word dx=px-qx
        word dy=py-qy
        if dx>5 or dx < -5 or dy>5 or dy < -5 { return }
        word d2=(dx*dx+dy*dy) as word
        if d2>25 { return }
        word surface=0
        if moving { surface=-120 }
        if dot>0 and dot<len2 {
            if dx*ey-dy*ex>=0 {
                reflect(ey,-ex,len2,0,surface,points)
            } else {
                reflect(-ey,ex,len2,0,surface,points)
            }
        } else {
            reflect(dx,dy,d2,0,surface,points)
        }
    }
    sub reflect(word dx,word dy,word d2,word kick,word surface,uword points) {
        if d2==0 {
            dy=-1
            d2=1
        }
        ; Unit normals in signed Q7, derived from an offline reciprocal-length table.
        ; Velocities are divided by eight before the dot product, keeping every
        ; intermediate in signed 16 bits. Reflection loses at most small fractions
        ; of a pixel, acceptable for this reduced mechanics prototype.
        if d2>=512 { return }
        word inverse
        if d2<256 { inverse=geometry.invlen0[d2 as ubyte] as word }
        else { inverse=geometry.invlen1[(d2-256) as ubyte] as word }
        word nx=dx*inverse/32
        word ny=dy*inverse/32
        word rvx=vx>>3
        word rvy=(vy-surface)>>3
        word dot=(rvx*nx+rvy*ny)>>7
        if dot>=0 { return }
        vx-=dot*nx/8
        vy-=dot*ny/8
        if kick!=0 {
            if dx<0 { vx-=kick } else { vx+=kick }
            if dy<0 { vy-=kick } else { vy+=kick }
        }
        if vx>384 { vx=384 }
        if vx < -384 { vx=-384 }
        if vy>448 { vy=448 }
        if vy < -448 { vy=-448 }
        x=oldx
        y=oldy
        cooldown=4
        hits++
        awarded+=points
    }
}
