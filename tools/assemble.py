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
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mediabin import FFMPEG, FFPROBE  # noqa: E402

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
ASSET_SUBDIRS = ("kb", "stock", "video", "intro", "archive", "ai", "graphic", "thumb")
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
    for sub in ASSET_SUBDIRS:
        d = ep / "assets" / sub
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if f.is_file() and f.suffix.lower() in MEDIA_EXT:
                idx.setdefault(f.stem, f)
                idx.setdefault(f.name, f)
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


def _the_take(ep):
    """The single trimmed narrator take (A-roll source). Multi-take A-roll isn't
    supported yet — returns the first one and the caller warns."""
    takes = sorted(ep.glob("assets/*.trimmed.mp4"))
    return takes[0] if takes else None


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


def resolve(ep, beats):
    idx = _asset_index(ep)
    take = _the_take(ep)
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
    """The authoritative VO length for a schema-2 timeline. Stored at seed/resync
    time; only recomputed from the word list when absent."""
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


def _anchors(items, toks, words, ref_end, vo_end):
    """Confident (ref_time, vo_time) knots for a piecewise-linear time remap.
    `items` = [(ref_time, anchor_text), ...] in order — the anchor text is
    fuzzy-matched against the word stream near where its ref_time would fall.
    Used by align() (ref = shotlist planned time, text = frag) and by
    resync_timeline() (ref = the beat's current `in`, text = its vo_anchor)."""
    anchors = [(0.0, 0.0)]
    cursor = 0
    for ref_t, raw in items:
        raw = (raw or "").strip()
        frag = [t for t in _norm(raw).split() if t]
        if _stage_dir(raw) or len(frag) < 4:
            continue
        exp = int(ref_t / ref_end * len(toks)) if ref_end else 0
        best, best_i = 0, exp
        for i in range(max(cursor, exp - 80), min(len(toks) - 1, exp + 200)):
            score = sum(1 for k, ft in enumerate(frag[:6]) if i + k < len(toks) and toks[i + k] == ft)
            if score > best:
                best, best_i = score, i
        if best >= 4 or best == min(6, len(frag)):
            vt = round(words[best_i]["t"], 2)
            pgap = ref_t - anchors[-1][0]          # ref distance since the last anchor
            vgap = vt - anchors[-1][1]             # VO distance the match implies
            # accept only if the match lands plausibly: no backwards pull, and the
            # run since the last anchor isn't compressed/stretched past 0.35×–2.6×.
            if pgap > 0 and vgap > 0.5 and vgap > 0.35 * pgap and vgap < 2.6 * pgap:
                anchors.append((ref_t, vt))
                cursor = best_i + len(frag)
    anchors.append((ref_end, vo_end))
    return anchors


def _remap_fn(anchors, vo_end):
    def remap(pt):
        for (p0, v0), (p1, v1) in zip(anchors, anchors[1:]):
            if pt <= p1 or (p1, v1) == anchors[-1]:
                f = (pt - p0) / (p1 - p0) if p1 > p0 else 0.0
                return v0 + f * (v1 - v0)
        return vo_end
    return remap


def align(beats, words):
    """Anchor the shotlist's planned timeline to the real VO — piecewise-linearly
    remap planned times onto VO time between the beats whose frag matches the
    voice confidently. Runs once, at seed."""
    beats.sort(key=lambda x: x["n"])
    if not words:
        return beats, round(beats[-1]["out"], 2) if beats else 0.0
    toks = [_norm(w["w"]) for w in words]
    vo_end = _vo_end_from_words(words)
    planned_end = beats[-1]["out"] or vo_end
    anchors = _anchors([(b["in"], b.get("frag")) for b in beats], toks, words, planned_end, vo_end)
    remap = _remap_fn(anchors, vo_end)

    for b in beats:
        b["in"] = round(remap(b["in"]), 2)
        b["out"] = round(remap(b["out"]), 2)
    for a, nb in zip(beats, beats[1:]):
        a["out"] = round(max(a["in"] + 0.6, nb["in"]), 2)
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
            if not aroll_keep and not graphic_keep and (dur < floor or (same_file and not promise_pay)):
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
            b["motion"] = "cut"
    return beats


