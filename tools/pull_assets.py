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
  archive met  commons (Wikimedia Commons)  aic (Art Institute of Chicago)
Keys live in tools/.env (gitignored). No .env -> only keyless sources run
(openverse, met, commons, aic).

Usage
  python tools/pull_assets.py E0XX-slug --init
      scaffold episodes/E0XX-slug/07-pull.tsv

  python tools/pull_assets.py E0XX-slug
      run every spec row -> 07-candidates.md (git record) + 07-candidates.html
      (open in a browser: thumbnails, tick the keepers, "Exportar" writes
      07-picks.txt). ~3 candidates per beat by default (opts n=).

  python tools/pull_assets.py E0XX-slug --download
      read 07-picks.txt (or, if absent, "- [x]" lines in 07-candidates.md),
      download each pick into assets/stock|archive/, verify resolution,
      append assets/CREDITS.md, print manifest rows for 07-assets.md

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

STOCK_IMG = ["pexels", "pixabay", "unsplash", "openverse"]         # kind: stock-img
STOCK_MOTION = ["pexelsv", "pixabayv", "pexels", "unsplash",       # kind: stock
                "pixabay", "openverse"]                            # video sources first
VIDEO_SRCS = {"pexelsv", "pixabayv"}
ARCHIVE_ALL = ["met", "commons", "aic"]   # the `archive` group keyword
ARCHIVE_SRCS = set(ARCHIVE_ALL)           # for assets/ folder routing
# note: AIC's IIIF CDN 403s direct downloads from some networks/CI (works from a
# normal browser). If --download fails on an aic pick, open its page + Download.

