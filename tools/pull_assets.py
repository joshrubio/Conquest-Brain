#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pull_assets.py — Stage 7 style pass (archive + free stock).
Protocol: brain/12-available-material-protocol.md, brain/06 Stage 7.

`07-style-pass.html` is the central artifact of Stage 7. It shows, per
beat, the resources the pull found (left) and the AI-generation prompts
from 07b (right). **Every beat gets its own row and its own card — the
cold-open hook beats are ordinary beats here too, no separate pool.**
Usuario 001 works entirely in that page, exports 07-picks.txt, and
--download turns every choice into files + 07-selection.md.

**No beat should ever sit at "sin fila."** Every shotlist beat whose
`tipo` is `archivo`/`stock`/`kb` needs a matching row in `07-pull.tsv`
(`ia`/`gráfico`/`acamara`/`negro` beats don't — they're covered another
way). If a row's search comes back empty or weak after a couple of
query refinements, don't leave the beat empty: turn it into a
recreation — change its `tipo` to `ia` in `06-shotlist.md`, add a prompt
block to `07b-ai-prompts.md`, and drop its row here (`brain/12`,
`brain/15`). Use `--beats` (below) to re-run only the rows you're
refining instead of the whole spec.

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

  python tools/pull_assets.py E0XX-slug --beats 5,12,47
      run only the listed rows (by their `beat` label) — for re-running
      a handful of refined queries without re-fetching everything.
      Merges into the existing 07-style-pass.md/.html; other beats keep
      their last results.

  python tools/pull_assets.py E0XX-slug --download
      read 07-picks.txt (from the picker's Finalizar button), download every
      choice into assets/{stock,video,archive,ai}/, verify resolution,
      append assets/CREDITS.md, write 07-selection.md, print manifest rows.

  python tools/pull_assets.py --check-keys
      report which API keys tools/.env provides
"""
import io
import re
import subprocess
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
CACHE_F = "_exports/07-pull-cache.json"   # gitignored — lets --beats re-run a
                                           # subset without re-searching the rest
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
# Tab-separated. Lines starting with # are ignored.
#
# ONE ROW PER SHOTLIST BEAT whose `tipo` is `archivo`/`stock`/`kb` — no
# exceptions, including the cold-open hook beats (they're ordinary beats
# here, not a separate intro pool). `ia`/`gráfico`/`acamara`/`negro` beats
# don't go here. If a beat's asset is reused across several beats (a
# PROMISE/PAY pair, an eco), one row still covers all of them — label it
# with the FIRST beat number.
#
# A beat should never end up "sin fila" in the style pass. If a row comes
# back with 0 or weak candidates: refine the query (broader terms, a
# different source, drop a `must=`/`min=` filter) and re-run just that
# beat — `python tools/pull_assets.py <slug> --beats 5,12` — instead of
# the whole file. If it's STILL empty after ~2 refinements, the honest
# call isn't to leave it blank: turn the beat into a recreation — set its
# `tipo` to `ia` in 06-shotlist.md, add a prompt block to
# 07b-ai-prompts.md, and delete its row here (brain/12, brain/15).
#
# columns:
#   beat    shotlist beat id (1, 25b, +B ...). Free text, just a label.
#   kind    stock | stock-img | archive | video
#   source  comma list, or a group keyword:
#             stock     = pexels+pixabay VIDEO first, then pexels/unsplash/
#                         pixabay/openverse images  (motion b-roll preferred)
#             stock-img = images only (pexels,pixabay,unsplash,openverse)
#             video     = pexels,pixabay video only — for the cold-open hook
#                         shots, prefer this or `stock` (§0: vídeo preferido)
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

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__slots__}

    @classmethod
    def from_dict(cls, d):
        return cls(d["src"], d["id"], d["url"], w=d.get("w", 0), h=d.get("h", 0),
                    author=d.get("author", ""), lic=d.get("lic", ""), page=d.get("page", ""),
                    dur=d.get("dur", 0), thumb=d.get("thumb", ""))


def load_pull_cache(slug):
    f = EP_DIR / slug / CACHE_F
    if not f.exists():
        return {}
    try:
        raw = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for beat, g in raw.items():
        out[beat] = (g["kind"], g["query"], g["srcs"],
                     [Cand.from_dict(c) for c in g["cands"]], g["notes"])
    return out


def save_pull_cache(slug, groups):
    """groups: [(beat, kind, query, srcs, cands, notes), ...] — the FULL merged
    set (live + reused), so the next --beats run has everything to fall back on."""
    f = EP_DIR / slug / CACHE_F
    f.parent.mkdir(parents=True, exist_ok=True)
    data = {beat: {"kind": kind, "query": query, "srcs": srcs,
                   "cands": [c.to_dict() for c in cands], "notes": notes}
            for beat, kind, query, srcs, cands, notes in groups}
    f.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


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


SHOTLIST_F = "06-shotlist.md"


def parse_timeline(slug):
    """The shotlist spine, in emission order. [] if no 06-shotlist.md.
    [{n, sec, tipo, asset, rotulo, motion, marcador, frag}]."""
    f = EP_DIR / slug / SHOTLIST_F
    if not f.exists():
        return []
    md = f.read_text(encoding="utf-8")
    m = re.search(r"##\s*Timeline.*?\n(\|.*?)(?:\n\n|\n##|\Z)", md, re.S)
    if not m:
        return []
    out = []
    for ln in m.group(1).splitlines():
        if not ln.strip().startswith("|"):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 10 or not c[0].isdigit():
            continue
        out.append({"n": c[0], "in": c[1], "dur": c[2], "sec": c[3],
                    "tipo": c[4].lower(), "asset": c[5].strip("`"),
                    "rotulo": "" if c[6] in ("—", "-") else c[6],
                    "motion": c[7], "marcador": "" if c[8] in ("—", "-") else c[8],
                    "frag": c[9]})
    return out


def parse_graphics_table(slug):
    """id -> {shows, datos, rotulo, style} from the 'Gráficos / motion' table."""
    f = EP_DIR / slug / SHOTLIST_F
    if not f.exists():
        return {}
    md = f.read_text(encoding="utf-8")
    m = re.search(r"##\s*Gr[aá]ficos?\s*/\s*motion.*?\n(\|.*?)(?:\n\n|\n##|\Z)", md, re.S | re.I)
    if not m:
        return {}
    out = {}
    for ln in m.group(1).splitlines():
        if not ln.strip().startswith("|"):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 3 or c[0].lower() in ("id", "") or set("".join(c)) <= set("-: "):
            continue
        out[c[0].strip("`")] = {
            "shows": c[2] if len(c) > 2 else "", "datos": c[3] if len(c) > 3 else "",
            "rotulo": c[4] if len(c) > 4 else "", "style": c[5] if len(c) > 5 else ""}
    return out


def _ai_beatset(beats_field):
    """'13·15·30·40' / 'beat 17 — …' -> {'13','15','30','40'} / {'17'}."""
    return set(re.findall(r"\d+[a-z]?", beats_field or ""))


def _card_html(esc, c, beat):
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
    toggles = '<input type="checkbox" class="pick" title="aprobar para este beat">'
    return (
        f'<div class="card" data-key="{esc(c.key)}" '
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


def build_html(slug, groups, ai_prompts=("", []), music=None,
               timeline=None, graphics=None):
    import html as _h
    esc = _h.escape
    neg, prompts = ai_prompts
    music = music or []
    graphics = graphics or {}
    timeline = timeline or []

    gbybeat = {b: (q, s, c, nt) for b, k, q, s, c, nt in groups}
    NEED = {"ia", "archivo", "stock", "kb", "gráfico", "grafico"}

    # timeline missing (no 06-shotlist yet) -> synthesise rows from the pull spec
    if not timeline:
        timeline = [{"n": b, "sec": "", "tipo": (k.lower() if k.lower() in NEED else "archivo"),
                     "asset": "", "rotulo": "", "motion": "", "marcador": "", "frag": q}
                    for b, k, q, s, c, nt in groups]

    # a shotlist asset reused across several beats (a PROMISE/PAY pair, an
    # "eco") only needs ONE 07-pull.tsv row — labelled with whichever beat
    # number is first. Every other beat sharing that same `asset` string
    # resolves to that same row here, so it never shows "sin fila" just
    # because its own beat number isn't the row's label.
    asset_to_row = {}
    for tb in timeline:
        if tb["n"] in gbybeat and tb.get("asset"):
            asset_to_row.setdefault(tb["asset"], tb["n"])

    def _row_for(n, asset):
        return gbybeat.get(n) or (gbybeat.get(asset_to_row.get(asset)) if asset else None)

    def _find_prompt(beat_n, asset):
        for p in prompts:
            if beat_n in _ai_beatset(p["beats"]) or p["fname"].rsplit(".", 1)[0] == asset:
                return p
        return None

    total = sum(1 for b in timeline if b["tipo"] in NEED) or len(groups)
    used_beats, seen_ai, neg_shown, cards = set(), set(), [False], []

    def _ai_block(p, n):
        out = []
        if neg and not neg_shown[0]:
            neg_shown[0] = True
            out.append(f'<details class="neg"><summary>negative prompt (compartido)</summary>'
                       f'<pre>{esc(neg)}</pre></details>')
        out.append(
            f'<div class="ai" data-ai="{esc(p["id"])}">'
            + (f'<p class="para">{esc(p["para"])}</p>' if p["para"] else "")
            + f'<pre>{esc(p["prompt"])}</pre>'
            f'<button class="cp">copiar prompt</button>'
            f'<div class="fn">genera la imagen, guárdala como '
            f'<code>{esc(p["fname"])}</code> y pega su ruta:</div>'
            f'<input class="aipath" data-ai="{esc(p["id"])}" data-beats="{esc(n)}" '
            f'data-fname="{esc(p["fname"])}" '
            f'placeholder="ruta local o URL de la imagen del beat {esc(n)}"></div>')
        return "".join(out)

    for b in timeline:
        n, tipo, asset = b["n"], b["tipo"], b["asset"]
        sec = f' <span class="sec">{esc(b["sec"])}</span>' if b["sec"] else ""
        mo = f' · {esc(b["motion"])}' if b["motion"] else ""
        cards.append(f'<section class="beat" data-tipo="{esc(tipo)}" data-beat="{esc(n)}">'
                     f'<h2>beat {esc(n)}{sec}<span class="k">{esc(tipo)}{mo}</span></h2>')
        mk = f' <span class="mk">{esc(b["marcador"])}</span>' if b["marcador"] else ""
        rot = f' <span class="rot">rótulo: «{esc(b["rotulo"])}»</span>' if b["rotulo"] else ""
        if b["frag"] or mk or rot:
            cards.append(f'<p class="frag">{esc(b["frag"])}{mk}{rot}</p>')

        if tipo == "ia":
            p = _find_prompt(n, asset)
            if p and p["id"] not in seen_ai:
                seen_ai.add(p["id"])
                cards.append(_ai_block(p, n))
            elif p:
                cards.append(f'<p class="ref">→ misma imagen que <code>{esc(p["id"])}</code> '
                             f'(<code>{esc(p["fname"])}</code>); genérala una sola vez.</p>')
            else:
                cards.append(f'<p class="empty">beat IA «{esc(asset)}» sin prompt en '
                             f'<code>07b-ai-prompts.md</code>.</p>'
                             f'<label class="beatcustom">recurso propio'
                             f'<input class="bcust" data-beat="{esc(n)}" '
                             f'placeholder="ruta o URL"></label>')

        elif tipo in ("gráfico", "grafico"):
            g = graphics.get(asset, {})
            png = EP_DIR / slug / "assets" / "graphic" / f"{asset}.png"
            rel = f"http://localhost:8765/episodes/{slug}/assets/graphic/{asset}.png"
            if png.exists():
                cards.append(f'<a class="gprev" href="{rel}" target="_blank">'
                             f'<img loading="lazy" src="{rel}" alt=""></a>')
            else:
                cards.append('<p class="empty">gráfico aún sin generar — '
                             f'<code>python tools/make_graphics.py {esc(slug)} --id {esc(asset)}</code></p>')
            cards.append('<div class="gmeta"><b>' + esc(asset) + '</b>'
                         + (f'<p>{esc(g.get("shows", ""))}</p>' if g.get("shows") else "")
                         + (f'<p class="st">estilo · {esc(g.get("style", ""))}</p>' if g.get("style") else "")
                         + '</div>')
            alt = gbybeat.get(n)
            if alt and alt[2]:
                used_beats.add(n)
                cards.append(f'<p class="pullq">alternativas de b-roll · "{esc(alt[0])}" · {esc(",".join(alt[1]))}</p>'
                             '<div class="grid">'
                             + "\n".join(_card_html(esc, c, n) for c in alt[2])
                             + '</div>')
            cards.append(
                f'<label class="beatcustom">¿el gráfico no hace falta? adjunta otro recurso '
                f'<span>— si pegas un link/ruta se usa ESE en el beat {esc(n)} y el gráfico se ignora</span>'
                f'<input class="bcust" data-beat="{esc(n)}" '
                f'placeholder="ruta local o URL (imagen o vídeo) para el beat {esc(n)}"></label>')

        elif tipo in ("archivo", "stock", "kb"):
            g = _row_for(n, asset)
            if g:
                used_beats.add(n)
                if asset and asset_to_row.get(asset) not in (None, n):
                    cards.append(f'<p class="ref">→ mismo recurso que el beat '
                                 f'<code>{esc(asset_to_row[asset])}</code> — se elige una vez, '
                                 f'se aplica a los dos.</p>')
                query, srcs, cands_, notes = g
                if not cands_:
                    cards.append('<p class="empty">— sin candidatos. '
                                 f'{esc("; ".join(notes)) or "amplía la query en 07-pull.tsv"} —</p>')
                else:
                    cards.append(f'<p class="pullq">pull · "{esc(query)}" · {esc(",".join(srcs))}</p>'
                                 '<div class="grid">'
                                 + "\n".join(_card_html(esc, c, n) for c in cands_)
                                 + '</div>')
            else:
                cards.append(f'<p class="empty">beat <code>{esc(tipo)}</code> «{esc(asset)}» sin fila en '
                             f'<code>07-pull.tsv</code> — pega un recurso, o añade la fila y re-corre el pull.</p>')
            cards.append(
                f'<label class="beatcustom">recurso propio '
                f'<span>— si lo pegas, se usa ESTE y se ignora la selección del beat</span>'
                f'<input class="bcust" data-beat="{esc(n)}" '
                f'placeholder="ruta local o URL para el beat {esc(n)}"></label>')
        else:
            lbl = {"acamara": "a cámara — lo cubre la toma del narrador (Stage 8); sin recurso que elegir",
                   "negro": "negro — sin recurso"}.get(tipo, esc(tipo) + " — sin recurso")
            cards.append(f'<p class="none">{lbl}</p>')
        cards.append('</section>')

    for b, k, query, srcs, cands_, notes in groups:
        if b in used_beats:
            continue
        cards.append(f'<section class="beat" data-beat="{esc(b)}"><h2>beat {esc(b)} '
                     f'<span class="k">extra · {esc(k)}</span></h2>'
                     f'<p class="frag">no está en la espina del shotlist</p>')
        if cands_:
            cards.append('<div class="grid">' + "\n".join(_card_html(esc, c, b) for c in cands_) + '</div>')
        cards.append(f'<label class="beatcustom">recurso propio '
                     f'<input class="bcust" data-beat="{esc(b)}" placeholder="ruta o URL"></label></section>')
    body = "\n".join(cards)

    # ---- Música (consideración) — al final ----
    lic_opts = "".join(f'<option>{l}</option>' for l in
                       ("CC-BY", "CC-BY-SA", "CC0", "YT Audio Library", "Pixabay"))
    own_music = "".join(
        f'<div class="mown" data-slot="{i}"><input class="mopath" placeholder="ruta local o URL (.mp3/.wav/.ogg)">'
        f'<input class="mometa" placeholder="título · autor">'
        f'<select class="molic">{lic_opts}</select>'
        f'<input class="mopage" placeholder="URL de la página (opcional)"></div>'
        for i in range(1, 5))
    own_box = ('<h3>Recursos propios <span>— pega tu pista; debe ser CC0 / CC-BY / CC-BY-SA '
               '(nada con NC o ND, `brain/12`). Título·autor y licencia son obligatorios para el crédito.</span></h3>'
               f'<div class="mownwrap">{own_music}</div>')
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
            '<p class="hint">solo CC-BY / CC-BY-SA / CC0. Marca sugeridas y/o pega las tuyas abajo; al exportar '
            'van como <code>music</code> y <code>--download</code> las baja a '
            '<code>brand/assets/music/</code> + <code>LICENSES.md</code>. '
            'Amplía el pool con <code>python tools/find_music.py "query"</code>.</p>'
            + own_box + '<h3>Sugeridas (Jamendo)</h3>' + "\n".join(rows) + '</section>')
    else:
        musicbox = ('<section class="musicbox"><h2>Música <span class="q">— lecho ominoso ambiental</span></h2>'
                    '<p class="hint">pega tus pistas abajo (CC0/CC-BY/CC-BY-SA), o amplía el pool sugerido con '
                    '<code>python tools/find_music.py "dark cinematic ambient"</code>.</p>'
                    + own_box + '</section>')

    # ---- AI prompts whose beat never appeared on the spine ----
    orphan = [p for p in prompts if p["id"] not in seen_ai]
    if orphan:
        oa = ['<section class="beat" data-tipo="ia"><h2>Prompts IA sueltos '
              '<span class="k">sin beat en la espina</span></h2>']
        for p in orphan:
            oa.append(f'<p class="frag">{esc(p["id"])} — {esc(p["slug"])} '
                      f'({esc(p["beats"] or "beats?")})</p>' + _ai_block(p, p["beats_short"]))
        oa.append('</section>')
        body += "\n" + "\n".join(oa)
    has_ai = "true" if prompts else "false"

    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Style pass — {esc(slug)}</title>
{T.FAVICON}
{T.CSS}
<style>
 #cnt,#aicnt{{font-variant-numeric:tabular-nums;color:var(--muted);font-size:.82rem}}
 .musicbox{{max-width:1980px;margin:1rem auto 3rem;padding:1.75rem 2rem;
   background:var(--surface);border:1px solid var(--line-2);border-radius:var(--r);box-shadow:var(--shadow)}}
 .musicbox>h2{{margin-top:0}}
 .ai input,.bcust{{font-size:.78rem}}
 .slot input:not(:placeholder-shown),
 .bcust:not(:placeholder-shown){{border-color:var(--lime-line);background:var(--lime-soft)}}
 .beatcustom{{display:block;margin-top:1rem;font-size:.76rem;color:var(--muted)}}
 .beatcustom>span{{opacity:.8}}
 .beatcustom .bcust,.beatcustom input{{margin-top:.35rem}}
 section:has(.bcust:not(:placeholder-shown)) .grid{{opacity:.4}}
 .pathrow{{display:flex;gap:.4rem;align-items:center;min-width:0}}
 .pathrow>input:not([type=file]){{flex:1;min-width:0}}
 .browse{{flex:none;font-size:.72rem;padding:.4rem .65rem;border-radius:6px;
   border:1px solid var(--line-2);background:var(--surface-2);color:inherit;
   cursor:pointer;white-space:nowrap}}
 .browse:hover{{border-color:var(--line);background:var(--bg-2)}}
 .browse:disabled{{opacity:.6;cursor:wait}}
 .mown .pathrow{{min-width:0}}
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
 .musicbox h3{{font-size:.82rem;color:var(--faint);margin:1.1rem 0 .5rem;font-weight:560}}
 .musicbox h3 span{{color:var(--muted);font-weight:400}}
 .mownwrap{{display:flex;flex-direction:column;gap:.5rem;margin-bottom:.6rem}}
 .mown{{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1.5fr) 110px minmax(0,1.2fr);gap:.5rem}}
 .mown input,.mown select{{font-size:.76rem;padding:.4rem .55rem;background:var(--bg-2);
   border:1px solid var(--line);border-radius:6px;color:inherit}}
 .mown .mopath:not(:placeholder-shown){{border-color:var(--lime-line);background:var(--lime-soft)}}
 @media(max-width:900px){{.mown{{grid-template-columns:1fr 1fr}}}}
 .wrap{{max-width:1100px;margin:0 auto;padding:1.75rem 1.5rem}}
 main{{min-width:0}}
 section.beat{{padding:1.4rem 0;border-bottom:1px solid var(--line)}}
 section.beat:last-child{{border-bottom:0}}
 section.beat[data-tipo="acamara"],section.beat[data-tipo="negro"]{{opacity:.5;padding:.7rem 0}}
 .frag{{color:var(--muted);font-size:.86rem;margin:.2rem 0 .9rem;font-style:italic}}
 .frag .mk{{font-style:normal;background:var(--surface-2);color:var(--muted);
   padding:.05rem .4rem;border-radius:5px;font-size:.72rem;margin-left:.3rem}}
 .frag .rot{{font-style:normal;color:var(--gold);font-size:.76rem;margin-left:.3rem}}
 .sec{{font-weight:400;color:var(--muted);font-size:.8rem;margin-left:.5rem}}
 .none{{color:var(--muted);font-size:.82rem;margin:.2rem 0}}
 .ref{{color:var(--muted);font-size:.84rem}}
 .pullq{{color:var(--muted);font-size:.76rem;margin:.2rem 0 .6rem}}
 .gprev{{display:block;max-width:640px;border:1px solid var(--line-2);border-radius:var(--r);
   overflow:hidden;margin:.4rem 0 .7rem}}
 .gprev img{{display:block;width:100%}}
 .gmeta{{font-size:.84rem;color:var(--muted);margin-bottom:.4rem}}
 .gmeta b{{color:var(--fg)}} .gmeta p{{margin:.2rem 0}} .gmeta .st{{font-size:.76rem;opacity:.8}}
 h2 .q{{font-weight:400;color:var(--muted)}}
 h2 .k{{float:right;font-weight:400;color:var(--muted);font-size:.8rem}}
 h3 span{{font-weight:400;color:var(--muted)}}
 .grid{{gap:1.1rem;grid-template-columns:repeat(auto-fill,minmax(235px,1fr))}}
 .card{{position:relative;padding:0;overflow:hidden;cursor:pointer;gap:0}}
 .card:has(.pick:checked){{border-color:var(--lime-line);
   box-shadow:inset 0 0 0 1px var(--lime-line);background:var(--lime-soft)}}
 .card>input{{position:absolute;z-index:2;margin:8px;left:0;width:20px;height:20px;cursor:pointer}}
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
 <span id="aicnt"></span>
 <button id="exp">Guardar</button>
 <button class="primary" id="close">Finalizar Stage 7</button>
 <button id="clr">Limpiar</button>
 <a class="btn ghost" id="assets" href="http://localhost:8765/episodes/{slug}/assets/" target="_blank">Carpeta de recursos</a>
 <span class="small" style="opacity:.7">«Guardar» descarga los recursos elegidos, sin cerrar el stage · «Finalizar» descarga y pliega el gate (avanza el pipeline)</span>
 <a class="btn ghost spacer" href="http://localhost:8765/">Volver al panel</a>
</header>
<div class="wrap">
<main>
{body}
</main>
</div>
{musicbox}
<script>
const SLUG="{esc(slug)}", HAS_AI={has_ai};
const LS="conquest-pass:"+SLUG, LSA=LS+":ai";
const cards=[...document.querySelectorAll('.card')];
const bcust=[...document.querySelectorAll('.bcust')];
const mtrk=[...document.querySelectorAll('.mtrk')];
const mown=[...document.querySelectorAll('.mown')];
const aip=[...document.querySelectorAll('.aipath')];
const cnt=document.getElementById('cnt'), aicnt=document.getElementById('aicnt');
function jget(k,d){{try{{return JSON.parse(localStorage.getItem(k))??d}}catch(e){{return d}}}}
function pk(c){{return c.querySelector('.pick')}}
function bmap(){{const m={{}}; bcust.forEach(i=>{{const v=i.value.trim(); if(v)m[i.dataset.beat]=v}}); return m;}}
function sync(){{
  const bm=bmap(), picks=[];
  cards.forEach(c=>{{ if(pk(c)&&pk(c).checked)picks.push(c.dataset.key); }});
  localStorage.setItem(LS,JSON.stringify(picks));
  localStorage.setItem(LS+':bcust',JSON.stringify(bm));
  const mus=mtrk.filter(t=>t.querySelector('.mtrack').checked).map(t=>t.dataset.key);
  localStorage.setItem(LS+':music',JSON.stringify(mus));
  const mo=mown.map(d=>({{p:d.querySelector('.mopath').value.trim(),
    m:d.querySelector('.mometa').value.trim(), l:d.querySelector('.molic').value,
    g:d.querySelector('.mopage').value.trim()}}));
  localStorage.setItem(LS+':mown',JSON.stringify(mo));
  const covered=new Set([...picks.map(k=>cards.find(c=>c.dataset.key===k).dataset.beat),
                         ...Object.keys(bm),
                         ...aip.filter(i=>i.value.trim()).map(i=>i.dataset.beats)]);
  cnt.textContent=covered.size+' / {total} beats'+(Object.keys(bm).length?(' ('+Object.keys(bm).length+' propios)'):'');
}}
function syncA(){{
  const o={{}}; aip.forEach(i=>{{const v=i.value.trim(); if(v)o[i.dataset.ai]=v;
    i.closest('.ai').classList.toggle('done',!!v)}});
  localStorage.setItem(LSA,JSON.stringify(o));
  aicnt.textContent = aip.length ? ('  ·  '+Object.keys(o).length+' / '+aip.length+' IA') : '';
}}
const initP=new Set(jget(LS,[]));
cards.forEach(c=>{{
  if(pk(c)&&initP.has(c.dataset.key))pk(c).checked=true;
  c.addEventListener('click',e=>{{
    if(e.target.closest('a,input'))return;
    const box=pk(c);
    if(box){{box.checked=!box.checked; sync();}}
  }});
  c.querySelectorAll('input').forEach(i=>i.addEventListener('change',sync));
}});
const initB=jget(LS+':bcust',{{}});
bcust.forEach(i=>{{if(initB[i.dataset.beat])i.value=initB[i.dataset.beat];
  i.addEventListener('input',sync)}});
const initM=new Set(jget(LS+':music',[]));
mtrk.forEach(t=>{{const b=t.querySelector('.mtrack');
  if(initM.has(t.dataset.key))b.checked=true;
  b.addEventListener('change',sync);
  t.addEventListener('click',e=>{{if(e.target.closest('a,audio,input'))return;
    b.checked=!b.checked; sync();}});}});
const initMO=jget(LS+':mown',[]);
mown.forEach((d,ix)=>{{const s=initMO[ix]||{{}};
  if(s.p)d.querySelector('.mopath').value=s.p;
  if(s.m)d.querySelector('.mometa').value=s.m;
  if(s.l)d.querySelector('.molic').value=s.l;
  if(s.g)d.querySelector('.mopage').value=s.g;
  d.querySelectorAll('input,select').forEach(i=>i.addEventListener('input',sync));}});
const initA=jget(LSA,{{}});
aip.forEach(i=>{{if(initA[i.dataset.ai])i.value=initA[i.dataset.ai];
  i.addEventListener('input',syncA)}});

// «Examinar…» — a browse button next to every path input. A browser can't
// hand JS a real local filesystem path (<input type=file> only exposes the
// bytes), so the picked file is uploaded straight to the local server and
// the returned relative path is what lands in the text input — same as
// pasting one by hand.
function wireBrowse(selector, accept, sub){{
  document.querySelectorAll(selector).forEach(inp=>{{
    if(inp.dataset.browseWired)return; inp.dataset.browseWired='1';
    const wrap=document.createElement('span'); wrap.className='pathrow';
    inp.parentNode.insertBefore(wrap,inp); wrap.appendChild(inp);
    const file=document.createElement('input');
    file.type='file'; file.hidden=true; if(accept)file.accept=accept;
    const btn=document.createElement('button');
    btn.type='button'; btn.className='browse'; btn.textContent='Examinar…';
    wrap.appendChild(file); wrap.appendChild(btn);
    btn.onclick=()=>file.click();
    file.onchange=async()=>{{
      const f=file.files[0]; if(!f)return;
      const prev=btn.textContent; btn.disabled=true; btn.textContent='subiendo…';
      try{{
        const url='http://localhost:8765/upload?ep='+encodeURIComponent(SLUG.slice(0,4))
          +'&name='+encodeURIComponent(f.name)+'&sub='+sub;
        const r=await fetch(url,{{method:'POST',body:f}});
        const j=await r.json().catch(()=>({{}}));
        if(!r.ok){{alert(j.error||('server '+r.status));return;}}
        inp.value=j.path; inp.dispatchEvent(new Event('input',{{bubbles:true}}));
      }}catch(e){{alert('No se pudo subir — ¿está corriendo el servidor local? (tools/serve.py)');}}
      finally{{btn.disabled=false; btn.textContent=prev; file.value='';}}
    }};
  }});
}}
wireBrowse('.bcust','image/*,video/*','custom');
wireBrowse('.aipath','image/*','ai');
wireBrowse('.mopath','audio/*','music');

sync(); syncA();
document.querySelectorAll('.cp').forEach(b=>b.onclick=()=>{{
  navigator.clipboard.writeText(b.previousElementSibling.textContent.trim());
  const t=b.textContent; b.textContent='copiado'; setTimeout(()=>b.textContent=t,1200);
}});
document.getElementById('clr').onclick=()=>{{
  cards.forEach(c=>c.querySelectorAll('input').forEach(i=>i.checked=false));
  mtrk.forEach(t=>t.querySelector('.mtrack').checked=false);
  mown.forEach(d=>d.querySelectorAll('input').forEach(i=>i.value=''));
  bcust.forEach(i=>i.value=''); aip.forEach(i=>i.value='');
  sync(); syncA();
}};
function buildTxt(){{
  const L=['# {PICKS_F} — generado por {PASS_HTML}',
           '# col1: <beat> | "music"',
           '# col2: source:id | custom:<beat> (música propia) | ai:id',
           '# col3: url o ruta.   custom:<beat> ANULA la selección de ese beat.',
           '# música propia: col4 = título · autor · col5 = licencia (CC0/CC-BY/CC-BY-SA) · col6 = página'];
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
  mown.forEach(d=>{{const p=d.querySelector('.mopath').value.trim();
    if(!p)return;
    const m=d.querySelector('.mometa').value.trim(), l=d.querySelector('.molic').value,
          g=d.querySelector('.mopage').value.trim();
    if(!m){{alert('Falta «título · autor» en una pista propia — es obligatorio para el crédito.');}}
    mus.push(['music','custom:'+d.dataset.slot,p,m,l,g].join('\\t'));}});
  if(mus.length){{L.push('# --- MÚSICA (consideración; brand/assets/music/) ---'); L.push(...mus);}}
  return L.join('\\n')+'\\n';
}}
function offerLocalSave(txt){{
  (async()=>{{
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
  }})();
}}
document.getElementById('exp').onclick=async()=>{{
  // «Guardar»: escribe 07-picks.txt + descarga los recursos elegidos. NO
  // cierra el stage — se puede pulsar tantas veces como haga falta mientras
  // se sigue eligiendo.
  const txt=buildTxt();
  try{{
    const r=await fetch('http://localhost:8765/picks',{{method:'POST',
      headers:{{'content-type':'application/json'}},
      body:JSON.stringify({{ep:SLUG.slice(0,4),payload:{{txt:txt}}}})}});
    if(r.ok){{const j=await r.json();
      alert('Guardado — descargando recursos.\\n'+(j.msg||'')+'\\nStage 7 sigue abierto; pulsa «Finalizar Stage 7» cuando termines.');return;}}
    const j=await r.json().catch(()=>({{}})); alert(j.error||('server '+r.status));
  }}catch(e){{}}
  offerLocalSave(txt);
}};
document.getElementById('close').onclick=async()=>{{
  // «Finalizar Stage 7»: guarda + descarga + pliega el gate de verdad
  // (advance.py fold) — no hace falta esperar al siguiente tick del loop,
  // el fold del Stage 7 es mecánico (solo descarga lo ya elegido).
  const txt=buildTxt();
  if(!confirm('¿Finalizar Stage 7? Guarda los picks, descarga los recursos y cierra el gate.'))return;
  try{{
    const r=await fetch('http://localhost:8765/finish',{{method:'POST',
      headers:{{'content-type':'application/json'}},
      body:JSON.stringify({{ep:SLUG.slice(0,4),stage:7,payload:{{txt:txt}}}})}});
    const j=await r.json().catch(()=>({{}}));
    if(r.ok){{alert('Stage 7 finalizado.\\n'+(j.msg||'')+'\\nPanel actualizado.');return;}}
    if(r.status===409){{alert(j.msg||j.error||'no se pudo finalizar');return;}}
    alert(j.error||('server '+r.status));
  }}catch(e){{
    alert('No se pudo finalizar — ¿está corriendo el servidor local? (tools/serve.py)');
    offerLocalSave(txt);
  }}
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


def run(slug, only=None):
    """only: set of beat labels to actually (re-)search — every other row
    reuses its cached result from the last full/partial run (07-pull-cache.json)
    so refining one query doesn't force re-fetching the whole episode."""
    keys = load_env()
    rows = read_spec(slug)
    cache = load_pull_cache(slug) if only else {}
    md = [f"# Style pass — {slug}", "",
          "> Stage 7 · central. Pull automático (`tools/pull_assets.py`) — **esto no es selección.**",
          f"> Trabaja en `{PASS_HTML}` (miniaturas + prompts IA). Para picar a mano aquí: `- [x]`.",
          "> stock = b-roll ilustrativo genérico, nunca 'lo real' (brain/12).", ""]
    groups, n_c, reused = [], 0, 0
    for beat, kind, source, query, rawopts in rows:
        if only and beat not in only and beat in cache:
            kind, query, srcs, cands, notes = cache[beat]
            reused += 1
        else:
            opts = parse_opts(rawopts)
            srcs, cands, notes = gather_beat(beat, kind, source, query, opts, keys)
        n_c += len(cands)
        groups.append((beat, kind, query, srcs, cands, notes))
        md.append(f"## beat {beat} — \"{query}\"  [{kind}: {','.join(srcs)}]\n")
        for c in cands:
            md.append(c.line())
        for note in notes:
            md.append(f"<!-- {note} -->")
        md.append("")
    missing = [b for b, *_r, cands, _n in groups if not cands]
    ep = EP_DIR / slug
    # the episode's own graphics (make_graphics.py) — render any that are missing
    # so every `gráfico` beat is previewable right here in the style pass. Cheap
    # (skips PNGs that already exist); best-effort — a missing Pillow/font won't
    # block the page.
    try:
        g = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "make_graphics.py"), slug],
                           capture_output=True, text=True, timeout=180)
        made = [ln.strip() for ln in (g.stdout or "").splitlines() if ln.strip().startswith("escrito")]
        if made:
            print(f"gráficos: {len(made)} render(s) nuevos en assets/graphic/")
    except Exception as e:
        print(f"gráficos: no se pudieron generar ({e})")
    ai = parse_ai_prompts(slug)
    music = parse_music()
    timeline = parse_timeline(slug)
    graphics = parse_graphics_table(slug)
    (ep / PASS_MD).write_text("\n".join(md) + "\n", encoding="utf-8")
    (ep / PASS_HTML).write_text(
        build_html(slug, groups, ai, music, timeline, graphics), encoding="utf-8")
    save_pull_cache(slug, groups)
    print(f"escrito  episodes/{slug}/{PASS_MD}   ({n_c} candidatos, {len(groups)} beats"
          + (f", {reused} reutilizados de la cache" if reused else "")
          + (f", {len(timeline)} beats en la espina" if timeline else "") + ")")
    if missing:
        print(f"AVISO: {len(missing)} beat(s) sin candidatos — {', '.join(missing)}. "
              "Afina la query y re-corre con --beats " + ",".join(missing) + " "
              "— o, si sigue vacío, conviértelo en beat `ia` (brain/12/15).")
    print(f"escrito  episodes/{slug}/{PASS_HTML}  <- ábrelo en el navegador"
          + (f"  ({len(ai[1])} prompts IA)" if ai[1] else "")
          + (f"  ({len(music)} tracks música)" if music else ""))
    print("siguiente: elige candidatos + rutas IA, «Finalizar Stage 7», corre --download")


