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
    return idx


def _the_take(ep):
    """The single trimmed narrator take (A-roll source). Multi-take A-roll isn't
    supported yet — returns the first one and the caller warns."""
    takes = sorted(ep.glob("assets/*.trimmed.mp4"))
    return takes[0] if takes else None


def resolve(ep, beats):
    idx = _asset_index(ep)
    take = _the_take(ep)
    for b in beats:
        if b["kind"] in ACAMARA:
            b["file"] = str(take.relative_to(ep).as_posix()) if take else None
            b["state"] = "ok" if take else "uncovered"
            b["motion"] = "cut"     # live video, never a Ken Burns move
            continue
        if b["kind"] == "negro" or not b["asset"]:
            continue
        hit = idx.get(b["asset"]) or idx.get(b["asset"].split(".")[0])
        if not hit:
            # prefix match: `intro01` -> `intro01_pexelsv_…`, `G4` -> `G4_age_ladder`
            aid = b["asset"].lower()
            hit = next((v for k, v in idx.items()
                        if k.lower() == aid or k.lower().startswith(aid + "_")), None)
        if not hit:
            # downloaded assets are named beatNN_* — try that
            for k, v in idx.items():
                if k.lower().startswith(f"beat{b['n']:02d}_") or k.lower().startswith(f"beat{b['n']}_"):
                    hit = v
                    break
        b["file"] = str(hit.relative_to(ep).as_posix()) if hit else None
        b["state"] = "uncovered" if (not b["file"] and b["kind"] != "negro") else "ok"
    # same-asset reuse: a held shot / PROMISE+PAY that names the same `asset` as a
    # beat that DID resolve borrows that file (assemble aligns times, not files).
    by_asset = {b["asset"]: b["file"] for b in beats if b["asset"] and b["file"]}
    for b in beats:
        if b["state"] == "uncovered" and b["asset"] in by_asset:
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


def align(beats, words):
    """Slide each beat's script fragment along the word stream; set in/out to real VO time."""
    if not words:
        return beats, 0.0
    toks = [_norm(w["w"]) for w in words]
    cursor = 0
    for b in beats:
        b["_al"] = False
        frag = [t for t in _norm(b["frag"]).split() if t]
        if not frag:
            continue
        best, best_i = 0, cursor
        window = range(max(0, cursor - 30), min(len(toks) - 1, cursor + 400))
        for i in window:
            score = sum(1 for k, ft in enumerate(frag[:8]) if i + k < len(toks) and toks[i + k] == ft)
            if score > best:
                best, best_i = score, i
        if best >= 2:
            b["in"] = round(words[best_i]["t"], 2)
            end_i = min(best_i + max(len(frag), 1), len(words) - 1)
            b["out"] = round(words[end_i]["t"], 2)
            b["_al"] = True
            cursor = best_i + len(frag)
    beats.sort(key=lambda x: x["n"])
    vo_end = round(words[-1]["t"] + 0.5, 2)
    # beats that never matched the VO (paraphrased frags — most acamara beats):
    # spread each un-aligned run across the gap between its aligned neighbours,
    # proportional to the shotlist dur. Never let one land past the VO.
    j = 0
    while j < len(beats):
        if beats[j]["_al"]:
            j += 1
            continue
        k = j
        while k < len(beats) and not beats[k]["_al"]:
            k += 1
        t0 = beats[j - 1]["out"] if j else 0.0
        t1 = beats[k]["in"] if k < len(beats) else vo_end
        run = beats[j:k]
        span = max(0.1, t1 - t0)
        wsum = sum(max(0.1, r.get("dur", 4)) for r in run) or len(run)
        acc = t0
        for r in run:
            share = span * max(0.1, r.get("dur", 4)) / wsum
            r["in"], r["out"] = round(acc, 2), round(acc + share, 2)
            acc += share
        j = k
    for a, nb in zip(beats, beats[1:]):
        a["out"] = round(max(a["in"] + 0.6, nb["in"]), 2)
    total = vo_end
    beats[-1]["out"] = total
    for b in beats:
        b.pop("_al", None)
    return beats, total


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