SPEC_HEADER = """# 07-pull.tsv — Stage 7 candidate-pull spec for this episode.
# Tab-separated. Lines starting with # are ignored. One row per shotlist beat
# that needs an image/clip pulled (own-graphics beats do NOT go here).
#
# columns:
#   beat    shotlist beat id (1, 25b, +B ...). Free text, just a label.
#   kind    stock | stock-img | archive | video
#   source  comma list, or a group keyword:
#             stock     = pexels+pixabay VIDEO first, then pexels/unsplash/
#                         pixabay/openverse images  (motion b-roll preferred)
#             stock-img = images only (pexels,pixabay,unsplash,openverse)
#             video     = pexels,pixabay video only
#             archive   = met,commons,aic
#   query   search terms
#   opts    key=value;key=value  (all optional)
#             n=3               total candidates for the beat (default 3)
#             motion=no         stock: drop video, images only
#             motion=only       stock: video only
#             orientation=landscape|portrait|square   (pexels/unsplash images)
#             min=3000          drop candidates whose long side < this many px
#                               (also filters video by width, e.g. min=1920)
#             license=cc0,by    openverse licence filter
#             must=hokusai      archive only — every term must appear in
#                               artist/title/tags (comma list = all required)
#
# stock = generic illustrative b-roll only, never "the real thing" (docs/12).
# A found stock video beats making our own b-roll later — prefer it.
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
    __slots__ = ("src", "id", "w", "h", "author", "lic", "url", "page", "dur", "thumb")

    def __init__(self, src, id, url, w=0, h=0, author="", lic="", page="", dur=0, thumb=""):
        self.src, self.id, self.url = src, str(id), url
        self.w, self.h, self.author, self.lic = w, h, author, lic
        self.page, self.dur, self.thumb = page, dur, thumb

    @property
    def key(self):
        return f"{self.src}:{self.id}"

    def dim(self):
        return f"{self.w}x{self.h}" if self.w else "?x?"

    def line(self):
        extra = f" · {self.dur}s" if self.dur else ""
        who = f" · {self.author}" if self.author else ""
        lic = f" · {self.lic}" if self.lic else ""
        pg = f"\n        page: {self.page}" if self.page else ""
        return f"- [ ] `{self.key}` · {self.dim()}{extra}{who}{lic} · {self.url}{pg}"


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
    if opts.get("orientation"):
        p["orientation"] = opts["orientation"]
    r = _get(base, headers={"Authorization": key}, params=p)
    out = []
    if video:
        for v in r.json().get("videos", []):
            files = sorted(v.get("video_files", []), key=lambda f: (f.get("width") or 0), reverse=True)
            if not files:
                continue
            f = files[0]
            out.append(Cand("pexelsv", v["id"], f["link"], f.get("width", 0), f.get("height", 0),
                            v.get("user", {}).get("name", ""), "Pexels License",
                            v.get("url", ""), v.get("duration", 0), thumb=v.get("image", "")))
    else:
        for ph in r.json().get("photos", []):
            out.append(Cand("pexels", ph["id"], ph["src"]["original"], ph.get("width", 0),
                            ph.get("height", 0), ph.get("photographer", ""), "Pexels License",
                            ph.get("url", ""), thumb=ph.get("src", {}).get("medium", "")))
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
            th = ""
            for q in ("tiny", "small", "medium", "large"):
                th = (vids.get(q) or {}).get("thumbnail") or th
            out.append(Cand("pixabayv", h["id"], best["url"], best.get("width", 0),
                            best.get("height", 0), h.get("user", ""), "Pixabay Content License",
                            h.get("pageURL", ""), h.get("duration", 0), thumb=th))
        else:
            # free API delivers largeImageURL capped at 1280 px on the long side,
            # regardless of imageWidth/imageHeight (those are the source dims)
            out.append(Cand("pixabay", h["id"], h.get("largeImageURL", ""),
                            0, 0, h.get("user", ""),
                            "Pixabay Content License (entrega <=1280 px)", h.get("pageURL", ""),
                            thumb=h.get("webformatURL", "")))
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
                        ph.get("links", {}).get("html", ""),
                        thumb=ph.get("urls", {}).get("small", "")))
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
                        h.get("foreign_landing_url", ""),
                        thumb=h.get("thumbnail", "") or h.get("url", "")))
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
        c = Cand("met", oid, img, 0, 0, "", "CC0 (The Met)", o.get("objectURL", ""),
                 thumb=o.get("primaryImageSmall", "") or img)
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
                        f"https://www.artic.edu/artworks/{a['id']}",
                        thumb=f"https://www.artic.edu/iiif/2/{iid}/full/400,/0/default.jpg"))
    return out


def q_commons(query, key, n, opts, video=False):
    if video:
        return []
    must = [x.strip() for x in opts.get("must", "").split(",") if x.strip()]
    r = _get("https://commons.wikimedia.org/w/api.php", params={
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": str(n * 5),
        "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": "420",
    })
    pages = ((r.json().get("query") or {}).get("pages") or {}).values()
    strip = lambda s: re.sub(r"<[^>]+>", "", s or "").strip()
    out = []
    for p in sorted(pages, key=lambda x: x.get("index", 99)):
        if len(out) >= n:
            break
        ii = (p.get("imageinfo") or [{}])[0]
        url = ii.get("url", "")
        if url.split("?")[0].lower().rsplit(".", 1)[-1] not in ("jpg", "jpeg", "png", "tif", "tiff"):
            continue
        meta = ii.get("extmetadata") or {}
        lic = strip((meta.get("LicenseShortName") or {}).get("value", ""))
        blob = (lic + " " + strip((meta.get("UsageTerms") or {}).get("value", ""))).lower()
        if not any(k in blob for k in ("public domain", "pd-", "cc0", "no known copyright",
                                       "no restrictions")):
            continue
        artist = strip((meta.get("Artist") or {}).get("value", ""))
        if artist.lower() in ("", "missing name", "unknown", "unknown author", "anonymous"):
            artist = ""
        title = p.get("title", "").replace("File:", "")
        desc = strip((meta.get("ImageDescription") or {}).get("value", ""))
        if not relevant(query, (title, artist, desc), must):
            continue
        out.append(Cand("commons", p.get("pageid"), url, ii.get("width", 0), ii.get("height", 0),
                        f"{artist} — {title}".strip(" —"), lic or "PD",
                        ii.get("descriptionurl", ""), thumb=ii.get("thumburl", "")))
    return out


DISPATCH = {"pexels": q_pexels, "pixabay": q_pixabay, "unsplash": q_unsplash,
            "openverse": q_openverse, "met": q_met, "commons": q_commons, "aic": q_aic,
            "pexelsv": q_pexels, "pixabayv": q_pixabay}
KEY_FOR = {"pexels": "PEXELS_API_KEY", "pixabay": "PIXABAY_API_KEY",
           "unsplash": "UNSPLASH_ACCESS_KEY",
           "pexelsv": "PEXELS_API_KEY", "pixabayv": "PIXABAY_API_KEY"}


def expand_sources(kind, source):
    s = source.strip().lower()
    if s in ("stock", "all"):
        return list(STOCK_MOTION)      # video first, then images
    if s in ("stock-img", "stockimg"):
        return list(STOCK_IMG)
    if s == "video":
        return ["pexelsv", "pixabayv"]
    if s == "archive":
        return list(ARCHIVE_ALL)
    return [{"pexels-video": "pexelsv", "pixabay-video": "pixabayv"}.get(x.strip(), x.strip())
            for x in s.split(",") if x.strip()]


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


def _ai_field(chunk, label):
    m = re.search(rf"\*\*{label}:\*\*\s*(.+)", chunk)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def parse_ai_prompts(slug):
    """(negative_prompt, [{id, slug, beats, beats_short, para, fname, prompt}]).
    ('', []) if 07b-ai-prompts.md is absent."""
    f = EP_DIR / slug / "07b-ai-prompts.md"
    if not f.exists():
        return "", []
    txt = f.read_text(encoding="utf-8")
    neg = ""
    m = re.search(r"## Negative prompt.*?```(.*?)```", txt, re.S)
    if m:
        neg = m.group(1).strip()
    out = []
    for chunk in re.split(r"\n## ", txt):
        hm = re.match(r"(ai\d{2}) — (\S+)", chunk)
        if not hm:
            continue
        beats = _ai_field(chunk, r"Beat\(s\) shotlist")
        fn = re.search(r"\*\*Guardar como:\*\*\s*`([^`]+)`", chunk)
        pm = re.search(r"```(.*?)```", chunk, re.S)
        out.append(dict(
            id=hm.group(1), slug=hm.group(2), beats=beats,
            beats_short=re.split(r"[—(]", beats)[0].strip() or hm.group(1),
            para=_ai_field(chunk, r"Para qué"),
            fname=fn.group(1) if fn else f"{slug.split('-')[0]}_{hm.group(1)}.png",
            prompt=pm.group(1).strip() if pm else ""))
    return neg, out


def build_html(slug, groups, ai_prompts=("", [])):
    import html as _h
    esc = _h.escape
    neg, prompts = ai_prompts
    total = sum(len(c) for _, _, _, _, c, _ in groups)
    cards = []
    for beat, kind, query, srcs, cands, notes in groups:
        cards.append(f'<section><h2>beat {esc(beat)} '
                     f'<span class="q">"{esc(query)}"</span> '
                     f'<span class="k">{esc(kind)} · {esc(",".join(srcs))}</span></h2>')
        if not cands:
            cards.append('<p class="empty">— sin candidatos. '
                         f'{esc("; ".join(notes)) or "amplía la query en 07-pull.tsv"} —</p>')
        cards.append('<div class="grid">')
        for c in cands:
            badges = [f'<b>{esc(c.dim())}</b>']
            if c.dur:
                badges.append(f'<b class="vid">▶ {c.dur}s</b>')
            if c.w and max(c.w, c.h) < 1920:
                badges.append('<b class="warn">baja-res</b>')
            if "1280" in c.lic:
                badges.append('<b class="warn">≤1280</b>')
            thumb = esc(c.thumb) if c.thumb else ""
            img = (f'<img loading="lazy" src="{thumb}" alt="">'
                   if thumb else '<div class="noimg">sin miniatura</div>')
            cards.append(
                f'<label class="card" data-key="{esc(c.key)}" data-beat="{esc(beat)}" '
                f'data-url="{esc(c.url)}"><input type="checkbox">{img}'
                f'<figcaption><span class="badges">{"".join(badges)}</span>'
                f'<code>{esc(c.key)}</code>'
                f'<span class="who">{esc(c.author or "")}</span>'
                f'<span class="lic">{esc(c.lic)}</span>'
                f'<span class="lnk"><a href="{esc(c.url)}" target="_blank" rel="noopener">full</a>'
                + (f' · <a href="{esc(c.page)}" target="_blank" rel="noopener">page</a>' if c.page else "")
                + '</span></figcaption></label>')
        cards.append('</div></section>')
    body = "\n".join(cards)

    # ---- right column: AI-generation prompts (07b) ----
    if prompts:
        ai = ['<h2 class="aih">Prompts IA <span>genera si el pull no trae lo que el beat necesita</span></h2>']
        if neg:
            ai.append(f'<details class="neg"><summary>negative prompt (compartido)</summary>'
                      f'<pre>{esc(neg)}</pre></details>')
        for p in prompts:
            ai.append(
                f'<div class="ai" data-ai="{esc(p["id"])}">'
                f'<h3><span class="beat">beat {esc(p["beats_short"])}</span> '
                f'{esc(p["id"])} — {esc(p["slug"])}</h3>'
                + (f'<p class="para">{esc(p["para"])}</p>' if p["para"] else "")
                + f'<pre>{esc(p["prompt"])}</pre>'
                f'<button class="cp">copiar prompt</button>'
                f'<div class="fn">guardar como <code>{esc(p["fname"])}</code></div>'
                f'<input class="aipath" data-ai="{esc(p["id"])}" '
                f'data-beats="{esc(p["beats_short"])}" data-fname="{esc(p["fname"])}" '
                f'placeholder="ruta local o URL de tu imagen generada">'
                '</div>')
        aside = "\n".join(ai)
        has_ai = "true"
    else:
        aside = ('<h2 class="aih">Prompts IA</h2><p class="empty">sin '
                 f'<code>07b-ai-prompts.md</code> — corre '
                 f'<code>python tools/build_ai_prompts.py {esc(slug)} &lt;slug&gt; …</code></p>')
        has_ai = "false"

    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Candidatos — {esc(slug)}</title>
<style>
 :root{{color-scheme:light dark}}
 *{{box-sizing:border-box}}
 body{{font:14px/1.4 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;
   background:Canvas;color:CanvasText}}
 header{{position:sticky;top:0;z-index:9;display:flex;gap:1rem;align-items:center;
   flex-wrap:wrap;padding:.7rem 1rem;background:Canvas;border-bottom:1px solid #8888;min-height:3.2rem}}
 header h1{{font-size:1rem;margin:0;font-weight:700}}
 #cnt{{font-variant-numeric:tabular-nums;opacity:.8}}
 button{{font:inherit;padding:.45rem .8rem;border:1px solid #8886;border-radius:7px;
   background:#8881;cursor:pointer}}
 button.primary{{background:#2563eb;color:#fff;border-color:#2563eb}}
 .wrap{{display:grid;grid-template-columns:minmax(0,1fr) 400px;gap:1.5rem;
   max-width:1900px;margin:0 auto;padding:1rem}}
 main{{min-width:0}}
 aside{{position:sticky;top:4rem;align-self:start;max-height:calc(100vh - 5rem);
   overflow:auto;border-left:1px solid #8884;padding-left:1rem}}
 @media(max-width:1100px){{.wrap{{grid-template-columns:1fr}}
   aside{{position:static;max-height:none;border-left:0;border-top:1px solid #8884;
   padding-left:0;padding-top:1rem}}}}
 section{{margin:0 0 2rem}}
 h2{{font-size:.95rem;border-bottom:1px solid #8884;padding-bottom:.3rem}}
 h2 .q{{font-weight:400;opacity:.75}} h2 .k{{float:right;font-weight:400;opacity:.55;font-size:.8rem}}
 .empty{{opacity:.6;font-style:italic}}
 .grid{{display:grid;gap:.8rem;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}}
 .card{{border:2px solid transparent;border-radius:9px;overflow:hidden;background:#8881;
   cursor:pointer;display:flex;flex-direction:column}}
 .card:has(:checked){{border-color:#2563eb;background:#2563eb22}}
 .card input{{position:absolute;width:22px;height:22px;margin:6px;accent-color:#2563eb}}
 .card img,.card .noimg{{width:100%;aspect-ratio:4/3;object-fit:cover;background:#0002;display:block}}
 .noimg{{display:flex;align-items:center;justify-content:center;opacity:.5;font-size:.8rem}}
 figcaption{{padding:.5rem .6rem;display:flex;flex-direction:column;gap:.2rem;font-size:.8rem}}
 .badges{{display:flex;gap:.3rem;flex-wrap:wrap}}
 .badges b{{font-weight:600;background:#8883;padding:.05rem .35rem;border-radius:4px}}
 .badges b.warn{{background:#f59e0b33;color:#b45309}}
 .badges b.vid{{background:#2563eb33}}
 code{{font-size:.75rem;opacity:.8}} .who{{opacity:.7}} .lic{{opacity:.55;font-size:.72rem}}
 .lnk{{font-size:.75rem}}
 .aih span{{font-weight:400;opacity:.6;font-size:.75rem}}
 details.neg{{font-size:.72rem;margin:.6rem 0}}
 details.neg pre,.ai pre{{white-space:pre-wrap;font-size:.67rem;background:#8881;
   padding:.5rem;border-radius:6px;max-height:9rem;overflow:auto;margin:.3rem 0}}
 .ai{{border:1px solid #8884;border-radius:9px;padding:.7rem;margin-bottom:1rem}}
 .ai.done{{border-color:#16a34a;background:#16a34a14}}
 .ai h3{{font-size:.82rem;margin:.1rem 0 .3rem;font-weight:600}}
 .ai .beat{{background:#8883;padding:.05rem .35rem;border-radius:4px;font-size:.7rem}}
 .ai.done .beat{{background:#16a34a33}}
 .ai .para{{opacity:.75;font-size:.76rem;margin:.2rem 0 .3rem}}
 .ai .fn{{font-size:.72rem;opacity:.7;margin:.35rem 0 .25rem}}
 .ai input{{width:100%;font:inherit;font-size:.76rem;padding:.4rem;border:1px solid #8886;
   border-radius:6px;background:Canvas;color:CanvasText}}
 .cp{{font-size:.7rem;padding:.25rem .55rem;margin-top:.1rem}}
</style></head><body>
<header>
 <h1>Stage 7 · {esc(slug)}</h1>
 <span id="cnt">0 / {total} seleccionadas</span><span id="aicnt"></span>
 <button class="primary" id="exp">Exportar 07-picks.txt</button>
 <button id="clr">Limpiar</button>
 <span style="opacity:.6;font-size:.8rem">guárdalo en la carpeta del episodio, luego <code>--download</code></span>
</header>
<div class="wrap">
<main>
{body}
</main>
<aside>
{aside}
</aside>
</div>
<script>
const SLUG="{esc(slug)}", HAS_AI={has_ai};
const LS="exodo-picks:"+SLUG, LSA=LS+":ai";
const boxes=[...document.querySelectorAll('.card')];
const aip=[...document.querySelectorAll('.aipath')];
const cnt=document.getElementById('cnt'), aicnt=document.getElementById('aicnt');
function jget(k,d){{try{{return JSON.parse(localStorage.getItem(k))??d}}catch(e){{return d}}}}
function sync(){{
  const s=[]; boxes.forEach(c=>{{if(c.querySelector('input').checked)s.push(c.dataset.key)}});
  localStorage.setItem(LS,JSON.stringify(s));
  cnt.textContent=s.length+' / {total} seleccionadas';
}}
function syncA(){{
  const o={{}}; aip.forEach(i=>{{const v=i.value.trim(); if(v)o[i.dataset.ai]=v;
    i.closest('.ai').classList.toggle('done',!!v)}});
  localStorage.setItem(LSA,JSON.stringify(o));
  aicnt.textContent = aip.length ? ('  ·  '+Object.keys(o).length+' / '+aip.length+' IA') : '';
}}
const initP=new Set(jget(LS,[]));
boxes.forEach(c=>{{const i=c.querySelector('input');
  if(initP.has(c.dataset.key))i.checked=true; i.addEventListener('change',sync)}});
const initA=jget(LSA,{{}});
aip.forEach(i=>{{if(initA[i.dataset.ai])i.value=initA[i.dataset.ai];
  i.addEventListener('input',syncA)}});
sync(); syncA();
document.querySelectorAll('.cp').forEach(b=>b.onclick=()=>{{
  navigator.clipboard.writeText(b.previousElementSibling.textContent.trim());
  const t=b.textContent; b.textContent='copiado ✓'; setTimeout(()=>b.textContent=t,1200);
}});
document.getElementById('clr').onclick=()=>{{
  boxes.forEach(c=>c.querySelector('input').checked=false); sync();
}};
document.getElementById('exp').onclick=async()=>{{
  const L=['# 07-picks.txt — beat<TAB>source:id<TAB>url  (generado por 07-candidates.html)'];
  boxes.forEach(c=>{{if(c.querySelector('input').checked)
    L.push(c.dataset.beat+'\\t'+c.dataset.key+'\\t'+c.dataset.url)}});
  const ail=[]; aip.forEach(i=>{{const v=i.value.trim(); if(v)
    ail.push(i.dataset.beats+'\\tai:'+i.dataset.ai+'\\t'+v)}});
  if(ail.length){{L.push('# --- IA generada (beats<TAB>ai:id<TAB>ruta o URL) ---'); L.push(...ail)}}
  const txt=L.join('\\n')+'\\n';
  try{{
    const fh=await window.showSaveFilePicker({{suggestedName:'07-picks.txt',
      types:[{{description:'texto',accept:{{'text/plain':['.txt']}}}}]}});
    const w=await fh.createWritable(); await w.write(txt); await w.close();
    alert('Guardado. Corre:  python tools/pull_assets.py '+SLUG+' --download');
    return;
  }}catch(e){{if(e&&e.name==='AbortError')return;}}
  navigator.clipboard&&navigator.clipboard.writeText(txt).catch(()=>{{}});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([txt],{{type:'text/plain'}}));
  a.download='07-picks.txt'; a.click();
}};
</script></body></html>
"""


