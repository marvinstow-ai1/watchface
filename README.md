# Pokemon Battle – Zepp-OS-Watchface

Watchface für die Amazfit Active 2 (Square), 390×450. Gebaut wird per GitHub Actions
(`zeus build`), die Installationsseite mit QR-Codes liegt auf GitHub Pages:

**https://marvinstow-ai1.github.io/watchface/**

## Installieren
1. Zepp-App → Profil → Active 2 Square → ganz unten **Entwicklermodus**
   (falls nicht sichtbar: Profil → Einstellungen → Über → 7× aufs Logo tippen)
2. Oben rechts **Scannen** → auf der Seite bei der gewünschten Variante im markierten Abschnitt (Active 2 Square) **QR B** scannen → Installation bestätigen
   (QR B / `zpkd1://` ist auf der Active 2 Square getestet; QR A ist nur eine Alternative)
3. Auf der Uhr lange aufs Zifferblatt drücken → **Pokemon Kompakt 92/90/88** oder **Pokemon Battle 86/84/82** wählen

Jeder Push auf `main` baut neu und aktualisiert die Seite.

## Layout / Varianten
Die Originalgrafiken liegen in `design/original-assets/`. `tools/inset_layout.py --scale 0.9` baut daraus
die Assets in `pokemon-watchface/assets/default.s/`:
- kompaktes Layout: Hintergrund aus seinen Bausteinen neu zusammengesetzt (weniger Leerraum in der Mitte,
  Lugia rechts neben Uhrzeit und Gegner-HP-Box)
- Uhrzeit (48x36) mit kleinen Sekunden (24x18) im selben Pixelstil, Platzierung nach Referenzbild
- Wochentage in fetter Pixelschrift, rechtsbündig mit dem Ende der HP-Leiste
- Schritt-/Akku-Symbole auf Ziffernhöhe
- alles um `SCALE` verkleinert und mittig gesetzt, damit die runden Display-Ecken nichts abschneiden

Das Skript schreibt `SCALE` und die Layout-Werte in den generierten Block von `watchface/index.js`.

Die CI baut mit `tools/build_variants.sh` mehrere Größen als eigene Watchfaces (je eigene appId):
- **Pokemon Kompakt 92/90/88**: aktuelles kompaktes Layout
- **Pokemon Battle 86/84/82**: bisheriges Layout, unverändert aus Commit `e25d517` gebaut

## Battles mit animierten Monstern
Web-App: **https://marvinstow-ai1.github.io/watchface/app/**. Dort Name eingeben und je ein GIF/APNG für
oben (Gegner, Frontansicht) und unten (eigenes Monster, Rückansicht) hochladen. Die App zeigt eine Vorschau
und speichert beim Klick auf „Bauen“ alles in einem Commit unter `battles/<name>/`, mit den Sprites und
`battle.json`. Die CI (`tools/build_battles.sh`) baut daraus je ein eigenes Watchface im Layout „Kompakt 92“:
Lugia und Gengar fallen weg, die Sprites laufen mit allen Frames in Endlosschleife (fps aus den
Frame-Dauern), pixelgenau eingepasst. Die appId ist fest aus dem Ordnernamen abgeleitet, ein erneutes
Hochladen unter demselben Namen ersetzt also das Watchface.

Die App braucht einen Fine-grained GitHub-Token nur für dieses Repo (Contents: Read and write,
Actions: Read). Er wird nur im Browser gespeichert.
