#!/usr/bin/env python3
"""
Baut die Watchface-Assets aus dem Original-Design (design/original-assets/, 390x450):

- Uhrzeit-Ziffern pixelgenau um TIME_ZOOM vergrößert
- Wochentage neu in fetter Pixelschrift (Stil der Uhrzeit, nur kleiner)
- alles gleichmäßig um SCALE verkleinert und mittig gesetzt, damit an den abgerundeten
  Ecken der Active 2 Square nichts abgeschnitten wird

Ergebnis: pokemon-watchface/assets/default.s/
SCALE und TIME_ZOOM müssen mit pokemon-watchface/watchface/index.js übereinstimmen.

Nutzung: python3 tools/inset_layout.py
"""
import shutil
from pathlib import Path

from PIL import Image

SCALE = 0.90
TIME_ZOOM = 6 / 5  # Uhrzeit-Pixel 5px -> 6px
SCREEN = (390, 450)
FILL = (248, 248, 248)  # Hintergrundfarbe des Designs
INK = (16, 16, 24, 255)  # Schriftfarbe des Designs

WEEK_CELL = 3  # Pixelgröße der Wochentag-Schrift (Original-Koordinaten)
WEEK_SIZE = (222, 21)  # Bildgröße wie im Original, Text rechtsbündig
WEEKDAYS = ["MONTAG", "DIENSTAG", "MITTWOCH", "DONNERSTAG", "FREITAG", "SAMSTAG", "SONNTAG"]

# Fette 7-Zeilen-Pixelbuchstaben im Stil der Uhrzeit-Ziffern
# (senkrechte Striche 2 Zellen breit, waagerechte 1 Zelle hoch).
GLYPHS = {
    "A": [".####.", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    "C": [".####.", "##..##", "##....", "##....", "##....", "##..##", ".####."],
    "D": ["#####.", "##..##", "##..##", "##..##", "##..##", "##..##", "#####."],
    "E": ["######", "##....", "##....", "#####.", "##....", "##....", "######"],
    "F": ["######", "##....", "##....", "#####.", "##....", "##....", "##...."],
    "G": [".####.", "##..##", "##....", "##.###", "##..##", "##..##", ".####."],
    "H": ["##..##", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    "I": ["####", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    "M": ["##...##", "###.###", "##.#.##", "##.#.##", "##...##", "##...##", "##...##"],
    "N": ["##...##", "###..##", "##.#.##", "##..###", "##...##", "##...##", "##...##"],
    "O": [".####.", "##..##", "##..##", "##..##", "##..##", "##..##", ".####."],
    "R": ["#####.", "##..##", "##..##", "#####.", "##.##.", "##..##", "##..##"],
    "S": [".#####", "##....", "##....", ".####.", "....##", "....##", "#####."],
    "T": ["######", "..##..", "..##..", "..##..", "..##..", "..##..", "..##.."],
    "W": ["##...##", "##...##", "##...##", "##.#.##", "##.#.##", "###.###", "##...##"],
}

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "design" / "original-assets"
DST = ROOT / "pokemon-watchface" / "assets" / "default.s"


def render_word(word):
    glyphs = [GLYPHS[c] for c in word]
    cols = sum(len(g[0]) for g in glyphs) + len(glyphs) - 1  # 1 Zelle Abstand
    width = cols * WEEK_CELL
    if width > WEEK_SIZE[0]:
        raise SystemExit(f"{word} ist zu breit ({width}px > {WEEK_SIZE[0]}px)")
    im = Image.new("RGBA", WEEK_SIZE, (0, 0, 0, 0))
    x0 = WEEK_SIZE[0] - width
    for g in glyphs:
        for y, row in enumerate(g):
            for x, c in enumerate(row):
                if c == "#":
                    im.paste(INK, (x0 + x * WEEK_CELL, y * WEEK_CELL,
                                   x0 + (x + 1) * WEEK_CELL, (y + 1) * WEEK_CELL))
        x0 += (len(g[0]) + 1) * WEEK_CELL
    return im


def scaled(im):
    size = tuple(max(1, round(v * SCALE)) for v in im.size)
    return im.resize(size, Image.LANCZOS)


def main():
    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir(parents=True)

    for src in sorted(SRC.rglob("*.png")):
        rel = src.relative_to(SRC).as_posix()
        out = DST / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(src)

        if rel == "icon.png":
            shutil.copy(src, out)  # Vorschaubild in der Zepp-App, bleibt wie es ist
        elif rel == "bg.png":
            small = scaled(im.convert("RGB"))
            bg = Image.new("RGB", SCREEN, FILL)
            bg.paste(small, ((SCREEN[0] - small.width) // 2, (SCREEN[1] - small.height) // 2))
            bg.save(out)
        elif rel.startswith("week/"):
            continue  # wird unten neu gerendert
        else:
            im = im.convert("RGBA")
            if rel.startswith("time/"):
                im = im.resize((round(im.width * TIME_ZOOM), round(im.height * TIME_ZOOM)), Image.NEAREST)
            scaled(im).save(out)

    (DST / "week").mkdir(exist_ok=True)
    for i, day in enumerate(WEEKDAYS, start=1):
        scaled(render_word(day)).save(DST / "week" / f"{i}.png")

    w, h = round(SCREEN[0] * SCALE), round(SCREEN[1] * SCALE)
    print(f"SCALE={SCALE}: Design {w}x{h}, Rand links/rechts {(SCREEN[0] - w) // 2}px, "
          f"oben/unten {(SCREEN[1] - h) // 2}px")


if __name__ == "__main__":
    main()
