#!/usr/bin/env bash
# Baut das Watchface in mehreren Größen (SCALE) als getrennte Watchfaces.
# Jede Variante bekommt eine eigene appId (app.json + APPID_OFFSET + Index) und den Namen
# "<NAME_PREFIX> <SCALE>", damit alle gleichzeitig auf der Uhr installiert sein können.
#
# Nutzung: [NAME_PREFIX="Pokemon Kompakt"] [APPID_OFFSET=3] tools/build_variants.sh <ausgabeordner> 92 90 88
# Ergebnis: <ausgabeordner>/<name-prefix-klein>-<SCALE>.zab
set -euo pipefail

OUT=$1; shift
NAME_PREFIX=${NAME_PREFIX:-Pokemon Battle}
APPID_OFFSET=${APPID_OFFSET:-0}
SLUG=$(echo "$NAME_PREFIX" | tr '[:upper:] ' '[:lower:]-')
ROOT=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$OUT" "$ROOT/build"

i=0
for S in "$@"; do
  D="$ROOT/build/pw-$S"
  rm -rf "$D"
  cp -r "$ROOT/pokemon-watchface" "$D"
  rm -rf "$D/dist"
  python3 "$ROOT/tools/inset_layout.py" --scale "0.$S" --project "$D"
  python3 - "$D/app.json" "$((APPID_OFFSET + i))" "$NAME_PREFIX $S" <<'EOF'
import json, sys
path, offset, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
app = json.load(open(path))
app["app"]["appId"] += offset
app["app"]["appName"] = name
for lang in app.get("i18n", {}).values():
    lang["appName"] = name
json.dump(app, open(path, "w"), indent=2)
print(f"{name}: appId {app['app']['appId']}")
EOF
  (cd "$D" && timeout 600 zeus build < /dev/null)
  cp "$D"/dist/*.zab "$OUT/$SLUG-$S.zab"
  i=$((i + 1))
done
ls -la "$OUT"
