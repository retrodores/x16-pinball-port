# X16 Pinball Attract Preview 3

The upper backbox box shows **Player 1**. The lower box shows launch, live
game and demo messages. The in-game controls legend is gone. The original
mixed-case message face shares the score's violet, with shaded edges and
stippled highlights.

Each ZIP contains a complete runtime for its edition, the Windows
launcher and both engine specification formats. Extract to a separate
folder, put matching x16emu.exe and rom.bin in its parent folder, and run
RUN-WINDOWS.bat.

Flippers are Z and /. Hold and release Space to launch. Press F2 for a new
game, F3 for the demo, M for music, and Escape to exit. The demo also starts
after about 15 seconds at a fresh idle table.

See VALIDATION.json for emulator checks and timing. The Windows launcher
is included as checked package content. Emulator gameplay tests ran on Linux.

Both editions passed from fresh ZIP extractions at 512 KB and 2 MB.
At 512 KB, 74 of 12,000 frames exceeded 133,333 cycles. The worst frame took 213,514 cycles.
At 2048 KB, 75 of 12,000 frames exceeded 133,333 cycles. The worst frame took 213,524 cycles.