def build_timeline(slug):
    ep = EP_DIR / slug
    if not ep.is_dir():
        raise SystemExit(f"no existe {ep}")
    sl = ep / "06-shotlist.md"
    if not sl.exists():
        raise SystemExit(f"no existe {sl.relative_to(ROOT)} — el Stage 6 no está hecho")
    beats = parse_spine(sl.read_text(encoding="utf-8"))
    resolve(ep, beats)
    words = load_words(ep)
    beats, total = align(beats, words)
    if not words:
        total = round(beats[-1]["out"], 2)

    prev = {}
    tj = ep / "09-timeline.json"
    if tj.exists():
        try:
            for b in json.loads(tj.read_text(encoding="utf-8")).get("beats", []):
                prev[b["n"]] = b
        except json.JSONDecodeError:
            pass
    # keep human decisions across re-builds
    for b in beats:
        p = prev.get(b["n"])
        if p:
            for k in ("approved", "fix", "motion", "asset", "nudge"):
                if p.get(k):
                    b[k] = p[k]
            if p.get("asset") and p["asset"] != b["asset"]:
                b["asset"] = p["asset"]
                resolve(ep, [b])

    data = {
        "ep": slug[:4], "slug": slug, "generated": _now(),
        "aligned": bool(words), "fps": FPS, "w": 3840, "h": 2160,
        "total": total, "ground": GROUND,
        "music": {"pool": music_pool(), "bed": (music_pool() or [""])[0],
                  "in": beats[0]["out"] if beats else 0, "out": total,
                  "duck_db": -5, "bed_db": -22},
        "beats": beats,
    }
    tj.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    n_un = sum(1 for b in beats if b["state"] == "uncovered")
    n_fix = sum(1 for b in beats if b.get("fix"))
    print(f"escrito  episodes/{slug}/09-timeline.json  "
          f"({len(beats)} beats · {_fmt(total)} · "
          f"{'alineado a la voz' if words else 'tiempos del shotlist (sin voz aún)'} · "
          f"{n_un} sin cubrir · {n_fix} con corrección)")
    return data


def _now():
    import datetime
    return datetime.date.today().isoformat()


def _fmt(s):
    s = int(round(s))
    return f"{s // 60:d}:{s % 60:02d}"


# ── waveform ─────────────────────────────────────────────────────────────

def waveform(slug):
    ep = EP_DIR / slug
    vo = next(iter(sorted(ep.glob("assets/*.trimmed.mp4"))), None)
    out = ep / "09-wave.b64"
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

