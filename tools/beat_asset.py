#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beat_asset.py — asset provenance for the Stage-9 edit room (schema-2 timeline).

  --list                          asset library as JSON, for the picker
  --set <id> --asset <asset-id>   point beat <id> at an asset already in assets/
  --set <id> --src "<url|path>"   fetch a new resource, point beat <id> at it
  --clear <id>                    remove beat <id>'s visual (goes 'sin cubrir')

Structural edits (add / split / merge / delete / reorder / set-dur) live in
tools/beat_ops.py and operate on 09-timeline.json by beat id — the spine
(`06-shotlist.md`) is a frozen seed and is never renumbered any more.

An asset swap patches `09-timeline.json beats[].asset` by id, pins the
id → file in `assets/_index.json`, appends an asset-id row to `07-picks.txt`
(SALA block) so a re-download can't undo it, and for a new archival asset
adds a `07-assets.md` row + an `03-source-log.csv` stub.

Prints JSON. serve.py's /beat-asset endpoint dispatches here.
"""
import csv
import io
import json
import re
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


# ─────────────────────────────────────────────────── asset library
def asset_library(slug):
    ep = EP_DIR / slug
    out, seen = [], set()
    for sub in SUBS:
        d = ep / "assets" / sub
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if f.is_file() and f.suffix.lower() in A.MEDIA_EXT and f.stem not in seen:
                seen.add(f.stem)
                out.append({"id": f.stem, "sub": sub,
                            "url": f"/episodes/{slug}/assets/{sub}/{f.name}",
                            "video": f.suffix.lower() in VIDEO_EXT, "kind": SUB_KIND[sub]})
    return out


# ─────────────────────────────────────────────────── timeline helpers
def _tj(slug):
    return EP_DIR / slug / "09-timeline.json"


def _load(slug):
    f = _tj(slug)
    if not f.exists():
        raise SystemExit("no encuentro 09-timeline.json — siembra la línea primero")
    d = json.loads(f.read_text(encoding="utf-8"))
    if d.get("schema", 1) < 2:
        raise SystemExit(f"09-timeline.json es schema 1 — corre  python tools/migrate_timeline.py {slug}")
    return f, d


def _beat(d, bid):
    return next((b for b in d.get("beats", []) if b.get("id") == bid), None)


def _rebuilt_beat(slug, bid):
    d = json.loads(_tj(slug).read_text(encoding="utf-8"))
    b = _beat(d, bid) or {}
    return {"id": bid, "asset": b.get("asset"), "file": b.get("file"),
            "state": b.get("state"), "kind": b.get("kind"), "motion": b.get("motion")}


# ─────────────────────────────────────────────────── fetch / pin / picks
def fetch_new(slug, src):
    """Fetch a URL / read a local path → assets/<sub>/swap_<hash>.<ext>.
    Content-hashed name — can't collide with a beat id. Returns (asset_id, kind, rel)."""
    import hashlib
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
    ass = EP_DIR / slug / "assets"
    aid = f"swap_{hashlib.sha1(data).hexdigest()[:10]}"
    (ass / sub).mkdir(parents=True, exist_ok=True)
    (ass / sub / f"{aid}{ext}").write_bytes(data)
    return aid, ("stock" if ext in VIDEO_EXT else "archivo"), f"assets/{sub}/{aid}{ext}"


def pin_asset(slug, asset_id, rel_path):
    f = EP_DIR / slug / "assets" / "_index.json"
    idx = {}
    if f.exists():
        try:
            idx = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    idx = {k: v for k, v in idx.items() if (EP_DIR / slug / v).exists()}
    idx[asset_id] = rel_path
    f.write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")


def patch_picks(slug, asset_id, resource):
    """Record a sala swap in 07-picks.txt, keyed by asset id (not beat number)
    so a re-download can't undo it. All sala rows live in one block."""
    f = EP_DIR / slug / "07-picks.txt"
    if not f.exists():
        return
    lines = f.read_text(encoding="utf-8").splitlines()
    row = f"{asset_id}\tsala\t{resource}"
    for i, ln in enumerate(lines):
        c = ln.split("\t")
        if len(c) >= 2 and c[0].strip() == asset_id:
            lines[i] = row
            f.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    for i, ln in enumerate(lines):
        if ln.strip().startswith("# --- SALA"):
            lines.insert(i + 1, row)
            break
    else:
        lines += ["", "# --- SALA (asset-id → recurso; swaps hechos en la sala) ---", row]
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")