# ---------------------------------------------------------------------- download
PICK_RE = re.compile(r"^\s*- \[x\] `([a-z]+):([^`]+)` .* · (https?://\S+)", re.I)
BEAT_RE = re.compile(r"^## beat (\S+) —")
EXT_OK = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
          "video/mp4": ".mp4", "video/quicktime": ".mov"}


def read_picks(slug):
    """(beat, src, id, url) list — beat may be 'music'. Prefer 07-picks.txt (from the
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
            picks.append((parts[0], src, cid, parts[2].strip().strip('"').strip("'"), parts[3:]))
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
            picks.append((beat, m.group(1), m.group(2), m.group(3), []))
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
    src = src.strip().strip('"').strip("'").strip()
    data, srcext = None, ""
    if src.lower().startswith(("http://", "https://")):
        d, _ = _fetch(src, "ai")
        if d is None:
            print(f"  FALLO  ai:{aid}  {src}")
            return
        data, srcext = d, Path(src.split("?")[0]).suffix
    else:
        for cand in (Path(src), ROOT / src, ep / src, dst_dir / src, Path.cwd() / src,
                     Path(src.replace("\\", "/"))):
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


def _resolve_media_page(url, keys):
    """A pexels/pixabay *page* URL -> a direct media URL via the API (needs the
    key). Returns (direct_url, src) or (None, None). Lets the user paste the
    normal share link for a per-beat / graphic-override resource."""
    u = url.strip().strip('"').strip("'")
    m = re.search(r"pexels\.com/.*?/video/[^/]*?-(\d+)/?$", u) or \
        re.search(r"pexels\.com/.*?/video/(\d+)/?$", u)
    if m and keys.get("PEXELS_API_KEY"):
        try:
            r = requests.get(f"https://api.pexels.com/videos/videos/{m.group(1)}",
                             headers={"Authorization": keys["PEXELS_API_KEY"]}, timeout=30)
            r.raise_for_status()
            files = sorted(r.json().get("video_files", []),
                           key=lambda f: (f.get("width") or 0), reverse=True)
            if files:
                return files[0]["link"], "pexelsv"
        except Exception:
            pass
    m = re.search(r"pexels\.com/(?:.*?/)?photo/[^/]*?-(\d+)/?$", u)
    if m and keys.get("PEXELS_API_KEY"):
        try:
            r = requests.get(f"https://api.pexels.com/v1/photos/{m.group(1)}",
                             headers={"Authorization": keys["PEXELS_API_KEY"]}, timeout=30)
            r.raise_for_status()
            return r.json()["src"]["original"], "pexels"
        except Exception:
            pass
    m = re.search(r"pixabay\.com/(videos|photos|images)/[^/]*?-(\d+)/?$", u)
    if m and keys.get("PIXABAY_API_KEY"):
        vid = m.group(1) == "videos"
        base = "https://pixabay.com/api/videos/" if vid else "https://pixabay.com/api/"
        try:
            r = requests.get(base, params={"key": keys["PIXABAY_API_KEY"], "id": m.group(2)},
                             timeout=30)
            r.raise_for_status()
            hits = r.json().get("hits", [])
            if hits and vid:
                best = max(hits[0]["videos"].values(), key=lambda x: x.get("width", 0))
                return best["url"], "pixabayv"
            if hits:
                return hits[0].get("largeImageURL", ""), "pixabay"
        except Exception:
            pass
    return None, None


_WIKI_FILE = re.compile(r"https?://[^/]*wik(?:ipedia|media)\.org/wiki/(?:[^:/]+:)?(?:File|Archivo|Datei):(.+)$", re.I)


def _fetch(url, src):
    """Fetch a URL (or read a local path). Returns (bytes, final_url) or (None, err)."""
    url = url.strip().strip('"').strip("'").strip()   # Windows «Copiar como ruta» añade comillas
    if not url.lower().startswith(("http://", "https://")):
        for cand in (Path(url), ROOT / url, Path.cwd() / url,
                     Path(url.replace("\\", "/"))):
            if cand.is_file():
                return cand.read_bytes(), cand.as_posix()
        return None, f"no existe la ruta: {url}"
    # a Wikimedia "/wiki/File:X" *description page* → the actual media file
    m = _WIKI_FILE.match(url)
    if m:
        url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + m.group(1).split("?")[0]
    tries, hdr = [url], {"User-Agent": UA}
    last = "?"
    for u in tries:
        try:
            r = requests.get(requests.utils.requote_uri(u), headers=hdr, timeout=90)
            r.raise_for_status()
            ct = r.headers.get("Content-Type", "").lower()
            if "text/html" in ct or r.content[:15].lstrip().lower().startswith((b"<!doctype", b"<html")):
                return None, f"la URL devolvió una página HTML, no un archivo ({u}) — pega el enlace directo a la imagen"
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
    if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        return ".wav"
    if data[:4] in (b"\x00\x00\x00\x18", b"\x00\x00\x00\x20") and data[4:8] == b"ftyp":
        return ".m4a"
    return ".mp3"


def _dl_music(key, url, mmeta):
    """Download a considered track into brand/assets/music/ + log its licence.
    Returns (filename, meta) for the caller to record in this episode's own
    07-selection.md — brand/assets/music/ is a pool shared across episodes,
    so that's the only place that knows *this* episode picked *this* file."""
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    data, _ = _fetch(url, "music")
    if data is None:
        print(f"  FALLO  música {key}  (sin descarga)")
        return None
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
            f"{m.get('lic', 'CC')}"
            + (f" — {m['page']}" if m.get("page") else "")
            + " — atribución obligatoria en 09-description.md")
    if line not in prev:
        lf.write_text(prev.rstrip() + "\n" + line + "\n", encoding="utf-8")
    return fn.name, m


