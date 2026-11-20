# GTR3QQ Space Cadet soundtrack cover

Original music: Matt Ridgeway (1995), `pinball.mid` / `rock2.mid`.
Commander X16 cover: GTR3QQ (2024), published by YouTube account
WheatenClient36. The author states that the cover is licensed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Keep the cover credit and license with the audio and state any audio changes.
The notice concerns the cover. Original composition and sample rights are
separate from the engine's license.

- [Creator's recording, credits and license statement](https://www.youtube.com/watch?v=HEgjkcY2iAg)
- [Creator's download post](https://cx16forum.com/forum/viewtopic.php?p=32984)

The user-supplied `pinball.7z` contains two ZSM v1 exports. Both were parsed
through the end command at the PCM boundary. Each declares 92 Hz and runs
5,376 ticks (58.435 seconds) before the loop. Playback in the game is pending.

| File | Sound generators | Total bytes | PCM sample data bytes |
| --- | --- | ---: | ---: |
| `Pinball_R6.zsm` | YM2151, VERA PSG and PCM | 1,667,042 | 1,514,832 |
| `Pinball.VERA_R2.zsm` | VERA PSG and PCM | 1,664,988 | 1,515,109 |

`Pinball_R6.zsm` SHA-256:
`4160e79d73474e9effd7e93c7426315c5c53f0fafe4bc92902885d2ff886cc05`.

The existing soundtrack loader reserves banks 32–44 for encoded commands.
It runs at 60 Hz, skips ZSM extension payloads, and uses fixed source length
and restart behavior. The game uses the VERA PCM FIFO for sound effects.
Both cover exports depend on PCM extension commands for the drums. Use the
combined YM2151 and VERA version for comparison with the creator's recording.

To retain the cover intact during play on 512 KB, prototype bounded disk
read-ahead for the drum data and a shared PCM mixer for music and game effects.
Schedule the command stream at its declared rate and honor the loop offset.
Validate audio across the loop, simultaneous effects, and toggle/reset behavior.
Measure FIFO underruns, music/effects balance and worst frame cycles at 8 MHz
on 512 KB and 2 MB before deciding whether it can ship as the default.

## Streaming feasibility at the cover's native PCM rate

The YM2151/VERA export plays 8-bit stereo drums at VERA rate 73
(27,847.3 stereo frames/s, 55,694.6 bytes/s). The creator explicitly calls
out the stereo drum balance. The fixture keeps stereo and rate 73 while
mixing the existing flipper, plunger and table effects from rate 29.

Run `python3 cadet/game/test_music_stream.py` on the VM after generating the
resident effects. Add `--frames 100 --sd-image /path/to/sdcard.img` for the
emulated r49 FAT32 SD-card path. Requires mtools for the SD run. An over-budget
result intentionally exits nonzero. The fixture uses synthetic stereo PCM
at the same data rate and the production effects renderer. It exercises
sequential MACPTR reads, an assembly mixer and VERA FIFO writes. It excludes
ZSM PSG/FM playback, instrument seeks, physics and graphics.

| r49 at 8 MHz | RAM | Intervals | Mean cycles | Peak cycles | Over 133,333 |
| --- | ---: | ---: | ---: | ---: | ---: |
| HostFS | 512 KB | 3,500 | 63,940 | 279,614 | 36 |
| HostFS | 2 MB | 3,500 | 63,641 | 252,475 | 22 |
| SD image | 512 KB | 100 | 163,265 | 234,164 | 79 |
| SD image | 2 MB | 100 | 162,038 | 234,066 | 78 |

The HostFS runs consumed about 3.27 MB each. No FIFO empty or full flag
was seen at the fixture's sampling points. The SD runs skipped 33 and 32
video intervals with measured work spanning multiple intervals. They
represent the emulated SD path, and hardware SD performance is unverified.
The direct KERNAL read and software mix approach misses the cycle budget
before the game workload is added. The current runtime stays selected.

For a separate 2 MB feasibility build, the original PCM area fits in 185 of
the 192 banks above the 512 KB boundary. The original 152,030-byte command
stream packs to 25,829 bytes with the project's LZSS algorithm, which fits
in the current music bank allocation. Resident samples would remove the
measured file-read cost while keeping the original stereo. This has yet to
be implemented or validated in-game. A 512 KB build still needs a separate
storage/mixing design and a native timing check.
