# Pokemon Battle – Zepp-OS-Watchface

Watchface für die Amazfit Active 2 (Square), 390×450. Gebaut wird per GitHub Actions
(`zeus build`), die Installationsseite mit QR-Codes liegt auf GitHub Pages:

**https://marvinstow-ai1.github.io/watchface/**

## Installieren
1. Zepp-App → Profil → Active 2 Square → ganz unten **Entwicklermodus**
   (falls nicht sichtbar: Profil → Einstellungen → Über → 7× aufs Logo tippen)
2. Oben rechts **Scannen** → auf der Seite den markierten **QR A** (Active 2 Square) scannen → Installation bestätigen
3. Klappt A nicht: **QR B** probieren
4. Auf der Uhr lange aufs Zifferblatt drücken → **Pokemon Battle** wählen

Jeder Push auf `main` baut neu und aktualisiert die Seite.

## Rand / Skalierung
Die Originalgrafiken liegen in `design/original-assets/`. `tools/inset_layout.py` verkleinert sie
(aktuell `SCALE = 0.86`) und setzt sie mittig nach `pokemon-watchface/assets/default.s/`, damit die
runden Display-Ecken nichts abschneiden. Bei Änderung von `SCALE` denselben Wert in
`pokemon-watchface/watchface/index.js` eintragen und das Skript erneut ausführen.
