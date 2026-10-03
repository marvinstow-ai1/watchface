#!/usr/bin/env python3
"""
Nimmt die von `zeus build` erzeugte .zab und baut daraus einen statischen
Ordner (site/) für GitHub Pages + QR-Codes für den Zepp-Entwicklermodus.

Vorgehen nach dem Muster von ZMake (melianmiko/zmake, zmake/zab_patch.py):
  - Watchface:  QR = watchface://<host>/<pfad>/<name>.json
                JSON zeigt auf die .bin (= device.zip aus der .zpk)
  - Fallback:   QR = zpkd1://<host>/<pfad>/<name>.zpk  (direkte .zpk)

Nutzung: python3 tools/make_install.py <pfad/zur.zab> <https-basis-url> <ausgabeordner>
"""
import json
import sys
import time
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import qrcode


def qr(data: str, path: Path):
    img = qrcode.make(data, box_size=10, border=4)
    img.save(path)


def main():
    zab_path, base_url, out = Path(sys.argv[1]), sys.argv[2].rstrip("/"), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    zab = ZipFile(zab_path)
    manifest = json.loads(zab.read("manifest.json"))
    links = []

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

        sources = [p.get("deviceSource") for p in zpk_info.get("platforms", []) if "deviceSource" in p]
        meta = {
            "appid": app["app"]["appId"],
            "name": app["app"]["appName"],
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
        links.append((stem, sources, wf_qr, zpk_qr))
        print(f"{stem}: deviceSources={sources}\n  A: {wf_qr}\n  B: {zpk_qr}")

    # Kleine Übersichtsseite
    rows = "".join(
        f"<h2>{s}</h2><p>deviceSources: {src}</p>"
        f"<p><b>A (zuerst probieren)</b><br><img src='{s}_qr_watchface.png' width=300><br><code>{a}</code></p>"
        f"<p><b>B (Fallback)</b><br><img src='{s}_qr_zpkd1.png' width=300><br><code>{b}</code></p>"
        for s, src, a, b in links
    )
    (out / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'>"
        "<title>Watchface QR</title><body style='font-family:sans-serif;padding:16px'>"
        "<h1>Pokemon Battle – QR-Codes</h1>"
        "<p>Zepp-App → Profil → Gerät → Entwicklermodus → Scannen</p>" + rows
    )


if __name__ == "__main__":
    main()
