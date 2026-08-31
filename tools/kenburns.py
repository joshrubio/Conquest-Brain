#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kenburns.py — orientation-aware Ken Burns for stills (Stage 9, brain/16 move 3).

The move is picked from the image's real aspect ratio vs the 16:9 frame:
  ~16:9  (0.90–1.90)      -> slow push-in 1.00 -> 1.10
  wide panorama (>1.90)   -> horizontal pan across the full width, no zoom
  portrait (<0.90)        -> vertical pan (default top->bottom; --dir up ends high)
  small (long side < frame long side)  -> static, centred on black, no move

Needs ffmpeg on PATH. Output is silent H.264, yuv420p, at channel resolution.

Usage
  python tools/kenburns.py IMAGE --dur 6 [--out OUT.mp4] [--res 1080|4k]
        [--move auto|push|panh|panv|static] [--dir down|up|lr|rl] [--fps 30]

  python tools/kenburns.py E0XX-slug --all [--dur 5] [--res 1080|4k]
        every still in episodes/E0XX-slug/assets/{archive,stock,ai}/ whose name
        starts with `beatNN_` -> episodes/E0XX-slug/assets/kb/beatNN_<name>.mp4
"""
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes"
RES = {"1080": (1920, 1080), "4k": (3840, 2160)}
# NOTE: a still whose long side < the frame's is rendered STATIC on black rather than
# scaled up — the project stays 4K, that clip just doesn't move (brain/16).
STILL_EXT = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
FILL = "force_original_aspect_ratio=increase"


def pick_move(w, h, frame_long):
    r = w / h
    if max(w, h) < frame_long:
        return "static"
    if r > 1.90:
        return "panh"
    if r < 0.90:
        return "panv"
    return "push"


def vf(move, direction, ow, oh, dur, fps):
    """Return the ffmpeg -vf filter chain for one still."""
    frames = max(1, round(dur * fps))
    if move == "static":
        return (f"scale={ow}:{oh}:force_original_aspect_ratio=decrease,"
                f"pad={ow}:{oh}:(ow-iw)/2:(oh-ih)/2:black,setsar=1")
    if move == "push":
        # pre-scale ~2x so zoompan has pixels to work with, then zoom 1.00 -> 1.10
        up = f"scale={ow*2}:{oh*2}:{FILL},crop={ow*2}:{oh*2}"
        step = 0.10 / frames
        zp = (f"zoompan=z='min(zoom+{step:.6f},1.10)':d={frames}:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={ow}x{oh}:fps={fps}")
        return f"{up},{zp},setsar=1"
    if move == "panh":
        # height fills the frame, width overflows; crop window slides across
        d = direction if direction in ("lr", "rl") else "lr"
        x = f"(iw-{ow})*t/{dur}" if d == "lr" else f"(iw-{ow})*(1-t/{dur})"
        return f"scale=-2:{oh},crop={ow}:{oh}:x='{x}':y=0,setsar=1"
    if move == "panv":
        d = direction if direction in ("down", "up") else "down"
        y = f"(ih-{oh})*t/{dur}" if d == "down" else f"(ih-{oh})*(1-t/{dur})"
        return f"scale={ow}:-2,crop={ow}:{oh}:x=0:y='{y}',setsar=1"
    raise ValueError(move)


def render(img, out, dur, res, move, direction, fps):
    ow, oh = RES[res]
    with Image.open(img) as im:
        w, h = im.size
    if move == "auto":
        move = pick_move(w, h, max(ow, oh))
    chain = vf(move, direction, ow, oh, dur, fps)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(img), "-t", f"{dur}",
           "-vf", chain, "-r", str(fps), "-c:v", "libx264", "-crf", "18",
           "-preset", "medium", "-pix_fmt", "yuv420p", "-an", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = r.returncode == 0 and out.exists()
    tag = "OK " if ok else "FAIL"
    print(f"  {tag} {out.name:40s} {w}x{h}  {move}{'/' + direction if direction else ''}  {dur}s")
    if not ok:
        print("       " + (r.stderr.strip().splitlines() or ["?"])[-1])
    return ok


def run_all(slug, dur, res, fps):
    ep = EP_DIR / slug
    if not ep.is_dir():
        sys.exit(f"no existe {ep}")
    kb = ep / "assets" / "kb"
    stills = []
    for sub in ("archive", "stock", "ai"):
        d = ep / "assets" / sub
        if d.is_dir():
            stills += [f for f in sorted(d.iterdir())
                       if f.suffix.lower() in STILL_EXT and re.match(r"(beat|E\d)", f.name, re.I)]
    if not stills:
        sys.exit("0 stills en assets/{archive,stock,ai}/ (¿ya corriste el --download del pase?)")
    print(f"{slug} — {len(stills)} stills -> assets/kb/\n")
    n = 0
    for f in stills:
        m = re.match(r"(beat[A-Za-z0-9+-]+)", f.name)
        stem = (m.group(1) + "_" if m else "") + f.stem.split("_", 1)[-1]
        n += render(f, kb / f"{stem}.mp4", dur, res, "auto", "", fps)
    print(f"\n{n}/{len(stills)} ok. Ajusta duración/movimiento por beat en 07c-edit.md y re-corre sueltos.")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)

    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default

    res = (opt("--res", "4k") or "4k").lower()      # channel target = 4K (brain/03)
    if res not in RES:
        sys.exit("--res: 1080 | 4k")
    fps = int(opt("--fps", "30"))
    dur = float(opt("--dur", "5"))

    if "--all" in a:
        run_all(a[0], dur, res, fps)
    else:
        img = Path(a[0])
        if not img.is_file():
            sys.exit(f"no existe la imagen: {img}")
        out = Path(opt("--out", str(img.with_suffix(".kb.mp4"))))
        move = opt("--move", "auto")
        direction = opt("--dir", "")
        sys.exit(0 if render(img, out, dur, res, move, direction, fps) else 1)
