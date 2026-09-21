#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble.py — Stage 9 first cut + render engine (brain/16 move 4).

Pure python + ffmpeg. No agent, no tokens. Turns the shotlist spine + the
chosen assets + the trimmed narration into:

  09-timeline.json   the editable timeline (tools/edit_timeline.py renders it)
  09-wave.b64        a data-URI waveform PNG of the VO spine (for the page)
  09-rough.mp4       a 720p proxy cut (Previsualizar re-renders regions of it)
  E0XX-slug-vN.mp4   the 4K master (--final)

What it reads (all optional — degrades to a planning view):
  06-shotlist.md            the "Timeline — la espina" table  (required)
  07-selection.md / 07-assets.md   asset-id -> filename
  assets/{kb,stock,video,intro,archive,ai,graphic}/*   the actual media
  assets/*.trimmed.mp4 + assets/*.words.json           the VO spine + word times
  brand/assets/music/*      the bed

Usage
  python tools/assemble.py E0XX-slug                 # (re)build 09-timeline.json + wave
  python tools/assemble.py E0XX-slug --seed          # seed once (no-op if already schema 2)
  python tools/assemble.py E0XX-slug --reseed        # force re-seed from the shotlist — discards edits
  python tools/assemble.py E0XX-slug --resync        # re-fit the line to a re-recorded VO (keeps dur_edited)
  python tools/assemble.py E0XX-slug --rough         #  + render the 720p proxy
  python tools/assemble.py E0XX-slug --preview 340 385   # re-render just that region of the proxy
  python tools/assemble.py E0XX-slug --final         # render the 4K master
  python tools/assemble.py E0XX-slug --dry           # print the ffmpeg command, render nothing
"""
import base64
import contextlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mediabin import FFMPEG, FFPROBE, keep_awake, cpu_threads, lower_priority  # noqa: E402
import pipeline as P  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes"
GROUND = "#100D09"          # brand letterbox / pad colour (brain/03)
FPS = 24
# 09-timeline.json schema. 1 = the derived timeline (parse_spine + align every
# rebuild). 2 = the authored timeline (brain/16 "timeline canónica"): each beat
# owns its `dur`, align() only seeds. seed_timeline() now writes 2; existing
# schema-1 files must be run through tools/migrate_timeline.py.
SCHEMA_CURRENT = 2
KIND_DIR = {"archivo": "archive", "stock": "stock", "kb": "kb", "ia": "ai",
            "gráfico": "graphic", "grafico": "graphic", "negro": None,
            "acamara": None, "a-cámara": None, "a-camara": None, "narrador": None}
ASSET_SUBDIRS = ("kb", "stock", "video", "intro", "archive", "ai", "graphic", "thumb", "cite")
MEDIA_EXT = (".mp4", ".mov", ".webm", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".gif")
STILL_EXT = (".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".gif")
MOTIONS = {"push", "pan-h", "pan-v", "static", "zoom", "cut"}
ACAMARA = {"acamara", "a-cámara", "a-camara", "narrador"}   # beat shows the narrator take


# ── parse the shotlist spine ────────────────────────────────────────────────

def _secs(mmss):
    mmss = str(mmss).strip()
    if not mmss or mmss in ("—", "-"):
        return None
    p = mmss.split(":")
    try:
        return int(p[0]) * 60 + float(p[1]) if len(p) == 2 else float(p[0])
    except ValueError:
        return None


def parse_spine(md):
    """Return the beat list from the 'Timeline — la espina' table."""
    m = re.search(r"Timeline\s*[—-]\s*la espina.*?\n(\|.*?)(?:\n\n|\n##|\Z)", md, re.S)
    if not m:
        raise SystemExit("06-shotlist.md: no encuentro la tabla 'Timeline — la espina'")
    rows = [r for r in m.group(1).splitlines() if r.strip().startswith("|")]
    beats, plan_t = [], 0.0
    for r in rows:
        c = [x.strip() for x in r.strip().strip("|").split("|")]
        if len(c) < 9 or c[0] in ("#", "…", "") or set("".join(c)) <= set("-: "):
            continue
        try:
            n = int(re.sub(r"\D", "", c[0]))
        except ValueError:
            continue
        dur = float(re.sub(r"[^\d.]", "", c[2]) or 4)
        tin = _secs(c[1])
        tin = plan_t if tin is None else tin
        motion = c[7].lower().strip() if c[7].lower().strip() in MOTIONS else "static"
        kind = c[4].lower().strip()
        beats.append({
            "n": n, "in": round(tin, 2), "out": round(tin + dur, 2), "dur": dur,
            "section": c[3].lower().strip(), "kind": kind,
            "asset": "" if c[5] in ("—", "-", "") else c[5].strip("`"),
            "label": "" if c[6] in ("—", "-") else c[6],
            "motion": motion,
            "marker": "" if c[8] in ("—", "-") else c[8].upper(),
            "frag": re.sub(r"[«»\"]", "", c[9]).strip() if len(c) > 9 else "",
            "file": None, "state": "plan",
        })
        plan_t = tin + dur
    if not beats:
        raise SystemExit("06-shotlist.md: la tabla de la espina está vacía")
    return beats


# ── resolve asset ids -> files ─────────────────────────────────────────────

def _asset_index(ep):
    """id -> path, scanning 07-selection.md then the assets/ subfolders."""
    idx = {}
    sel = ep / "07-selection.md"
    if sel.exists():
        for mm in re.finditer(r"`?([A-Za-z0-9_+.-]+)`?\s*[→:|]\s*`?(assets/[^\s`|]+)`?",
                              sel.read_text(encoding="utf-8")):
            f = ep / mm.group(2)
            if f.exists():
                idx[mm.group(1)] = f
    # 07-picks.txt is the style pass's own decisions. A `<beat>\tcustom:<beat>\t<assets/…>` row is the
    # editor's OWN file for that beat and "ANULA la selección de ese beat" (its header says so).
    # Nothing else maps such a file to its beat (pulled candidates are named beatNN_*, a custom
    # upload isn't), so E003's five custom picks read «sin asset» although the files were on disk.
    # Registered as beat<n>_custom_<stem> BEFORE the folder scan, so resolve()'s beatNN_ fallback
    # finds the custom file ahead of any pulled candidate for the same beat.
    picks, local_picks = ep / "07-picks.txt", []
    if picks.exists():
        for line in picks.read_text(encoding="utf-8").splitlines():
            cols = line.split("\t")
            if line.startswith("#") or len(cols) < 3 or not cols[0].strip().isdigit():
                continue
            if cols[1].strip().startswith("custom:") and cols[2].strip().startswith("assets/"):
                f = ep / cols[2].strip()
                if f.exists():
                    idx.setdefault(f"beat{int(cols[0])}_custom_{f.stem}", f)
            elif cols[2].strip().startswith("assets/") and (ep / cols[2].strip()).exists():
                local_picks.append((int(cols[0]), ep / cols[2].strip()))
    for sub in ASSET_SUBDIRS:
        d = ep / "assets" / sub
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if f.is_file() and f.suffix.lower() in MEDIA_EXT:
                idx.setdefault(f.stem, f)
                idx.setdefault(f.name, f)
    # 07-selection.md rows `| <beat> | <source> | <res> | `assets/…` |` are decisions: beat <n>
    # gets that file. Files named beatNN_* are found by resolve() already; the AI illustrations
    # are saved as `E003_aiNN_<slug>` (07b-ai-prompts.md), and no shotlist asset id derives from
    # that name (`e003_laboratorio-ingles-1928` <-> `…_ai06_laboratorio-1928`), so 15 `ia` beats
    # read «sin asset» although their images were on disk. Register them under beat<n>_<stem>,
    # where resolve()'s beatNN_ fallback looks. setdefault: an explicit id or pin always wins.
    if sel.exists():
        for mm in re.finditer(r"^\|\s*(\d+)\s*\|[^\n]*?`(assets/[^`\s|]+)`\s*\|",
                              sel.read_text(encoding="utf-8"), re.M):
            f = ep / mm.group(2)
            if f.exists():
                idx.setdefault(f"beat{int(mm.group(1))}_{f.stem}", f)
    # …and only then any other local pick (an ai:/…: row with a path): the generated selection above
    # names the final files (E003_aiNN_<slug>), so it wins; a `custom:` pick already went first.
    for n_, f_ in local_picks:                 # any other local pick (an ai:/…: row with a path)
        idx.setdefault(f"beat{n_}_pick_{f_.stem}", f_)
    # explicit pins (assets/_index.json, written by beat_asset.py) win over the
    # subdir scan — an edit-room swap can never be shadowed by a leftover file
    pin = ep / "assets" / "_index.json"
    if pin.exists():
        try:
            for k, v in json.loads(pin.read_text(encoding="utf-8")).items():
                if (ep / v).exists():
                    idx[k] = ep / v
        except (json.JSONDecodeError, TypeError):
            pass
    return idx


def _cite_meta(ep):
    """beat-number (str) -> {obra, año, dist} parsed from 07-cite-selection.md
    (brain/20 §4.7, written by clip_finder.py --extract) — feeds the case-file
    label burned onto a `cita` beat's bake (§4.3)."""
    f = ep / "07-cite-selection.md"
    if not f.exists():
        return {}
    out = {}
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        c = [x.strip() for x in line.strip("|").split("|")]
        if len(c) < 6 or not c[0].isdigit():
            continue
        out[c[0]] = {"obra": c[3], "año": c[4], "dist": c[5]}
    return out


def _the_take(ep):
    """The single trimmed narrator take (A-roll source). Multi-take A-roll isn't
    supported yet — returns the first one and the caller warns."""
    takes = sorted(ep.glob("assets/*.trimmed.mp4"))
    return takes[0] if takes else None


def _pending_takes(ep):
    """Original takes whose cuts are queued but not yet rendered into the 4K
    <take>.trimmed.mp4 (trim_talk.py --soft leaves <take>.render.pending)."""
    return [m.with_name(m.name.replace(".render.pending", ".mp4"))
            for m in sorted(ep.glob("assets/*.render.pending"))]


def _soft_vo(ep):
    """09-vo.m4a while cuts are pending — trim_talk --soft wrote it for the
    CURRENT cut list, so it (not the stale/absent trimmed take) is the truth
    for the voice's length and waveform. None when nothing is pending."""
    f = ep / "09-vo.m4a"
    return f if _pending_takes(ep) and f.exists() else None


def ensure_trimmed(slug):
    """Bake any queued cuts into the 4K trimmed take before a render that reads
    it (--rough / --final). If a background render of it is already running
    («Finalizar» / «Renderizar recorte» start one) wait for it; otherwise do it
    here. Then refresh the room's proxies from the fresh take."""
    import time
    ep = EP_DIR / slug
    for take in _pending_takes(ep):
        lock = take.with_suffix(".apply.lock")
        while P.lock_alive(lock):
            print(f"  esperando el recorte de {take.name} (en curso en segundo plano)…")
            time.sleep(10)
        if not take.with_suffix(".render.pending").exists():
            continue                       # that render finished and cleared it
        print(f"  recorte pendiente de {take.name} → renderizando la toma recortada…")
        r = subprocess.run([sys.executable, str(Path(__file__).parent / "trim_talk.py"),
                            str(take), "--apply"])
        if r.returncode != 0:
            raise SystemExit(f"el recorte de {take.name} falló — no se renderiza con una toma vieja")
    if _pending_takes(ep) == [] and list(ep.glob("assets/*.trimmed.mp4")):
        vo_proxy(slug)
        take_proxy(slug)


_ASPECT_CACHE = {}
MAX_STILL_PX = 4320        # long side; a museum scan at 130 MP chokes ffmpeg's zoompan


def _still_proxy(path, ep):
    """Museum scans run 40–130 MP — ffmpeg's Ken Burns crawls on them. Downscale
    once to `assets/_proxy/`, long side {MAX_STILL_PX}px, and use that instead."""
    try:
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        with Image.open(path) as im:
            if max(im.size) <= MAX_STILL_PX:
                return path
            out = ep / "assets" / "_proxy" / (path.stem + ".jpg")
            if out.exists() and out.stat().st_mtime >= path.stat().st_mtime:
                return out
            out.parent.mkdir(parents=True, exist_ok=True)
            s = MAX_STILL_PX / max(im.size)
            im.convert("RGB").resize((round(im.width * s), round(im.height * s)),
                                     Image.LANCZOS).save(out, quality=92)
            print(f"  proxy  {out.name}  ({im.width}x{im.height} -> {round(im.width*s)}x{round(im.height*s)})")
            return out
    except Exception:
        return path


def _negro_card(text, ep):
    """A `negro` beat that carries a rótulo (e.g. beat 8's «5 años… / 10 años…»)
    is a black slate with that text on it, not an empty black hole. ffmpeg's
    drawtext isn't in every static build, so bake it with Pillow and cache it."""
    import hashlib
    key = hashlib.md5(text.encode("utf-8")).hexdigest()[:10]
    out = ep / "assets" / "_proxy" / f"negro_{key}.png"
    if out.exists():
        return out
    try:
        from PIL import Image, ImageDraw, ImageFont
        w, h = 3840, 2160
        safe_w, safe_h = w * 0.86, h * 0.80        # keep text inside a title-safe box
        im = Image.new("RGB", (w, h), (6, 5, 3))
        d = ImageDraw.Draw(im)
        lines = [s.strip() for s in re.split(r"\s*/\s*|\s*\n\s*", text) if s.strip()] or [text]
        fpath = next((c for c in (r"C:\Windows\Fonts\georgia.ttf", r"C:\Windows\Fonts\times.ttf",
                                  "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                                  "/Library/Fonts/Georgia.ttf") if Path(c).exists()), None)

        def _font(px):
            try:
                return ImageFont.truetype(fpath, px) if fpath else ImageFont.load_default()
            except Exception:
                return ImageFont.load_default()

        # start at 168 px, shrink to fit the title-safe box (a long rótulo line or
        # many "/"-separated lines would otherwise clip at the frame edge)
        size, lh = 168, 240
        while size > 40:
            fnt = _font(size)
            widest = max((d.textlength(ln, font=fnt) for ln in lines), default=0)
            if widest <= safe_w and len(lines) * lh <= safe_h:
                break
            size = int(size * 0.9)
            lh = int(size * 1.43)
        fnt = _font(size)
        if size < 168:
            print(f"  negro card: rótulo largo → fuente {size}px (de 168) para que quepa")
        y = h / 2 - len(lines) * lh / 2 + (lh - size) / 2
        for ln in lines:
            d.text(((w - d.textlength(ln, font=fnt)) / 2, y), ln, font=fnt, fill=(214, 203, 181))
            y += lh
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out)
        return out
    except Exception:
        return None


def _cite_card(ep, obra, año, dist, w, h):
    """The case-file device (brain/03) applied to a `cita` excerpt (brain/20
    §4.3 — every moving excerpt gets it): a translucent file-strip across the
    lower frame naming the work under fair-use commentary, Courier Prime (or
    the nearest mono fallback), thin gold rule. Transparent RGBA, meant to be
    ffmpeg-`overlay`ed onto the excerpt. Cached by content+resolution."""
    import hashlib
    key = hashlib.md5(f"{obra}|{año}|{dist}|{w}x{h}".encode("utf-8")).hexdigest()[:10]
    out = ep / "assets" / "_proxy" / f"cite_{key}.png"
    if out.exists():
        return out
    try:
        from PIL import Image, ImageDraw, ImageFont
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        bar_h = round(h * 0.14)
        d.rectangle([0, h - bar_h, w, h], fill=(6, 5, 3, 190))
        d.rectangle([0, h - bar_h, w, h - bar_h + max(2, round(h * 0.0025))],
                    fill=(196, 162, 87, 255))
        fpath = next((c for c in (r"C:\Windows\Fonts\cour.ttf", r"C:\Windows\Fonts\consola.ttf",
                                  "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                                  "/Library/Fonts/Courier New.ttf") if Path(c).exists()), None)

        def _font(px):
            try:
                return ImageFont.truetype(fpath, px) if fpath else ImageFont.load_default()
            except Exception:
                return ImageFont.load_default()

        size = max(14, round(h * 0.024))
        f1, f2 = _font(size), _font(round(size * 0.86))
        pad = round(w * 0.02)
        y1 = h - bar_h + round(bar_h * 0.22)
        y2 = h - bar_h + round(bar_h * 0.58)
        d.text((pad, y1), "EXPEDIENTE: CITA — CRÍTICA/COMENTARIO", font=f1, fill=(214, 203, 181, 255))
        line2 = f"«{obra}» ({año}) — {dist}" if dist else f"«{obra}» ({año})"
        d.text((pad, y2), line2, font=f2, fill=(196, 162, 87, 255))
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out)
        return out
    except Exception:
        return None


def _aspect(path):
    """w/h of a still, cached. ~1.0 square, <1 portrait, >1.78 wide."""
    k = str(path)
    if k in _ASPECT_CACHE:
        return _ASPECT_CACHE[k]
    ar = 0.0
    try:
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None      # museum scans are legitimately huge
        with Image.open(path) as im:
            ar = round(im.width / im.height, 3) if im.height else 0.0
    except Exception:
        try:
            r = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0",
                                "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)],
                               capture_output=True, text=True, timeout=15)
            wv, hv = (int(x) for x in r.stdout.strip().split(",")[:2])
            ar = round(wv / hv, 3) if hv else 0.0
        except Exception:
            ar = 0.0
    _ASPECT_CACHE[k] = ar
    return ar


def _planned_take(ep):
    """The trimmed take a queued cut list WILL render (trim_talk --apply on «Finalizar» / «Renderizar
    ahora» / --rough / --final), while it doesn't exist yet. None when nothing is pending."""
    pend = _pending_takes(ep)
    return pend[0].with_suffix(".trimmed.mp4") if pend else None


def resolve(ep, beats):
    idx = _asset_index(ep)
    # A-roll beats point at the trimmed take. While cuts are queued that file isn't rendered yet
    # (or is stale) but it is the one that WILL be — the beats are covered, not «sin asset»
    # (E002: all 33 a-cámara beats flipped to «sin cubrir» the moment the render was deferred).
    take = _the_take(ep) or _planned_take(ep)
    for b in beats:
        if b["kind"] in ACAMARA:
            b["file"] = str(take.relative_to(ep).as_posix()) if take else None
            b["state"] = "ok" if take else "uncovered"
            b["motion"] = "cut"     # live video, never a Ken Burns move
            continue
        asset = b.get("asset") or ""
        if b["kind"] == "negro":
            b["file"], b["state"] = None, "plan"
            continue
        if not asset:                     # cleared / never assigned — reset any stale file
            b["file"], b["state"] = None, "uncovered"
            continue
        hit = idx.get(asset) or idx.get(asset.split(".")[0])
        if not hit:
            # prefix match: `intro01` -> `intro01_pexelsv_…`, `G4` -> `G4_age_ladder`
            aid = asset.lower()
            hit = next((v for k, v in idx.items()
                        if k.lower() == aid or k.lower().startswith(aid + "_")), None)
        if not hit:
            # downloaded assets are named beatNN_* (legacy) — try that. schema-2
            # beats carry `id` ("b7") not `n`; the spine row number is the digits.
            bn = b.get("n")
            if bn is None and isinstance(b.get("id"), str) and b["id"][1:].isdigit():
                bn = int(b["id"][1:])
            if bn is not None:
                for k, v in idx.items():
                    if k.lower().startswith(f"beat{bn:02d}_") or k.lower().startswith(f"beat{bn}_"):
                        hit = v
                        break
        if hit and hit.suffix.lower() in STILL_EXT:
            b["aspect"] = _aspect(hit)
            hit = _still_proxy(hit, ep)
        b["file"] = str(hit.relative_to(ep).as_posix()) if hit else None
        b["state"] = "uncovered" if (not b["file"] and b["kind"] != "negro") else "ok"
    # same-asset reuse: a held shot / PROMISE+PAY that names the same `asset` as a
    # beat that DID resolve borrows that file (assemble aligns times, not files).
    by_asset = {b["asset"]: b["file"] for b in beats if b.get("asset") and b.get("file")}
    for b in beats:
        if b.get("state") == "uncovered" and b.get("asset") in by_asset:
            b["file"], b["state"] = by_asset[b["asset"]], "ok"
    return beats


# ── align beats to the trimmed VO ─────────────────────────────────────────

def _norm(s):
    return re.sub(r"[^\wáéíóúñ ]", "", s.lower())


def load_words(ep):
    """Concatenate every take's words.json in script order, offsetting each."""
    takes = sorted(ep.glob("assets/*.words.json"))
    if not takes:
        return []
    words, offset = [], 0.0
    for wj in takes:
        try:
            ws = json.loads(wj.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for w in ws:
            words.append({"w": w["w"], "t": w["t"] + offset})
        trimmed = wj.with_name(wj.name.replace(".words.json", ".trimmed.mp4"))
        soft = _soft_vo(ep) if wj.with_name(wj.name.replace(".words.json", ".render.pending")).exists() else None
        if soft:                           # cuts queued: the trimmed take is stale/absent
            offset += _duration(soft)
        else:
            offset += _duration(trimmed) if trimmed.exists() else (ws[-1]["t"] + 1 if ws else 0)
    return words


def _vo_end_from_words(words):
    """The VO's end time. Whisper's `t` is the word *start*, so the tail scales
    with the last word's length — a flat +0.5 s clipped a long final word like
    "Hokusai"."""
    if not words:
        return 0.0
    _lastw = len(words[-1]["w"].strip(".,;:!?»«…"))
    return round(words[-1]["t"] + min(1.8, 0.45 + 0.10 * _lastw), 2)


def get_vo_end(ep, stored=None):
    """The authoritative VO length for a schema-2 timeline. Measures the real
    trimmed take directly when it's there — exact, no guessing about how long
    the last word's tail actually runs after its whisper-reported *start*,
    which is what clipped mid-sentence endings before (E001's last word,
    "Hokusai", then E002's sign-off — see _vo_end_from_words). Falls back to
    the stored value, then the word-length heuristic, only when there's no
    take yet to measure (e.g. mid-seed, before --apply has ever rendered one)."""
    soft = _soft_vo(ep)                    # queued cuts: the trimmed take is stale/absent
    take = soft or _the_take(ep)
    if take:
        d = _duration(take)
        if d > 0:
            return round(d, 2)
    if isinstance(stored, (int, float)) and stored > 0:
        return float(stored)
    return _vo_end_from_words(load_words(ep))


def resync_available(slug):
    """True when the trimmed VO changed since the timeline was last seeded/synced
    (a re-record or a re-trim) — the edit room shows a «Re-sincronizar» banner."""
    ep = EP_DIR / slug
    if (ep / "09-resync.flag").exists():
        return True
    data = _prev_json(ep / "09-timeline.json")
    if data.get("schema", 1) < 2 or not data.get("words_sig"):
        return False
    return _words_sig(load_words(ep)) != data["words_sig"]


def derive_times(beats, vo_end, fps=FPS):
    """Lay the authored beats on the VO backbone (brain/16, schema 2): each
    beat's `in`/`out` is the cumulative sum of the authored `dur`s before it,
    frame-quantised, contiguous (`in[i] == out[i-1]`), last beat snapped to
    `vo_end`. The VO is the fixed measure; changing one `dur` ripples every beat
    after it. No neighbour ever loses time to a lock."""
    if not beats:
        return beats
    frame = 1.0 / fps
    cursor, prev_out = 0.0, 0.0
    for b in beats:
        b["in"] = prev_out
        cursor += max(0.0, float(b.get("dur") or 0.0))
        prev_out = round(round(cursor / frame) * frame, 3)
        b["out"] = prev_out
    last = beats[-1]
    if vo_end and vo_end > last["in"] + 0.1:
        last["out"] = round(float(vo_end), 3)
    elif vo_end:
        print(f"  ⚠ vo_end {vo_end:.2f}s cae dentro del último beat "
              f"(in {last['in']:.2f}s) — no se ajusta el cierre")
    return beats


def _stage_dir(raw):
    """A frag that is a stage direction / production note, not delivered speech."""
    return raw.startswith(("[", "‹", "(")) or bool(
        re.search(r"tipo de cta|en pantalla|^nota\b|wordmark", raw, re.I))


def _tag_tok(n):
    return f"zzs{int(n):02d}"                          # a [S05] source tag as a (rare, precise) token


def _is_tag(tok):
    return tok.startswith("zzs") and tok[3:].isdigit()


def _anchor_tokens(raw, keep_tags=False):
    """The spoken words of a beat's anchor text: source tags [S05] and `code` are not speech (unless
    `keep_tags`, used to find the beat in the SCRIPT, where the sentence citing that source carries the
    same tag), and an ellipsis splits two separate quotes («un bulbo... una mansión»), not one phrase."""
    raw = re.sub(r"`[^`]*`", " ", raw or "")
    if keep_tags:
        raw = re.sub(r"\[S(\d+)\]", lambda m: " " + _tag_tok(m.group(1)) + " ", raw)
    raw = re.sub(r"\[[^\]]*\]", " ", raw)
    toks = []
    for seg in re.split(r"\.{2,}|…", raw):
        toks += [t for t in _norm(seg).split() if t]
    return toks


def _anchors(items, toks, words, ref_end, vo_end, *, thr=0.55, top=8, look=15, mu=0.25, bonus=0.5,
             keep_tags=False):
    """Confident (ref_time, vo_time) knots for a piecewise-linear time remap.
    `items` = [(ref_time, anchor_text), ...] in order. Used by align() (ref = shotlist planned time,
    text = frag) and by resync_timeline() (ref = the beat's authored start, text = its vo_anchor).

    A monotonic GLOBAL fuzzy alignment instead of «6 exact consecutive words near where the plan
    predicts»: that needed the take to run as planned and the narrator to read the script verbatim,
    so a longer take (E003: 1272 s vs 932 s planned), a paraphrase, a short or elliptical anchor or
    a [S05] tag left most beats unanchored, and everything between two far-apart anchors was
    stretched linearly (measured: 35 % of E003's beats had their own words inside their window;
    the same seed now reaches 68 %, E002 74 → 95 %, E001 72 → 88 %).
      1. every window of the transcript is scored by the idf-weighted share of the anchor's content
         words it contains (rare words count more; the plan's position is NOT used);
      2. dynamic programming picks, for the beats in order, the set of windows that maximises match
         quality with strictly increasing positions (a phrase said twice — intro and sign-off — is
         resolved by order) minus a small penalty for implausible local time-scaling."""
    import math
    N = len(toks)
    if not N or not items:
        return [(0.0, 0.0), (ref_end, vo_end)]
    df, pos = {}, {}
    for i, t in enumerate(toks):
        df[t] = df.get(t, 0) + 1
        pos.setdefault(t, []).append(i)

    def idf(t):
        return math.log((N + 1) / (df.get(t, 0) + 1)) + 1.0

    g = (vo_end / ref_end) if ref_end else 1.0
    cands = []                                         # per item: [(score, first_word_index)]
    for _ref_t, raw in items:
        raw = (raw or "").strip()
        at = _anchor_tokens(raw, keep_tags)
        content = [t for t in dict.fromkeys(at) if len(t) >= 4 and t in df]
        if _stage_dir(raw) or len([t for t in at if len(t) >= 4]) < 2 or not content:
            cands.append([])
            continue
        W = int(len(at) * 2.2) + 5
        tot = sum(idf(t) for t in content)
        diff = [0.0] * (N + W + 2)
        for t in content:
            w = idf(t)
            for q in pos[t]:                           # windows starting in [q-W+1, q] contain q
                diff[max(0, q - W + 1)] += w
                diff[q + 1] -= w
        cov, run = [], 0.0
        for k in range(N):
            run += diff[k]
            cov.append(run / tot)
        peaks = sorted(((cov[k], k) for k in range(N) if cov[k] >= thr
                        and (k == 0 or cov[k] >= cov[k - 1]) and (k == N - 1 or cov[k] > cov[k + 1])),
                       reverse=True)
        out = []
        for sc, k in peaks:
            if any(abs(k - o[1]) < W for o in out):
                continue
            first = next((m for m in range(k, min(N, k + W)) if toks[m] in content), k)
            out.append((sc, first))                    # start = first anchor word actually spoken
            if len(out) >= top:
                break
        cands.append(sorted(out, key=lambda x: x[1]))

    n = len(items)
    best = {}                                          # (item, cand) -> (value, previous key)
    for i in range(n):
        for ci, (sc, k) in enumerate(cands[i]):
            base = sc + bonus
            bv, bp = base, None
            for j in range(max(0, i - look), i):
                for cj, (_sc2, k2) in enumerate(cands[j]):
                    if k2 >= k or (j, cj) not in best:
                        continue
                    dv = words[k]["t"] - words[k2]["t"]
                    dp = items[i][0] - items[j][0]
                    if dv < 0.4 or dp < 0:
                        continue
                    pen = 0.0
                    if dp > 1.0:
                        pen = mu * min(2.0, abs(math.log(max(dv, 0.4) / max(dp, 0.4) / g)))
                    v = best[(j, cj)][0] + base - pen - 0.02 * (i - j - 1)
                    if v > bv:
                        bv, bp = v, (j, cj)
            best[(i, ci)] = (bv, bp)
    if not best:
        return [(0.0, 0.0), (ref_end, vo_end)]
    key, chain = max(best, key=lambda kk: best[kk][0]), []
    while key is not None:
        chain.append(key)
        key = best[key][1]
    knots = [(0.0, 0.0)]
    for i, ci in reversed(chain):
        r, v = items[i][0], round(words[cands[i][ci][1]]["t"], 2)
        if r > knots[-1][0] and v > knots[-1][1] + 0.3 and v < vo_end - 0.3 and r < ref_end:
            knots.append((r, v))
    knots.append((ref_end, vo_end))
    return knots


def _narration_text(text):
    """The spoken part of 05-script.md: the [NARRACIÓN] / [A CÁMARA] lines and plain paragraphs; not
    headings, tables, bullets, quotes or the other [TAG] production notes."""
    keep = {"NARRACIÓN", "NARRACION", "A CÁMARA", "CÁMARA", "CAMARA", "A CAMARA"}
    out = []
    for line in text.splitlines():
        ln = line.strip()
        if not ln or ln.startswith(("#", ">", "|", "---", "- ", "* ", "<!--", "```")):
            continue
        m = re.match(r"^\[([A-ZÁÉÍÓÚÑ /]+)\]\s*(.*)$", ln)
        if m:
            if m.group(1) in keep:
                out.append(m.group(2))
            continue
        out.append(ln)
    return " ".join(out)


def _script_map(ep, words, min_cover=0.8):
    """Global alignment of the SCRIPT's narration to the transcript, so a beat can be placed by where its
    text sits in the script even when the narrator rephrased it (E003's script matched 95 % of the
    voice). Returns {tok, pidx, s2t} or None when there is no usable script (fewer than 80 % of the
    voice matched: another format, or a take that departs from the script) — the voice-only anchors
    then run alone, exactly as before."""
    import bisect
    import difflib
    f = ep / "05-script.md"
    if not f.exists() or not words:
        return None
    try:
        text = _narration_text(f.read_text(encoding="utf-8"))
        text = re.sub(r"`[^`]*`|\*\*|\*|_", " ", text)
        tok, pidx, n = [], [], 0                       # tok: with tag tokens; pidx: spoken words before it
        for m in re.finditer(r"\[S(\d+)\]|([^\[\]]+)|\[[^\]]*\]", text):
            if m.group(1):
                tok.append(_tag_tok(m.group(1)))
                pidx.append(n)
            elif m.group(2):
                for w in _norm(m.group(2)).split():
                    tok.append(w)
                    pidx.append(n)
                    n += 1
        plain = [t for t in tok if not _is_tag(t)]
        if len(plain) < 200:
            return None
        V = [_norm(w["w"]).replace(" ", "") for w in words]
        blocks = [b for b in difflib.SequenceMatcher(None, plain, V, autojunk=False).get_matching_blocks() if b.size]
        if sum(b.size for b in blocks) / max(1, len(V)) < min_cover:
            return None
        pts = sorted({pt for b in blocks for pt in ((b.a, b.b), (b.a + b.size - 1, b.b + b.size - 1))})
        si = [pt[0] for pt in pts]

        def s2t(pi):
            k = bisect.bisect_right(si, pi) - 1
            if k < 0:
                j = 0.0
            elif k >= len(pts) - 1:
                j = float(pts[-1][1])
            else:
                (a0, j0), (a1, j1) = pts[k], pts[k + 1]
                j = j0 + (pi - a0) / (a1 - a0) * (j1 - j0) if a1 > a0 else float(j0)
            j = max(0.0, min(len(words) - 1.0, j))
            lo = int(j)
            hi = min(len(words) - 1, lo + 1)
            return words[lo]["t"] + (j - lo) * (words[hi]["t"] - words[lo]["t"])
        return {"tok": tok, "pidx": pidx, "s2t": s2t}
    except Exception:                                  # a script we can't parse must never break a seed
        return None


def _knots_with_script(voice, items, ref_end, vo_end, script):
    """Merge two kinds of evidence into one knot list. `voice` = knots from anchors spoken verbatim
    (the most direct proof). `script` adds a knot for every beat whose text — including its [Sxx] source
    tags — can be found in the script: its script position is mapped to voice time through the global
    alignment. Same beat: the voice wins. Conflicts (non-monotone) drop the script knot."""
    if not script:
        return voice
    tok, pidx = script["tok"], script["pidx"]
    pseudo = [{"t": float(i)} for i in range(len(tok))]
    try:
        sk = _anchors(items, tok, pseudo, ref_end, float(len(tok)), keep_tags=True)[1:-1]
    except Exception:
        return voice
    have = {round(r, 3) for r, _ in voice[1:-1]}
    cand = [(r, v, 0) for r, v in voice[1:-1]]
    for r, pidx_f in sk:
        if round(r, 3) in have:
            continue
        k = min(len(tok) - 1, max(0, int(round(pidx_f))))
        cand.append((r, script["s2t"](pidx[k]), 1))
    cand.sort()
    out = []
    for r, v, pri in cand:
        while True:
            if not out or v > out[-1][1] + 0.3:
                out.append((r, v, pri))
                break
            if out[-1][2] > pri:                       # top is a script knot, this is spoken evidence
                out.pop()
                continue
            break
    knots = [voice[0]]
    for r, v, _ in out:
        if r > knots[-1][0] and v > knots[-1][1] + 0.3 and v < vo_end - 0.3 and r < ref_end:
            knots.append((r, round(v, 2)))
    knots.append(voice[-1])
    return knots


def sync_report(beats, words, pad=0.75):
    """Independent sync check (does NOT use the aligner): is each beat's own anchor text actually
    spoken inside its [in, out] window? Returns {n, ok, pct, worst:[(id, in, spoken_at)]} for the
    beats with a usable anchor. Low % = the timeline and the voice disagree (E002 sat at 22 %
    with a 40 s drift at the close and nothing said so)."""
    rows = []
    wt = [(_norm(w["w"]), w["t"]) for w in words]
    if not wt:
        return {"n": 0, "ok": 0, "pct": 100, "worst": []}
    toks = [t for t, _ in wt]
    for b in beats:
        raw = b.get("vo_anchor") or b.get("frag") or ""
        if b.get("kind") == "negro" or not raw or _stage_dir(raw.strip()):
            continue
        A = [t for t in _anchor_tokens(raw) if len(t) >= 4]
        if len(A) < 2:
            continue
        inside = {t for t, x in wt if b["in"] - pad <= x <= b["out"] + pad}
        hit = sum(1 for a in A if a in inside) / len(A)
        rows.append((b, A, hit))
    ok = sum(1 for _b, _A, h in rows if h >= 0.5)
    worst = []
    for b, A, h in rows:
        if h >= 0.5:
            continue
        aset, W = set(A), int(len(A) * 2.5) + 3
        bc, bt = 0, None
        for i in range(0, max(1, len(toks) - W)):
            c = len({t for t in toks[i:i + W] if t in aset})
            if c > bc:
                bc, bt = c, wt[i][1]
        if bt is not None and bc / len(A) >= 0.6:       # only when the phrase can be located
            worst.append((b["id"], round(b["in"], 1), round(bt, 1)))
    worst.sort(key=lambda w: -abs(w[1] - w[2]))
    return {"n": len(rows), "ok": ok, "pct": round(100 * ok / len(rows)) if rows else 100, "worst": worst[:5]}


def uncovered_reasons(ep, beats):
    """Why each `sin cubrir` beat is uncovered, from the Stage-7 files, so the answer isn't «elige
    uno» for a beat that never had candidates to choose from (E003: 3 of the last 4 had no
    07-pull.tsv row at all, one had candidates nobody ticked)."""
    def _rows(name, pred=lambda c: True):
        f = ep / name
        out = set()
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                c = line.split("\t")
                if line.startswith("#") or len(c) < 2 or not c[0].strip().isdigit() or not pred(c):
                    continue
                out.add(int(c[0]))
        return out
    pulled, picked = _rows("07-pull.tsv"), _rows("07-picks.txt")
    first_of = {}                                       # asset id -> the first beat that uses it (it carries the pull row)
    for b in beats:
        if b.get("asset") and b.get("kind") not in ACAMARA:
            first_of.setdefault(b["asset"], b.get("id") or f"b{b.get('n')}")
    out = []
    for b in beats:
        if b.get("state") != "uncovered":
            continue
        bid = b.get("id") or (f"b{b['n']}" if b.get("n") is not None else "?")   # timeline beats carry id, a fresh spine only n
        n = int(bid[1:]) if bid[1:].isdigit() else None
        kind = b.get("kind")
        first = first_of.get(b.get("asset") or "")
        if kind in ACAMARA:
            why = "toma recortada aún no disponible"
        elif first and first != bid:
            why = f"reutiliza el asset de {first} (PAY/eco): se cubre al elegir el de ese beat"
        elif not (b.get("asset") or ""):
            why = "quitado / sin asset asignado"
        elif n in picked:
            why = "hay una elección en 07-picks.txt pero su archivo no existe en disco"
        elif kind in ("archivo", "stock", "video") and n not in pulled:
            why = "sin fila en 07-pull.tsv (el Stage 7 nunca buscó candidatos para este beat)"
        elif kind in ("archivo", "stock", "video"):
            why = "tiene candidatos en el style pass pero no se eligió ninguno"
        elif kind == "ia":
            why = "falta generar la imagen IA (07b-ai-prompts.md)"
        elif kind in GRAPHIC:
            why = "gráfico sin generar (make_graphics.py)"
        else:
            why = "sin archivo"
        out.append((bid, b.get("asset") or "", why))
    return out


def _remap_fn(anchors, vo_end):
    def remap(pt):
        for (p0, v0), (p1, v1) in zip(anchors, anchors[1:]):
            if pt <= p1 or (p1, v1) == anchors[-1]:
                f = (pt - p0) / (p1 - p0) if p1 > p0 else 0.0
                return v0 + f * (v1 - v0)
        return vo_end
    return remap


def align(beats, words, script=None):
    """Anchor the shotlist's planned timeline to the real VO — piecewise-linearly
    remap planned times onto VO time between the beats whose frag matches the
    voice confidently (plus, when a `script` map is given, the beats located through the script).
    Runs once, at seed."""
    beats.sort(key=lambda x: x["n"])
    if not words:
        return beats, round(beats[-1]["out"], 2) if beats else 0.0
    toks = [_norm(w["w"]) for w in words]
    vo_end = _vo_end_from_words(words)
    planned_end = beats[-1]["out"] or vo_end
    items = [(b["in"], b.get("frag")) for b in beats]
    anchors = _anchors(items, toks, words, planned_end, vo_end)
    anchors = _knots_with_script(anchors, items, planned_end, vo_end, script)
    remap = _remap_fn(anchors, vo_end)

    # Place each START on its anchor, or right after the previous beat's minimum length when the voice
    # doesn't leave room. Precise anchors leave short beats (a 3 s montage under one quick phrase);
    # remap() alone squeezed them below the floor and tidy_subfloor() then MERGED them away —
    # E003 lost its bodegón, its grabado satírico and two AI images that way. A visual beat that
    # doesn't fit now runs late only until the next anchor, where it snaps back to the voice. Only
    # a narrator cut too short to register (no asset) is still merged.
    planned = [remap(b["in"]) for b in beats]
    starts = []
    for i, b in enumerate(beats):
        if i == 0:
            starts.append(round(planned[0], 2))
            continue
        pv = beats[i - 1]
        hold = 0.6 if pv["kind"] in ACAMARA else (3.0 if pv["kind"] in GRAPHIC else MIN_BEAT)
        st = max(planned[i], starts[i - 1] + hold)
        starts.append(round(min(st, vo_end - 0.6 * (len(beats) - i)), 2))
    for i, b in enumerate(beats):
        b["in"] = starts[i]
        b["out"] = starts[i + 1] if i + 1 < len(beats) else round(vo_end, 2)
    total = vo_end
    beats[-1]["out"] = total
    beats = tidy_subfloor(beats, total)
    flag_rhythm(beats)
    for b in beats:
        b.pop("_al", None)
    return beats, total


def flag_rhythm(beats):
    """Advisory rhythm markers (brain/11) — the edit page shows a warning marker,
    the audit tools surface the list. Never touches timing. Recomputed from
    scratch each call so a schema-2 rebuild reflects the current cut.
      b['pace'] — a still/graphic held too long, or a graphic too brief to read
      b['dup']  — a graphic id reused, or an asset over-used per video / section
    """
    for b in beats:
        b.pop("pace", None)
        b.pop("dup", None)
    for b in beats:
        dur = b["out"] - b["in"]
        plan = b.get("dur", dur)
        if b["kind"] in ACAMARA:
            pass                               # a piece to camera runs as long as the
            #                                    voice needs it (house format, brain/11 §1b)
        elif b["kind"] in GRAPHIC and dur < MIN_GRAPHIC:
            b["pace"] = round(dur, 1)          # too brief to read (brain/11 §2.2)
        elif dur > max(2.5 * plan, 20):
            b["pace"] = round(dur, 1)          # held way past plan
    # asset over-reuse (brain/11 §2.2): a graphic id used >1× without a
    # PROMISE/PAY/eco tag, or any asset used >3× / >2× in one section.
    seen, per_sec = {}, {}
    for b in beats:
        a = b.get("asset") or ""
        if not a or b["kind"] in ACAMARA or b["kind"] == "negro":
            continue
        ref = b["n"] if b.get("n") is not None else b.get("id")
        mk = (b.get("marker") or b.get("marcador") or "").lower()
        tagged = any(t in mk for t in ("promise", "pay", "eco"))
        seen.setdefault(a, []).append(ref)
        per_sec.setdefault((a, b.get("section", "")), []).append(ref)
        if a.startswith("G") and len(seen[a]) == 2 and not tagged:
            b["dup"] = seen[a][0]
            print(f"  ⚠ gráfico {a} repetido (beat {ref} ↔ {seen[a][0]}) sin marcador")
        elif not a.startswith("G") and len(seen[a]) == 4 and not tagged:
            b["dup"] = seen[a][0]
            print(f"  ⚠ asset {a} usado {len(seen[a])}× (beats {seen[a]}) — diversifica")
        if len(per_sec[(a, b.get('section', ''))]) == 3 and not tagged:
            print(f"  ⚠ asset {a} usado 3× en «{b.get('section')}» (beats {per_sec[(a, b.get('section', ''))]})")
    return beats


MIN_BEAT = 2.8          # a B-roll shot shorter than this is a wasted flash
MIN_ACAMARA = 2.5       # a talking-head cut shorter than this doesn't register
MIN_GRAPHIC = 5.0       # a graphic on screen less than this can't be read (brain/11 §2.2)
GRAPHIC = ("gráfico", "grafico")


def _apply_edits(beats):
    """Edit-room overrides applied on top of align(), and kept across re-builds:
      b['slot']      — a float sort key: the beat moves to that position in the
                       sequence and takes the time window there (the VO stays put,
                       only which picture shows when changes)
      b['dur_lock']  — a locked shot length in seconds; the delta is taken from
                       the next beat (lengthening a shot shortens its neighbour)
    """
    if not beats:
        return beats
    for i, b in enumerate(beats):
        b["_i"] = i
    if any(isinstance(b.get("slot"), (int, float)) for b in beats):
        win = [(b["in"], b["out"]) for b in beats]
        beats = sorted(beats, key=lambda b: b["slot"] if isinstance(b.get("slot"), (int, float)) else b["_i"])
        for k, b in enumerate(beats):
            b["in"], b["out"] = win[k]
    def _floor(x):
        return MIN_ACAMARA if x["kind"] in ACAMARA else MIN_BEAT
    for i in range(len(beats) - 1):
        b, nb = beats[i], beats[i + 1]
        d = b.get("dur_lock")
        if not d:
            continue
        # move the b/nb boundary to give b the locked length, but never take nb
        # (or b) below its floor — a bigger hold than that needs a merge, not this
        lo = b["in"] + _floor(b)
        hi = nb["out"] - _floor(nb)
        cut = round(min(max(b["in"] + float(d), lo), hi), 2)
        b["out"], nb["in"] = cut, cut
    for b in beats:
        b.pop("_i", None)
    return beats


def tidy_subfloor(beats, total, merge_same_file=True):
    """Kill the millisecond flashes and the pile-ups: merge any beat too short
    to register into its neighbour, and (when `merge_same_file`) collapse two
    identical shots in a row — except a deliberate PROMISE→PAY reuse or a fresh
    SPLIT — into one move.

    Called once from seed_timeline() and from the edit room's opt-in «Ordenar»
    button. The per-save rebuild does NOT call this — a schema-2 timeline may
    legitimately hold a sub-floor beat the editor put there on purpose."""
    out = []
    for b in beats:
        floor = MIN_ACAMARA if b["kind"] in ACAMARA else MIN_BEAT
        dur = b["out"] - b["in"]
        if out:
            prev = out[-1]
            same_file = (merge_same_file and b.get("file")
                         and b["file"] == prev.get("file"))
            # a PROMISE→PAY reuse, or a beat just split in the cutting room (the 2nd
            # half is deliberately the same shot until the editor reassigns it)
            promise_pay = ({(prev.get("marker") or "")[:3], (b.get("marker") or "")[:3]} & {"PRO", "PAY"}
                           or "SPLIT" in ((prev.get("marker") or ""), (b.get("marker") or "")))
            # don't merge a real A-roll beat away — the narrator on camera is a
            # deliberate structural beat even if the alignment shrank it a bit
            aroll_keep = b["kind"] in ACAMARA and dur >= MIN_ACAMARA and not (same_file and not promise_pay)
            # a graphic beat is a deliberate structural beat — don't merge it away
            # for being a bit short (it gets a pace flag instead, below)
            graphic_keep = b["kind"] in GRAPHIC and dur >= 3.0 and not (same_file and not promise_pay)
            if not aroll_keep and not graphic_keep and (dur < floor - 0.005 or (same_file and not promise_pay)):   # (0.005: 43.40-40.60 is 2.7999999… in floats — a beat exactly at the floor was being merged away)
                # absorb: the later narration wins the asset unless it has none
                keep_new = bool(b.get("file")) and (dur >= prev["out"] - prev["in"] or not prev.get("file"))
                if keep_new:
                    for k in ("asset", "file", "aspect", "motion", "marker",
                              "frag", "vo_anchor", "label", "kind"):
                        if b.get(k):
                            prev[k] = b[k]
                prev["out"] = b["out"]
                prev["merged"] = prev.get("merged", 0) + 1
                continue
        out.append(b)
    # keep original beat numbers (gaps are fine) so the edit page's saved human
    # decisions still key correctly across rebuilds
    return out


def _duration(path):
    try:
        r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(path)], capture_output=True, text=True, timeout=20)
        return float(r.stdout.strip() or 0)
    except Exception:
        return 0.0


# ── build 09-timeline.json ────────────────────────────────────────────────

def music_pool():
    d = ROOT / "brand" / "assets" / "music"
    return [f"brand/assets/music/{f.name}" for f in sorted(d.glob("*.mp3"))] if d.is_dir() else []


def _episode_music_tracks(ep):
    """This episode's own music picks, in the order chosen on the Stage 7 style
    pass — from the `## Música` section `pull_assets.py --download` writes into
    07-selection.md (one row per picked track, `Archivo` column = the file it
    downloaded into the shared brand/assets/music/ pool). Multiple tracks play
    back-to-back, then the whole sequence loops to fill the video (see the
    render's aloop-over-concat below) — that's what lets a video with more
    beats than the picked music can cover still have a full bed."""
    sel = ep / "07-selection.md"
    if not sel.exists():
        return []
    m = re.search(r"## Música\b.*?\n\n(.*?)(?:\n##\s|\Z)", sel.read_text(encoding="utf-8"), re.S)
    if not m:
        return []
    tracks = []
    for line in m.group(1).splitlines():
        cell = re.findall(r"`([^`]+)`", line)
        if cell and cell[-1] not in tracks:
            tracks.append(cell[-1])
    return [t for t in tracks if (ROOT / t).exists()]


def _require_ep(slug):
    ep = EP_DIR / slug
    if not ep.is_dir():
        raise SystemExit(f"no existe {ep}")
    if not (ep / "06-shotlist.md").exists():
        raise SystemExit(f"no existe episodes/{slug}/06-shotlist.md — el Stage 6 no está hecho")
    return ep


def _derive_motion(beats):
    """Resolve each still's real Ken Burns move (aspect-aware, no dead holds) so
    the JSON matches what render() does. The authored `motion` is the input."""
    for b in beats:
        if b["kind"] in ("archivo", "ia", "kb", "gráfico", "grafico"):
            b["motion"] = kb_move(b, 3840, 2160)
        if b["kind"] in GRAPHIC and b.get("motion") in ("cut", "static", "", None):
            b["motion"] = "push"
        if (b.get("file") or "").lower().endswith((".mp4", ".mov", ".webm")):
            # brain/20 §4.3: every moving cita excerpt gets a push/reframe move,
            # never a flat hold — everything else stays a hard cut (no zoompan).
            b["motion"] = "push" if b["kind"] == "cita" else "cut"
    return beats


def _music_block(prev_music, beats, total, ep=None):
    _mrange = {"bed_db": (-48, -6), "vo_gain_db": (-8, 8), "duck_db": (0, 20)}
    mix = {k: prev_music[k] for k in _mrange
           if isinstance(prev_music.get(k), (int, float)) and _mrange[k][0] <= prev_music[k] <= _mrange[k][1]}
    pool = music_pool()
    # tracks: an authored timeline's own list always wins (the editor may have
    # pruned/reordered it in the Sala) — only derive fresh from Stage 7's picks
    # (or fall back to the pool / a legacy single "bed") the first time there's
    # nothing authored yet.
    prev_tracks = prev_music.get("tracks")
    if isinstance(prev_tracks, list) and prev_tracks:
        tracks = [t for t in prev_tracks if isinstance(t, str) and t]
    elif prev_music.get("bed"):
        tracks = [prev_music["bed"]]                      # migrate an old single-bed timeline
    else:
        tracks = (_episode_music_tracks(ep) if ep is not None else []) or (pool[:1] if pool else [])
    return {"pool": pool, "tracks": tracks, "bed": tracks[0] if tracks else "",
            # array[0] is always the first shot shown (array order == playback
            # order, even after a reorder), so music still starts when it ends
            "in": beats[0]["out"] if beats else 0, "out": total,
            "bed_db": -30, "vo_gain_db": 0, "duck_db": 8, **mix}


def _words_sig(words):
    """A short digest of the trimmed VO word list — changes iff a re-record /
    re-trim moved the voice, so a schema-2 timeline can offer «Re-sincronizar»."""
    import hashlib
    h = hashlib.sha1()
    for w in words:
        h.update(f"{w['w']}|{round(w['t'], 2)}\n".encode("utf-8"))
    return h.hexdigest()[:16]


def _prev_json(tj):
    if not tj.exists():
        return {}
    try:
        return json.loads(tj.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _idn(bid):
    return int(bid[1:]) if isinstance(bid, str) and bid[1:].isdigit() else 0


_AUTHORED_KEYS = ("id", "dur", "section", "kind", "asset", "label", "motion",
                  "marker", "vo_anchor", "fix", "nudge", "dur_edited",
                  "in", "out", "file", "state", "aspect", "pace", "dup")


_ALWAYS = ("id", "dur", "section", "kind", "asset", "motion", "in", "out", "state")


def _authored_beat(b):
    """A schema-2 beat: authored fields first, derived fields (in/out/file/…)
    kept for the page to read directly. Everything else (n, frag, slot,
    dur_lock, approved, _i, _al) is dropped."""
    out = {}
    for k in _AUTHORED_KEYS:
        if k not in b:
            continue
        v = b[k]
        if k not in _ALWAYS and (v is None or v == "" or (k == "dur_edited" and not v)):
            continue
        out[k] = v
    return out


def _report(slug, beats, total, aligned):
    n_un = sum(1 for b in beats if b.get("state") == "uncovered")
    n_fix = sum(1 for b in beats if b.get("fix"))
    print(f"escrito  episodes/{slug}/09-timeline.json  "
          f"({len(beats)} beats · {_fmt(total)} · "
          f"{'alineado a la voz' if aligned else 'tiempos del shotlist (sin voz aún)'} · "
          f"{n_un} sin cubrir · {n_fix} con corrección)")
    ep = EP_DIR / slug
    if aligned:
        sr = sync_report(beats, load_words(ep))
        if sr["n"]:
            print(f"  sincronía: {sr['ok']}/{sr['n']} beats ({sr['pct']} %) con su frase dentro de su ventana"
                  + ("  ⚠ BAJA — la línea y la voz no coinciden; revisa antes de montar" if sr["pct"] < 60 else ""))
            for bid, at, said in sr["worst"][:3]:
                print(f"    ⚠ {bid}: empieza en {at:.0f}s y su frase se dice en {said:.0f}s")
    for bid, asset, why in uncovered_reasons(ep, beats)[:14]:
        print(f"  sin cubrir {bid} «{asset}» — {why}")


def build_timeline(slug):
    """Back-compat entry: seed the timeline if there isn't one, then rebuild it.
    Every existing caller (render, --rough, --final, --timeline-only) still works."""
    if not (EP_DIR / slug / "09-timeline.json").exists():
        seed_timeline(slug)
    return rebuild_timeline(slug)


def seed_timeline(slug, force=False):
    """Create 09-timeline.json ONCE from the shotlist spine + the trimmed VO
    (brain/16 «timeline canónica»). align() runs here and only here. Idempotent:
    an existing schema-2 file is returned untouched unless `force`; a schema-1
    file is never clobbered silently — migrate it first."""
    ep = _require_ep(slug)
    tj = ep / "09-timeline.json"
    cur = _prev_json(tj)
    if cur and not force:
        if cur.get("schema", 1) >= 2:
            print(f"  09-timeline.json ya sembrada (schema {cur['schema']}) — no la toco")
            return cur
        raise SystemExit(
            f"09-timeline.json es schema 1 (línea derivada, quizá editada a mano).\n"
            f"  migra antes de sembrar:  python tools/migrate_timeline.py {slug}")

    beats = parse_spine((ep / "06-shotlist.md").read_text(encoding="utf-8"))
    resolve(ep, beats)
    words = load_words(ep)
    beats, total = align(beats, words, _script_map(ep, words))   # tidy_subfloor + flag_rhythm run inside
    if not words:
        total = round(beats[-1]["out"], 2)
    _derive_motion(beats)

    if SCHEMA_CURRENT < 2:
        # legacy shape — the seed still writes a derived timeline until the
        # migration commit flips SCHEMA_CURRENT to 2
        data = {"ep": slug[:4], "slug": slug, "generated": _now(), "schema": 1,
                "aligned": bool(words), "fps": FPS, "w": 3840, "h": 2160,
                "total": total, "ground": GROUND,
                "music": _music_block({}, beats, total, ep=ep), "beats": beats}
        tj.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        _report(slug, beats, total, bool(words))
        return data

    vo_end = round(_vo_end_from_words(words), 2) if words else round(total, 2)
    ab = to_authored_beats(beats, vo_end)
    derive_times(ab, vo_end)              # write canonical (cumsum) in/out, not align's
    total = round(ab[-1]["out"], 2) if ab else total
    data = authored_doc(slug, ab, vo_end=vo_end, total=total,
                        words_sig=_words_sig(words), aligned=bool(words),
                        music=_music_block({}, ab, total, ep=ep))
    tj.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    _report(slug, ab, round(total, 2), bool(words))
    return data


def to_authored_beats(beats, vo_end):
    """Turn derived beats (n, frag, in/out) into authored schema-2 beats: `id`
    from the spine row, `dur` = the current on-screen length (so the first
    rebuild reproduces the same cut), `vo_anchor` from `frag`. The last beat's
    `dur` closes exactly on vo_end so cumulative sum lands there."""
    for b in beats:
        if "id" not in b and b.get("n") is not None:
            b["id"] = f"b{b['n']}"
        b["vo_anchor"] = b.get("vo_anchor") or b.pop("frag", "") or ""
        b["dur"] = round(b["out"] - b["in"], 3)
    if beats and vo_end:
        beats[-1]["dur"] = round(float(vo_end) - beats[-1]["in"], 3)
    return [_authored_beat(b) for b in beats]


def authored_doc(slug, ab, *, vo_end, total, words_sig, aligned, music, seeded=None):
    return {
        "ep": slug[:4], "slug": slug, "generated": _now(), "schema": 2,
        "seeded": seeded or _now(), "aligned": aligned,
        "fps": FPS, "w": 3840, "h": 2160,
        "vo_end": round(float(vo_end), 2), "total": round(float(total), 2), "ground": GROUND,
        "next_id": max((_idn(b.get("id")) for b in ab), default=0) + 1,
        "words_sig": words_sig,
        "music": music, "beats": ab,
    }


def rebuild_timeline(slug):
    """Recompute 09-timeline.json in place, keeping every edit-room decision.
    Schema 1 → the legacy path (re-parse the spine, re-align, fold the overrides).
    Schema 2 → the authored path: read the beats, lay them on the VO by
    cumulative `dur`, re-resolve files. No align()."""
    ep = _require_ep(slug)
    tj = ep / "09-timeline.json"
    cur = _prev_json(tj)
    if not cur:
        return seed_timeline(slug)
    if cur.get("schema", 1) >= 2:
        return _rebuild_authored(slug, ep, tj, cur)
    return _rebuild_schema1(slug, ep, tj)


def _rebuild_authored(slug, ep, tj, data):
    beats = data.get("beats", [])
    resolve(ep, beats)
    _derive_motion(beats)
    words = load_words(ep)
    vo_end = get_vo_end(ep, data.get("vo_end"))
    total = round(data.get("total") or 0.0, 2)
    if beats:
        derive_times(beats, vo_end)
        total = round(beats[-1]["out"], 2)
    flag_rhythm(beats)
    ab = [_authored_beat(b) for b in beats]
    out = dict(data)
    out.update({
        "generated": _now(), "schema": 2,
        "aligned": bool(words), "fps": FPS,
        "w": data.get("w", 3840), "h": data.get("h", 2160),
        "vo_end": round(vo_end, 2) if vo_end else data.get("vo_end", 0),
        "total": total, "ground": data.get("ground", GROUND),
        "next_id": data.get("next_id") or (max((_idn(b.get("id")) for b in ab), default=0) + 1),
        "words_sig": data.get("words_sig") or _words_sig(words),
        "music": _music_block(data.get("music", {}), ab, total, ep=ep),
        "beats": ab,
    })
    tj.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    _report(slug, ab, total, bool(words))
    return out


def _rebuild_schema1(slug, ep, tj):
    beats = parse_spine((ep / "06-shotlist.md").read_text(encoding="utf-8"))
    resolve(ep, beats)
    words = load_words(ep)
    beats, total = align(beats, words)
    if not words:
        total = round(beats[-1]["out"], 2)
    _derive_motion(beats)

    prev = {}
    try:
        for b in json.loads(tj.read_text(encoding="utf-8")).get("beats", []):
            prev[b["n"]] = b
    except (json.JSONDecodeError, KeyError):
        pass
    # keep the edit room's decisions across re-builds: fix / nudge (and the
    # motion the user picked on a beat they worked). `asset` is NOT restored —
    # an asset change goes through the shotlist (beat_asset.py patches the spine
    # row), so parse_spine above is already authoritative. (Legacy schema-1 path.)
    for b in beats:
        p = prev.get(b["n"])
        if not p:
            continue
        touched = any(p.get(k) for k in ("fix", "nudge"))
        for k in ("fix", "nudge", "dur_lock", "slot"):
            if p.get(k) is not None:
                b[k] = p[k]
        if touched and p.get("motion"):
            b["motion"] = p["motion"]

    beats = _apply_edits(beats)
    total = round(beats[-1]["out"], 2) if beats else total
    prev_music = _prev_json(tj).get("music", {}) or {}
    data = {
        "ep": slug[:4], "slug": slug, "generated": _now(), "schema": 1,
        "aligned": bool(words), "fps": FPS, "w": 3840, "h": 2160,
        "total": total, "ground": GROUND,
        "music": _music_block(prev_music, beats, total, ep=ep),
        "beats": beats,
    }
    tj.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    _report(slug, beats, total, bool(words))
    return data


def resync_timeline(slug, keep_edits=True):
    """Re-fit a schema-2 timeline to a re-recorded / re-trimmed VO (brain/16).
    3-way merge: a beat the editor set the duration of (`dur_edited`) keeps its
    `dur`; every other beat is re-fitted to the new voice by remapping its
    current start through its `vo_anchor`. Only fires on «Re-sincronizar».
    `keep_edits=False` re-anchors EVERY beat to the voice and lets go of the hand-set durations:
    those were fixed against a voice that has since been re-trimmed, so keeping them keeps the
    drift (E002: 75 of 98 beats hand-set, 22 % in sync, up to 40 s out at the close). Order,
    added / split beats and assets are untouched either way."""
    ep = _require_ep(slug)
    tj = ep / "09-timeline.json"
    data = _prev_json(tj)
    if data.get("schema", 1) < 2:
        raise SystemExit("«Re-sincronizar» solo aplica a una línea schema 2 (migra primero)")
    beats = data.get("beats", [])
    if not beats:
        raise SystemExit("la línea no tiene beats")
    new_words = load_words(ep)
    if not new_words:
        raise SystemExit("no hay voz trimmeada — nada que re-sincronizar")

    old_vo_end = float(data.get("vo_end") or beats[-1]["out"])
    new_vo_end = _vo_end_from_words(new_words)

    # A timeline that was seeded BEFORE the voice existed (Stage 9 opens before the take is recorded)
    # was never aligned: its times are the shotlist's plan. Re-fitting a plan is a lossy patch (E003:
    # it left 464 s in the last beat), so when nothing in it was authored by hand this is really the
    # FIRST alignment — do the full one.
    never_aligned = (not data.get("aligned")) or data.get("words_sig") in ("", _words_sig([]))
    if never_aligned:
        try:
            spine = [f"b{b['n']}" for b in parse_spine((ep / "06-shotlist.md").read_text(encoding="utf-8"))]
        except (OSError, SystemExit):
            spine = []
        ids = [b.get("id") for b in beats]
        authored = (any(b.get("dur_edited") or b.get("fix") or b.get("approved") or b.get("slot") for b in beats)
                    or ids != spine)
        if spine and not authored:
            seeded = seed_timeline(slug, force=True)
            (ep / "09-resync.flag").unlink(missing_ok=True)
            note = "primera alineación completa con la voz (la línea se sembró antes de que existiera la toma)"
            print(note)
            return {"note": note, "vo_shift": round(new_vo_end - old_vo_end, 1), "kept": 0,
                    "refit": len(seeded.get("beats", [])), "anchors": 0, "total": seeded.get("total")}

    # the reference clock is the AUTHORED one: `in` = cumulative sum of `dur` (derive_times). The stored
    # in/out can be stale (a schema-1 migration left E003's last beat at in 558 with total 932).
    ref = [dict(b) for b in beats]
    derive_times(ref, old_vo_end)
    old_total = ref[-1]["out"]
    toks = [_norm(w["w"]) for w in new_words]
    items = [(r["in"], b.get("vo_anchor")) for r, b in zip(ref, beats)]
    anchors = _anchors(items, toks, new_words, old_total, new_vo_end)
    anchors = _knots_with_script(anchors, items, old_total, new_vo_end, _script_map(ep, new_words))
    remap = _remap_fn(anchors, new_vo_end)
    prop_in = [round(remap(r["in"]), 3) for r in ref] + [round(new_vo_end, 3)]

    # Walk forward placing each START: on its anchor (prop_in), or right after the previous beat if the
    # previous one's minimum length doesn't leave room. The old `dur = max(floor, gap)` inflated every
    # short beat and the inflation ADDED UP, dragging everything behind it late; here a beat that
    # can't fit is late only until the next anchor, where the start snaps back to the voice.
    kept = refit = 0
    starts = [0.0]
    for i, b in enumerate(beats):
        if b.get("dur_edited") and keep_edits:
            kept += 1
            starts.append(starts[i] + float(b.get("dur") or 0.0))
            continue
        b.pop("dur_edited", None)              # (re-anchored: no longer a hand-set duration)
        fl = (MIN_ACAMARA if b["kind"] in ACAMARA
              else MIN_GRAPHIC if b["kind"] in GRAPHIC else MIN_BEAT)
        nxt = max(prop_in[i + 1], starts[i] + fl)
        b["dur"] = round(nxt - starts[i], 3)
        starts.append(nxt)
        refit += 1

    resolve(ep, beats)
    _derive_motion(beats)
    derive_times(beats, new_vo_end)
    flag_rhythm(beats)
    ab = [_authored_beat(b) for b in beats]
    data["beats"] = ab
    data["vo_end"] = round(new_vo_end, 2)
    data["total"] = round(ab[-1]["out"], 2)
    data["words_sig"] = _words_sig(new_words)
    data["seeded"] = _now()
    data["aligned"] = True
    data["music"] = _music_block(data.get("music", {}), ab, data["total"], ep=ep)
    tj.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (ep / "09-resync.flag").unlink(missing_ok=True)

    shift = round(new_vo_end - old_vo_end, 1)
    n_anchor = len(anchors) - 2
    note = (f"re-sincronizado · voz {shift:+.1f}s · {kept} beats con duración fija "
            f"conservados · {refit} re-ajustados · {n_anchor} anclas de voz")
    print(note)
    return {"note": note, "vo_shift": shift, "kept": kept, "refit": refit,
            "anchors": n_anchor, "total": data["total"]}


def _now():
    import datetime
    return datetime.date.today().isoformat()


def _fmt(s):
    s = int(round(s))
    return f"{s // 60:d}:{s % 60:02d}"


# ── waveform ─────────────────────────────────────────────────────────────

def vo_proxy(slug):
    """09-vo.m4a — the trimmed VO as a small AAC file the edit page plays live
    (the trimmed take can be ~800 MB). Skipped if newer than the take."""
    ep = EP_DIR / slug
    vo = next(iter(sorted(ep.glob("assets/*.trimmed.mp4"))), None)
    out = ep / "09-vo.m4a"
    if not vo:
        return None
    if out.exists() and out.stat().st_mtime >= vo.stat().st_mtime:
        return out
    r = subprocess.run([FFMPEG, "-y", "-i", str(vo), "-vn", "-ac", "1",
                        "-c:a", "aac", "-b:a", "128k", str(out)], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  escrito  09-vo.m4a")
    return out


def take_proxy(slug):
    """09-take.mp4 — a small 720p proxy of the trimmed narrator take for the edit
    page's live compositor. The 4K/1080p master runs ~800 MB; seeking into it
    stutters. This is a light 540p stream, muted (voice is #vo), with a keyframe
    twice a second so the one seek per beat-switch lands fast and the decoder
    keeps up on playback. Cached — skipped if newer than the take."""
    ep = EP_DIR / slug
    vo = next(iter(sorted(ep.glob("assets/*.trimmed.mp4"))), None)
    out = ep / "09-take.mp4"
    if not vo:
        return None
    if out.exists() and out.stat().st_mtime >= vo.stat().st_mtime:
        return out
    r = subprocess.run([FFMPEG, "-y", "-i", str(vo),
                        "-vf", "scale=-2:540,fps=24", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "32", "-g", "12", "-keyint_min", "12", "-sc_threshold", "0",
                        "-an", "-movflags", "+faststart", str(out)],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  escrito  09-take.mp4  ({out.stat().st_size // (1024 * 1024)} MB)")
    else:
        print(f"  09-take.mp4 falló: {(r.stderr or r.stdout)[-200:]}")
    return out


def waveform(slug):
    ep = EP_DIR / slug
    vo = _soft_vo(ep) or next(iter(sorted(ep.glob("assets/*.trimmed.mp4"))), None)
    out = ep / "09-wave.b64"
    vo_proxy(slug)
    take_proxy(slug)
    if not vo:
        out.write_text("", encoding="utf-8")
        print("  sin voz trimmeada aún — waveform vacío")
        return
    png = ep / "_wave.png"
    cmd = [FFMPEG, "-y", "-i", str(vo), "-filter_complex",
           "aformat=channel_layouts=mono,showwavespic=s=2400x120:colors=#9c927a",
           "-frames:v", "1", str(png)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0 and png.exists():
        b = base64.b64encode(png.read_bytes()).decode()
        out.write_text("data:image/png;base64," + b, encoding="utf-8")
        png.unlink(missing_ok=True)
        print(f"  escrito  09-wave.b64  ({len(b) // 1024} KB)")
    else:
        out.write_text("", encoding="utf-8")
        print("  FALLO showwavespic — waveform vacío")


# ── render (ffmpeg filter_complex) ───────────────────────────────────────

def kb_move(b, w, h):
    """Pick the Ken Burns move for a still. A portrait asset always pans
    vertically (the whole image is seen — never black bars + a tiny picture);
    a panorama pans horizontally — this even overrides an explicit `cut`, since
    you can't hard-hold an off-ratio image without bars or a brutal crop. For a
    frame-ratio still: honour `cut`, else push/zoom, and never `static` (a dead
    frame for seconds is wasted screen time)."""
    mv = b.get("motion", "static")
    ar, far = b.get("aspect") or 0.0, w / h
    if ar and ar < far * 0.80:
        return "pan-v"
    if ar and ar > far * 1.40:
        return "pan-h"
    if mv == "cut":
        return "cut"
    if mv in ("static", "", None):
        return "push"
    return mv


def _kb_canvas(w, h):
    """The 16:9 canvas the geq zoom works on before the final downscale. geq is
    smooth at any size (continuous sampling, no crop-rounding) — a bigger canvas
    only adds sharpness, and its cost is ~linear in pixels. So: light 1.5×
    supersample for the 720p proxy, native for the 4K master (no point, and it
    would grind)."""
    cw = 1920 if w <= 1280 else w
    return cw, round(cw * 9 / 16)


def _still_move(b, w, h):
    mv = kb_move(b, w, h)
    return mv if mv in ("pan-v", "pan-h", "cut", "push", "zoom") else "push"


def _geq_zoom_vf(mv, w, h, dur):
    """The push/zoom move as a `geq` per-pixel remap of a continuously-scaling
    centre-anchored coordinate. `zoompan` rounds its crop window to whole pixels
    every frame — on a slow zoom that stair-steps ~1 px and reads as a tremble.
    geq has no crop window and no rounding. Slower (single-threaded), so
    render() bakes each zoom beat to a cached clip (_kb_render)."""
    amt = 0.20 if mv == "zoom" else 0.10
    cw, ch = _kb_canvas(w, h)
    z = f"(1+{amt}*min(1,T/{dur:.3f}))"
    gx = f"X/{z}+(1-1/{z})*W/2"
    gy = f"Y/{z}+(1-1/{z})*H/2"
    return (f"setsar=1,scale={cw}:{ch}:force_original_aspect_ratio=increase,"
            f"crop={cw}:{ch},format=yuv420p,"
            f"geq=lum='p({gx},{gy})':cb='p({gx},{gy})':cr='p({gx},{gy})',"
            f"scale={w}:{h}:flags=lanczos")


def _kb_render(ep, b, w, h, fps):
    """Bake a beat's push/zoom move to a cached clip (geq is too slow to run on
    every render). Keyed by file+mtime+move+dur+resolution — a dur or asset
    change re-renders just that beat. Works on a looped still, or — for a
    `cita` beat (brain/20 §4.3: every moving excerpt gets a push/reframe move)
    — a short video clip played once; a `cita` bake also overlays the
    case-file device (brain/03) in the same pass. Returns the clip Path, or
    None on failure."""
    import hashlib
    src = ep / b["file"]
    if not src.exists():
        return None
    is_video = src.suffix.lower() in (".mp4", ".mov", ".webm")
    is_cita = b["kind"] == "cita"
    mv = _still_move(b, w, h)
    dur = max(0.4, b["out"] - b["in"])
    card = None
    if is_cita:
        meta = _cite_meta(ep).get(str(_idn(b.get("id"))), {})
        card = _cite_card(ep, meta.get("obra", "?"), meta.get("año", "?"), meta.get("dist", ""), w, h)
    try:
        mt = int(src.stat().st_mtime)
    except OSError:
        mt = 0
    key = hashlib.sha1(
        f"{b['file']}|{mt}|{mv}|{round(dur, 2)}|{w}x{h}|{card.name if card else ''}|geq2"
        .encode("utf-8")
    ).hexdigest()[:12]
    cache = ep / "assets" / "_kb" / f"kb_{key}.mp4"
    # a good cache entry is a real clip roughly the beat's length (a killed bake
    # leaves a stub / truncated file — re-render it)
    if cache.exists() and cache.stat().st_size > 4096 and abs(_duration(cache) - dur) < 0.3:
        return cache
    cache.unlink(missing_ok=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    proxy = w <= 1920
    src_args = (["-t", f"{dur:.3f}", "-i", str(src)] if is_video else
                ["-loop", "1", "-framerate", str(fps), "-t", f"{dur:.3f}", "-i", str(src)])
    zoom_vf = _geq_zoom_vf(mv, w, h, dur) + f",fps={fps},format=yuv420p"
    if card:
        cmd = [FFMPEG, "-y", *src_args, "-loop", "1", "-i", str(card), "-an",
               "-filter_complex",
               f"[0:v]{zoom_vf}[base];[base][1:v]overlay=0:0:shortest=1,format=yuv420p[vout]",
               "-map", "[vout]",
               "-c:v", "libx264", "-preset", "veryfast" if proxy else "slow",
               "-crf", "20" if proxy else "16", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", str(cache)]
    else:
        cmd = [FFMPEG, "-y", *src_args, "-an",
               "-vf", zoom_vf,
               "-c:v", "libx264", "-preset", "veryfast" if proxy else "slow",
               "-crf", "20" if proxy else "16", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", str(cache)]
    print(f"  ken burns  {b['id']} ({mv} {dur:.1f}s{' + expediente' if card else ''}) → assets/_kb/{cache.name} …")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0 or not cache.exists() or abs(_duration(cache) - dur) > 0.3:
        print(f"  ⚠ geq falló para {b['id']}: {(r.stderr or r.stdout)[-200:]}")
        cache.unlink(missing_ok=True)
        return None
    return cache


def _clip_filter(i, b, w, h, fps, mv=None):
    """A panning still -> a [vN] stream that FILLS WxH (no letterbox), animated
    over `t` on a real frame stream. `crop` — fixed WxH window, moving x/y —
    keeps the aspect and never jitters. (push/zoom go through _kb_render.)"""
    d = max(0.4, b["out"] - b["in"])
    mv = mv or _still_move(b, w, h)
    fill = f"[{i}:v]setsar=1,scale={w}:{h}:force_original_aspect_ratio=increase"
    if mv == "pan-v":       # hold width, travel the tall overflow top→bottom
        f = f"{fill},crop={w}:{h}:x='(iw-{w})/2':y='(ih-{h})*min(1,t/{d:.3f})'"
    elif mv == "pan-h":     # hold height, travel the wide overflow left→right
        f = f"{fill},crop={w}:{h}:x='(iw-{w})*min(1,t/{d:.3f})':y='(ih-{h})/2'"
    elif mv in ("push", "zoom"):     # fallback if _kb_render failed — inline geq
        f = f"[{i}:v]{_geq_zoom_vf(mv, w, h, d)}"
    else:                   # cut — hard hold, centred, no move
        f = f"{fill},crop={w}:{h}:x='(iw-{w})/2':y='(ih-{h})/2'"
    return f + f",trim=duration={d:.3f},setpts=PTS-STARTPTS,setsar=1,fps={fps},format=yuv420p[v{i}]"


def _video_hold_filter(i, p, dur, w, h, fps):
    """Plain scale-crop-play-straight treatment for a video clip — no zoompan.
    Speeds a clip up a touch to fit when it's a bit shorter than the beat;
    loops only when it's far too short or already long enough. Returns
    (extra `-i` input args, the filter_complex line producing [v{i}])."""
    clip_dur = _duration(p)
    ratio = (dur / clip_dur) if clip_dur > 0.1 else 1.0
    base = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1"
    if 1.03 < ratio <= 2.6:
        return (["-i", str(p)],
                f"[{i}:v]{base},setpts={ratio:.4f}*PTS,fps={fps},"
                f"trim=duration={dur:.3f},setpts=PTS-STARTPTS[v{i}]")
    return (["-stream_loop", "-1", "-t", f"{dur:.3f}", "-i", str(p)],
            f"[{i}:v]{base},fps={fps},trim=duration={dur:.3f},"
            f"setpts=PTS-STARTPTS[v{i}]")


CHUNK_BEATS = 10                # beats per ffmpeg run in the 4K master (see render())


def _render_chunked(ep, slug, data, beats, build, video_fc, limited, audio, x264, out, prog, fps, w, h, lut, dry):
    """4K master as: video in runs of CHUNK_BEATS beats (each encoded once, kept), the voice + music mix as one
    small audio file, then a stream-copy mux. Same picture and sound as the single-pass graph, but memory stays
    at a few GB and a finished run survives a crash, a sleep or a cancel (relaunch = skip what is done)."""
    import hashlib
    import os
    import threading
    import time
    chunks = [beats[k:k + CHUNK_BEATS] for k in range(0, len(beats), CHUNK_BEATS)]
    cdir = ep / "_chunks"

    def chunk_key(chunk):
        parts = []
        for b in chunk:
            f = b.get("file")
            st = (ep / f).stat() if f and (ep / f).exists() else None
            parts.append([f, b.get("kind"), round(b["in"], 3), round(b["out"], 3), b.get("motion"), b.get("label"),
                          b.get("aspect"), (st.st_size, int(st.st_mtime)) if st else None])
        parts.append([w, h, fps, lut, x264])
        return hashlib.sha1(json.dumps(parts, default=str).encode("utf-8")).hexdigest()[:10]

    plan = [(k, c, cdir / f"part_{k:02d}_{chunk_key(c)}.mp4") for k, c in enumerate(chunks)]
    if dry:
        print(f"4K master en {len(chunks)} tandas de <= {CHUNK_BEATS} beats + audio aparte + mux; "
              f"hechas ya: {sum(1 for _, _, pth in plan if pth.exists())}")
        return
    cdir.mkdir(exist_ok=True)
    for old in cdir.glob("part_*.mp4"):                    # runs of an older edit of the timeline
        if old not in {pth for _, _, pth in plan}:
            old.unlink(missing_ok=True)
    total = float(data.get("total") or beats[-1]["out"])
    print(f"render 4K master · {len(beats)} beats en {len(chunks)} tandas …")
    done_s = 0.0
    for k, chunk, part in plan:
        span = max(0.0, chunk[-1]["out"] - chunk[0]["in"])
        if part.exists() and part.stat().st_size > 0 and _duration(part) > 0:
            print(f"  tanda {k + 1}/{len(chunks)} ya hecha ({part.name})")
            done_s += span
            continue
        inp, flt, vm = build(chunk)
        cmd = [FFMPEG, "-y", "-filter_complex_threads", "2", *limited(inp),
               "-filter_complex", video_fc(flt, vm, len(chunk)), "-map", "[vout]", "-r", str(fps), *x264, "-an",
               "-progress", str(cdir / "chunk.progress"), "-stats_period", "2", "-f", "mp4", str(part) + ".tmp"]
        # the room's bar reads the master's own progress file: mirror this run's clock + the finished runs'
        stop = threading.Event()

        def mirror(base=done_s):
            cp = cdir / "chunk.progress"
            while not stop.is_set():
                try:
                    us = re.findall(r"out_time_us=(\d+)", cp.read_text(encoding="utf-8", errors="replace"))
                    cur = int(us[-1]) / 1e6 if us else 0.0
                    prog.write_text(f"out_time_us={int((base + cur) * 1e6)}\nprogress=continue\n", encoding="utf-8")
                except (OSError, ValueError):
                    pass
                stop.wait(2.0)

        th = threading.Thread(target=mirror, daemon=True)
        th.start()
        t0_ = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        stop.set()
        tmp = Path(str(part) + ".tmp")
        if r.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
            tmp.unlink(missing_ok=True)
            print(f"FALLO ffmpeg (tanda {k + 1}/{len(chunks)}):\n" + "\n".join(r.stderr.strip().splitlines()[-6:]))
            sys.exit(1)
        os.replace(tmp, part)
        done_s += span
        print(f"  tanda {k + 1}/{len(chunks)} hecha en {(time.time() - t0_) / 60:.1f} min  ({part.stat().st_size // (1024 * 1024)} MB)")

    # voice + music: one small file
    audio_f = cdir / "audio.m4a"
    ain, fca, amap = audio(0)
    if amap:
        acmd = [FFMPEG, "-y", *ain, "-filter_complex", fca.lstrip(";"), *amap, "-c:a", "aac", "-b:a", "320k", str(audio_f)]
        print("  mezcla de audio …")
        r = subprocess.run(acmd, capture_output=True, text=True, cwd=ROOT)
        if r.returncode != 0 or not audio_f.exists():
            print("FALLO ffmpeg (audio):\n" + "\n".join(r.stderr.strip().splitlines()[-6:]))
            sys.exit(1)
    lst = cdir / "parts.txt"
    lst.write_text("".join(f"file '{pth.as_posix()}'\n" for _, _, pth in plan), encoding="utf-8")
    tmp_out = Path(str(out) + ".part")
    mux = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(lst)]
    if amap:
        mux += ["-i", str(audio_f), "-map", "0:v", "-map", "1:a"]
    mux += ["-c", "copy", "-movflags", "+faststart", "-f", "mp4", str(tmp_out)]
    print("  uniendo tandas + audio …")
    r = subprocess.run(mux, capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0 or not tmp_out.exists() or tmp_out.stat().st_size == 0:
        tmp_out.unlink(missing_ok=True)
        print("FALLO ffmpeg (mux):\n" + "\n".join(r.stderr.strip().splitlines()[-6:]))
        sys.exit(1)
    os.replace(tmp_out, out)
    prog.unlink(missing_ok=True)
    print(f"escrito  episodes/{slug}/{out.name}  ({out.stat().st_size // (1024 * 1024)} MB)")
    hf = ep / "_exports" / "09-final-hash.txt"
    hf.parent.mkdir(parents=True, exist_ok=True)
    hf.write_text(P.timeline_content_hash(data), encoding="utf-8")
    shutil.rmtree(cdir, ignore_errors=True)                # the master is done: free the intermediates


def render(slug, mode, t0=None, t1=None, dry=False):
    ep = EP_DIR / slug
    tj = ep / "09-timeline.json"
    if not tj.exists():
        build_timeline(slug)
    data = json.loads(tj.read_text(encoding="utf-8"))
    beats = [b for b in data["beats"]
             if (t0 is None or b["out"] > t0) and (t1 is None or b["in"] < t1)]
    if not beats:
        raise SystemExit("nada que renderizar en ese rango")
    proxy = mode != "final"
    w, h = (1280, 720) if proxy else (data["w"], data["h"])
    fps = data["fps"]

    take_path = _the_take(ep)
    take_dur = _duration(take_path) if take_path else 0.0

    def _build(sub):
        """ffmpeg input args, per-beat filter lines and [vN] labels for a run of beats (index = position in `sub`)."""
        inputs, filters, vmaps = [], [], []
        for i, b in enumerate(sub):
            f = b.get("file")
            # an A-roll beat whose window falls past the end of the trimmed take
            # (timeline / take out of sync) -> black, never a fatal seek-past-EOF
            acamara_ok = b["kind"] in ACAMARA and f and (ep / f).exists() and (
                take_dur == 0.0 or b["in"] < take_dur - 0.2)
            dur = max(0.4, b["out"] - b["in"])
            card = _negro_card(b["label"], ep) if (b["kind"] == "negro" and b.get("label")) else None
            if card:
                # a black slate with the beat's rótulo burned in
                inputs += ["-loop", "1", "-t", f"{dur:.3f}", "-i", str(card)]
                filters.append(
                    f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
                    f"crop={w}:{h},setsar=1,fps={fps},trim=duration={dur:.3f},"
                    f"setpts=PTS-STARTPTS[v{i}]")
            elif b["kind"] == "negro" or not f or (b["kind"] in ACAMARA and not acamara_ok):
                if b["kind"] in ACAMARA:
                    if f and not (ep / f).exists():
                        print(f"  beat {b.get('n', b.get('id'))}: a cámara pero la toma recortada aún no está renderizada → negro")
                    else:
                        print(f"  beat {b.get('n', b.get('id'))}: a cámara pero in={b['in']:.1f}s > toma {take_dur:.1f}s → negro")
                inputs += ["-f", "lavfi", "-t", f"{dur:.3f}",
                           "-i", f"color=c={GROUND}:s={w}x{h}:r={fps}"]
                filters.append(f"[{i}:v]trim=duration={dur:.3f},"
                               f"setpts=PTS-STARTPTS[v{i}]")
            elif b["kind"] in ACAMARA:
                # A-roll: show the narrator take for this beat's slot. The beat's
                # in/out are already on the VO-spine timeline; for a single take
                # (offset 0) that is the take's own time, so trim it there.
                p = ep / f
                d = max(0.4, b["out"] - b["in"])
                if take_dur:
                    d = min(d, take_dur - b["in"])
                inputs += ["-ss", f'{b["in"]:.3f}', "-t", f'{d:.3f}', "-i", str(p)]
                filters.append(
                    f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
                    f"crop={w}:{h},setsar=1,fps={fps},trim=duration={d:.3f},"
                    f"setpts=PTS-STARTPTS[v{i}]")
            else:
                p = ep / f
                if p.suffix.lower() in STILL_EXT:
                    mv = _still_move(b, w, h)
                    kb = _kb_render(ep, b, w, h, fps) if mv in ("push", "zoom") else None
                    if kb:                          # pre-baked geq zoom → just normalise it
                        inputs += ["-i", str(kb)]
                        filters.append(
                            f"[{i}:v]scale={w}:{h},setsar=1,fps={fps},"
                            f"trim=duration={dur:.3f},setpts=PTS-STARTPTS,format=yuv420p[v{i}]")
                    else:                           # pan/cut, or geq failed → animate inline
                        inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{dur:.3f}", "-i", str(p)]
                        filters.append(_clip_filter(i, b, w, h, fps, mv))
                elif b["kind"] == "cita":
                    # brain/20 §4.3 — every moving excerpt gets a push/reframe move
                    # + the case-file device, baked together in one pass.
                    mv = _still_move(b, w, h)
                    kb = _kb_render(ep, b, w, h, fps) if mv in ("push", "zoom") else None
                    if kb:
                        inputs += ["-i", str(kb)]
                        filters.append(
                            f"[{i}:v]scale={w}:{h},setsar=1,fps={fps},"
                            f"trim=duration={dur:.3f},setpts=PTS-STARTPTS,format=yuv420p[v{i}]")
                    else:                           # bake failed → plain hold, never crash the render
                        extra, flt = _video_hold_filter(i, p, dur, w, h, fps)
                        inputs += extra
                        filters.append(flt)
                else:
                    # video B-roll: scale-crop to frame, play it straight — NO zoompan
                    # (that would explode the frame count). If the clip is a bit
                    # SHORTER than the beat, slow it to fit (nicer than a visible
                    # loop); only loop when it's far too short or long enough already.
                    extra, flt = _video_hold_filter(i, p, dur, w, h, fps)
                    inputs += extra
                    filters.append(flt)
            vmaps.append(f"[v{i}]")
        return inputs, filters, vmaps


    vo = next(iter(sorted(ep.glob("assets/*.trimmed.mp4"))), None)
    # house grade (brain/03) — opt-in and **only on the 4K master**. The proxy
    # skips it (the edit page is tagged "sin grade"); lut3d per frame roughly
    # doubles a slow proxy render for a look you check once.
    grade = ROOT / "brand" / "assets" / "grade.cube"
    lut = f"lut3d={grade.relative_to(ROOT).as_posix()}," if (grade.exists() and not proxy) else ""

    def _video_fc(filters, vmaps, n):
        return (";\n".join(filters) + ";\n" + "".join(vmaps) + f"concat=n={n}:v=1:a=0[vraw];"
                + f"[vraw]{lut}format=yuv420p[vout]")

    def _limited(inputs):
        """One decode thread per input. ffmpeg gives every decoder one thread PER CPU CORE and each thread
        holds 4K frames: with ~100 inputs that exhausted RAM + the page file («Cannot allocate memory -12»
        at frame 0, E002's 4K master, 15.7 GB laptop)."""
        out = []
        for a in inputs:
            if a == "-i":
                out += ["-threads", "1"]
            out.append(a)
        return out

    def _audio(vo_idx):
        """(input args, filter_complex fragment starting with ';', map args) — voice trim/gain + music bed
        ducked under the voice. `vo_idx` = index the voice input will have in the command."""
        ain, fca, amap = [], "", []
        if vo:
            ain += ["-i", str(vo)]
            # a region render (--preview) must trim the VO to that window, or ffmpeg
            # keeps encoding until the full-length audio ends (a 30 s clip + 16 min)
            region = t0 is not None or t1 is not None
            va = f"[{vo_idx}:a]"
            if region:
                fca += (f";[{vo_idx}:a]atrim=start={t0 or 0:.3f}"
                        + (f":end={t1:.3f}" if t1 else "") + ",asetpts=PTS-STARTPTS[voa]")
                va = "[voa]"
            mus = data["music"]
            vg = float(mus.get("vo_gain_db", 0) or 0)
            if vg:                                      # voice trim, before the mix + sidechain
                fca += f";{va}volume={vg:+.1f}dB[vog]"
                va = "[vog]"
            tracks = [t for t in (mus.get("tracks") or ([mus["bed"]] if mus.get("bed") else []))
                      if t and (ROOT / t).exists()]
            if tracks and not proxy:
                duck = max(0.0, float(mus.get("duck_db", 8) or 8))
                ratio = max(2.0, min(12.0, 2.0 + duck / 2.0))   # 0 dB → gentle, 18 dB → hard
                base = vo_idx + 1
                for t in tracks:
                    ain += ["-i", str(ROOT / t)]
                # normalize every track to the same format first — concat refuses
                # mismatched sample rate/layout, and a jamendo/pixabay/own-file mix
                # is exactly the case where that happens.
                for i in range(len(tracks)):
                    fca += (f";[{base+i}:a]aformat=sample_fmts=fltp:sample_rates=48000:"
                            f"channel_layouts=stereo[mt{i}]")
                if len(tracks) > 1:
                    # several picks: play them back-to-back once, then loop that
                    # whole sequence — a single track loops on its own instead.
                    seq = "".join(f"[mt{i}]" for i in range(len(tracks)))
                    fca += f";{seq}concat=n={len(tracks)}:v=0:a=1[mseq]"
                    loop_src = "[mseq]"
                else:
                    loop_src = "[mt0]"
                # The voice feeds BOTH the sidechain key and the mix. An input stream ([98:a]) can be read
                # twice, but a filter OUTPUT label ([vog] — the voice with its gain — or [voa]) can be consumed
                # only once: with vo_gain_db != 0 ffmpeg read the second use as a stream specifier and aborted
                # with «Stream specifier 'vog' … matches no streams» (E002's 4K master, after 9 h of clips).
                va_sc = va_mx = va
                if not va.split(":")[0].strip("[").isdigit():           # a filter-output label → split it
                    fca += f";{va}asplit=2[vasc][vamx]"
                    va_sc, va_mx = "[vasc]", "[vamx]"
                fca += (f";{loop_src}aloop=loop=-1:size=2e9,volume={mus.get('bed_db', -30)}dB[bed];"
                        f"[bed]{va_sc}sidechaincompress=threshold=0.03:ratio={ratio:.1f}:release=400[ducked];"
                        f"{va_mx}[ducked]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1[aout]")
                amap = ["-map", "[aout]"]
            else:
                fca += f";{va}loudnorm=I=-14:TP=-1[aout]"
                amap = ["-map", "[aout]"]
        return ain, fca, amap

    X264 = ["-c:v", "libx264", "-preset", "veryfast" if proxy else "slow", "-crf", "26" if proxy else "17",
            "-threads", str(cpu_threads()), "-pix_fmt", "yuv420p"]
    out = ep / ("09-rough.mp4" if proxy else _master_name(ep, slug))
    prog = ep / ("09-rough.progress" if proxy else "09-final.progress")
    full = t0 is None and t1 is None

    # ── the 4K master, in runs of beats ──────────────────────────────────────
    # One ffmpeg with ~100 inputs keeps a decoder + queued 4K frames open for EVERY beat at once (measured on
    # E002: 10.5 GB resident / 24 GB committed on a 15.7 GB laptop — the system was unusable and it failed
    # twice). A run of CHUNK_BEATS beats needs a few GB, and a finished run is kept, so a crash / sleep /
    # cancel resumes where it stopped instead of starting the whole encode again.
    if (not proxy) and full and len(beats) > CHUNK_BEATS:
        return _render_chunked(ep, slug, data, beats, _build, _video_fc, _limited, _audio, X264, out, prog,
                               fps, w, h, lut, dry)

    inputs, filters, vmaps = _build(beats)
    fc = _video_fc(filters, vmaps, len(beats))
    if not proxy:
        inputs = _limited(inputs)
    n_in = sum(1 for a in inputs if a == "-i")
    cmd = [FFMPEG, "-y", *(["-filter_complex_threads", "2"] if not proxy else []), *inputs]
    ain, fca, a_map = _audio(n_in)
    cmd += ain
    fc += fca

    cmd += ["-filter_complex", fc, "-map", "[vout]", *a_map, "-r", str(fps), *X264]
    if a_map:
        cmd += ["-c:a", "aac", "-b:a", "256k" if proxy else "320k"]

    # ffmpeg -progress: a key=value stream the edit room polls for the bar.
    # Only for a full render — a region (--preview) is too quick to bother.
    # (Don't pre-delete it — serve.py seeds it at out_time_us=0 so the bar has
    # something to read in the gap before ffmpeg starts writing.)
    if not dry and full:
        cmd += ["-progress", str(prog), "-stats_period", "1"]
    cmd.append(str(out))

    if dry:
        print(" \\\n  ".join(cmd))
        return
    print(f"render {'720p proxy' if proxy else '4K master'} · {len(beats)} beats"
          + (f" · {_fmt(t0 or 0)}–{_fmt(t1 or data['total'])}" if (t0 or t1) else "") + " …")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    prog.unlink(missing_ok=True)
    if r.returncode != 0 or not out.exists():
        print("FALLO ffmpeg:\n" + "\n".join(r.stderr.strip().splitlines()[-6:]))
        sys.exit(1)
    print(f"escrito  episodes/{slug}/{out.name}  ({out.stat().st_size // (1024*1024)} MB)")
    if not proxy:
        # stamp what got rendered so advance.py's Stage-9 fold can tell a real
        # edit apart from the timeline's mtime just moving (autosave on open).
        hf = ep / "_exports" / "09-final-hash.txt"
        hf.parent.mkdir(parents=True, exist_ok=True)
        hf.write_text(P.timeline_content_hash(data), encoding="utf-8")


def _master_name(ep, slug):
    n = 1 + len(list(ep.glob(f"{slug[:4]}-*-v*.mp4")))
    return f"{slug}-v{n}.mp4"


# ── CLI ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    slug = a[0]
    dry = "--dry" in a
    if any(x in a for x in ("--final", "--rough", "--preview")):
        lower_priority()          # a long render must not make the laptop sluggish (children inherit it)
    if "--preview" in a:
        i = a.index("--preview")
        render(slug, "proxy", float(a[i + 1]), float(a[i + 2]), dry)
    elif "--reseed" in a:             # force re-seed from the spine — DISCARDS edits
        seed_timeline(slug, force=True)
    elif "--seed" in a:               # seed once; no-op if a schema-2 line already exists
        seed_timeline(slug, force=False)
    elif "--resync" in a:             # 3-way merge a schema-2 line onto a re-recorded VO
        resync_timeline(slug)
    elif "--final" in a:
        with keep_awake():                # the whole thing: waiting for / running the 4K trim is
            ensure_trimmed(slug)          # as long as the render and slept through 3 h once
            build_timeline(slug)
            render(slug, "final", dry=dry)
    elif "--rough" in a:
        with keep_awake():
            ensure_trimmed(slug)
            build_timeline(slug)
            waveform(slug)
            render(slug, "proxy", dry=dry)
    elif "--wave" in a:               # refresh only 09-wave.b64 (+ proxies) — no timeline rebuild
        waveform(slug)
    elif "--timeline-only" in a:      # rebuild 09-timeline.json in place (edit-room saves)
        rebuild_timeline(slug)
    else:
        build_timeline(slug)
        waveform(slug)
