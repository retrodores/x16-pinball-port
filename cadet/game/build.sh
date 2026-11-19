#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
mkdir -p cadet/play-build
if [ "${1:-}" = assets ]; then
 python3 cadet/build_graphics.py cadet/play-build
 python3 cadet/game/pack_model.py
 python3 cadet/game/pack_music.py
 python3 cadet/game/pack_sprites.py
 python3 cadet/game/pack_depth.py
 python3 cadet/game/prepare_runtime.py
 python3 cadet/game/pack_dynamic.py
fi
python3 cadet/game/build_native.py
