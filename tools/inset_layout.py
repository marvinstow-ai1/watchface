#!/usr/bin/env python3
"""
Baut die Watchface-Assets aus dem Original-Design (design/original-assets/, 390x450):

- Kompaktes Layout: Der Hintergrund wird aus seinen Bausteinen (Gegner-HP-Box, Lugia,
  unterer Teil mit Gengar/HP-Box/Menü) neu zusammengesetzt, mit weniger Leerraum in der
  Mitte und einer Uhrzeit-Zeile über die ganze Breite oben (Lugia rutscht darunter).
- Uhrzeit-Ziffern pixelgenau vergrößert (TIME_ZOOM), Sekunden klein im selben Stil (SEC_ZOOM)
- Wochentage neu in fetter Pixelschrift (Stil der Uhrzeit, nur kleiner)
- Schritt-/Akku-Symbole auf Ziffern-Zellgröße, kleine Ziffern 1px enger
- alles gleichmäßig um SCALE verkleinert und mittig gesetzt, damit an den abgerundeten
  Ecken der Active 2 Square nichts abgeschnitten wird

Ergebnis: <projekt>/assets/default.s/; SCALE und die Layout-Werte werden in den
generierten Block von <projekt>/watchface/index.js eingetragen.

Nutzung: python3 tools/inset_layout.py [--scale 0.9] [--project pokemon-watchface]
"""
import argparse
import re
import shutil
from pathlib import Path

from PIL import Image

SCALE = 0.9  # Standard; per --scale überschreibbar
TIME_ZOOM = 7 / 5  # Uhrzeit-Pixel 5px -> 7px (Ziffern 56x42)
SEC_ZOOM = 3 / 5  # Sekunden-Pixel 5px -> 3px (Ziffern 24x18)

# Kompaktes Layout (Koordinaten im Original-Design). Die Uhrzeit-Zeile ist 42px hoch.
DESIGN_H = 392  # Höhe des neu zusammengesetzten Designs (statt 450)
BOX_DY = 10  # Gegner-HP-Box rutscht unter die größere Uhrzeit
LUGIA_DY = 46  # Lugia rutscht unter die Uhrzeit-Zeile
BOTTOM_FROM, BOTTOM_DY = 226, -58  # alles ab y=226 (Gengar, HP-Box, Menü) rückt nach oben
PIECES = [  # (Ausschnitt im Original, Verschiebung)
    ((0, BOTTOM_FROM, 390, 450), BOTTOM_DY),
    ((15, 33, 219, 81), BOX_DY),  # Gegner-HP-Box
    ((229, 0, 375, 142), LUGIA_DY),  # Lugia
]
SCREEN = (390, 450)
FILL = (248, 248, 248)  # Hintergrundfarbe des Designs
INK = (16, 16, 24, 255)  # Schriftfarbe des Designs

WEEK_CELL = 3  # Pixelgröße der Wochentag-Schrift (Original-Koordinaten)
WEEK_SIZE = (222, 21)  # Bildgröße wie im Original, Text rechtsbündig
WEEK_MAX_WIDTH = 207  # links davon steht Gengar (bis x=155); rechter Rand = Ende der HP-Leiste
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

ICON_CELL = (24, 18)  # Symbole (Schuh, Akku) so groß wie eine Ziffer
SMALL_PITCH = 23  # kleine Ziffern 24 -> 23px breit, damit 5-stellige Schritte in die Box passen

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "design" / "original-assets"


def render_word(word):
    glyphs = [GLYPHS[c] for c in word]
    ink = sum(len(g[0]) for g in glyphs) * WEEK_CELL
    gap = WEEK_CELL  # 1 Zelle Abstand; bei langen Wörtern (DONNERSTAG) etwas enger
    if ink + (len(glyphs) - 1) * gap > WEEK_MAX_WIDTH:
        gap = WEEK_CELL - 1
    width = ink + (len(glyphs) - 1) * gap
    if width > WEEK_MAX_WIDTH:
        raise SystemExit(f"{word} ist zu breit ({width}px > {WEEK_MAX_WIDTH}px)")
    im = Image.new("RGBA", WEEK_SIZE, (0, 0, 0, 0))
    x0 = WEEK_SIZE[0] - width
    for g in glyphs:
        for y, row in enumerate(g):
            for x, c in enumerate(row):
                if c == "#":
                    im.paste(INK, (x0 + x * WEEK_CELL, y * WEEK_CELL,
                                   x0 + (x + 1) * WEEK_CELL, (y + 1) * WEEK_CELL))
        x0 += len(g[0]) * WEEK_CELL + gap
    return im