def _music_block(prev_music, beats, total):
    _mrange = {"bed_db": (-48, -6), "vo_gain_db": (-8, 8), "duck_db": (0, 20)}
    mix = {k: prev_music[k] for k in _mrange
           if isinstance(prev_music.get(k), (int, float)) and _mrange[k][0] <= prev_music[k] <= _mrange[k][1]}
    pool = music_pool()
    return {"pool": pool, "bed": prev_music.get("bed") or (pool or [""])[0],
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
    beats, total = align(beats, words)          # tidy_subfloor + flag_rhythm run inside
    if not words:
        total = round(beats[-1]["out"], 2)
    _derive_motion(beats)

    if SCHEMA_CURRENT < 2:
        # legacy shape — the seed still writes a derived timeline until the
        # migration commit flips SCHEMA_CURRENT to 2
        data = {"ep": slug[:4], "slug": slug, "generated": _now(), "schema": 1,
                "aligned": bool(words), "fps": FPS, "w": 3840, "h": 2160,
                "total": total, "ground": GROUND,
                "music": _music_block({}, beats, total), "beats": beats}
        tj.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        _report(slug, beats, total, bool(words))
        return data

    vo_end = round(_vo_end_from_words(words), 2) if words else round(total, 2)
    ab = to_authored_beats(beats, vo_end)
    derive_times(ab, vo_end)              # write canonical (cumsum) in/out, not align's
    total = round(ab[-1]["out"], 2) if ab else total
    data = authored_doc(slug, ab, vo_end=vo_end, total=total,
                        words_sig=_words_sig(words), aligned=bool(words),
                        music=_music_block({}, ab, total))
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
        "music": _music_block(data.get("music", {}), ab, total),
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
        "music": _music_block(prev_music, beats, total),
        "beats": beats,
    }
    tj.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    _report(slug, beats, total, bool(words))
    return data


def resync_timeline(slug):
    """Re-fit a schema-2 timeline to a re-recorded / re-trimmed VO (brain/16).
    3-way merge: a beat the editor set the duration of (`dur_edited`) keeps its
    `dur`; every other beat is re-fitted to the new voice by remapping its
    current start through its `vo_anchor`. Only fires on «Re-sincronizar»."""
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
    old_total = beats[-1]["out"]
    toks = [_norm(w["w"]) for w in new_words]
    anchors = _anchors([(b["in"], b.get("vo_anchor")) for b in beats],
                       toks, new_words, old_total, new_vo_end)
    remap = _remap_fn(anchors, new_vo_end)
    prop_in = [round(remap(b["in"]), 3) for b in beats] + [round(new_vo_end, 3)]

    kept = refit = 0
    for i, b in enumerate(beats):
        if b.get("dur_edited"):
            kept += 1
            continue
        fl = (MIN_ACAMARA if b["kind"] in ACAMARA
              else MIN_GRAPHIC if b["kind"] in GRAPHIC else MIN_BEAT)
        b["dur"] = round(max(fl, prop_in[i + 1] - prop_in[i]), 3)
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
    data["music"] = _music_block(data.get("music", {}), ab, data["total"])
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
    vo = next(iter(sorted(ep.glob("assets/*.trimmed.mp4"))), None)
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


