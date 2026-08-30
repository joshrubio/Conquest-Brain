#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pull_assets.py — Stage 7 candidate pull (archive + free stock).
Protocol: docs/12-available-material-protocol.md, docs/06 Stage 7.

Reads a per-episode spec (07-pull.tsv), queries free APIs, and writes a
candidate list (07-candidates.md) with direct download URLs, licence,
author and resolution. The photography pass stays human: Josh ticks the
candidates he wants, then --download pulls them into assets/.

APIs
  stock   pexels  pixabay  unsplash  openverse
  video   pexels  pixabay
  archive met     aic (Art Institute of Chicago)
Keys live in tools/.env (gitignored). No .env -> only keyless sources run
(openverse, met, aic).

Usage
  python tools/pull_assets.py E0XX-slug --init
      scaffold episodes/E0XX-slug/07-pull.tsv

  python tools/pull_assets.py E0XX-slug
      run every spec row -> episodes/E0XX-slug/07-candidates.md

  python tools/pull_assets.py E0XX-slug --download
      read 07-candidates.md, download every "- [x]" candidate into
      assets/stock|archive/, verify resolution, append assets/CREDITS.md,
      print manifest rows for 07-assets.md

  python tools/pull_assets.py --check-keys
      report which API keys tools/.env provides
"""
import io
import re
import sys
import time
import json
from pathlib import Path
from urllib.parse import urlencode

import requests
from PIL import Image

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes"
ENV = Path(__file__).resolve().parent / ".env"
UA = "ExodoOficial/1.0 (educational documentary; contact joshuerubio@gmail.com)"
TIMEOUT = 30

STOCK_ALL = ["pexels", "pixabay", "unsplash", "openverse"]
ARCHIVE_ALL = ["met", "aic"]

SPEC_HEADER = """# 07-pull.tsv — Stage 7 candidate-pull spec for this episode.
# Tab-separated. Lines starting with # are ignored. One row per shotlist beat
# that needs an image/clip pulled (own-graphics beats do NOT go here).
#
# columns:
#   beat    shotlist beat id (1, 25b, +B ...). Free text, just a label.
#   kind    stock | archive | video
#   source  comma list, or a group keyword:
#             stock   = pexels,pixabay,unsplash,openverse
#             archive = met,aic
#           video only supports pexels,pixabay
#   query   search terms
#   opts    key=value;key=value  (all optional)
#             n=4               candidates per source (default 4)
#             orientation=landscape|portrait|square   (pexels/unsplash)
#             min=3000          drop candidates whose long side < this many px
#             license=cc0,by    openverse licence filter
#             must=hokusai      archive only — every term must appear in
#                               artist/title/tags (comma list = all required)
#
# stock = generic illustrative b-roll only, never "the real thing" (docs/12).
#
beat\tkind\tsource\tquery\topts
"""


# ----------------------------------------------------------------------------- env
def load_env():
    keys = {}
    if ENV.exists():
        for line in ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            keys[k.strip()] = v.strip().strip('"').strip("'")
    return keys


def check_keys():
    k = load_env()
    print(f"tools/.env: {'found' if ENV.exists() else 'MISSING'}\n")
    for name in ("PEXELS_API_KEY", "PIXABAY_API_KEY", "UNSPLASH_ACCESS_KEY"):
        v = k.get(name, "")
        print(f"  {'OK ' if v else '  ·'} {name:22s} {'set' if v else '(not set)'}")
    print("\n  OK  openverse / met / aic  — no key needed")


# --------------------------------------------------------------------------- model
class Cand:
    __slots__ = ("src", "id", "w", "h", "author", "lic", "url", "page", "dur")

    def __init__(self, src, id, url, w=0, h=0, author="", lic="", page="", dur=0):
        self.src, self.id, self.url = src, str(id), url
        self.w, self.h, self.author, self.lic, self.page, self.dur = w, h, author, lic, page, dur

    def line(self):
        dim = f"{self.w}x{self.h}" if self.w else "?x?"
        extra = f" · {self.dur}s" if self.dur else ""
        who = f" · {self.author}" if self.author else ""
        lic = f" · {self.lic}" if self.lic else ""
        pg = f"\n      page: {self.page}" if self.page else ""
        return f"- [ ] `{self.src}:{self.id}` · {dim}{extra}{who}{lic} · {self.url}{pg}"


STOP = {"the", "and", "for", "with", "from", "also", "known", "view", "views",
        "print", "prints", "series", "japan", "japanese", "old", "man", "scene"}


def relevant(query, fields, must=None):
    """Keep an archive hit if every `must` term is present AND at least one
    meaningful query word (>3 chars, not a stop word) appears."""
    hay = " ".join(f for f in fields if f).lower()
    for m in (must or []):
        if m.lower() not in hay:
            return False
    toks = {w for w in re.findall(r"[a-z]{4,}", query.lower()) if w not in STOP}
    if not toks:
        return True
    return any(t in hay for t in toks)


def _get(url, headers=None, params=None):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    r = requests.get(url, headers=h, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r


# ------------------------------------------------------------------------- sources
def q_pexels(query, key, n, opts, video=False):
    if not key:
        return []
    base = "https://api.pexels.com/videos/search" if video else "https://api.pexels.com/v1/search"
    p = {"query": query, "per_page": max(n, 1)}
    if not video and opts.get("orientation"):
        p["orientation"] = opts["orientation"]
    r = _get(base, headers={"Authorization": key}, params=p)
    out = []
    if video:
        for v in r.json().get("videos", []):
            files = sorted(v.get("video_files", []), key=lambda f: (f.get("width") or 0), reverse=True)
            if not files:
                continue
            f = files[0]
            out.append(Cand("pexels", v["id"], f["link"], f.get("width", 0), f.get("height", 0),
                            v.get("user", {}).get("name", ""), "Pexels License",
                            v.get("url", ""), v.get("duration", 0)))
    else:
        for ph in r.json().get("photos", []):
            out.append(Cand("pexels", ph["id"], ph["src"]["original"], ph.get("width", 0),
                            ph.get("height", 0), ph.get("photographer", ""), "Pexels License",
                            ph.get("url", "")))
    return out


def q_pixabay(query, key, n, opts, video=False):
    if not key:
        return []
    base = "https://pixabay.com/api/videos/" if video else "https://pixabay.com/api/"
    p = {"key": key, "q": query, "per_page": max(n, 3)}
    if not video:
        p["image_type"] = "photo"
    r = _get(base, params=p)
    out = []
    for h in r.json().get("hits", [])[:n]:
        if video:
            vids = h.get("videos", {})
            best = max(vids.values(), key=lambda x: x.get("width", 0)) if vids else None
            if not best:
                continue
            out.append(Cand("pixabay", h["id"], best["url"], best.get("width", 0),
                            best.get("height", 0), h.get("user", ""), "Pixabay Content License",
                            h.get("pageURL", ""), h.get("duration", 0)))
        else:
            # free API delivers largeImageURL capped at 1280 px on the long side,
            # regardless of imageWidth/imageHeight (those are the source dims)
            out.append(Cand("pixabay", h["id"], h.get("largeImageURL", ""),
                            0, 0, h.get("user", ""),
                            "Pixabay Content License (entrega <=1280 px)", h.get("pageURL", "")))
    return out


def q_unsplash(query, key, n, opts, video=False):
    if not key or video:
        return []
    p = {"query": query, "per_page": max(n, 1)}
    if opts.get("orientation"):
        p["orientation"] = opts["orientation"]
    r = _get("https://api.unsplash.com/search/photos",
             headers={"Authorization": f"Client-ID {key}", "Accept-Version": "v1"}, params=p)
    out = []
    for ph in r.json().get("results", []):
        raw = ph["urls"]["raw"]
        full = raw + ("&" if "?" in raw else "?") + "q=90&fm=jpg"
        out.append(Cand("unsplash", ph["id"], full, ph.get("width", 0), ph.get("height", 0),
                        ph.get("user", {}).get("name", ""), "Unsplash License",
                        ph.get("links", {}).get("html", "")))
    return out


def q_openverse(query, key, n, opts, video=False):
    if video:
        return []
    p = {"q": query, "page_size": max(n, 1)}
    if opts.get("license"):
        p["license"] = opts["license"]
    r = _get("https://api.openverse.org/v1/images/", params=p)
    out = []
    for h in r.json().get("results", []):
        lic = f"{h.get('license', '').upper()} {h.get('license_version', '')}".strip()
        out.append(Cand("openverse", h["id"], h.get("url", ""), h.get("width", 0) or 0,
                        h.get("height", 0) or 0, h.get("creator", "") or "", lic,
                        h.get("foreign_landing_url", "")))
    return out


def q_met(query, key, n, opts, video=False):
    if video:
        return []
    must = [x.strip() for x in opts.get("must", "").split(",") if x.strip()]
    r = _get("https://collectionapi.metmuseum.org/public/collection/v1/search",
             params={"q": query, "hasImages": "true"})
    ids = (r.json().get("objectIDs") or [])[: n * 6]
    out = []
    for oid in ids:
        if len(out) >= n:
            break
        try:
            o = _get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}").json()
        except requests.HTTPError:
            continue
        time.sleep(0.15)
        img = o.get("primaryImage") or ""
        if not img or not o.get("isPublicDomain"):
            continue
        who = o.get("artistDisplayName") or "—"
        title = o.get("title") or ""
        tags = " ".join(t.get("term", "") for t in (o.get("tags") or []))
        if not relevant(query, (who, title, tags, o.get("culture", ""), o.get("period", "")), must):
            continue
        c = Cand("met", oid, img, 0, 0, "", "CC0 (The Met)", o.get("objectURL", ""))
        c.author = f"{who} — {title}".strip(" —")
        out.append(c)
    return out[:n]


def q_aic(query, key, n, opts, video=False):
    if video:
        return []
    must = [x.strip() for x in opts.get("must", "").split(",") if x.strip()]
    fields = ("id,title,image_id,artist_display,date_display,is_public_domain,"
              "term_titles,classification_titles")
    r = _get("https://api.artic.edu/api/v1/artworks/search",
             headers={"AIC-User-Agent": UA},
             params={"q": query, "fields": fields, "limit": n * 4,
                     "query[term][is_public_domain]": "true"})
    out = []
    for a in r.json().get("data", []):
        if len(out) >= n:
            break
        iid = a.get("image_id")
        if not iid or not a.get("is_public_domain"):
            continue
        terms = " ".join(a.get("term_titles") or []) + " " + " ".join(a.get("classification_titles") or [])
        if not relevant(query, (a.get("title", ""), a.get("artist_display", ""), terms), must):
            continue
        url = f"https://www.artic.edu/iiif/2/{iid}/full/full/0/default.jpg"
        w = h = 0
        try:
            info = _get(f"https://www.artic.edu/iiif/2/{iid}/info.json",
                        headers={"AIC-User-Agent": UA}).json()
            w, h = info.get("width", 0), info.get("height", 0)
        except Exception:
            pass
        who = (a.get("artist_display") or "").split("\n")[0]
        out.append(Cand("aic", a["id"], url, w, h,
                        f"{who} — {a.get('title', '')}".strip(" —"),
                        "CC0 (Art Institute of Chicago)",
                        f"https://www.artic.edu/artworks/{a['id']}"))
    return out


DISPATCH = {"pexels": q_pexels, "pixabay": q_pixabay, "unsplash": q_unsplash,
            "openverse": q_openverse, "met": q_met, "aic": q_aic}
KEY_FOR = {"pexels": "PEXELS_API_KEY", "pixabay": "PIXABAY_API_KEY",
           "unsplash": "UNSPLASH_ACCESS_KEY"}


def expand_sources(kind, source):
    s = source.strip().lower()
    if s in ("stock", "all"):
        return STOCK_ALL
    if s == "archive":
        return ARCHIVE_ALL
    return [x.strip() for x in s.split(",") if x.strip()]


def parse_opts(raw):
    o = {}
    for part in (raw or "").split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            o[k.strip()] = v.strip()
    return o


# --------------------------------------------------------------------------- run
def read_spec(slug):
    f = EP_DIR / slug / "07-pull.tsv"
    if not f.exists():
        sys.exit(f"no {f.relative_to(ROOT)} — corre:  python tools/pull_assets.py {slug} --init")
    rows = []
    for ln in f.read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        cells = ln.split("\t")
        if cells[0].strip().lower() == "beat":
            continue
        while len(cells) < 5:
            cells.append("")
        rows.append([c.strip() for c in cells[:5]])
    return rows


def run(slug):
    keys = load_env()
    rows = read_spec(slug)
    out = [f"# Candidatos de recursos — {slug}",
           "",
           "> Stage 7 · pull automático (`tools/pull_assets.py`). **Esto no es selección.**",
           "> Marca `- [x]` los que quieras y corre `--download`. Todo lo demás se ignora.",
           "> stock = b-roll ilustrativo genérico, nunca 'lo real' (docs/12).",
           ""]
    n_c = 0
    for beat, kind, source, query, rawopts in rows:
        opts = parse_opts(rawopts)
        n = int(opts.get("n", 4))
        want_video = kind.lower() == "video"
        srcs = expand_sources(kind, source)
        out.append(f"## beat {beat} — \"{query}\"  [{kind}: {','.join(srcs)}]\n")
        for src in srcs:
            fn = DISPATCH.get(src)
            if not fn:
                out.append(f"  <!-- fuente desconocida: {src} -->")
                continue
            key = keys.get(KEY_FOR.get(src, ""), "")
            if src in KEY_FOR and not key:
                out.append(f"  <!-- {src}: sin API key en tools/.env, saltado -->")
                continue
            try:
                cands = fn(query, key, n, opts, video=want_video)
            except requests.HTTPError as e:
                out.append(f"  <!-- {src}: HTTP {e.response.status_code} -->")
                continue
            except Exception as e:
                out.append(f"  <!-- {src}: {e} -->")
                continue
            mn = int(opts.get("min", 0))
            if mn:
                cands = [c for c in cands if (not c.w) or max(c.w, c.h) >= mn]
            if not cands:
                out.append(f"  <!-- {src}: 0 resultados -->")
                continue
            for c in cands:
                out.append("  " + c.line().replace("\n      ", "\n        "))
                n_c += 1
            out.append("")
            time.sleep(0.3)
        out.append("")
    dst = EP_DIR / slug / "07-candidates.md"
    dst.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"escrito  {dst.relative_to(ROOT)}  ({n_c} candidatos, {len(rows)} beats)")
    print("siguiente: marca `- [x]` los elegidos y corre --download")


# ---------------------------------------------------------------------- download
PICK_RE = re.compile(r"^\s*- \[x\] `([a-z]+):([^`]+)` .* · (https?://\S+)", re.I)
BEAT_RE = re.compile(r"^## beat (\S+) —")
EXT_OK = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
          "video/mp4": ".mp4", "video/quicktime": ".mov"}


def download(slug):
    keys = load_env()
    md = EP_DIR / slug / "07-candidates.md"
    if not md.exists():
        sys.exit(f"no {md.relative_to(ROOT)} — corre el pull primero")
    beat = "?"
    picks = []
    for ln in md.read_text(encoding="utf-8").splitlines():
        b = BEAT_RE.match(ln)
        if b:
            beat = b.group(1)
        m = PICK_RE.match(ln)
        if m:
            picks.append((beat, m.group(1), m.group(2), m.group(3)))
    if not picks:
        sys.exit("0 candidatos marcados `- [x]` en 07-candidates.md")

    ep = EP_DIR / slug
    rows, credits = [], []
    for beat, src, cid, url in picks:
        sub = "archive" if src in ARCHIVE_ALL else "stock"
        (ep / "assets" / sub).mkdir(parents=True, exist_ok=True)
        tries = [url]
        hdr = {"User-Agent": UA}
        if src == "aic":
            # AIC IIIF 403s on full/full for some images / non-browser clients;
            # walk down the size ladder, send a browser-ish UA + Referer
            hdr = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"),
                   "Referer": "https://www.artic.edu/"}
            tries = [url] + [url.replace("/full/full/", f"/full/{w},/") for w in (3840, 1686, 843)]
        r = None
        for u in tries:
            try:
                rr = requests.get(requests.utils.requote_uri(u), headers=hdr, timeout=90)
                rr.raise_for_status()
                r = rr
                url = u
                break
            except Exception as e:
                last = e
        if r is None:
            hint = ""
            if src == "aic":
                hint = "  (AIC bloquea descarga directa desde algunas redes — abre la page y usa el botón Download)"
            print(f"  FALLO  {src}:{cid}  {last}{hint}")
            continue
        ct = r.headers.get("content-type", "").split(";")[0].strip()
        ext = EXT_OK.get(ct, Path(url.split("?")[0]).suffix or ".bin")
        safe_beat = re.sub(r"[^A-Za-z0-9+-]", "", beat)
        name = f"beat{safe_beat}_{src}_{re.sub(r'[^A-Za-z0-9]', '', cid)[:16]}{ext}"
        path = ep / "assets" / sub / name
        path.write_bytes(r.content)
        dim = ""
        if ext in (".jpg", ".png", ".webp"):
            try:
                im = Image.open(io.BytesIO(r.content))
                dim = f"{im.width}x{im.height}"
            except Exception:
                dim = "?"
        # Unsplash: ping download endpoint (API terms)
        if src == "unsplash":
            key = keys.get("UNSPLASH_ACCESS_KEY", "")
            if key:
                try:
                    requests.get(f"https://api.unsplash.com/photos/{cid}/download",
                                 headers={"Authorization": f"Client-ID {key}"}, timeout=15)
                except Exception:
                    pass
        rel = path.relative_to(ep)
        print(f"  OK  {name}  {dim}")
        rows.append(f"| {beat} |  | {src}:{cid} | {url} |  |  | {dim} |  |  | `{rel.as_posix()}` |")
        credits.append(f"- beat {beat}: {src}:{cid} — {url}")

    if rows:
        hdr = ("| # | Beat(s) | Qué es | Enlace de descarga | Museo / nº | Licencia "
               "| Res. real | Uso | Pase | Archivo local |\n|---|---|---|---|---|---|---|---|---|---|")
        print("\n--- filas para 07-assets.md ---\n" + hdr)
        for r in rows:
            print(r)
        cf = ep / "assets" / "CREDITS.md"
        prev = cf.read_text(encoding="utf-8") if cf.exists() else "# Créditos de recursos\n"
        cf.write_text(prev.rstrip() + "\n" + "\n".join(credits) + "\n", encoding="utf-8")
        print(f"\ncréditos → {cf.relative_to(ROOT)}")


# -------------------------------------------------------------------------- init
def init(slug):
    d = EP_DIR / slug
    if not d.is_dir():
        sys.exit(f"no existe {d}")
    f = d / "07-pull.tsv"
    if f.exists():
        sys.exit(f"ya existe {f.relative_to(ROOT)}")
    sample = ("1\tarchive\tmet,aic\tkatsushika hokusai\tn=5\n"
              "7\tstock\tpexels,unsplash\tedo period japanese street crowd\torientation=landscape;min=3000\n"
              "2\tvideo\tpexels,pixabay\tocean wave breaking slow motion\tn=3\n")
    f.write_text(SPEC_HEADER + sample, encoding="utf-8")
    print(f"creado  {f.relative_to(ROOT)}  (edita las filas y corre el pull)")


# -------------------------------------------------------------------------- main
if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    if args[0] == "--check-keys":
        check_keys()
        sys.exit(0)
    slug = args[0]
    rest = set(args[1:])
    if "--init" in rest:
        init(slug)
    elif "--download" in rest:
        download(slug)
    else:
        run(slug)
