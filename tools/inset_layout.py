#!/usr/bin/env python3
"""
Verkleinert das Original-Design (design/original-assets/, 390x450) gleichmäßig und setzt
es mittig auf den Bildschirm, damit an den abgerundeten Ecken der Active 2 Square nichts
abgeschnitten wird. Ergebnis: pokemon-watchface/assets/default.s/

SCALE muss mit SCALE in pokemon-watchface/watchface/index.js übereinstimmen.

Nutzung: python3 tools/inset_layout.py
"""
import shutil
from pathlib import Path

from PIL import Image

SCALE = 0.86
SCREEN = (390, 450)
FILL = (248, 248, 248)  # Hintergrundfarbe des Designs

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "design" / "original-assets"
DST = ROOT / "pokemon-watchface" / "assets" / "default.s"


def scaled_size(size):
    return tuple(max(1, round(v * SCALE)) for v in size)


def main():
    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir(parents=True)

    for src in sorted(SRC.rglob("*.png")):
        rel = src.relative_to(SRC)
        out = DST / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(src)

        if rel.as_posix() == "icon.png":
            shutil.copy(src, out)  # Vorschaubild in der Zepp-App, bleibt wie es ist
        elif rel.as_posix() == "bg.png":
            small = im.convert("RGB").resize(scaled_size(im.size), Image.LANCZOS)
            bg = Image.new("RGB", SCREEN, FILL)
            bg.paste(small, ((SCREEN[0] - small.width) // 2, (SCREEN[1] - small.height) // 2))
            bg.save(out)
        else:
            im.convert("RGBA").resize(scaled_size(im.size), Image.LANCZOS).save(out)

    w, h = scaled_size(SCREEN)
    print(f"SCALE={SCALE}: Design {w}x{h}, Rand links/rechts {(SCREEN[0] - w) // 2}px, "
          f"oben/unten {(SCREEN[1] - h) // 2}px")


if __name__ == "__main__":
    main()
