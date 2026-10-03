#!/usr/bin/env python3
"""
Nimmt die von `zeus build` erzeugte .zab und baut daraus einen statischen
Ordner (site/) für GitHub Pages + QR-Codes für den Zepp-Entwicklermodus.

Vorgehen nach dem Muster von ZMake (melianmiko/zmake, zmake/zab_patch.py):
  - Watchface:  QR = watchface://<host>/<pfad>/<name>.json
                JSON zeigt auf die .bin (= device.zip aus der .zpk)
  - Fallback:   QR = zpkd1://<host>/<pfad>/<name>.zpk  (direkte .zpk)

Nutzung: python3 tools/make_install.py <pfad/zur.zab> <https-basis-url> <ausgabeordner> [devices.json]

Optional: devices.json von Zepp (Zeus-Geräteliste), um deviceSource-IDs Gerätenamen
zuzuordnen. Das Paket, das die Ziel-Uhr (TARGET_NAME) enthält, steht oben.
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
    return names


def qr(data: str, path: Path):
    img = qrcode.make(data, box_size=10, border=4)
    img.save(path)


def main():
    zab_path, base_url, out = Path(sys.argv[1]), sys.argv[2].rstrip("/"), Path(sys.argv[3])
    device_names = load_device_names(sys.argv[4] if len(sys.argv) > 4 else None)
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

        # deviceSources stehen in der app.json der device.zip (targets.*.platforms)
        sources = [
            p["deviceSource"]
            for t in app.get("targets", {}).values()
            for p in t.get("platforms", [])
            if "deviceSource" in p
        ]
        screen = ", ".join(
            f"{p.get('screenType', '?')} {p.get('screenResolution', '?')} {p.get('cpuPlatform', '?')}"
            for p in zpk_info.get("platforms", [])
        )
        devices = sorted({device_names.get(int(s), str(s)) for s in sources})
        is_target = any(TARGET_NAME.lower() in d.lower() for d in devices)
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
        links.append((not is_target, stem, screen, devices, wf_qr, zpk_qr))
        print(f"{stem}: [{screen}] deviceSources={sources}\n  devices={devices}\n  A: {wf_qr}\n  B: {zpk_qr}")

    links.sort()
    if not any(not other for other, *_ in links):
        print(f"WARNUNG: kein Paket mit '{TARGET_NAME}' gefunden (Geräteliste fehlt?)")

    # Kleine Übersichtsseite
    rows = "".join(
        ("<hr>" if other else f"<h2 style='color:#c00'>&#9733; {TARGET_NAME}: diese QR-Codes nehmen</h2>")
        + f"<h3>{', '.join(devs)}</h3><p>{scr} &middot; Paket {s}</p>"
        f"<p><b>A (zuerst probieren)</b><br><img src='{s}_qr_watchface.png' width=300><br><code>{a}</code></p>"
        f"<p><b>B (Fallback)</b><br><img src='{s}_qr_zpkd1.png' width=300><br><code>{b}</code></p>"
        + ("" if other else "<hr><h2>Andere Geräte</h2>")
        for other, s, scr, devs, a, b in links
    )
    (out / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'>"
        "<title>Watchface QR</title><body style='font-family:sans-serif;padding:16px'>"
        "<h1>Pokemon Battle – QR-Codes</h1>"
        "<p>Zepp-App → Profil → Gerät → Entwicklermodus → Scannen</p>" + rows
    )


if __name__ == "__main__":
    main()
