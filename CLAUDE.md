# Auftrag: Zepp-OS-Watchface per GitHub Actions bauen und installierbar machen

## Ziel
Das Watchface in `pokemon-watchface/` soll auf eine **Amazfit Active 2 Square** (390×450, Zepp OS) kommen,
**ohne lokalen PC**. Gebaut wird in GitHub Actions, gehostet auf GitHub Pages, installiert per QR-Code
im Entwicklermodus der Zepp-App.

Am Ende braucht der User **nur eine URL** (GitHub-Pages-Seite mit QR-Codes), die er auf einem beliebigen
Bildschirm öffnet und mit der Zepp-App scannt.

## Was schon da ist
| Pfad | Inhalt |
|---|---|
| `pokemon-watchface/` | Fertiges Zepp-OS-Projekt (API 3.0, `app.json`, `watchface/index.js`, Bild-Assets in `assets/default.s/`) |
| `.github/workflows/build-watchface.yml` | Workflow: `zeus build` → `tools/make_install.py` → GitHub Pages |
| `tools/make_install.py` | Entpackt die `.zab`, legt `.bin`/`.json`/`.zpk` + QR-Codes + `index.html` in `site/` |
| `vorschau.png` | So soll es aussehen |

**Wichtig: Die Grafiken und das Layout NICHT ändern.** Sie sind fertig und abgenommen.

## Schritte
1. **Repo vorbereiten:** Alles aus diesem Paket ins Repo-Root committen, mit der Ordnerstruktur genau wie oben.
2. **GitHub Pages aktivieren:** Repo → Settings → Pages → Source: **GitHub Actions**.
   Pages braucht bei Free-Accounts ein **öffentliches Repo**. Vorher mit dem User klären, ob das okay ist.
3. **Workflow laufen lassen** (Push auf `main` oder manuell starten) und die Logs prüfen.
4. **`zeus build` zum Laufen bringen.** Das ist die wahrscheinlichste Fehlerquelle:
   - Falls Zeus interaktiv nachfragt oder hängt: Optionen prüfen (`zeus build --help`) und ggf. per `yes |` oder Flags nicht-interaktiv machen.
   - Falls Zeus das Target bzw. die Plattform in `app.json` nicht akzeptiert: Aktuell steht da `"platforms": [{ "st": "s", "dw": 390 }]` mit Target `default` und Assets in `assets/default.s/`.
     Zeus listet die Geräte aus `https://upload-cdn.zepp.com/zeppos/devkit/zeus/v1/devices.json`. Den `deviceSource` bzw. das Muster für die **Active 2 Square** dort nachschlagen und `app.json` passend anpassen (z.B. explizite `deviceSource` in `platforms`).
     Asset-Ordner und Target-Namen konsistent halten (`assets/<target>.<st>/`).
   - Falls `apiVersion` 3.0 Probleme macht: Die Active 2 läuft auf Zepp OS 4/5, also passende API-Version wählen.
   - Wenn Zeus doch einen Login verlangt, **stoppen und dem User Bescheid geben**. Keine Zugangsdaten ins Repo.
5. **Ergebnis prüfen:** Unter der Pages-URL muss `index.html` mit zwei QR-Codes liegen:
   - **A (watchface://…json)**: zuerst probieren
   - **B (zpkd1://…zpk)**: Fallback
   Außerdem prüfen, ob die `.json`, `.bin` und `.zpk` unter der URL tatsächlich abrufbar sind (HTTP 200).
6. **Dem User die Pages-URL geben** und diese Anleitung dazu:
   - Zepp-App → Profil → Active 2 Square → ganz unten **Entwicklermodus** (falls nicht sichtbar: Profil → Einstellungen → Über → 7× aufs Logo tippen)
   - Oben rechts **Scannen** → QR A scannen → Installation bestätigen
   - Wenn A nicht klappt: QR B probieren
   - Auf der Uhr lange aufs Zifferblatt drücken → **Pokemon Battle** wählen

## Hintergrund zur Installationsmethode (unverifiziert!)
Der offizielle Weg wäre `zeus preview`. Der braucht aber einen Zepp-Login im Browser und geht in CI nicht.
Deshalb nutzen wir das Schema, das Community-Tools verwenden (Quelle: `melianmiko/zmake`, Datei `zmake/zab_patch.py`):
- Watchface: `watchface://<host>/<pfad>/<name>.json` → JSON mit `url` zur `.bin` (= `device.zip` aus der `.zpk`)
- App/Fallback: `zpkd1://<host>/<pfad>/<name>.zpk`

Ob die aktuelle Zepp-App das für die Active 2 Square akzeptiert, ist **nicht garantiert**. Wenn beide QR-Codes scheitern:
- ZMake-Repo und amazfitwatchfaces.com-Forum nach aktuellen Hinweisen zum QR-Format durchsuchen
- Ergebnis ehrlich an den User melden. Seine Fallback-Optionen: Foto-Zifferblatt in der Zepp-App oder `zeus preview` auf einem privaten PC.

## Regeln
- Den User vor dem Öffentlichmachen des Repos fragen.
- Keine Zepp-Zugangsdaten oder Tokens committen.
- Kurz und ehrlich berichten: was geklappt hat, was nicht und was der User als Nächstes tun muss.