def _drain(order, buckets, need):
    """Round-robin pop from buckets in `order` until `need` items or empty."""
    got, i, guard = [], 0, 0
    while len(got) < need and any(buckets.get(s) for s in order):
        s = order[i % len(order)]
        if buckets.get(s):
            got.append(buckets[s].pop(0))
        i += 1
        guard += 1
        if guard > len(order) * (need + 4):
            break
    return got


def gather_beat(beat, kind, source, query, opts, keys):
    """Query every source, trim to `n` total (default 3). For `stock` beats
    VIDEO candidates come first (motion b-roll saves editing work later);
    images fill the rest. opts: motion=no (images only) / motion=only (video).
    Returns (srcs, cands, notes)."""
    n = max(1, int(opts.get("n", 3)))
    srcs = expand_sources(kind, source)
    motion = opts.get("motion", "").lower()
    if motion == "no":
        srcs = [s for s in srcs if s not in VIDEO_SRCS]
    elif motion == "only":
        srcs = [s for s in srcs if s in VIDEO_SRCS]
    if not srcs:
        return [], [], ["sin fuentes tras filtro motion="]
    per = max(1, -(-n // len(srcs)))          # ceil(n / nsrcs)
    mn = int(opts.get("min", 0))
    buckets, notes = {}, []
    for src in srcs:
        fn = DISPATCH.get(src)
        if not fn:
            notes.append(f"fuente desconocida: {src}")
            continue
        key = keys.get(KEY_FOR.get(src, ""), "")
        if src in KEY_FOR and not key:
            notes.append(f"{src}: sin API key en tools/.env")
            continue
        try:
            cands = fn(query, key, per + 2, opts, video=src in VIDEO_SRCS)
        except requests.HTTPError as e:
            notes.append(f"{src}: HTTP {getattr(e.response, 'status_code', '?')}")
            continue
        except Exception as e:
            notes.append(f"{src}: {e}")
            continue
        if mn:
            cands = [c for c in cands if (not c.w) or max(c.w, c.h) >= mn]
        ori = opts.get("orientation", "")
        if ori == "landscape":
            cands = [c for c in cands if not (c.w and c.h and c.h > c.w)]
        elif ori == "portrait":
            cands = [c for c in cands if not (c.w and c.h and c.w > c.h)]
        if not cands:
            notes.append(f"{src}: 0 resultados")
        buckets[src] = cands
        time.sleep(0.3)
    vid_order = [s for s in srcs if s in VIDEO_SRCS]
    img_order = [s for s in srcs if s not in VIDEO_SRCS]
    merged = _drain(vid_order, buckets, n)                 # video first
    merged += _drain(img_order, buckets, n - len(merged))  # images fill the rest
    return srcs, merged, notes


def run(slug):
    keys = load_env()
    rows = read_spec(slug)
    md = [f"# Candidatos de recursos — {slug}", "",
          "> Stage 7 · pull automático (`tools/pull_assets.py`). **Esto no es selección.**",
          "> Trabaja en `07-candidates.html` (miniaturas). Para picar a mano aquí: `- [x]`.",
          "> stock = b-roll ilustrativo genérico, nunca 'lo real' (docs/12).", ""]
    groups, n_c = [], 0
    for beat, kind, source, query, rawopts in rows:
        opts = parse_opts(rawopts)
        srcs, cands, notes = gather_beat(beat, kind, source, query, opts, keys)
        groups.append((beat, kind, query, srcs, cands, notes))
        md.append(f"## beat {beat} — \"{query}\"  [{kind}: {','.join(srcs)}]\n")
        for c in cands:
            md.append(c.line())
            n_c += 1
        for note in notes:
            md.append(f"<!-- {note} -->")
        md.append("")
    ep = EP_DIR / slug
    ai = parse_ai_prompts(slug)
    (ep / "07-candidates.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (ep / "07-candidates.html").write_text(build_html(slug, groups, ai), encoding="utf-8")
    print(f"escrito  episodes/{slug}/07-candidates.md   ({n_c} candidatos, {len(rows)} beats)")
    print(f"escrito  episodes/{slug}/07-candidates.html  <- ábrelo en el navegador"
          + (f"  ({len(ai[1])} prompts IA en la columna derecha)" if ai[1] else ""))
    print("siguiente: marca las miniaturas, pega rutas IA, «Exportar 07-picks.txt», corre --download")


# ---------------------------------------------------------------------- download
PICK_RE = re.compile(r"^\s*- \[x\] `([a-z]+):([^`]+)` .* · (https?://\S+)", re.I)
BEAT_RE = re.compile(r"^## beat (\S+) —")
EXT_OK = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
          "video/mp4": ".mp4", "video/quicktime": ".mov"}


def read_picks(slug):
    """(beat, src, id, url) list. Prefer 07-picks.txt (from the HTML picker),
    fall back to '- [x]' lines in 07-candidates.md."""
    ep = EP_DIR / slug
    pf = ep / "07-picks.txt"
    if pf.exists():
        picks = []
        for ln in pf.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            parts = ln.split("\t")
            if len(parts) < 3 or ":" not in parts[1]:
                continue
            src, cid = parts[1].split(":", 1)
            picks.append((parts[0], src, cid, parts[2]))
        if picks:
            print(f"picks: 07-picks.txt ({len(picks)})")
            return picks
    md = ep / "07-candidates.md"
    if not md.exists():
        sys.exit(f"no {md.relative_to(ROOT)} — corre el pull primero")
    beat, picks = "?", []
    for ln in md.read_text(encoding="utf-8").splitlines():
        b = BEAT_RE.match(ln)
        if b:
            beat = b.group(1)
        m = PICK_RE.match(ln)
        if m:
            picks.append((beat, m.group(1), m.group(2), m.group(3)))
    if not picks:
        sys.exit("0 picks — usa 07-candidates.html («Exportar 07-picks.txt») "
                 "o marca `- [x]` en 07-candidates.md")
    print(f"picks: 07-candidates.md ({len(picks)})")
    return picks


def _dl_ai(ep, beat, aid, src, fname, rows, credits):
    """Place a Josh-generated AI image into assets/ai/ under its 07b filename."""
    dst_dir = ep / "assets" / "ai"
    dst_dir.mkdir(parents=True, exist_ok=True)
    data, srcext = None, ""
    if src.lower().startswith(("http://", "https://")):
        try:
            r = requests.get(requests.utils.requote_uri(src),
                             headers={"User-Agent": UA}, timeout=90)
            r.raise_for_status()
            data = r.content
            srcext = Path(src.split("?")[0]).suffix
        except Exception as e:
            print(f"  FALLO  ai:{aid}  {e}")
            return
    else:
        for cand in (Path(src), ROOT / src, ep / src, dst_dir / src):
            if cand.is_file():
                data, srcext = cand.read_bytes(), cand.suffix
                break
        if data is None:
            print(f"  FALLO  ai:{aid}  no existe la ruta: {src}")
            return
    ext = srcext.lower() if srcext.lower() in (".png", ".jpg", ".jpeg", ".webp") else Path(fname).suffix
    dst = dst_dir / (Path(fname).stem + ext)
    dst.write_bytes(data)
    dim = "?"
    try:
        im = Image.open(io.BytesIO(data))
        dim = f"{im.width}x{im.height}"
    except Exception:
        pass
    rel = dst.relative_to(ep).as_posix()
    print(f"  OK  {dst.name}  {dim}  (IA)")
    rows.append(f"| {beat} |  | {aid} — ilustración propia (IA) | — | — | "
                f"ilustración propia (IA) — rótulo en pantalla | {dim} |  |  | `{rel}` |")
    credits.append(f"- beat {beat}: {aid} — ilustración propia (IA), rótulo «Ilustración — Éxodo» en pantalla")


def download(slug):
    keys = load_env()
    picks = read_picks(slug)
    ep = EP_DIR / slug
    ai_fname = {p["id"]: p["fname"] for p in parse_ai_prompts(slug)[1]}
    rows, credits = [], []
    for beat, src, cid, url in picks:
        if src == "ai":
            _dl_ai(ep, beat, cid, url, ai_fname.get(cid, f"{cid}.png"), rows, credits)
            continue
        sub = ("video" if src in VIDEO_SRCS
               else "archive" if src in ARCHIVE_SRCS else "stock")
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
    sample = ("1\tarchive\tmet,commons,aic\tkatsushika hokusai\tmust=hokusai;n=3\n"
              "7\tstock\tstock\tocean wave breaking slow motion\tmin=1920;n=3\n"
              "12\tstock-img\tstock-img\tworn rice paper texture\tmin=2500;n=3\n")
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
