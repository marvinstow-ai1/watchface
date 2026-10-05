#!/usr/bin/env bash
# Baut jedes Battle aus battles/<ordner>/battle.json als eigenes Watchface (Layout "Kompakt 92"
# mit animierten Monstern). Name = "name" aus battle.json; appId fest aus dem Ordnernamen
# abgeleitet, damit ein erneuter Build dasselbe Watchface auf der Uhr ersetzt.
#
# Nutzung: tools/build_battles.sh <ausgabeordner>
# Ergebnis: <ausgabeordner>/battle-<ordner>.zab und <ausgabeordner>/battles.txt
#           (Reihenfolge für die Seite: neueste zuerst)
set -euo pipefail

OUT=$1
ROOT=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$OUT" "$ROOT/build"
: > "$OUT/battles.txt"

# neueste zuerst (Feld "created" in battle.json, sonst Ordnername)
mapfile -t DIRS < <(python3 - "$ROOT/battles" <<'EOF'
import json, sys
from pathlib import Path
items = []
for f in Path(sys.argv[1]).glob("*/battle.json"):
    items.append((json.loads(f.read_text()).get("created", ""), f.parent.name))
for _, name in sorted(items, reverse=True):
    print(name)
EOF
)

for B in "${DIRS[@]}"; do
  D="$ROOT/build/battle-$B"
  rm -rf "$D"
  cp -r "$ROOT/pokemon-watchface" "$D"
  rm -rf "$D/dist"
  python3 "$ROOT/tools/inset_layout.py" --scale 0.92 --project "$D" --battle "$ROOT/battles/$B"
  python3 - "$D/app.json" "$ROOT/battles/$B" <<'EOF'
import json, sys, zlib
from pathlib import Path
path, bdir = sys.argv[1], Path(sys.argv[2])
cfg = json.loads((bdir / "battle.json").read_text())
app = json.load(open(path))
app["app"]["appId"] = 1100000 + zlib.crc32(bdir.name.encode()) % 800000
app["app"]["appName"] = cfg["name"]
for lang in app.get("i18n", {}).values():
    lang["appName"] = cfg["name"]
json.dump(app, open(path, "w"), indent=2, ensure_ascii=False)
print(f"{cfg['name']}: appId {app['app']['appId']}")
EOF
  (cd "$D" && timeout 600 zeus build < /dev/null)
  cp "$D"/dist/*.zab "$OUT/battle-$B.zab"
  ls -la "$OUT/battle-$B.zab"
  echo "$OUT/battle-$B.zab" >> "$OUT/battles.txt"
done
