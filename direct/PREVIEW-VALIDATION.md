# Direct preview validation — 2026-11-16

Environment: connected development VM, LLVM-MOS SDK 23.4.0, 64tass 1.59,
Commander X16 emulator r49 and matching r49 ROM. CPU is set to 8 MHz in the
validation runs; automated instrumented tests use warp only to shorten host
waiting. Actual SDL keyboard runs use normal, unwarped execution.

- Core native suite: **736 tests pass** across 512 KB and 2048 KB. Original
  method extraction and the retained 240-frame static-world comparison remain
  unchanged. Flipper/contact comparisons and plunger tests still pass.
- Release timing regression: **40/40** full-charge release timings clear the
  chute with the preview's 120 Hz cadence, using the actual world adapter.
- Normal-ROM instrumented UI boots at **both RAM sizes**: full charge, chute
  clearance, both flippers, press/release handling, a pause tap whose press and
  release both precede the next frame, and restored BASIC text screen pass.
- Exact distribution CMDRX.PRG, actual SDL key events via Xvfb/xdotool, at
  **both RAM sizes**: N, held Space and release, both Shift keys, pause/resume,
  Escape and restored BASIC output pass. Captures verify the visible status
  changes, full charge bar and both flipper sprite changes.
- CMDRX.PRG: **35032 bytes**. Bank-1 UI.BIN: **6985 bytes**. WORLD.BIN:
  **193640 bytes**, banks 32..55. Runtime assets fit 512 KB banked RAM.

The frame-budget gate deliberately remains **FAIL**: the retained 60 Hz core
scenarios measure 525087 cycles (world) and 1089833 cycles (integrated mechanics),
against the unchanged 133333-cycle limit. Those are core diagnostic measurements,
not a complete timing profile of the new display loop. The visible preview uses
two 120 Hz simulation updates and is also visibly slow on the stock CPU.

No original extracted method or vendor source was changed. Adaptations are the
native 120 Hz scheduler, banked VERA presentation, camera projection, asset panel
conversion and keyboard input. Main and test PRGs have separately linked UI state
addresses; the distribution always pairs normal.prg with normal-ui.bin.

Run from the source root after `sh direct/build.sh` and `sh direct/build-preview.sh`:

```sh
prove -v direct/t/native.t
python3 direct/t/preview_native.py
xvfb-run -a python3 direct/t/preview_boot.py 512
xvfb-run -a python3 direct/t/preview_boot.py 2048
python3 direct/t/preview_screens.py
perl direct/t/frame_budget.pl  # expected failure until CPU work is complete
```

The source checkpoint includes the logs and the two actual SDL screenshots
used for reviewing full charge and flipper display. Windows launcher batch
syntax was reviewed; the binaries themselves were tested in the Linux r49
emulator. No physical X16 or Windows emulator test has been performed.
