#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beat_asset.py — swap the visual asset of one Stage-9 beat, from the edit room.

  python tools/beat_asset.py <slug> --list
      print the asset library as JSON [{id, url, kind, video}] for the picker

  python tools/beat_asset.py <slug> --set <n> --asset <id>
      point beat <n> at an asset already in assets/

  python tools/beat_asset.py <slug> --set <n> --src "<url | local path>"
      fetch a new resource → assets/<sub>/beat<n>_custom_<n>.<ext>, point beat <n> at it

Patches the `asset` (and `tipo`, image↔vídeo) cell of that beat's row in
06-shotlist.md, then rebuilds 09-timeline.json (keeping the edit room's
approved/fix/nudge). Prints JSON {n, asset, file, state, tipo, motion}.
serve.py's /beat-asset endpoint calls this.

Not for `acamara` / `negro` beats — those don't carry an asset.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import assemble as A  # noqa: E402
import pull_assets as PA  # noqa: E402

EP_DIR = A.EP_DIR
SUBS = ("graphic", "archive", "video", "stock", "kb", "ai", "intro")
SUB_KIND = {"graphic": "gráfico", "archive": "archivo", "video": "stock",
            "stock": "stock", "kb": "kb", "ai": "ia", "intro": "stock"}
VIDEO_EXT = (".mp4", ".mov", ".webm")
NO_ASSET = {"acamara", "a-cámara", "a-camara", "narrador", "negro"}


def asset_library(slug):
    ep = EP_DIR / slug
    out = []
    for sub in SUBS:
        d = ep / "assets" / sub
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if f.is_file() and f.suffix.lower() in A.MEDIA_EXT:
                out.append({
                    "id": f.stem, "sub": sub,
                    "url": f"/episodes/{slug}/assets/{sub}/{f.name}",
                    "video": f.suffix.lower() in VIDEO_EXT,
                    "kind": SUB_KIND[sub],
                })
    # de-dupe by id, first sub wins (matches assemble._asset_index order)
    seen, uniq = set(), []
    for a in out:
        if a["id"] in seen:
            continue
        seen.add(a["id"])
        uniq.append(a)
    return uniq


def _row_cells(line):
    """A shotlist table row -> its '|'-split segments (seg[1]=#, seg[5]=tipo,
    seg[6]=asset, ... seg[10]=frag) plus the leading/trailing ''."""
    return line.split("|")


def patch_shotlist(slug, n, asset, tipo=None):
    """Replace the asset (and optionally tipo) cell of beat <n>'s spine row.
    Returns the previous asset id."""
    f = EP_DIR / slug / "06-shotlist.md"
    lines = f.read_text(encoding="utf-8").splitlines()
    in_spine = False
    for i, ln in enumerate(lines):
        if "Timeline" in ln and "la espina" in ln:
            in_spine = True
            continue
        if in_spine and ln.startswith("## "):
            break
        if not (in_spine and ln.lstrip().startswith("|")):
            continue
        seg = _row_cells(ln)
        if len(seg) < 11 or seg[1].strip() != str(n):
            continue
        old = seg[6].strip()
        seg[6] = f" {asset} "
        if tipo:
            seg[5] = f" {tipo} "
        lines[i] = "|".join(seg)
        f.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return old
    raise SystemExit(f"no encuentro el beat {n} en la tabla 'Timeline — la espina'")


def fetch_new(slug, n, src):
    """Fetch a URL / read a local path → assets/<sub>/beat<n>_custom_<n><ext>.
    Returns (asset_id, tipo)."""
    keys = PA.load_env()
    url, s = src, "custom"
    if url.lower().startswith("http") and ("pexels.com" in url or "pixabay.com" in url):
        direct, dsrc = PA._resolve_media_page(url, keys)
        if direct:
            url, s = direct, dsrc
    data, final = PA._fetch(url, s)
    if data is None:
        raise SystemExit(f"no se pudo traer el recurso: {final}")
    ext = PA._ext_for(data, final, s)
    sub = "video" if ext in VIDEO_EXT else "archive"
    dst = EP_DIR / slug / "assets" / sub
    dst.mkdir(parents=True, exist_ok=True)
    name = f"beat{n}_custom_{n}{ext}"
    (dst / name).write_bytes(data)
    # a stale proxy for this beat name would shadow the new file
    px = EP_DIR / slug / "assets" / "_proxy" / f"beat{n}_custom_{n}.jpg"
    px.unlink(missing_ok=True)
    return f"beat{n}_custom_{n}", ("stock" if ext in VIDEO_EXT else "archivo")


def beat_kind_in_spine(slug, n):
    md = (EP_DIR / slug / "06-shotlist.md").read_text(encoding="utf-8")
    for b in A.parse_spine(md):
        if b["n"] == n:
            return b["kind"]
    return None


def apply(slug, n, asset=None, src=None):
    kind = beat_kind_in_spine(slug, n)
    if kind is None:
        return {"error": f"beat {n} no está en la espina"}
    if kind in NO_ASSET:
        return {"error": f"el beat {n} es «{kind}» — no lleva asset que cambiar"}

    tipo = None
    if src:
        asset, tipo = fetch_new(slug, n, src)
    elif asset:
        lib = {a["id"]: a for a in asset_library(slug)}
        if asset not in lib:
            return {"error": f"«{asset}» no está en assets/ — pega una ruta/URL en su lugar"}
        # the beat's tipo follows the new asset (a swap can turn a `gráfico` beat
        # into `archivo`, or an image beat into `stock` video)
        tipo = lib[asset]["kind"]
    else:
        return {"error": "falta --asset o --src"}

    old = patch_shotlist(slug, n, asset, tipo)
    r = subprocess.run([sys.executable, str(TOOLS / "assemble.py"), slug, "--timeline-only"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        return {"error": "assemble.py falló: " + (r.stderr or r.stdout)[-300:]}
    tj = json.loads((EP_DIR / slug / "09-timeline.json").read_text(encoding="utf-8"))
    beat = next((b for b in tj["beats"] if b["n"] == n), None)
    if not beat:
        return {"n": n, "asset": asset, "file": None, "state": "merged",
                "note": "el beat se fusionó con un vecino tras re-alinear"}
    return {"n": n, "asset": beat.get("asset"), "file": beat.get("file"),
            "state": beat.get("state"), "tipo": beat.get("kind"),
            "motion": beat.get("motion"), "was": old}


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    slug = a[0].strip("/\\")
    if "--list" in a:
        print(json.dumps(asset_library(slug), ensure_ascii=False))
        sys.exit(0)
    if "--set" in a:
        n = int(a[a.index("--set") + 1])
        asset = a[a.index("--asset") + 1] if "--asset" in a else None
        src = a[a.index("--src") + 1] if "--src" in a else None
        print(json.dumps(apply(slug, n, asset, src), ensure_ascii=False))
        sys.exit(0)
    print(__doc__)
    sys.exit(2)
