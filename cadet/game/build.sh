#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
CC="${MOS_CC:-/opt/llvm-mos-sdk-23.4.0/llvm-mos/bin/mos-cx16-clang}"
mkdir -p cadet/play-build
if [ "${1:-}" = assets ]; then
 python3 cadet/build_graphics.py cadet/play-build
 python3 cadet/game/pack_model.py
 python3 cadet/game/pack_music.py
 python3 cadet/game/pack_sprites.py
 python3 cadet/game/prepare_runtime.py
fi
for variant in CADET TEST; do
 defs="-DPIN_AUDIO"
 if [ "$variant" = TEST ]; then defs="$defs -DGAME_TEST"; fi
 "$CC" -Os $defs -Icadet/play-build wireframe/widemul.s wireframe/sqrt.s \
 wireframe/narrowmul_shared.s cadet/game/signedmul.s cadet/game/fraction.s cadet/game/audio.s \
 cadet/game/engine.c cadet/game/play.c -Wl,-Map,cadet/play-build/$variant.map \
 -o cadet/play-build/$variant.PRG
done
