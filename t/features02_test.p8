%encoding iso
%import syslib
%import boundaries
%import physics
%import video
%import sound
%import session
%import score
%import storage
%import tap
main {
 sub start() {
  video.init()
  sound.init()
  tap.ok(not video.error and boundaries.ready and sound.ready,"all wall, plunger and original effect assets load")
  tap.ok(geometry.BALL_DIAMETER==7,"ball sprite enlarged from five to seven pixels")
  physics.new_game()
  repeat 64 { physics.frame(4) }
  tap.ok(physics.plunger_frame==7 and physics.y==200*256,"full charge visibly pulls the plunger and ball back")
  video.objects()
  tap.ok(cx16.vpeek(1,$fc50)==$70 and cx16.vpeek(1,$fc51)==$8e,"full charge selects original pulled-plunger artwork")
  physics.frame(0)
  tap.ok(physics.plunger_frame==7 and physics.state==1,"release starts a spring return")
  repeat 7 { physics.frame(0) }
  tap.ok(physics.plunger_frame==0,"plunger returns through animation frames")
  session.mode=session.ATTRACT
  session.listen()
  tap.ok(session.mode==session.LISTEN and session.input(7)==0,"music-only mode suppresses gameplay input")
  session.listen()
  tap.ok(session.mode==session.ATTRACT,"leaving listening restores attract mode")
  session.play()
  tap.ok(session.mode==session.PLAY and physics.lives==3,"start play creates a fresh three-ball game")
  session.mode=session.ATTRACT
  physics.new_game()
  repeat 64 { void session.input(0) }
  tap.ok(session.input(0)==0,"attract mode releases its charged shot")
  sound.music_on=true
  sound.effects_on=false
  sound.fx_remaining=0
  sound.effect(2)
  tap.ok(sound.fx_remaining==0,"sound-effects switch suppresses original effect requests")
  cx16.VERA_AUDIO_CTRL=$8c
  sound.music_pos=512
  ubyte bank=@($00)
  sound.service()
  tap.say("# music open/failed/count: ") txt.print_ub(sound.music_open as ubyte) txt.spc() txt.print_ub(sound.failed as ubyte) txt.spc() txt.print_uw(sound.read_count) txt.nl()
  tap.ok(sound.music_open and not sound.failed and sound.read_count==512,"original theme streams in sector-sized blocks")
  tap.ok(@($00)==bank,"PCM mixer restores banked RAM selector")
  tap.ok(cx16.VERA_AUDIO_RATE==21 and cx16.VERA_AUDIO_CTRL & 64 ==0,"music data reaches the running PCM FIFO")
  sound.music_on=false
  sound.effects_on=true
  cx16.VERA_AUDIO_CTRL=$8c
  sound.effect(2)
  uword length=sound.fx_remaining
  sound.service()
  tap.ok(not sound.music_open and sound.fx_remaining<length,"original effects play independently of music")
  sound.effects_on=false
  sound.service()
  tap.ok(sound.fx_remaining==0 and cx16.VERA_AUDIO_RATE==0,"both audio switches off produce silence")
  score.clear()
  score.add16(1)
  score.begin_format()
  score.format_step()
  score.add16(2)
  score.format_step()
  tap.ok(not score.busy and score.dirty and score.text[39]=='1',"incremental conversion keeps a coherent snapshot and queues new points")
  score.format()
  tap.ok(score.text[39]=='3',"queued score is converted without losing intervening awards")
  sound.quiet()
  tap.done()
 }
}