def add_assets_md_row(slug, label, src_note):
    f = EP_DIR / slug / "07-assets.md"
    if not f.exists():
        return
    lines = f.read_text(encoding="utf-8").splitlines()
    last, inm = None, False
    for i, ln in enumerate(lines):
        if ln.strip().startswith("## Manifiesto"):
            inm = True
        elif inm and ln.startswith("## "):
            break
        elif inm and ln.lstrip().startswith("|") and not set(ln) <= set("|-: "):
            last = i
    if last is None:
        return
    row = (f"| + | sala | {label} | {src_note} | por confirmar | — | por confirmar | "
           f"full-frame | **añadido en la sala** |")
    lines.insert(last + 1, row)
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")


def add_sourcelog_stub(slug, label, claim):
    f = EP_DIR / slug / "03-source-log.csv"
    if not f.exists():
        return None
    rows = list(csv.reader(io.StringIO(f.read_text(encoding="utf-8"))))
    ids = [r[0] for r in rows[1:] if r and re.match(r"S\d+", r[0])]
    nxt = f"S{max((int(x[1:]) for x in ids), default=0) + 1:02d}"
    new = [nxt, claim, "", "", "", "", "C", "", "", "", "PENDIENTE — rellenar",
           f"stub creado en la sala para «{label}» — completar fuente y derechos antes del render"]
    buf = io.StringIO()
    csv.writer(buf).writerows(rows + [new])
    f.write_text(buf.getvalue(), encoding="utf-8")
    return nxt


# ─────────────────────────────────────────────────── operations
def op_set(slug, bid, asset=None, src=None):
    f, d = _load(slug)
    b = _beat(d, bid)
    if not b:
        return {"error": f"no hay beat {bid} en la línea"}
    if b.get("kind") in NO_ASSET:
        return {"error": f"el beat {bid} es «{b.get('kind')}» — no lleva asset que cambiar"}
    was = b.get("asset") or ""
    if src:
        asset, kind, rel = fetch_new(slug, src)
        pin_asset(slug, asset, rel)
        patch_picks(slug, asset, rel)
        b["kind"] = kind
        if kind in ("archivo", "stock", "kb"):
            add_assets_md_row(slug, (b.get("vo_anchor") or asset)[:70], f"traído en la sala: {src}")
            add_sourcelog_stub(slug, asset, f"[{bid}] {(b.get('vo_anchor') or '')[:120]}")
    elif asset:
        lib = {a["id"]: a for a in asset_library(slug)}
        if asset not in lib:
            return {"error": f"«{asset}» no está en assets/ — pega una ruta/URL"}
        b["kind"] = lib[asset]["kind"]
    else:
        return {"error": "falta --asset o --src"}
    b["asset"] = asset
    if (b.get("marker") or "").upper() == "SPLIT":
        b.pop("marker", None)                       # 2nd half of a split, now reassigned
    b.pop("approved", None)                         # a new visual needs re-approval
    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        A.rebuild_timeline(slug)
    return {**_rebuilt_beat(slug, bid), "was": was}


def op_clear(slug, bid):
    f, d = _load(slug)
    b = _beat(d, bid)
    if not b:
        return {"error": f"no hay beat {bid} en la línea"}
    if b.get("kind") in NO_ASSET:
        return {"error": f"el beat {bid} ya no lleva visual («{b.get('kind')}»)"}
    b["asset"] = ""
    b.pop("label", None)
    b.pop("approved", None)
    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        A.rebuild_timeline(slug)
    return {**_rebuilt_beat(slug, bid), "note": "visual quitado — beat sin cubrir"}


# ─────────────────────────────────────────────────── CLI
def _arg(a, name):
    return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else None


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    slug = a[0].strip("/\\")
    try:
        if "--list" in a:
            print(json.dumps(asset_library(slug), ensure_ascii=False))
        elif "--set" in a:
            print(json.dumps(op_set(slug, _arg(a, "--set"), _arg(a, "--asset"), _arg(a, "--src")),
                             ensure_ascii=False))
        elif "--clear" in a:
            print(json.dumps(op_clear(slug, _arg(a, "--clear")), ensure_ascii=False))
        else:
            print(__doc__)
            sys.exit(2)
    except SystemExit as ex:
        if isinstance(ex.code, str):
            print(json.dumps({"error": ex.code}, ensure_ascii=False))
            sys.exit(1)
        raise