def download(slug):
    keys = load_env()
    picks = read_picks(slug)
    ep = EP_DIR / slug
    ai_fname = {p["id"]: p["fname"] for p in parse_ai_prompts(slug)[1]}
    mmeta = {m["key"]: m for m in parse_music()}
    beat_rows, ai_rows, credits, music_rows = [], [], [], []

    for beat, src, cid, url, meta in picks:
        if beat.lower() == "music":
            if src == "custom":
                if cid in ("", "undefined", "null"):
                    n_prev = len(list(MUSIC_DIR.glob("custom_*"))) if MUSIC_DIR.exists() else 0
                    cid = str(n_prev + 1)
                # meta = [título·autor, licencia, page]
                t_a = (meta[0] if len(meta) > 0 else "").split("·")
                own = {"title": t_a[0].strip(), "artist": (t_a[1].strip() if len(t_a) > 1 else ""),
                       "lic": (meta[1].strip() if len(meta) > 1 else ""),
                       "page": meta[2].strip() if len(meta) > 2 else ""}
                ALLOWED = ("CC0", "CC-BY", "CC-BY-SA", "YT AUDIO LIBRARY", "PIXABAY")
                if own["lic"].upper() not in ALLOWED:
                    print(f"  SALTADA  música propia {url}  — licencia «{own['lic']}» no permitida "
                          f"(CC0 / CC-BY / CC-BY-SA / YT Audio Library / Pixabay, brain/12)")
                    continue
                if not own["title"]:
                    print(f"  SALTADA  música propia {url}  — falta «título · autor» para el crédito")
                    continue
                r = _dl_music(f"custom:{cid}", url, {f"custom:{cid}": own})
            else:
                r = _dl_music(f"{src}:{cid}", url, mmeta)
            if r:
                fname, m = r
                music_rows.append((m.get("title", ""), m.get("artist", ""),
                                    m.get("lic", ""), f"brand/assets/music/{fname}"))
            continue

        if src == "ai":
            _dl_ai(ep, beat, cid, url, ai_fname.get(cid, f"{cid}.png"), ai_rows, credits)
            continue

        if src == "custom" and url.lower().startswith("http") and (
                "pexels.com" in url or "pixabay.com" in url):
            direct, dsrc = _resolve_media_page(url, keys)
            if direct:
                print(f"  resuelto  {url}  ->  {dsrc}")
                url, src = direct, dsrc
            elif "/video/" in url or "/videos/" in url or "/photo/" in url:
                print(f"  AVISO  {url} es una página, no un archivo — "
                      f"añade la API key o pega el enlace directo / una ruta local")

        data, final = _fetch(url, src)
        if data is None:
            print(f"  FALLO  {src}:{cid}  {final}")
            continue
        ext = _ext_for(data, final, src)
        dim = _dims(data, ext)

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

        print(f"  OK  {name}  {dim}")
        beat_rows.append((beat, f"{src}:{cid}", final, dim, rel))
        credits.append(f"- {beat}: {src}:{cid} — {final if final.startswith('http') else '(archivo propio)'}")

    _write_selection(ep, slug, beat_rows, ai_rows, music_rows)
    if credits:
        cf = ep / "assets" / "CREDITS.md"
        cf.parent.mkdir(parents=True, exist_ok=True)
        prev = cf.read_text(encoding="utf-8") if cf.exists() else "# Créditos de recursos\n"
        cf.write_text(prev.rstrip() + "\n" + "\n".join(credits) + "\n", encoding="utf-8")
        print(f"\ncréditos    → episodes/{slug}/assets/CREDITS.md")


