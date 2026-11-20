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
