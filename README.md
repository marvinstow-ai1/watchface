# Pokemon Battle – Zepp-OS-Watchface

Watchface für die Amazfit Active 2 (Square), 390×450. Gebaut wird per GitHub Actions
(`zeus build`), die Installationsseite mit QR-Codes liegt auf GitHub Pages:

**https://marvinstow-ai1.github.io/watchface/**

## Installieren
1. Zepp-App → Profil → Active 2 Square → ganz unten **Entwicklermodus**
   (falls nicht sichtbar: Profil → Einstellungen → Über → 7× aufs Logo tippen)
2. Oben rechts **Scannen** → auf der Seite bei der gewünschten Variante im markierten Abschnitt (Active 2 Square) **QR B** scannen → Installation bestätigen
   (QR B / `zpkd1://` ist auf der Active 2 Square getestet; QR A ist nur eine Alternative)
3. Auf der Uhr lange aufs Zifferblatt drücken → **Pokemon Battle 86** (bzw. 84/82) wählen

Jeder Push auf `main` baut neu und aktualisiert die Seite.

## Rand / Skalierung / Varianten
Die Originalgrafiken liegen in `design/original-assets/`. `tools/inset_layout.py --scale 0.86` baut daraus
die Assets in `pokemon-watchface/assets/default.s/`: Uhrzeit-Ziffern vergrößert (`TIME_ZOOM`), Wochentage
in fetter Pixelschrift neu gezeichnet (rechtsbündig mit dem Ende der HP-Leiste), Schritt-/Akku-Symbole auf
Ziffernhöhe, alles um `SCALE` verkleinert und mittig gesetzt, damit die runden Display-Ecken nichts
abschneiden. Das Skript trägt `SCALE` auch in `watchface/index.js` ein.

Die CI baut mit `tools/build_variants.sh` mehrere Größen (aktuell 86, 84, 82 %) als eigene Watchfaces
(„Pokemon Battle 86“ usw., je eigene appId), die gleichzeitig installiert sein können.
