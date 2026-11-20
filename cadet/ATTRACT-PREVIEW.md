# X16 attract preview

The same engine runs the demo in Space Cadet X16 and Space CmdrX16. Let a
fresh table idle for about 15 seconds or press F3. The demo uses the regular
plunger, flippers, physics, scoring, and lamp events. Its own purple caption
tracks four bumper hits followed by two ramp entries. It holds the final
score for about three seconds and starts a new demo.

Press F2 to start a fresh manual game. A flipper, the plunger, or nudge also
takes over from a fresh manual game and applies that control. F3 can leave
an active demo and cannot replace a manual game in progress. M still toggles
music and Escape exits.

## Reference recording

The five-minute Windows capture shows an idle attract entry, a
target-selection-to-ramp sequence, progress counts, and a 500,000-point
mission completion. The 500,000 message identifies a mission reward. The
recording also shows launch training, a reflex award, a multiplier, patterned
lamp transitions, and a final score followed by a fresh demo. The preview
implements its own two objectives on the existing engine. The Windows
mission and jackpot rules, and their synchronized lamp sequences, are still
outside this preview.

The recording contains a mixed stereo track. The median one-second RMS in
the quiet 0:14–0:22 passage was about 756 on the signed 16-bit scale. The upper
quartile during 0:22–5:00 was about 4352. The resulting 15.2 dB contrast is a
guide to the mix, since the two windows do not expose independent stems.
The preview uses an effects-forward default based on that comparison. Its
matched music-only and effects-only emulator scenes measured a 14.16 dB
effects lead at 512 KB and 14.27 dB at 2 MB.

## Building and checking

From a prepared checkout, regenerate the music with
`python3 cadet/build_music.py`, then `python3 cadet/game/pack_music.py`.
Run `sh cadet/game/build.sh` to build the matched engine and overlays.
An existing extraction for either edition needs all three matching engine
files (`CADET.PRG`, `CADET.PHY`, and `CADET.RUL`) and both new
`MUSIC*.BIN` banks. Keep the edition-specific assets in their own folders.

Linux UI smoke tests ran on Space Cadet X16 first, then Space CmdrX16, at
512 KB and 2 MB. They checked idle entry, actual score and objective
progression, F3 entry, F2 and flipper takeover, and the four new-ball
gate lamp regions. The host controller fixture checks the game-over
pause and restart, idle clock wrap, score-independent objective state,
and the manual-game takeover guard. The native build audit verified
the overlay files against their ELF sections.

The 133333-cycle timing gate remains a release blocker.
