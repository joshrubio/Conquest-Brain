#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pull_assets.py — Stage 7 style pass (archive + free stock + intro).
Protocol: brain/12-available-material-protocol.md, brain/06 Stage 7.

`07-style-pass.html` is the central artifact of Stage 7. It shows,
per beat, the resources the pull found (left) and the AI-generation
prompts from 07b (right); an Intro section at the top collects the cold
open (brain/02 §0). Usuario 001 works entirely in that page, exports 07-picks.txt,
and --download turns every choice into files + 07-selection.md.

APIs
  stock   pexels  pixabay  unsplash  openverse   (video: pexels, pixabay)
  archive met  commons (Wikimedia Commons)
Keys live in tools/.env (gitignored). No .env -> only keyless sources run
(openverse, met, commons).

Usage
  python tools/pull_assets.py E0XX-slug --init
      scaffold episodes/E0XX-slug/07-pull.tsv

  python tools/pull_assets.py E0XX-slug
      run every spec row -> 07-style-pass.md (git record)
      + 07-style-pass.html (the picker). ~3 candidates per beat.

  python tools/pull_assets.py E0XX-slug --download
      read 07-picks.txt (from the picker's Finalizar button), download every
      choice into assets/{intro,stock,video,archive,ai}/, verify resolution,
      append assets/CREDITS.md, write 07-selection.md, print manifest rows.

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme as T  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes"
ENV = Path(__file__).resolve().parent / ".env"
UA = "ConquestOficial/1.0 (educational documentary; contact joshuerubio@gmail.com)"
TIMEOUT = 30

SPEC_F = "07-pull.tsv"
PASS_MD = "07-style-pass.md"
PASS_HTML = "07-style-pass.html"
PICKS_F = "07-picks.txt"
SELECTION_F = "07-selection.md"
MUSIC_DIR = ROOT / "brand" / "assets" / "music"
MUSIC_CAND = MUSIC_DIR / "candidates.md"

STOCK_IMG = ["pexels", "pixabay", "unsplash", "openverse"]         # kind: stock-img
STOCK_MOTION = ["pexelsv", "pixabayv", "pexels", "unsplash",       # kind: stock
                "pixabay", "openverse"]                            # video sources first
VIDEO_SRCS = {"pexelsv", "pixabayv"}
ARCHIVE_ALL = ["met", "commons"]          # the `archive` group keyword
ARCHIVE_SRCS = set(ARCHIVE_ALL)           # for assets/ folder routing

SPEC_HEADER = """# 07-pull.tsv — Stage 7 candidate-pull spec for this episode.
# Tab-separated. Lines starting with # are ignored. One row per shotlist beat
# that needs an image/clip pulled (own-graphics beats do NOT go here).
#
# columns:
#   beat    shotlist beat id (1, 25b, +B ...). Free text, just a label.
#           use INTRO1, INTRO2 ... for cold-open clip searches (brain/02 §0) —
#           their results land in the Intro section of the pass, not a beat.
#   kind    stock | stock-img | archive | video | intro
#   source  comma list, or a group keyword:
#             stock     = pexels+pixabay VIDEO first, then pexels/unsplash/
#                         pixabay/openverse images  (motion b-roll preferred)
#             stock-img = images only (pexels,pixabay,unsplash,openverse)
#             video     = pexels,pixabay video only
#             intro     = pexels,pixabay video — high-impact cold-open footage
#             archive   = met,commons
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
# stock = generic illustrative b-roll only, never "the real thing" (brain/12).
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
    print("\n  OK  openverse / met / commons  — no key needed")


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
            "openverse": q_openverse, "met": q_met, "commons": q_commons,
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
    if s in ("video", "intro"):
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
    f = EP_DIR / slug / SPEC_F
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


def _card_html(esc, c, beat, intro_only=False):
    badges = [f'<b>{esc(c.dim())}</b>']
    if c.dur:
        badges.append(f'<b class="vid">vídeo {c.dur}s</b>')
    if c.w and max(c.w, c.h) < 1920:
        badges.append('<b class="warn">baja-res</b>')
    if "1280" in c.lic:
        badges.append('<b class="warn">≤1280</b>')
    thumb = esc(c.thumb) if c.thumb else ""
    img = (f'<img loading="lazy" src="{thumb}" alt="">'
           if thumb else '<div class="noimg">sin miniatura</div>')
    if intro_only:
        toggles = '<input type="checkbox" class="ick" title="usar en la intro">'
    else:
        toggles = ('<input type="checkbox" class="pick" title="aprobar para este beat">'
                   '<label class="itog" title="incluir en la intro">'
                   '<input type="checkbox" class="ick"><span>intro</span></label>')
    return (
        f'<div class="card{" introcard" if intro_only else ""}" data-key="{esc(c.key)}" '
        f'data-beat="{esc(beat)}" data-url="{esc(c.url)}">{toggles}{img}'
        f'<figcaption><span class="badges">{"".join(badges)}</span>'
        f'<code>{esc(c.key)}</code>'
        f'<span class="who">{esc(c.author or "")}</span>'
        f'<span class="lic">{esc(c.lic)}</span>'
        f'<span class="lnk"><a href="{esc(c.url)}" target="_blank" rel="noopener">full</a>'
        + (f' · <a href="{esc(c.page)}" target="_blank" rel="noopener">page</a>' if c.page else "")
        + '</span></figcaption></div>')


def parse_music():
    """brand/assets/music/candidates.md -> [{key,id,title,artist,lic,dur,tag,url,page}]."""
    if not MUSIC_CAND.exists():
        return []
    txt = MUSIC_CAND.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"^## `([^`]+)` — (.+?)(?: · (.+))?$", txt, re.M):
        block = txt[m.end():txt.find("\n## ", m.end()) if "\n## " in txt[m.end():] else len(txt)]
        meta = re.search(r"^- (\d+:\d\d) · (CC[^\n·]*?)(?: · «[^»]*»)?(?: · (.+))?$", block, re.M)
        url = re.search(r"download: (\S+)", block)
        page = re.search(r"page: (\S+)", block)
        out.append({
            "key": m.group(1), "id": m.group(1).split(":", 1)[-1],
            "title": m.group(2).strip(), "artist": (m.group(3) or "").strip(),
            "dur": meta.group(1) if meta else "", "lic": meta.group(2).strip() if meta else "CC",
            "tag": (meta.group(3) or "").strip() if meta else "",
            "url": url.group(1) if url else "", "page": page.group(1) if page else "",
        })
    return out


def build_html(slug, groups, ai_prompts=("", []), intro_sug=None, music=None):
    import html as _h
    esc = _h.escape
    neg, prompts = ai_prompts
    intro_sug = intro_sug or []
    music = music or []
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
            cards.append(_card_html(esc, c, beat))
        cards.append('</div>')
        cards.append(
            f'<label class="beatcustom">recurso propio '
            f'<span>— si lo pegas, se usa ESTE y se ignora la selección del beat</span>'
            f'<input class="bcust" data-beat="{esc(beat)}" '
            f'placeholder="ruta local o URL para el beat {esc(beat)}"></label>')
        cards.append('</section>')
    body = "\n".join(cards)

    # ---- Intro section (cold open, brain/02 §0) ----
    slots = "".join(
        f'<label class="slot"><span>{i}</span><input class="intropath" data-slot="{i}" '
        f'placeholder="ruta o URL para la intro"></label>'
        for i in range(1, 6))
    if intro_sug:
        sug = ('<h3>Sugeridos — footage de impacto para el tema '
               f'<span>({len(intro_sug)})</span></h3><div class="grid">'
               + "\n".join(_card_html(esc, c, "intro", intro_only=True) for c in intro_sug)
               + '</div>')
    else:
        sug = ('<p class="empty">sin clips sugeridos — añade filas '
               '<code>INTRO1 … intro …</code> en 07-pull.tsv</p>')
    introbox = (
        '<section class="introbox"><h2>Intro / cold open '
        '<span class="q">— §0: hook visual de 2–5 planos (brain/02)</span></h2>'
        '<p class="hint">pega hasta 5 recursos propios, y/o marca sugeridos, '
        'y/o marca «intro» en cualquier card de abajo. El orden de exportación es: '
        'propios (1–5) → sugeridos → cards.</p>'
        f'<div class="slots">{slots}</div>{sug}</section>')

    # ---- Música (consideración) — al final ----
    if music:
        rows = []
        for m in music:
            meta = " · ".join(x for x in (m["dur"], m["lic"], m["tag"]) if x)
            rows.append(
                f'<label class="mtrk" data-key="{esc(m["key"])}" data-url="{esc(m["url"])}">'
                f'<input type="checkbox" class="mtrack">'
                f'<span class="mt"><b>{esc(m["title"])}</b> · {esc(m["artist"])}</span>'
                f'<span class="mm">{esc(meta)}</span>'
                f'<audio controls preload="none" src="{esc(m["url"])}"></audio>'
                + (f'<a href="{esc(m["page"])}" target="_blank" rel="noopener">page</a>' if m["page"] else "")
                + '</label>')
        musicbox = (
            '<section class="musicbox"><h2>Música <span class="q">— lecho ominoso ambiental '
            '(brain/16). Hoy consideramos todas; mañana quedan 3–5.</span></h2>'
            '<p class="hint">solo CC-BY / CC-BY-SA / CC0. Marca las que consideras; al exportar '
            'van como <code>music</code> y <code>--download</code> las baja a '
            '<code>brand/assets/music/</code> + <code>LICENSES.md</code>. '
            'Amplía el pool con <code>python tools/find_music.py "query"</code>.</p>'
            + "\n".join(rows) + '</section>')
    else:
        musicbox = ('<section class="musicbox"><h2>Música</h2><p class="empty">sin '
                    '<code>brand/assets/music/candidates.md</code> — corre '
                    '<code>python tools/find_music.py "dark cinematic ambient"</code></p></section>')

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
<title>Style pass — {esc(slug)}</title>
{T.CSS}
<style>
 #cnt,#introcnt,#aicnt{{font-variant-numeric:tabular-nums;color:var(--muted);font-size:.82rem}}
 .introbox,.musicbox{{max-width:1980px;margin:1rem auto 0;padding:1.75rem 2rem;
   background:var(--surface);border:1px solid var(--line-2);border-radius:var(--r);box-shadow:var(--shadow)}}
 .musicbox{{margin:0 auto 3rem}}
 .introbox>h2,.musicbox>h2{{margin-top:0}}
 .slots{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
   gap:.6rem;margin-bottom:1.5rem}}
 .slot{{display:flex;align-items:center;gap:.5rem;font-size:.78rem;color:var(--muted)}}
 .slot>span{{width:1rem;text-align:right;flex:none}}
 .slot input{{font-size:.76rem;padding:.4rem .55rem}}
 .ai input,.bcust{{font-size:.78rem}}
 .slot input:not(:placeholder-shown),
 .bcust:not(:placeholder-shown){{border-color:var(--lime-line);background:var(--lime-soft)}}
 .beatcustom{{display:block;margin-top:1rem;font-size:.76rem;color:var(--muted)}}
 .beatcustom>span{{opacity:.8}}
 .beatcustom .bcust,.beatcustom input{{margin-top:.35rem}}
 section:has(.bcust:not(:placeholder-shown)) .grid{{opacity:.4}}
 .mtrk{{display:grid;grid-template-columns:20px minmax(180px,1fr) auto 320px auto;
   gap:.9rem;align-items:center;padding:.55rem .3rem;border-bottom:1px solid var(--line);
   font-size:.82rem;cursor:pointer}}
 .mtrk:last-child{{border-bottom:0}}
 .mtrk:has(.mtrack:checked){{background:var(--lime-soft)}}
 .mtrk input[type=checkbox]{{width:18px;height:18px}}
 .mtrk .mm{{color:var(--muted);font-size:.75rem}}
 .mtrk audio{{height:34px;width:320px}}
 @media(max-width:900px){{.mtrk{{grid-template-columns:20px 1fr;grid-auto-flow:row}}
   .mtrk audio{{width:100%}}}}
 .wrap{{display:grid;grid-template-columns:minmax(0,1fr) 420px;gap:2.25rem;
   max-width:1980px;margin:0 auto;padding:1.75rem 1.5rem}}
 main{{min-width:0}}
 aside{{position:sticky;top:4.4rem;align-self:start;max-height:calc(100vh - 5.6rem);
   overflow:auto;border-left:1px solid var(--line);padding-left:1.5rem}}
 @media(max-width:1100px){{.wrap{{grid-template-columns:1fr;gap:1.5rem}}
   aside{{position:static;max-height:none;border-left:0;border-top:1px solid var(--line);
   padding-left:0;padding-top:1.5rem}}}}
 h2 .q{{font-weight:400;color:var(--muted)}}
 h2 .k{{float:right;font-weight:400;color:var(--muted);font-size:.8rem}}
 h3 span{{font-weight:400;color:var(--muted)}}
 .grid{{gap:1.1rem;grid-template-columns:repeat(auto-fill,minmax(235px,1fr))}}
 .card{{position:relative;padding:0;overflow:hidden;cursor:pointer;gap:0}}
 .card:has(.pick:checked){{border-color:var(--lime-line);
   box-shadow:inset 0 0 0 1px var(--lime-line);background:var(--lime-soft)}}
 .card:has(.ick:checked){{outline:2px dashed var(--bone);outline-offset:2px}}
 .card>input,.card .itog{{position:absolute;z-index:2;margin:8px}}
 .card>input{{left:0;width:20px;height:20px;cursor:pointer}}
 .card .itog{{right:0;display:flex;align-items:center;gap:.25rem;font-size:.66rem;
   background:#0c0a07d9;color:var(--bone);padding:.15rem .4rem;border-radius:6px;
   border:1px solid var(--line-2)}}
 .card .itog input{{width:13px;height:13px}}
 .card img,.card .noimg{{width:100%;aspect-ratio:4/3;object-fit:cover;
   background:#0d0c09;display:block}}
 .noimg{{display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:.8rem}}
 figcaption{{padding:.7rem .8rem .8rem;display:flex;flex-direction:column;gap:.28rem;font-size:.8rem}}
 .badges{{display:flex;gap:.35rem;flex-wrap:wrap;margin-bottom:.1rem}}
 .badges b{{font-weight:600;background:var(--surface-2);color:var(--muted);
   padding:.08rem .4rem;border-radius:5px;font-size:.72rem}}
 .badges b.warn{{background:var(--gold-soft);color:var(--gold)}}
 .badges b.vid{{background:var(--lime-soft);color:var(--lime)}}
 .who{{color:var(--fg)}} .lic{{color:var(--muted);font-size:.72rem}}
 .lnk{{font-size:.75rem;margin-top:.1rem}}
 .aih span{{font-weight:400;color:var(--muted);font-size:.75rem}}
 details.neg{{font-size:.74rem;margin:.8rem 0;color:var(--muted)}}
 details.neg pre,.ai pre{{font-size:.68rem;max-height:9.5rem}}
 .ai{{border:1px solid var(--line-2);border-radius:var(--r);padding:.95rem;margin-bottom:1.25rem;
   background:var(--surface)}}
 .ai.done{{border-color:var(--lime-line);background:var(--lime-soft)}}
 .ai h3{{font-size:.82rem;margin:.1rem 0 .4rem;font-weight:600}}
 .ai .beat{{background:var(--surface-2);color:var(--muted);padding:.08rem .4rem;
   border-radius:5px;font-size:.7rem}}
 .ai.done .beat{{background:var(--lime-soft);color:var(--lime)}}
 .ai .para{{color:var(--muted);font-size:.77rem;margin:.25rem 0 .35rem}}
 .ai .fn{{font-size:.73rem;color:var(--muted);margin:.45rem 0 .3rem}}
 .cp{{font-size:.7rem;padding:.3rem .6rem;margin-top:.15rem}}
</style></head><body>
<header>
 <h1>Style pass · {esc(slug)}</h1>
 <span id="cnt">0 / {total} beats</span>
 <span id="introcnt"></span>
 <span id="aicnt"></span>
 <button class="primary" id="exp">Finalizar Stage 7</button>
 <button id="clr">Limpiar</button>
 <a class="btn ghost" id="assets" href="http://localhost:8765/episodes/{slug}/assets/" target="_blank">Carpeta de recursos</a>
 <span class="small" style="opacity:.7">al finalizar se descargan los recursos elegidos ahí</span>
</header>
{introbox}
<div class="wrap">
<main>
{body}
</main>
<aside>
{aside}
</aside>
</div>
{musicbox}
<script>
const SLUG="{esc(slug)}", HAS_AI={has_ai};
const LS="conquest-pass:"+SLUG, LSA=LS+":ai", LSI=LS+":intro";
const cards=[...document.querySelectorAll('.card')];
const slots=[...document.querySelectorAll('.intropath')];
const bcust=[...document.querySelectorAll('.bcust')];
const mtrk=[...document.querySelectorAll('.mtrk')];
const aip=[...document.querySelectorAll('.aipath')];
const cnt=document.getElementById('cnt'), icnt=document.getElementById('introcnt'),
      aicnt=document.getElementById('aicnt');
function jget(k,d){{try{{return JSON.parse(localStorage.getItem(k))??d}}catch(e){{return d}}}}
function pk(c){{return c.querySelector('.pick')}}
function ik(c){{return c.querySelector('.ick')}}
function bmap(){{const m={{}}; bcust.forEach(i=>{{const v=i.value.trim(); if(v)m[i.dataset.beat]=v}}); return m;}}
function sync(){{
  const bm=bmap(), picks=[],intro=[];
  cards.forEach(c=>{{
    if(pk(c)&&pk(c).checked)picks.push(c.dataset.key);
    if(ik(c)&&ik(c).checked)intro.push(c.dataset.key);
  }});
  localStorage.setItem(LS,JSON.stringify(picks));
  localStorage.setItem(LSI,JSON.stringify(intro));
  localStorage.setItem(LS+':slots',JSON.stringify(slots.map(s=>s.value)));
  localStorage.setItem(LS+':bcust',JSON.stringify(bm));
  const mus=mtrk.filter(t=>t.querySelector('.mtrack').checked).map(t=>t.dataset.key);
  localStorage.setItem(LS+':music',JSON.stringify(mus));
  const sl=slots.filter(s=>s.value.trim()).length;
  const covered=new Set([...picks.map(k=>cards.find(c=>c.dataset.key===k).dataset.beat),
                         ...Object.keys(bm)]);
  cnt.textContent=covered.size+' / {total} beats'+(Object.keys(bm).length?(' ('+Object.keys(bm).length+' propios)'):'');
  icnt.textContent='  ·  intro: '+(sl+intro.length)+'  ('+sl+' propios + '+intro.length+' cards)';
}}
function syncA(){{
  const o={{}}; aip.forEach(i=>{{const v=i.value.trim(); if(v)o[i.dataset.ai]=v;
    i.closest('.ai').classList.toggle('done',!!v)}});
  localStorage.setItem(LSA,JSON.stringify(o));
  aicnt.textContent = aip.length ? ('  ·  '+Object.keys(o).length+' / '+aip.length+' IA') : '';
}}
const initP=new Set(jget(LS,[])), initI=new Set(jget(LSI,[]));
cards.forEach(c=>{{
  if(pk(c)&&initP.has(c.dataset.key))pk(c).checked=true;
  if(ik(c)&&initI.has(c.dataset.key))ik(c).checked=true;
  c.addEventListener('click',e=>{{
    if(e.target.closest('a,input,.itog'))return;
    const box=pk(c)||ik(c);
    if(box){{box.checked=!box.checked; sync();}}
  }});
  c.querySelectorAll('input').forEach(i=>i.addEventListener('change',sync));
}});
const initS=jget(LS+':slots',[]);
slots.forEach((s,ix)=>{{if(initS[ix])s.value=initS[ix]; s.addEventListener('input',sync)}});
const initB=jget(LS+':bcust',{{}});
bcust.forEach(i=>{{if(initB[i.dataset.beat])i.value=initB[i.dataset.beat];
  i.addEventListener('input',sync)}});
const initM=new Set(jget(LS+':music',[]));
mtrk.forEach(t=>{{const b=t.querySelector('.mtrack');
  if(initM.has(t.dataset.key))b.checked=true;
  b.addEventListener('change',sync);
  t.addEventListener('click',e=>{{if(e.target.closest('a,audio,input'))return;
    b.checked=!b.checked; sync();}});}});
const initA=jget(LSA,{{}});
aip.forEach(i=>{{if(initA[i.dataset.ai])i.value=initA[i.dataset.ai];
  i.addEventListener('input',syncA)}});
sync(); syncA();
document.querySelectorAll('.cp').forEach(b=>b.onclick=()=>{{
  navigator.clipboard.writeText(b.previousElementSibling.textContent.trim());
  const t=b.textContent; b.textContent='copiado'; setTimeout(()=>b.textContent=t,1200);
}});
document.getElementById('clr').onclick=()=>{{
  cards.forEach(c=>c.querySelectorAll('input').forEach(i=>i.checked=false));
  mtrk.forEach(t=>t.querySelector('.mtrack').checked=false);
  slots.forEach(s=>s.value=''); bcust.forEach(i=>i.value=''); aip.forEach(i=>i.value='');
  sync(); syncA();
}};
document.getElementById('exp').onclick=async()=>{{
  const L=['# {PICKS_F} — generado por {PASS_HTML}',
           '# col1: <beat> | "intro" | "music"',
           '# col2: source:id | custom:N (intro) | custom:<beat> | ai:id',
           '# col3: url o ruta.   custom:<beat> ANULA la selección de ese beat.'];
  const intro=[];
  slots.forEach(s=>{{const v=s.value.trim(); if(v)intro.push('intro\\tcustom:'+s.dataset.slot+'\\t'+v)}});
  cards.forEach(c=>{{if(ik(c)&&ik(c).checked)intro.push('intro\\t'+c.dataset.key+'\\t'+c.dataset.url)}});
  if(intro.length){{L.push('# --- INTRO (cold open §0, en orden) ---'); L.push(...intro);}}
  const bm=bmap(), beats=[];
  Object.keys(bm).forEach(b=>beats.push(b+'\\tcustom:'+b+'\\t'+bm[b]));   // propio -> anula el beat
  cards.forEach(c=>{{if(pk(c)&&pk(c).checked&&!(c.dataset.beat in bm))
    beats.push(c.dataset.beat+'\\t'+c.dataset.key+'\\t'+c.dataset.url)}});
  if(beats.length){{L.push('# --- BEATS ---'); L.push(...beats);}}
  const ail=[]; aip.forEach(i=>{{const v=i.value.trim(); if(v)
    ail.push(i.dataset.beats+'\\tai:'+i.dataset.ai+'\\t'+v)}});
  if(ail.length){{L.push('# --- IA generada ---'); L.push(...ail);}}
  const mus=[]; mtrk.forEach(t=>{{if(t.querySelector('.mtrack').checked)
    mus.push('music\\t'+t.dataset.key+'\\t'+t.dataset.url)}});
  if(mus.length){{L.push('# --- MÚSICA (consideración; brand/assets/music/) ---'); L.push(...mus);}}
  const txt=L.join('\\n')+'\\n';
  // 1: write 07-picks.txt via the server, then let advance.py run --download
  try{{
    const w=await fetch('http://localhost:8765/'+
      'episodes/'+SLUG+'/{PICKS_F}',{{method:'GET'}}); // probe server up
  }}catch(e){{}}
  try{{
    const r=await fetch('http://localhost:8765/finish',{{method:'POST',
      headers:{{'content-type':'application/json'}},
      body:JSON.stringify({{ep:SLUG.slice(0,4),stage:7,payload:{{txt:txt,picks:txt}}}})}});
    if(r.ok){{const j=await r.json();
      alert('Stage 7 cerrado — descargando recursos.\\n'+(j.msg||'')+'\\nDashboard actualizado.');return;}}
  }}catch(e){{}}
  try{{
    const fh=await window.showSaveFilePicker({{suggestedName:'{PICKS_F}',
      types:[{{description:'texto',accept:{{'text/plain':['.txt']}}}}]}});
    const w=await fh.createWritable(); await w.write(txt); await w.close();
    alert('Guardado (server no detectado). Corre:  python tools/pull_assets.py '+SLUG+' --download');
    return;
  }}catch(e){{if(e&&e.name==='AbortError')return;}}
  navigator.clipboard&&navigator.clipboard.writeText(txt).catch(()=>{{}});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([txt],{{type:'text/plain'}}));
  a.download='{PICKS_F}'; a.click();
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
    md = [f"# Style pass — {slug}", "",
          "> Stage 7 · central. Pull automático (`tools/pull_assets.py`) — **esto no es selección.**",
          f"> Trabaja en `{PASS_HTML}` (miniaturas + prompts IA + intro). Para picar a mano aquí: `- [x]`.",
          "> stock = b-roll ilustrativo genérico, nunca 'lo real' (brain/12).", ""]
    groups, intro_sug, n_c = [], [], 0
    for beat, kind, source, query, rawopts in rows:
        opts = parse_opts(rawopts)
        srcs, cands, notes = gather_beat(beat, kind, source, query, opts, keys)
        n_c += len(cands)
        if kind.lower() == "intro" or beat.lower().startswith("intro"):
            for c in cands:
                if len(intro_sug) < 5 and c.key not in {x.key for x in intro_sug}:
                    intro_sug.append(c)
            md.append(f"## intro — \"{query}\"  [{kind}]\n")
        else:
            groups.append((beat, kind, query, srcs, cands, notes))
            md.append(f"## beat {beat} — \"{query}\"  [{kind}: {','.join(srcs)}]\n")
        for c in cands:
            md.append(c.line())
        for note in notes:
            md.append(f"<!-- {note} -->")
        md.append("")
    ep = EP_DIR / slug
    ai = parse_ai_prompts(slug)
    music = parse_music()
    (ep / PASS_MD).write_text("\n".join(md) + "\n", encoding="utf-8")
    (ep / PASS_HTML).write_text(build_html(slug, groups, ai, intro_sug, music), encoding="utf-8")
    print(f"escrito  episodes/{slug}/{PASS_MD}   ({n_c} candidatos, {len(groups)} beats"
          + (f", {len(intro_sug)} clips intro" if intro_sug else "") + ")")
    print(f"escrito  episodes/{slug}/{PASS_HTML}  <- ábrelo en el navegador"
          + (f"  ({len(ai[1])} prompts IA)" if ai[1] else "")
          + (f"  ({len(music)} tracks música)" if music else ""))
    print("siguiente: intro + miniaturas + rutas IA, «Finalizar Stage 7», corre --download")


# ---------------------------------------------------------------------- download
PICK_RE = re.compile(r"^\s*- \[x\] `([a-z]+):([^`]+)` .* · (https?://\S+)", re.I)
BEAT_RE = re.compile(r"^## beat (\S+) —")
EXT_OK = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
          "video/mp4": ".mp4", "video/quicktime": ".mov"}


def read_picks(slug):
    """(beat_or_'intro', src, id, url) list. Prefer 07-picks.txt (from the
    picker), fall back to '- [x]' lines in 07-style-pass.md (beats only)."""
    ep = EP_DIR / slug
    pf = ep / PICKS_F
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
            print(f"picks: {PICKS_F} ({len(picks)})")
            return picks
    md = ep / PASS_MD
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
        sys.exit(f"0 picks — usa {PASS_HTML} («Finalizar Stage 7») "
                 f"o marca `- [x]` en {PASS_MD}")
    print(f"picks: {PASS_MD} ({len(picks)})")
    return picks


def _dl_ai(ep, beat, aid, src, fname, rows, credits):
    """Place a user-generated AI image into assets/ai/ under its 07b filename.
    Appends a (beat, 'ai:id', '(propia)', dim, relpath) tuple to `rows`."""
    dst_dir = ep / "assets" / "ai"
    dst_dir.mkdir(parents=True, exist_ok=True)
    data, srcext = None, ""
    if src.lower().startswith(("http://", "https://")):
        d, _ = _fetch(src, "ai")
        if d is None:
            print(f"  FALLO  ai:{aid}  {src}")
            return
        data, srcext = d, Path(src.split("?")[0]).suffix
    else:
        for cand in (Path(src), ROOT / src, ep / src, dst_dir / src, Path.cwd() / src):
            if cand.is_file():
                data, srcext = cand.read_bytes(), cand.suffix
                break
        if data is None:
            print(f"  FALLO  ai:{aid}  no existe la ruta: {src}")
            return
    ext = srcext.lower() if srcext.lower() in (".png", ".jpg", ".jpeg", ".webp") else Path(fname).suffix
    dst = dst_dir / (Path(fname).stem + ext)
    dst.write_bytes(data)
    dim = _dims(data, ext) or "?"
    rel = f"assets/ai/{dst.name}"
    print(f"  OK  {dst.name}  {dim}  (IA)")
    rows.append((beat, f"ai:{aid}", "(propia)", dim, rel))
    credits.append(f"- {beat}: {aid} — ilustración propia (IA), rótulo «Ilustración — Conquest» en pantalla")


def _fetch(url, src):
    """Fetch a URL (or read a local path). Returns (bytes, final_url) or (None, err)."""
    if not url.lower().startswith(("http://", "https://")):
        for cand in (Path(url), ROOT / url, Path.cwd() / url):
            if cand.is_file():
                return cand.read_bytes(), cand.as_posix()
        return None, f"no existe la ruta: {url}"
    tries, hdr = [url], {"User-Agent": UA}
    last = "?"
    for u in tries:
        try:
            r = requests.get(requests.utils.requote_uri(u), headers=hdr, timeout=90)
            r.raise_for_status()
            return r.content, u
        except Exception as e:
            last = e
    return None, last


def _dims(data, ext):
    if ext.lower() in (".jpg", ".jpeg", ".png", ".webp"):
        try:
            im = Image.open(io.BytesIO(data))
            return f"{im.width}x{im.height}"
        except Exception:
            return "?"
    return ""


def _ext_for(data, final_url, src):
    ext = Path(final_url.split("?")[0]).suffix.lower()
    if ext in (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".webm", ".tif", ".tiff"):
        return ext
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[4:12] == b"ftypmp42" or data[4:8] == b"ftyp":
        return ".mp4"
    if src in VIDEO_SRCS:
        return ".mp4"
    return ".jpg"


def _audio_ext(data):
    if data[:3] == b"ID3" or data[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xfa", b"\xff\xf2"):
        return ".mp3"
    if data[:4] == b"OggS":
        return ".ogg"
    if data[:4] == b"fLaC":
        return ".flac"
    return ".mp3"


def _dl_music(key, url, mmeta):
    """Download a considered track into brand/assets/music/ + log its licence."""
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    data, _ = _fetch(url, "music")
    if data is None:
        print(f"  FALLO  música {key}  (sin descarga)")
        return
    m = mmeta.get(key, {})
    safe = re.sub(r"[^A-Za-z0-9]+", "-", m.get("title", key)).strip("-").lower()[:40] or "track"
    fn = MUSIC_DIR / f"{key.replace(':', '_')}_{safe}{_audio_ext(data)}"
    fn.write_bytes(data)
    print(f"  OK  {fn.name}  ({len(data)//1024} KB)  (música)")
    lf = MUSIC_DIR / "LICENSES.md"
    prev = lf.read_text(encoding="utf-8") if lf.exists() else (
        "# Licencias — música de fondo\n\n> CC, no dominio público. "
        "Atribuir cada pista (autor + licencia) en la descripción del vídeo.\n")
    line = (f"- `{fn.name}` — {m.get('title', '')} · {m.get('artist', '')} — "
            f"{m.get('lic', 'CC')} — atribución obligatoria en 09-description.md")
    if line not in prev:
        lf.write_text(prev.rstrip() + "\n" + line + "\n", encoding="utf-8")


def download(slug):
    keys = load_env()
    picks = read_picks(slug)
    ep = EP_DIR / slug
    ai_fname = {p["id"]: p["fname"] for p in parse_ai_prompts(slug)[1]}
    mmeta = {m["key"]: m for m in parse_music()}
    intro_rows, beat_rows, ai_rows, credits = [], [], [], []
    intro_n = 0

    for beat, src, cid, url in picks:
        is_intro = beat.lower() == "intro"

        if beat.lower() == "music":
            _dl_music(f"{src}:{cid}", url, mmeta)
            continue

        if src == "ai" and not is_intro:
            _dl_ai(ep, beat, cid, url, ai_fname.get(cid, f"{cid}.png"), ai_rows, credits)
            continue

        data, final = _fetch(url, src)
        if data is None:
            print(f"  FALLO  {'intro ' if is_intro else ''}{src}:{cid}  {final}")
            continue
        ext = _ext_for(data, final, src)
        dim = _dims(data, ext)

        if is_intro:
            intro_n += 1
            sub, name = "intro", f"intro{intro_n:02d}_{src}_{re.sub(r'[^A-Za-z0-9]', '', cid)[:14]}{ext}"
        else:
            if src == "custom":                       # the user's own path for this beat
                sub = "video" if ext in (".mp4", ".mov", ".webm") else "archive"
            elif src in VIDEO_SRCS:
                sub = "video"
            elif src in ARCHIVE_SRCS:
                sub = "archive"
            else:
                sub = "stock"
            safe = re.sub(r"[^A-Za-z0-9+-]", "", beat)
            name = f"beat{safe}_{src}_{re.sub(r'[^A-Za-z0-9]', '', cid)[:14]}{ext}"
        dst = ep / "assets" / sub
        dst.mkdir(parents=True, exist_ok=True)
        (dst / name).write_bytes(data)
        rel = f"assets/{sub}/{name}"

        if src == "unsplash" and keys.get("UNSPLASH_ACCESS_KEY"):
            try:
                requests.get(f"https://api.unsplash.com/photos/{cid}/download",
                             headers={"Authorization": f"Client-ID {keys['UNSPLASH_ACCESS_KEY']}"},
                             timeout=15)
            except Exception:
                pass

        tag = "intro" if is_intro else beat
        print(f"  OK  {name}  {dim}")
        row = (beat if not is_intro else str(intro_n), f"{src}:{cid}", final, dim, rel)
        (intro_rows if is_intro else beat_rows).append(row)
        credits.append(f"- {tag}: {src}:{cid} — {final if final.startswith('http') else '(archivo propio)'}")

    _write_selection(ep, slug, intro_rows, beat_rows, ai_rows)
    if credits:
        cf = ep / "assets" / "CREDITS.md"
        cf.parent.mkdir(parents=True, exist_ok=True)
        prev = cf.read_text(encoding="utf-8") if cf.exists() else "# Créditos de recursos\n"
        cf.write_text(prev.rstrip() + "\n" + "\n".join(credits) + "\n", encoding="utf-8")
        print(f"\ncréditos    → episodes/{slug}/assets/CREDITS.md")


def _write_selection(ep, slug, intro_rows, beat_rows, ai_rows):
    L = [f"# Selección — Stage 7 style pass · {slug}", "",
         f"> Generado por `pull_assets.py --download` desde `{PICKS_F}`. "
         f"Este es el registro de decisiones del pase; se pliega en `07-assets.md`.", ""]
    if intro_rows:
        L += ["## Intro / cold open (§0) — orden de pantalla", "",
              "| # | Fuente | Res. | Archivo |", "|---|--------|------|---------|"]
        L += [f"| {n} | {s} | {d or '—'} | `{p}` |" for n, s, _u, d, p in intro_rows]
        L += [""]
    if beat_rows:
        L += ["## Por beat", "", "| Beat | Fuente | Res. | Archivo |",
              "|------|--------|------|---------|"]
        L += [f"| {b} | {s} | {d or '—'} | `{p}` |" for b, s, _u, d, p in beat_rows]
        L += [""]
    if ai_rows:
        L += ["## Ilustración IA (rótulo «Ilustración — Conquest» en pantalla)", "",
              "| Beat | id | Res. | Archivo |", "|------|----|------|---------|"]
        L += [f"| {b} | {s.split(':', 1)[1]} | {d} | `{p}` |" for b, s, _u, d, p in ai_rows]
        L += [""]
    (ep / SELECTION_F).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"\nselección   → episodes/{slug}/{SELECTION_F}")
    hdr = ("| Beat/Intro | Fuente | Enlace | Licencia | Res. | Uso | Pase | Archivo |\n"
           "|---|---|---|---|---|---|---|---|")
    body = []
    for n, s, u, d, p in intro_rows:
        body.append(f"| intro {n} | {s} | {u} |  | {d} |  |  | `{p}` |")
    for b, s, u, d, p in beat_rows:
        body.append(f"| {b} | {s} | {u} |  | {d} |  |  | `{p}` |")
    for b, s, u, d, p in ai_rows:
        body.append(f"| {b} | {s} | (propia) | ilustración IA — rótulo en pantalla | {d} |  |  | `{p}` |")
    if body:
        print("\n--- filas para 07-assets.md ---\n" + hdr + "\n" + "\n".join(body))


# -------------------------------------------------------------------------- init
def init(slug):
    d = EP_DIR / slug
    if not d.is_dir():
        sys.exit(f"no existe {d}")
    f = d / SPEC_F
    if f.exists():
        sys.exit(f"ya existe {f.relative_to(ROOT)}")
    sample = ("INTRO1\tintro\tintro\t<tema> cinematic aerial\torientation=landscape;min=1920;n=3\n"
              "1\tarchive\tmet,commons\t<sujeto>\tmust=<sujeto>;n=3\n"
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