def scaled(im):
    size = tuple(max(1, round(v * SCALE)) for v in im.size)
    return im.resize(size, Image.LANCZOS)


def fit_icon(im):
    """Symbol proportional auf Ziffern-Zellgröße bringen, zentriert in der Zelle."""
    f = min(ICON_CELL[0] / im.width, ICON_CELL[1] / im.height)
    icon = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
    cell = Image.new("RGBA", ICON_CELL, (0, 0, 0, 0))
    cell.paste(icon, ((ICON_CELL[0] - icon.width) // 2, (ICON_CELL[1] - icon.height) // 2))
    return cell


def compose_bg(src):
    """Original-Hintergrund in Bausteine zerlegen und kompakt neu zusammensetzen."""
    design = Image.new("RGB", (SCREEN[0], DESIGN_H), FILL)
    for (x0, y0, x1, y1), dy in PIECES:
        piece = src.crop((x0, y0, x1, y1))
        # nur Nicht-Hintergrund-Pixel übernehmen, damit sich Bausteine nicht überdecken
        mask = Image.new("L", piece.size, 0)
        px, mp = piece.load(), mask.load()
        for y in range(piece.height):
            for x in range(piece.width):
                if sum(abs(a - b) for a, b in zip(px[x, y], FILL)) > 12:
                    mp[x, y] = 255
        design.paste(piece, (x0, y0 + dy), mask)
    return design


def write_layout_block(index_js):
    js = index_js.read_text()
    block = (
        "// <generated: tools/inset_layout.py>\n"
        f"const SCALE = {SCALE}\n"
        f"const DESIGN_H = {DESIGN_H}\n"
        f"const BOTTOM_DY = {BOTTOM_DY}\n"
        "// </generated>"
    )
    js, n = re.subn(r"// <generated: tools/inset_layout.py>.*?// </generated>", block, js, flags=re.S)
    if n != 1:
        raise SystemExit(f"generierter Layout-Block nicht in {index_js} gefunden")
    index_js.write_text(js)


def main():
    global SCALE
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=SCALE)
    ap.add_argument("--project", type=Path, default=ROOT / "pokemon-watchface")
    args = ap.parse_args()
    SCALE = args.scale
    DST = args.project / "assets" / "default.s"

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
            small = scaled(compose_bg(im.convert("RGB")))
            bg = Image.new("RGB", SCREEN, FILL)
            bg.paste(small, ((SCREEN[0] - small.width) // 2, (SCREEN[1] - small.height) // 2))
            bg.save(out)
        elif rel.startswith("week/"):
            continue  # wird unten neu gerendert
        else:
            im = im.convert("RGBA")
            if rel.startswith("time/"):
                if rel != "time/colon.png":  # Sekunden: gleiche Schrift, klein
                    sec = im.resize((round(im.width * SEC_ZOOM), round(im.height * SEC_ZOOM)), Image.NEAREST)
                    (DST / "sec").mkdir(exist_ok=True)
                    scaled(sec).save(DST / "sec" / Path(rel).name)
                im = im.resize((round(im.width * TIME_ZOOM), round(im.height * TIME_ZOOM)), Image.NEAREST)
            elif rel == "shoe.png" or rel.startswith("batt/"):
                im = fit_icon(im)
            elif rel.startswith("small/"):
                im = im.crop((0, 0, SMALL_PITCH, im.height))
            scaled(im).save(out)

    (DST / "week").mkdir(exist_ok=True)
    for i, day in enumerate(WEEKDAYS, start=1):
        scaled(render_word(day)).save(DST / "week" / f"{i}.png")

    write_layout_block(args.project / "watchface" / "index.js")

    w, h = round(SCREEN[0] * SCALE), round(DESIGN_H * SCALE)
    print(f"SCALE={SCALE}: Design {w}x{h}, Rand links/rechts {(SCREEN[0] - w) // 2}px, "
          f"oben/unten {(SCREEN[1] - h) // 2}px")


if __name__ == "__main__":
    main()
