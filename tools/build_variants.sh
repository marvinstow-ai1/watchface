#!/usr/bin/env bash
# Baut das Watchface in mehreren Größen (SCALE) als getrennte Watchfaces.
# Jede Variante bekommt eine eigene appId und den Namen "Pokemon Battle <SCALE>",
# damit alle gleichzeitig auf der Uhr installiert sein können.
# Variante 0 behält die appId aus app.json (ersetzt beim Installieren die bisherige Version).
#
# Nutzung: tools/build_variants.sh <ausgabeordner-fuer-zabs> 86 84 82
set -euo pipefail

OUT=$1; shift
ROOT=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$OUT" "$ROOT/build"

i=0
for S in "$@"; do
  D="$ROOT/build/pw-$S"
  rm -rf "$D"
  cp -r "$ROOT/pokemon-watchface" "$D"
  rm -rf "$D/dist"
  python3 "$ROOT/tools/inset_layout.py" --scale "0.$S" --project "$D"
  python3 - "$D/app.json" "$i" "$S" <<'EOF'
import json, sys
path, i, s = sys.argv[1], int(sys.argv[2]), sys.argv[3]
app = json.load(open(path))
app["app"]["appId"] += i
name = f"Pokemon Battle {s}"
app["app"]["appName"] = name
for lang in app.get("i18n", {}).values():
    lang["appName"] = name
json.dump(app, open(path, "w"), indent=2)
print(f"{name}: appId {app['app']['appId']}")
EOF
  (cd "$D" && timeout 600 zeus build < /dev/null)
  cp "$D"/dist/*.zab "$OUT/pokemon-battle-$S.zab"
  i=$((i + 1))
done
ls -la "$OUT"
