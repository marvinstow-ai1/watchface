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

Battle-Modus (--battle battles/<name>/): Lugia und Gengar fallen aus dem Hintergrund, stattdessen
laufen die Sprites aus battle.json (GIF/APNG/PNG) als Animation in den beiden Plätzen
(alle Frames, Endlosschleife, fps aus den Frame-Dauern).

--preview-out <ordner>: leerer Hintergrund (ohne Monster) + slots.json für die Web-App-Vorschau.

Ergebnis: <projekt>/assets/default.s/; SCALE und die Layout-Werte werden in den
generierten Block von <projekt>/watchface/index.js eingetragen.

Nutzung: python3 tools/inset_layout.py [--scale 0.9] [--project pokemon-watchface]
"""
import argparse
import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageOps, ImageSequence

SCALE = 0.92  # Standard (Referenz: Kompakt 92); per --scale überschreibbar
TIME_ZOOM = 6 / 5  # Uhrzeit-Pixel 5px -> 6px (Ziffern 48x36)
SEC_ZOOM = 3 / 5  # Sekunden-Pixel 5px -> 3px (Ziffern 24x18)

# Kompaktes Layout (Koordinaten im Original-Design), Platzierung nach der Referenz des Users:
# Uhrzeit (36px hoch) oben links, Gegner-HP-Box direkt darunter, Lugia rechts knapp unter
# der Sekundenhöhe, darunter Wochentag/HP-Box/Menü ohne großen Leerraum.
DESIGN_H = 378  # Höhe des neu zusammengesetzten Designs (statt 450)
BOX_DY = 4  # Gegner-HP-Box rutscht unter die größere Uhrzeit
LUGIA_DY = 23  # Lugia beginnt knapp unter den Sekunden
BOTTOM_FROM, BOTTOM_DY = 226, -72  # alles ab y=226 (Gengar, HP-Box, Menü) rückt nach oben
PIECES = [  # (Ausschnitt im Original, Verschiebung)
    ((0, BOTTOM_FROM, 390, 450), BOTTOM_DY),
    ((15, 33, 219, 81), BOX_DY),  # Gegner-HP-Box
    ((229, 0, 375, 142), LUGIA_DY),  # Lugia
]
GENGAR_AREA = (40, 226, 172, 339)  # im Original; wird im Battle-Modus geleert

# Plätze für die Monster im kompakten Design (x0, y0, x1, y1). Sprites bleiben in Originalgröße
# (1:1 Bildschirmpixel, optional ganzzahlig gezoomt); nur wenn sie größer als der Platz sind, werden
# sie auf die größte passende Größe verkleinert. Waagerecht zentriert; oben (Gegner) senkrecht
# zentriert, unten (eigenes Monster) steht es auf der Menübox.
SLOTS = {
    "top": (224, 22, 382, 164),  # Gegner (Frontansicht), wo Lugia war
    "bottom": (40, 88, 172, 262),  # eigenes Monster (Rückansicht), wo Gengar war
}
MAX_FPS = 30
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


def compose_bg(src, monsters=True):
    """Original-Hintergrund in Bausteine zerlegen und kompakt neu zusammensetzen.
    monsters=False: ohne Lugia und Gengar (Plätze für animierte Sprites)."""
    if not monsters:
        src = src.copy()
        src.paste(FILL, GENGAR_AREA)
    design = Image.new("RGB", (SCREEN[0], DESIGN_H), FILL)
    for (x0, y0, x1, y1), dy in PIECES:
        if not monsters and dy == LUGIA_DY:
            continue
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


def screen_bg(monsters=True):
    small = scaled(compose_bg(Image.open(SRC / "bg.png").convert("RGB"), monsters))
    bg = Image.new("RGB", SCREEN, FILL)
    bg.paste(small, ((SCREEN[0] - small.width) // 2, (SCREEN[1] - small.height) // 2))
    return bg


def load_sprite(path, flip=False):
    """Alle Frames eines GIF/APNG/PNG als RGBA (zusammengesetzt), auf gemeinsamen Inhalt
    zugeschnitten; dazu die Bildrate aus den Frame-Dauern."""
    im = Image.open(path)
    frames, durations = [], []
    for f in ImageSequence.Iterator(im):
        frames.append(f.convert("RGBA"))
        durations.append(f.info.get("duration") or 100)
    boxes = [f.getchannel("A").getbbox() for f in frames]
    boxes = [b for b in boxes if b]
    if not boxes:
        raise SystemExit(f"{path}: keine sichtbaren Pixel (Hintergrund nicht transparent?)")
    box = (min(b[0] for b in boxes), min(b[1] for b in boxes),
           max(b[2] for b in boxes), max(b[3] for b in boxes))
    frames = [f.crop(box) for f in frames]
    if flip:
        frames = [ImageOps.mirror(f) for f in frames]
    fps = round(1000 * len(durations) / sum(durations))
    return frames, max(1, min(MAX_FPS, fps))


def slot_on_screen(key):
    """Platz in Bildschirm-Pixeln (das Design ist um SCALE verkleinert und zentriert)."""
    ox = (SCREEN[0] - round(SCREEN[0] * SCALE)) // 2
    oy = (SCREEN[1] - round(DESIGN_H * SCALE)) // 2
    x0, y0, x1, y1 = SLOTS[key]
    return ox + round(x0 * SCALE), oy + round(y0 * SCALE), ox + round(x1 * SCALE), oy + round(y1 * SCALE)


def fit_to_slot(frames, key, zoom=1):
    """Sprite in Originalgröße (mal zoom, pixelgenau) in den Platz setzen; nur wenn es zu groß
    ist, auf die größte passende Größe verkleinern. Liefert Frames und Bildschirm-Position."""
    x0, y0, x1, y1 = slot_on_screen(key)
    if zoom > 1:
        frames = [fr.resize((fr.width * zoom, fr.height * zoom), Image.NEAREST) for fr in frames]
    w, h = frames[0].size
    f = min(1, (x1 - x0) / w, (y1 - y0) / h)
    if f < 1:
        size = (max(1, round(w * f)), max(1, round(h * f)))
        frames = [fr.resize(size, Image.LANCZOS) for fr in frames]
        w, h = size
    x = x0 + (x1 - x0 - w) // 2
    y = y0 + (y1 - y0 - h) // 2 if key == "top" else y1 - h
    return frames, (x, y)


def build_anims(battle_dir, dst):
    cfg = json.loads((battle_dir / "battle.json").read_text())
    anims = {}
    (dst / "anim").mkdir(exist_ok=True)
    for key in ("top", "bottom"):
        frames, fps = load_sprite(battle_dir / cfg[key], cfg.get(f"flip_{key}", False))
        zoom = max(1, min(4, int(cfg.get(f"zoom_{key}", 1))))
        frames, (x, y) = fit_to_slot(frames, key, zoom)
        for i, fr in enumerate(frames):
            fr.save(dst / "anim" / f"{key}_{i}.png")
        anims[key] = {"x": x, "y": y, "fps": fps, "frames": len(frames)}  # Bildschirm-Pixel
        print(f"{cfg['name']} {key}: {cfg[key]} (Zoom {zoom}) -> {len(frames)} Frames, {fps} fps, "
              f"{frames[0].width}x{frames[0].height} px bei ({x},{y})")
    return cfg, anims


def write_preview(out):
    """Bildschirm ohne Monster, mit Beispiel-Uhrzeit/-Datum usw., plus Platz-Koordinaten
    (Bildschirm-Pixel) für die Vorschau in der Web-App."""
    import tempfile

    out.mkdir(parents=True, exist_ok=True)
    ox = (SCREEN[0] - round(SCREEN[0] * SCALE)) // 2
    oy = (SCREEN[1] - round(DESIGN_H * SCALE)) // 2
    X = lambda x: ox + round(x * SCALE)
    Y = lambda y: oy + round(y * SCALE)
    YB = lambda y: Y(y + BOTTOM_DY)
    L = lambda v: round(v * SCALE)
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        generate_assets(d, monsters=False)
        bg = Image.open(d / "bg.png").convert("RGBA")

        def put(name, x, y):
            im = Image.open(d / name).convert("RGBA")
            bg.alpha_composite(im, (x, y))
            return im.width

        # gleiche Positionen wie in watchface/index.js
        x = X(20)
        for n in ["time/1.png", "time/2.png", "time/colon.png", "time/3.png", "time/4.png"]:
            x += put(n, x, Y(0))
        x = X(20) + 4 * L(48) + L(18) + L(4)
        for n in ["sec/5.png", "sec/6.png"]:
            x += put(n, x, Y(0))
        put("week/1.png", X(369 - 222), YB(250))
        x = X(232)
        for n in ["date/0.png", "date/5.png"]:
            x += put(n, x, YB(298))
        put("date/dot.png", X(282), YB(298))
        x = X(290)
        for n in ["date/1.png", "date/0.png"]:
            x += put(n, x, YB(298))
        put("shoe.png", X(17), YB(368))
        x = X(45)
        for c in "4512":
            x += put(f"small/{c}.png", x, YB(368))
        put("batt/3.png", X(17), YB(403))
        x = X(45)
        for n in ["small/9.png", "small/3.png", "small/pct.png"]:
            x += put(n, x, YB(403))
        bg.convert("RGB").save(out / "bg.png")
    slots = {k: [ox + round(x0 * SCALE), oy + round(y0 * SCALE), ox + round(x1 * SCALE), oy + round(y1 * SCALE)]
             for k, (x0, y0, x1, y1) in SLOTS.items()}
    (out / "slots.json").write_text(json.dumps({"scale": SCALE, "screen": SCREEN, "slots": slots}))


def generate_assets(DST, monsters=True):
    """Alle Assets (außer Monster-Animationen) für das kompakte Layout nach DST schreiben."""
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
            screen_bg(monsters).save(out)
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


def write_layout_block(index_js, anims=None):
    js = index_js.read_text()
    block = (
        "// <generated: tools/inset_layout.py>\n"
        f"const SCALE = {SCALE}\n"
        f"const DESIGN_H = {DESIGN_H}\n"
        f"const BOTTOM_DY = {BOTTOM_DY}\n"
        f"const ANIM = {json.dumps(anims) if anims else 'null'}\n"
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
    ap.add_argument("--battle", type=Path, help="Ordner mit battle.json + Sprites")
    ap.add_argument("--preview-out", type=Path, help="nur Vorschau-Dateien für die Web-App schreiben")
    args = ap.parse_args()
    SCALE = args.scale
    if args.preview_out:
        write_preview(args.preview_out)
        return
    DST = args.project / "assets" / "default.s"

    generate_assets(DST, monsters=not args.battle)

    anims = None
    if args.battle:
        cfg, anims = build_anims(args.battle, DST)
    write_layout_block(args.project / "watchface" / "index.js", anims)

    w, h = round(SCREEN[0] * SCALE), round(DESIGN_H * SCALE)
    print(f"SCALE={SCALE}: Design {w}x{h}, Rand links/rechts {(SCREEN[0] - w) // 2}px, "
          f"oben/unten {(SCREEN[1] - h) // 2}px")


if __name__ == "__main__":
    main()
