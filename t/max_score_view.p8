%encoding iso
%zeropage basicsafe
%import video
%import physics
%import score
main {
    sub start() {
        video.init()
        physics.new_game()
        video.objects()
        sys.memset(&score.total,16,255)
        score.format()
        video.request_score()
        repeat 3 { video.score_row() }
        while true { sys.waitvsync() }
    }
}
