#!/usr/bin/env python3
"""
Nimmt die von `zeus build` erzeugte .zab und baut daraus einen statischen
Ordner (site/) für GitHub Pages + QR-Codes für den Zepp-Entwicklermodus.

Vorgehen nach dem Muster von ZMake (melianmiko/zmake, zmake/zab_patch.py):
  - Watchface:  QR = watchface://<host>/<pfad>/<name>.json
                JSON zeigt auf die .bin (= device.zip aus der .zpk)
  - Fallback:   QR = zpkd1://<host>/<pfad>/<name>.zpk  (direkte .zpk)

Nutzung: python3 tools/make_install.py <https-basis-url> <ausgabeordner> <devices.json> <zab> [<zab> ...]

devices.json (Zeus-Geräteliste von Zepp) ordnet deviceSource-IDs Gerätenamen zu; fehlt sie,
leere Datei oder "{}" übergeben. Pro .zab (Variante) zeigt die Seite das Paket der Ziel-Uhr
(TARGET_NAME) oben, die Pakete für andere Uhren eingeklappt.
"""
import json
import sys
import time
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import qrcode

TARGET_NAME = "Active 2 Square"


def load_device_names(path):
    """deviceSource -> Gerätename aus der Zeus-Geräteliste (Struktur generisch durchsuchen)."""
    names = {}
    if not path or not Path(path).is_file():
        return names
    try:
        data = json.loads(Path(path).read_text())
    except ValueError:
        return names

    def walk(node):
        if isinstance(node, dict):
            src = node.get("deviceSource")
            name = node.get("productName") or node.get("deviceName") or node.get("name")
            if src is not None and isinstance(name, str):
                for s in src if isinstance(src, list) else [src]:
                    try:
                        names.setdefault(int(s), name)
                    except (TypeError, ValueError):
                        pass
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    print(f"Geräteliste: {len(names)} deviceSources bekannt")
    return names


def qr(data: str, path: Path):
    img = qrcode.make(data, box_size=10, border=4)
    img.save(path)


def process_zab(zab_path, base_url, out, device_names):
    """Entpackt eine .zab nach out/ und liefert (appName, [(is_target, stem, screen, devices, A, B)])."""
    zab = ZipFile(zab_path)
    manifest = json.loads(zab.read("manifest.json"))
    links = []
    app_name = None

    for zpk_info in manifest["zpks"]:
        name = zpk_info["name"]                       # z.B. xyz.zpk
        stem = name[:-4]
        zpk_bytes = zab.read(name)
        (out / name).write_bytes(zpk_bytes)          # für zpkd1-Fallback

        zpk = ZipFile(BytesIO(zpk_bytes))
        device_zip = zpk.read("device.zip")
        (out / f"{stem}.bin").write_bytes(device_zip)

        with ZipFile(BytesIO(device_zip)) as d:
            app = json.loads(d.read("app.json"))
            icon = app["app"].get("icon", "icon.png")
            preview = None
            for cand in (f"assets/{icon}",) + tuple(n for n in d.namelist() if n.endswith(icon)):
                try:
                    preview = d.read(cand)
                    break
                except KeyError:
                    continue
        if preview:
            (out / f"{stem}.png").write_bytes(preview)
        app_name = app["app"]["appName"]

        # deviceSources stehen in der app.json der device.zip (platforms bzw. targets.*.platforms)
        platforms = list(app.get("platforms", []))
        for t in app.get("targets", {}).values():
            platforms += t.get("platforms", [])
        sources = [p["deviceSource"] for p in platforms if "deviceSource" in p]
        screen = ", ".join(
            f"{p.get('screenType', '?')} {p.get('screenResolution', '?')} {p.get('cpuPlatform', '?')}"
            for p in zpk_info.get("platforms", [])
        )
        devices = sorted({device_names.get(int(s), str(s)) for s in sources})
        norm = lambda t: " ".join("".join(c if c.isalnum() else " " for c in t.lower()).split())
        is_target = any(norm(TARGET_NAME) in norm(d) for d in devices)  # "Active 2 (Square)"
        meta = {
            "appid": app["app"]["appId"],
            "name": app_name,
            "updated_at": round(time.time() / 1000),
            "url": f"{base_url}/{stem}.bin",
            "preview": f"{base_url}/{stem}.png",
            "devices": sources,
        }
        (out / f"{stem}.json").write_text(json.dumps(meta))

        wf_qr = base_url.replace("https:", "watchface:") + f"/{stem}.json"
        zpk_qr = base_url.replace("https:", "zpkd1:") + f"/{name}"
        qr(wf_qr, out / f"{stem}_qr_watchface.png")
        qr(zpk_qr, out / f"{stem}_qr_zpkd1.png")
        links.append((is_target, stem, screen, devices, wf_qr, zpk_qr))
        print(f"{app_name} {stem}: [{screen}] deviceSources={sources}\n  devices={devices}\n  A: {wf_qr}\n  B: {zpk_qr}")

    if not any(t for t, *_ in links):
        print(f"WARNUNG: {app_name}: kein Paket mit '{TARGET_NAME}' gefunden (Geräteliste fehlt?)")
    return app_name, links


def package_html(stem, screen, devices, a, b):
    return (
        f"<h3>{', '.join(devices)}</h3><p>{screen} &middot; Paket {stem}</p>"
        f"<p><b>B (zpkd1, auf der Active 2 Square getestet)</b><br><img src='{stem}_qr_zpkd1.png' width=300><br><code>{b}</code></p>"
        f"<p><b>A (watchface, Alternative)</b><br><img src='{stem}_qr_watchface.png' width=300><br><code>{a}</code></p>"
    )


def main():
    base_url, out = sys.argv[1].rstrip("/"), Path(sys.argv[2])
    device_names = load_device_names(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)

    sections = []
    for zab_path in sys.argv[4:]:
        app_name, links = process_zab(Path(zab_path), base_url, out, device_names)
        target = [l for l in links if l[0]]
        others = [l for l in links if not l[0]]
        html = f"<hr><h2>{app_name}</h2>"
        html += "".join(
            f"<p style='color:#c00'><b>&#9733; {TARGET_NAME}: diese QR-Codes nehmen</b></p>" + package_html(*l[1:])
            for l in target
        )
        if others:
            html += "<details><summary>Andere Uhren</summary>" + "".join(package_html(*l[1:]) for l in others) + "</details>"
        sections.append(html)

    (out / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'>"
        "<title>Watchface QR</title><body style='font-family:sans-serif;padding:16px'>"
        "<h1>Pokemon Battle – QR-Codes</h1>"
        "<p>Zepp-App → Profil → Gerät → Entwicklermodus → Scannen. Jede Variante ist ein eigenes "
        "Watchface (Zahl = Größe in %), alle können gleichzeitig installiert sein.</p>" + "".join(sections)
    )


if __name__ == "__main__":
    main()