def _clip_filter(i, b, w, h, fps):
    """One beat -> a [vN] stream scaled/padded to WxH on GROUND, with its Ken Burns move."""
    d = max(0.4, b["out"] - b["in"])
    src = f"[{i}:v]"
    base = (f"{src}scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color={GROUND},setsar=1,fps={fps},"
            f"trim=duration={d:.3f},setpts=PTS-STARTPTS")
    mv = b.get("motion", "static")
    if b["kind"] in ("archivo", "ia", "kb", "gráfico") and mv != "cut":
        fr = max(1, int(d * fps))
        if mv == "push":
            base += (f",scale={w*2}:{h*2},zoompan=z='min(zoom+0.0008,1.10)':"
                     f"d={fr}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps={fps}")
        elif mv == "pan-h":
            base += (f",scale={int(w*1.25)}:{h},zoompan=z=1:d={fr}:"
                     f"x='(iw-{w})*on/{fr}':y=0:s={w}x{h}:fps={fps}")
        elif mv == "pan-v":
            base += (f",scale={w}:{int(h*1.25)},zoompan=z=1:d={fr}:"
                     f"x=0:y='(ih-{h})*on/{fr}':s={w}x{h}:fps={fps}")
        elif mv == "zoom":
            base += (f",scale={w*2}:{h*2},zoompan=z='min(zoom+0.0016,1.20)':"
                     f"d={fr}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps={fps}")
    return base + f"[v{i}]"


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
        if b["kind"] == "negro" or not f or (b["kind"] in ACAMARA and not acamara_ok):
            if b["kind"] in ACAMARA:
                print(f"  beat {b['n']}: a cámara pero in={b['in']:.1f}s > toma {take_dur:.1f}s → negro")
            inputs += ["-f", "lavfi", "-t", f'{max(0.4, b["out"]-b["in"]):.3f}',
                       "-i", f"color=c={GROUND}:s={w}x{h}:r={fps}"]
            filters.append(f"[{i}:v]trim=duration={max(0.4,b['out']-b['in']):.3f},"
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
            still = p.suffix.lower() in STILL_EXT
            if still:
                inputs += ["-loop", "1", "-t", f'{max(0.4,b["out"]-b["in"]):.3f}', "-i", str(p)]
            else:
                inputs += ["-i", str(p)]
            filters.append(_clip_filter(i, b, w, h, fps))
        vmaps.append(f"[v{i}]")

    vo = next(iter(sorted(ep.glob("assets/*.trimmed.mp4"))), None)
    fc = ";\n".join(filters) + ";\n" + "".join(vmaps) + f"concat=n={len(beats)}:v=1:a=0[vraw];"
    # house grade (brain/03) — opt-in: applied only if brand/assets/grade.cube exists.
    # ffmpeg splits filter args on ':', so pass the LUT relative and run with cwd=ROOT.
    grade = ROOT / "brand" / "assets" / "grade.cube"
    lut = f"lut3d={grade.relative_to(ROOT).as_posix()}," if grade.exists() else ""
    fc += f"[vraw]{lut}format=yuv420p[vout]"

    cmd = [FFMPEG, "-y", *inputs]
    a_map = []
    if vo:
        cmd += ["-i", str(vo)]
        vo_idx = len(beats)
        bed = data["music"].get("bed")
        if bed and (ROOT / bed).exists() and not proxy:
            cmd += ["-i", str(ROOT / bed)]
            fc += (f";[{vo_idx+1}:a]aloop=loop=-1:size=2e9,volume={data['music']['bed_db']}dB[bed];"
                   f"[bed][{vo_idx}:a]sidechaincompress=threshold=0.02:ratio=6:release=300[ducked];"
                   f"[{vo_idx}:a][ducked]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1[aout]")
            a_map = ["-map", "[aout]"]
        else:
            fc += f";[{vo_idx}:a]loudnorm=I=-14:TP=-1[aout]"
            a_map = ["-map", "[aout]"]

    cmd += ["-filter_complex", fc, "-map", "[vout]", *a_map,
            "-r", str(fps), "-c:v", "libx264",
            "-preset", "veryfast" if proxy else "slow",
            "-crf", "26" if proxy else "17", "-pix_fmt", "yuv420p"]
    if a_map:
        cmd += ["-c:a", "aac", "-b:a", "256k" if proxy else "320k"]
    out = ep / ("09-rough.mp4" if proxy else _master_name(ep, slug))
    cmd.append(str(out))

    if dry:
        print(" \\\n  ".join(cmd))
        return
    print(f"render {'720p proxy' if proxy else '4K master'} · {len(beats)} beats"
          + (f" · {_fmt(t0 or 0)}–{_fmt(t1 or data['total'])}" if (t0 or t1) else "") + " …")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
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
    elif "--final" in a:
        build_timeline(slug)
        render(slug, "final", dry=dry)
    elif "--rough" in a:
        build_timeline(slug)
        waveform(slug)
        render(slug, "proxy", dry=dry)
    else:
        build_timeline(slug)
        waveform(slug)
