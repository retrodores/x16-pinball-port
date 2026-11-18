# Fidelity Lab 0.1 validation

Built and tested on the authorized VM via Desktop Commander. Stock r49 emulator,
matching ROM, 65C02 CPU at 8 MHz. No accelerated CPU instruction set required.
This validates the audition and isolated C modules, not a playable original table.

| Check | Result |
|---|---|
| 512 KB and 2048 KB: complete native music stream | One full loop each; zero stream errors |
| 60 Hz ZSM nominal duration | 527.933333 seconds |
| Measured loop, 512 KB / 2048 KB | 527.955240 / 527.946337 emulated seconds |
| Decoded and native YM / PSG register writes | 66,525 / 50,952, exact agreement |
| Decoded melodic attacks / percussion onsets | 7,263 / 6,876, all 14,139 ledger entries match tick and voice order |
| Maximum measured music IRQ | 23,490 cycles (17.62% of a conservative 133,333-cycle budget) |
| All 60 PCM files, both RAM sizes | Exact amplitude-run sequence and order in recorded emulator output |
| PCM transition timing error | Max 2.82 mix samples, <0.058 ms; allowance <5 for host-clock resampling |
| Maximum PCM-only IRQ | 5,853 cycles |
| Normal interactive PRG | Selection, play, M, S, Escape work; BASIC restored |
| Tile output / audio interference | Table region exactly equals packed reference pixels, before and during combined music + PCM |
| Directed line / route module | 3,766 assertions pass on host (ASan/UBSan) and native 65C02 |
| Scoring module | Six assertions pass: host, cc65 and LLVM-MOS, both RAM sizes |
| Scoring comparison, 1000 bumper/rebound pairs | cc65 4,066,908 cycles; LLVM-MOS 1,014,182 cycles |

The compiler result is one small workload, not a whole-game benchmark. Continue
with plain C where practical and use measured assembly in hot paths. LLVM-MOS
is retained for the runnable build; cc65 is a working comparison target for the
initial rules module. This does not claim the entire recovered C++ engine is C.

PCM oracle: volume register 11 yields exact recorded amplitude multiples of 184.
Compare the complete sequence of amplitude changes against the converted PCM,
then check transition times at the true hardware rate. This catches wrong samples,
missing/reordered data and stalls without confusing the emulator's integer host
sample clock with VERA's sample-and-hold phase. Idle PCM is explicitly muted to
avoid retaining a nonzero last sample between effects.

Music timing: the converter rounds onsets to 60 Hz; a VGA frame is 16.8 ms.
The player adds one extra music tick per 125 frames. Individual interrupt scheduling
adds up to roughly one frame of jitter; the conversion's 8.34 ms rounding limit
alone is not a claim of total hardware onset error. Loop length no longer drifts
by about four seconds over the complete theme.

Graphics: 773 16x16 4bpp tiles, 98,944 tile bytes + 4096 map + 512 palette bytes.
Original table spatial dimensions are retained. Palette fitting gives 31.25 dB
full-composition RGB PSNR / 28.96 dB on nonblack pixels; colors are approximate.
Audition text uses another tile layer and font in upper VRAM. Final gameplay must
re-budget that temporary text area for ball/flipper/lighting animation.

The 41 OBS correlation candidates are an audit aid. Only one exceeds the selected
0.70 strong-match threshold; most are ambiguous due to the capture's music and
mixed effects. The DAT supplies 48 sound resources and 84 named component mappings.
Do not represent these candidates as a complete verified annotation of the video.

No claims here of 2 MHz restored-game performance, complete mission logic,
original-table no-escape trajectories, or Windows GM instrument equivalence.
The next integration must pass original table trajectory tests with wall/gate/ramp
layer state, swept flippers and circles before it replaces Wireframe 0.2.