def _write_selection(ep, slug, beat_rows, ai_rows, music_rows=None):
    L = [f"# Selección — Stage 7 style pass · {slug}", "",
         f"> Generado por `pull_assets.py --download` desde `{PICKS_F}`. "
         f"Este es el registro de decisiones del pase; se pliega en `07-assets.md`.", ""]
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
    if music_rows:
        L += ["## Música", "",
              "> En este orden — Stage 9 las pone en cola una detrás de otra y repite la "
              "secuencia completa en bucle hasta cubrir todo el vídeo (una sola pista: "
              "bucle simple; dos o más: bucle de la secuencia).", "",
              "| # | Título | Autor | Licencia | Archivo |",
              "|---|--------|-------|----------|---------|"]
        L += [f"| {i} | {t or '—'} | {a or '—'} | {lic or '—'} | `{p}` |"
              for i, (t, a, lic, p) in enumerate(music_rows, 1)]
        L += [""]
    (ep / SELECTION_F).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"\nselección   → episodes/{slug}/{SELECTION_F}")
    hdr = ("| Beat | Fuente | Enlace | Licencia | Res. | Uso | Pase | Archivo |\n"
           "|---|---|---|---|---|---|---|---|")
    body = []
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
    sample = ("2\tstock\tstock\t<tema del cold open> cinematic\torientation=landscape;min=1920;n=3\n"
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
    rest = args[1:]
    only = None
    if "--beats" in rest:
        i = rest.index("--beats")
        only = {b.strip() for b in rest[i + 1].split(",") if b.strip()}
        del rest[i:i + 2]
    rest = set(rest)
    if "--init" in rest:
        init(slug)
    elif "--download" in rest:
        download(slug)
    else:
        run(slug, only=only)
