# X16 Pinball Opening Show Preview

Cold start and F2 play the supplied installation's SOUND1.WAV, converted
to the X16 PCM format. The table opens with a wider lamp sweep through
the upper playfield, lanes, and center rings. The startup sound is an
effect. It is available when music is muted.

The show keeps the prior five-second opening, player label, and ball-feed
order. F2 skips an active show and F3 enters the demo. The engine borrows
the first gameplay PCM banks for the opening sound, then reloads the
gameplay effects before serving or entering the demo. The bank reload can
briefly pause PCM playback. Storage timing on physical X16 remains untested.

Each ZIP includes the game runtime, sound data, and RUN-WINDOWS.bat.
Put x16emu.exe and its matching rom.bin in the parent folder. The 512 KB
editions use the standard music and the 2 MB editions use Cover Balance.

Linux r49 validation includes audio matching, lamp-frame comparisons,
first ball launch, F2 skip and F3 takeover. Windows launcher execution
and the extended 133,333-cycle target remain open.
