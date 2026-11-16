#!/bin/sh
set -eu
cd "$(dirname "$0")"
mkdir -p build
if [ -n "${JAR:-}" ]; then
    java -jar "$JAR" -target cx16 -srcdirs src -out build src/cmdrx.p8
else
    "${PROG8C:-prog8c}" -target cx16 -srcdirs src -out build src/cmdrx.p8
fi
cp assets/*.BIN assets/*.PCM build/
cp build/cmdrx.prg build/CMDRX.PRG