def _clip_filter(i, b, w, h, fps):
    """One beat -> a [vN] stream that FILLS WxH (no letterbox) with its move.
    All moves use ONE `zoompan` on a single still — NO `fps` filter before it
    (that would feed zoompan N frames and it emits d per frame → d*N frames,
    a 15 min video rendered as 60 min: the bug that was here)."""
    d = max(0.4, b["out"] - b["in"])
    fr = max(1, int(round(d * fps)))
    mv = kb_move(b, w, h)
    src = f"[{i}:v]setsar=1"
    # scale so the still at least fills the frame; `increase` = one dim overflows
    fillbig = f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase"
    fill = f"scale={w}:{h}:force_original_aspect_ratio=increase"
    zp = f"d={fr}:s={w}x{h}:fps={fps}"
    if mv == "pan-v":       # travel the tall overflow top→bottom
        f = (f"{src},{fill},zoompan=z=1:{zp}:x='(iw-{w})/2':y='(ih-{h})*on/{max(1,fr-1)}'")
    elif mv == "pan-h":     # travel the wide overflow left→right
        f = (f"{src},{fill},zoompan=z=1:{zp}:x='(iw-{w})*on/{max(1,fr-1)}':y='(ih-{h})/2'")
    elif mv == "zoom":      # push harder, to a detail
        f = (f"{src},{fillbig},crop={w * 2}:{h * 2},zoompan="
             f"z='min(zoom+0.0016,1.20)':{zp}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'")
    elif mv == "cut":       # hard hold, fills the frame, no move
        f = (f"{src},{fill},crop={w}:{h},zoompan=z=1:{zp}:x=0:y=0")
    else:                   # push (default) — slow zoom-in
        f = (f"{src},{fillbig},crop={w * 2}:{h * 2},zoompan="
             f"z='min(zoom+0.0008,1.10)':{zp}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'")
    # concat needs every segment identical: square pixels + fixed size + fps
    return f + f",trim=duration={d:.3f},setpts=PTS-STARTPTS,setsar=1,fps={fps}[v{i}]"


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

    inputs, filters, vmaps = [], [], []
    for i, b in enumerate(beats):
        f = b.get("file")
        # an A-roll beat whose window falls past the end of the trimmed take
        # (timeline / take out of sync) -> black, never a fatal seek-past-EOF
        acamara_ok = b["kind"] in ACAMARA and f and (
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
                inputs += ["-loop", "1", "-t", f"{dur:.3f}", "-i", str(p)]
                filters.append(_clip_filter(i, b, w, h, fps))
            else:
                # video B-roll: scale-crop to frame, play it straight — NO zoompan
                # (that would explode the frame count). If the clip is a bit
                # SHORTER than the beat, slow it to fit (nicer than a visible
                # loop); only loop when it's far too short or long enough already.
                clip_dur = _duration(p)
                ratio = (dur / clip_dur) if clip_dur > 0.1 else 1.0
                base = (f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
                        f"crop={w}:{h},setsar=1")
                if 1.03 < ratio <= 2.6:
                    inputs += ["-i", str(p)]
                    filters.append(
                        f"{base},setpts={ratio:.4f}*PTS,fps={fps},"
                        f"trim=duration={dur:.3f},setpts=PTS-STARTPTS[v{i}]")
                else:
                    inputs += ["-stream_loop", "-1", "-t", f"{dur:.3f}", "-i", str(p)]
                    filters.append(
                        f"{base},fps={fps},trim=duration={dur:.3f},"
                        f"setpts=PTS-STARTPTS[v{i}]")
        vmaps.append(f"[v{i}]")

    vo = next(iter(sorted(ep.glob("assets/*.trimmed.mp4"))), None)
    fc = ";\n".join(filters) + ";\n" + "".join(vmaps) + f"concat=n={len(beats)}:v=1:a=0[vraw];"
    # house grade (brain/03) — opt-in and **only on the 4K master**. The proxy
    # skips it (the edit page is tagged "sin grade"); lut3d per frame roughly
    # doubles a slow proxy render for a look you check once.
    grade = ROOT / "brand" / "assets" / "grade.cube"
    lut = f"lut3d={grade.relative_to(ROOT).as_posix()}," if (grade.exists() and not proxy) else ""
    fc += f"[vraw]{lut}format=yuv420p[vout]"

    cmd = [FFMPEG, "-y", *inputs]
    a_map = []
    if vo:
        cmd += ["-i", str(vo)]
        vo_idx = len(beats)
        # a region render (--preview) must trim the VO to that window, or ffmpeg
        # keeps encoding until the full-length audio ends (a 30 s clip + 16 min)
        region = t0 is not None or t1 is not None
        va = f"[{vo_idx}:a]"
        if region:
            fc += (f";[{vo_idx}:a]atrim=start={t0 or 0:.3f}"
                   + (f":end={t1:.3f}" if t1 else "") + ",asetpts=PTS-STARTPTS[voa]")
            va = "[voa]"
        mus = data["music"]
        vg = float(mus.get("vo_gain_db", 0) or 0)
        if vg:                                      # voice trim, before the mix + sidechain
            fc += f";{va}volume={vg:+.1f}dB[vog]"
            va = "[vog]"
        bed = mus.get("bed")
        if bed and (ROOT / bed).exists() and not proxy:
            duck = max(0.0, float(mus.get("duck_db", 8) or 8))
            ratio = max(2.0, min(12.0, 2.0 + duck / 2.0))   # 0 dB → gentle, 18 dB → hard
            cmd += ["-i", str(ROOT / bed)]
            fc += (f";[{vo_idx+1}:a]aloop=loop=-1:size=2e9,volume={mus.get('bed_db', -30)}dB[bed];"
                   f"[bed]{va}sidechaincompress=threshold=0.03:ratio={ratio:.1f}:release=400[ducked];"
                   f"{va}[ducked]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1[aout]")
            a_map = ["-map", "[aout]"]
        else:
            fc += f";{va}loudnorm=I=-14:TP=-1[aout]"
            a_map = ["-map", "[aout]"]

    cmd += ["-filter_complex", fc, "-map", "[vout]", *a_map,
            "-r", str(fps), "-c:v", "libx264",
            "-preset", "veryfast" if proxy else "slow",
            "-crf", "26" if proxy else "17", "-pix_fmt", "yuv420p"]
    if a_map:
        cmd += ["-c:a", "aac", "-b:a", "256k" if proxy else "320k"]
    out = ep / ("09-rough.mp4" if proxy else _master_name(ep, slug))

    # ffmpeg -progress: a key=value stream the edit room polls for the bar.
    # Only for a full render — a region (--preview) is too quick to bother.
    # (Don't pre-delete it — serve.py seeds it at out_time_us=0 so the bar has
    # something to read in the gap before ffmpeg starts writing.)
    prog = ep / ("09-rough.progress" if proxy else "09-final.progress")
    if not dry and t0 is None and t1 is None:
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
        build_timeline(slug)
        render(slug, "final", dry=dry)
    elif "--rough" in a:
        build_timeline(slug)
        waveform(slug)
        render(slug, "proxy", dry=dry)
    elif "--timeline-only" in a:      # rebuild 09-timeline.json in place (edit-room saves)
        rebuild_timeline(slug)
    else:
        build_timeline(slug)
        waveform(slug)
