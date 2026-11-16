%encoding iso
%import syslib
storage {
    ubyte[16] best
    ubyte[21] record
    bool failed=false
    bool changed=false
    str filename="CMDRX.HI"
    str writefile="@:CMDRX.HI,S,W"
    sub observe() {
        ubyte i
        if score.greater(&best) {
            for i in 0 to 15 { best[i]=score.total[i] }
            changed=true
        }
    }
    sub load() {
        ubyte i
        ubyte checksum=0
        bool valid=true
        for i in 0 to 15 { best[i]=0 }
        cbm.SETNAM(8,filename)
        cbm.SETLFS(2,8,2)
        void cbm.OPEN()
        if_cs { cbm.CLOSE(2) return }
        void cbm.CHKIN(2)
        for i in 0 to 20 {
            if cbm.READST()!=0 { valid=false break }
            record[i]=cbm.CHRIN()
        }
        cbm.CLRCHN()
        cbm.CLOSE(2)
        if not valid { return }
        if record[0]!=67 or record[1]!=67 or record[2]!=88 or record[3]!=1 { return }
        for i in 0 to 19 { checksum ^= record[i] }
        if checksum!=record[20] { return }
        for i in 0 to 15 { best[i]=record[i+4] }
        changed=false
    }
    sub save() {
        ubyte i
        ubyte checksum=0
        failed=false
        if not changed { return }
        record[0]=67 record[1]=67 record[2]=88 record[3]=1
        for i in 0 to 15 { record[i+4]=best[i] }
        for i in 0 to 19 { checksum ^= record[i] }
        record[20]=checksum
        cbm.SETNAM(14,writefile)
        cbm.SETLFS(2,8,2)
        void cbm.OPEN()
        if_cs { failed=true cbm.CLOSE(2) return }
        cbm.CHKOUT(2)
        for i in 0 to 20 { cbm.CHROUT(record[i]) }
        if cbm.READST()!=0 { failed=true }
        cbm.CLRCHN()
        cbm.CLOSE(2)
        if not failed { changed=false }
    }
}
