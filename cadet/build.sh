#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
MOS_CC=${MOS_CC:-/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang}
mkdir -p cadet/build
# The release includes generated assets. --assets rebuilds from the supplied
# original installation + DAT inventory at the paths documented in README.md.
if [ "${1:-}" = --assets ]; then
 python3 cadet/audit_audio.py
 python3 cadet/build_graphics.py
 python3 cadet/build_music.py
fi
python3 cadet/build_routes.py
python3 cadet/prepare_lab.py
for mode in LAB MUSIC_TEST PCM_TEST; do
 if [ "$mode" = LAB ]; then
  "$MOS_CC" -Os -Icadet/build cadet/lab.c cadet/player.s -o "cadet/build/$mode.PRG"
 else
  "$MOS_CC" -Os "-D$mode" -Icadet/build cadet/lab.c cadet/player.s -o "cadet/build/$mode.PRG"
 fi
done
"$MOS_CC" -Os -Icadet/build cadet/routes.c cadet/routes_probe.c -o cadet/build/ROUTES_TEST.PRG
"$MOS_CC" -Os cadet/rules.c cadet/rules_probe.c -o cadet/build/RULES_LLVM.PRG
cc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -Icadet/build cadet/routes.c cadet/routes_probe.c -o cadet/build/routes-host
cadet/build/routes-host
cc -std=c99 -Wall -Wextra -Werror cadet/rules.c cadet/rules_probe.c -o cadet/build/rules-host
cadet/build/rules-host
if command -v cl65 >/dev/null 2>&1; then
 cl65 -t cx16 --cpu 65c02 -Oirs cadet/rules.c cadet/rules_probe.c -o cadet/build/RULES_CC65.PRG
fi
printf 'Built cadet/build/LAB.PRG and native test probes.\n'
