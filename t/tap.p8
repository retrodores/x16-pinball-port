%encoding iso
%import syslib
%import textio
%import emudbg
tap {
    uword count=0
    sub say(str s) { emudbg.console_write(s) }
    sub ok(bool good, str label) {
        if count==0 { say("# TAP BEGIN") emudbg.console_nl() }
        emudbg.console_nl()
        count++
        if not good { say("not ") }
        say("ok - ") say(label) emudbg.console_nl()
    }
    sub done() {
        say("1..")
        ; Decimal plan through KERNAL for simplicity.
        txt.print_uw(count)
        cbm.CHROUT(13)
        @($9fb4)=0
        %asm {{ jmp $ffff }}
    }
}
