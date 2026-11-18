# CmdrX Cadet Fidelity Lab 0.1

This is a runnable original-art/audio audition and a C-port checkpoint, **not a
playable Space Cadet table**. Keep the accepted Wireframe 0.2 for play. Its practice
geometry is not proof of Space Cadet's legal routes. No original artwork has been
placed over that unrelated physics layout.

## Run

Extract the complete release. Use a current X16 emulator with its matching ROM.
Tested on stock r49, 65C02, 8 MHz, both 512 KB and 2048 KB banked RAM.
From the release directory:

```
x16emu -c02 -mhz 8 -ram 512 -fsroot . -prg LAB.PRG -run
```

Windows: drag x16emu.exe onto RUN-WINDOWS.bat, or pass its full path as the first
argument. The launcher uses the ROM beside that emulator. The distribution does
not include an emulator, ROM or original Windows executable.

- M: start/restart or stop the complete Space Cadet theme.
- Left/right: select one of the 60 converted effects.
- Space: load and play that effect.
- S: stop effects and music.
- Escape: restore BASIC screen and interrupt vector.

The static score panels, plunger and flippers are artwork only in this audition.
Effect selection loads from disk; the finished game must cache frequent effects.
Start music before auditioning effects to hear them together.

## What is native

The original 365 x 470 table retains every spatial pixel, plus the original backbox,
on a 640 x 480 display. VERA uses 773 deduplicated 16 x 16 tiles, 4 bits per pixel
and 16 palette banks. Colors are reduced to VERA's 12-bit palette/local tile limits;
this is not color-identical to Windows. Original rest poses are composed into the
background. Animation and ball sprites remain to be integrated.

All 60 supplied WAVs are signed 8-bit mono VERA PCM, resampled to the actual rate
of register 29 (11062.622 Hz). Relative source loudness is preserved; one master
volume applies to all effects. THEME.ZSM is a standard ZSM v1 native music stream:
YM2151 melodic voices and VERA PSG percussion. It retains all 14,139 note starts,
without active-note stealing, and the source pitch-bend events. Tick quantization
is 60 Hz (maximum onset rounding 8.34 ms). The player compensates VGA's
59.5238 Hz refresh using 126 music ticks per 125 frames, avoiding tempo drift.
Instrument patches, percussion envelopes and unsupported GM expression remain
adaptations. The result is not yet Windows General MIDI timbre-perfect.
PINBALL2.MID is bitmap font data, not another music track.

## C reconstruction and route fidelity

The recovered original C++ source is already available and retained as the oracle.
A wholesale C rewrite/cc65 compile is not, by itself, a performance solution.
This checkpoint starts with small plain-C modules:

- rules.c: original attack/launch bumper level awards and rebound award, plus the
  requested exact 128-bit score accumulation extension.
- routes.c: directed swept-line rejection, collision masks, one-way pass/block
  classification and original ramp plane/exit state changes. World coordinates
  are Q8, plane slopes Q12; runtime uses integers only.
- routes.json/CSV: source-derived topology catalog. Tests use all 538 relevant
  original line edges: 455 wall/table edges, 18 one-way faces (9 components), and
  65 ramp edges. They test forward/reverse crossing, parallel movement, inactive
  faces, wrong layers, event-only ramp lines and height/mask changes.

These route tests are not whole-game trajectory tests. Circles, flipper sweeps,
collision response, penetration recovery, dynamic gates, sinks, missions and
actual rendered-ball integration remain. The route predicate assumes finite
motion/coordinates within the documented world bounds and does not implement the
original ray's negative-distance penetration tolerance.

## Evidence and limits

VALIDATION.md records emulator tests and measurements. audits/ includes original
component-to-sound references, source hashes, note ledger, graphics metrics and
OBS waveform candidates. Candidate OBS matches are explicitly not all confirmed;
layered music/effects and lossy AAC make many ambiguous. Original DAT references
are the stronger event-to-sound evidence.

Six WAV names referenced by DAT are absent from both the supplied installation
and the installer ZIP: SOUND2, SOUND37, SOUND44, SOUND52, SOUND59 and SOUND62.WAV.
They have not been invented or silently substituted. Some references may be unused;
trace their actual original call sites before deciding the final handling.

## Source/recovery

SOURCE.zip contains the earlier direct port, accepted wireframe, recovered
vendor source with the earlier port adaptations and this new cadet/ work. VM: /opt/cmdrx-cadet-fidelity, branch
spacecadet-fidelity. The accepted /opt/cmdrx-cadet-direct worktree and tag
wireframe-v0.2 remain separate. There is no configured remote for this repository.

Build: extract SOURCE.zip, then `sh cadet/build.sh` from its source/ directory.
Generated assets are included, so the native build does not need the Windows game.
Requires LLVM-MOS, a host C compiler and Python with Pillow/numpy/scipy. Optional
cc65 builds the scoring comparison. MOS_CC overrides the default VM compiler path.
Full asset regeneration (`--assets`) also needs mido and the original supplied
installation at /opt/spacecadet-x16-analysis/input/game plus its evidence/inventory.json.
The original analyzer and source provenance are retained with this checkpoint.
Tests: test_lab.py MUSIC_TEST/PCM_TEST 512/2048; keyboard_lab.py runs under Xvfb;
ROUTES_TEST.PRG and RULES_*.PRG run with emulator -testbench. Test tools default to
the documented VM emulator paths. Audio captures are excluded from the source ZIP.

Original Space Cadet artwork, samples and composition belong to their respective
rights holders. Converted here from the user's supplied assets. Recovered
SpaceCadetPinball code is MIT licensed; see direct/vendor/LICENSE and upstream
https://github.com/k4zmu2a/SpaceCadetPinball, pinned cb9b7b886244a27773f66b0b19fdc2998392565e.
