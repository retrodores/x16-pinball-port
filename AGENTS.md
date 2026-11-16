# CmdrX Cadet
Use /opt/cmdrx-cadet on the connected Linux VM for implementation and emulation.
The analysis/reference workspace is /opt/spacecadet-x16-analysis; preserve it.
The selected display is 320x240 8bpp. Keep the game title CmdrX Cadet.
The first prototype uses reduced screen-space mechanics; do not describe it as
a faithful complete port. Preserve original asset and decompilation attribution.

On direct-engine, follow direct/AGENTS.md and the user decision to port recovered
C++ directly through LLVM-MOS. Preserve src/ as the old prototype reference.
Use assembly or fixed-point adaptation only after measuring and comparing behavior.
Parenthesize numeric casts inside compound arithmetic expressions in Prog8.
The score is unsigned 128-bit little endian, including saves and comparisons.
Never silently wrap, truncate, or narrow score intermediates.
No original Windows executable or ROM belongs in release packages.
Keep generated play assets separate from source and mark their origin.

Build with ./build.sh. Test with prove -v t/native.t.
Tests import actual production modules and execute native 65C02 PRGs on r49.
Run tests with both X16_RAM_KB=512 and X16_RAM_KB=2048 before packaging.
Native frame-budget tests must stay below 133333 cycles at 8 MHz. Do not relax
this bound to hide a regression. Scores are presented asynchronously so expensive
conversion and pixel drawing happen on different simulation frames.
Update tests with behavior changes; the user should not need manual test upkeep.
Keep all subprocesses bounded. Record known gaps in README.md and CHANGELOG.md.
