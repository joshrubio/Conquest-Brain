#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_grade.py — bake a channel look into a 3D LUT (`brand/assets/grade.cube`).

A .cube LUT is the interchange format every grading app reads (DaVinci Resolve,
Premiere, CapCut). `assemble.py` applies it with ffmpeg's `lut3d` filter just
before the encode, IF `brand/assets/grade.cube` exists — so the grade is
opt-in: drop the .cube in place and every episode inherits the look; delete it
and the render is untouched.

  python tools/make_grade.py --explore FRAME.png
        render every preset onto FRAME → FRAME.explore.png (a labelled grid) to compare

  python tools/make_grade.py --preset warm-archival [--size 33]
        write brand/assets/grade.cube from that preset

  python tools/make_grade.py --preset warm-archival --preview FRAME.png
        also write FRAME.graded.png + FRAME.split.png (left raw | right graded)

Presets live in PRESETS below — tune the knobs and re-run. The .cube is text
(~1–2 MB at size 33); commit it.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mediabin import FFMPEG  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "brand" / "assets" / "grade.cube"
REC709 = np.array([0.2126, 0.7152, 0.0722])

# Each preset: lift/gain/gamma per channel (CDL-ish), a contrast S around pivot,
# a saturation scale, a highlight knee, and an optional split-tone
# (shadow tint, highlight tint, strength).  All in 0..1 display space.
PRESETS = {
    # barely-there: neutralise the fluorescent cast, tiny contrast, keep it honest
    "clean": dict(lift=[.004, .004, .004], gain=[1.01, 1.00, .985], gamma=[1, 1, 1.01],
                  contrast=1.05, pivot=.45, sat=.97, knee=.90),
    # the house candle: warm lifted blacks, cream highlights, gentle
    "warm-archival": dict(lift=[.018, .012, .006], gain=[1.05, 1.00, .90], gamma=[.97, 1, 1.06],
                          contrast=1.13, pivot=.44, sat=.88, knee=.80,
                          sh_tint=[.98, .99, 1.03], hi_tint=[1.03, 1.0, .93], tone=.12),
    # true-crime / investigation: cool, steely, desaturated, blacks hold
    "cool-forensic": dict(lift=[.004, .008, .012], gain=[.95, .99, 1.05], gamma=[1.03, 1, .97],
                          contrast=1.16, pivot=.43, sat=.80, knee=.82,
                          sh_tint=[.93, .98, 1.08], hi_tint=[.98, 1.0, 1.04], tone=.14),
    # bleach bypass: high contrast, near-monochrome, silver highs, crushed blacks
    "bleach-bypass": dict(lift=[-.01, -.01, -.008], gain=[1.06, 1.05, 1.04], gamma=[.92, .93, .94],
                          contrast=1.34, pivot=.46, sat=.55, knee=.72),
    # teal & amber: the trailer look — shadows teal, skin/highs amber, punchy
    "teal-amber": dict(lift=[.006, .010, .014], gain=[1.06, 1.00, .93], gamma=[.97, 1, 1.03],
                       contrast=1.20, pivot=.44, sat=1.06, knee=.80,
                       sh_tint=[.90, 1.02, 1.10], hi_tint=[1.08, 1.01, .88], tone=.20),
    # Kodak print: rich, filmic, natural — soft contrast, warm-neutral, gentle rolloff
    "film-print": dict(lift=[.012, .010, .010], gain=[1.03, 1.00, .97], gamma=[.99, 1, 1.02],
                       contrast=1.10, pivot=.45, sat=.94, knee=.76,
                       sh_tint=[1.0, .99, .99], hi_tint=[1.02, 1.0, .97], tone=.08),
    # editorial matte: lifted blacks (matte), low contrast, muted — art-book calm
    "editorial-matte": dict(lift=[.05, .05, .045], gain=[.97, .97, .965], gamma=[1.02, 1.02, 1.03],
                            contrast=.94, pivot=.45, sat=.82, knee=.9),
    # sepia doc: heavy amber lean, low sat, warm blacks — classic history channel
    "sepia-doc": dict(lift=[.03, .018, .004], gain=[1.06, .99, .82], gamma=[.93, 1, 1.12],
                      contrast=1.12, pivot=.44, sat=.62, knee=.78,
                      sh_tint=[1.04, .99, .90], hi_tint=[1.06, 1.0, .84], tone=.18),
    # golden hour: warm, bright, lush — punchy highlights, no lifted blacks, inviting
    "golden-hour": dict(lift=[.006, .004, .002], gain=[1.08, 1.01, .90], gamma=[.95, .99, 1.05],
                        contrast=1.18, pivot=.46, sat=1.08, knee=.82,
                        sh_tint=[1.0, .99, 1.0], hi_tint=[1.07, 1.02, .88], tone=.14),
    # nordic cold: clean cool, bright, low-ish sat but not crushed — calm, modern
    "nordic-cold": dict(lift=[.006, .012, .018], gain=[.97, 1.0, 1.04], gamma=[1.02, 1.0, .99],
                        contrast=1.10, pivot=.46, sat=.88, knee=.86,
                        sh_tint=[.95, 1.0, 1.06], hi_tint=[.99, 1.01, 1.03], tone=.10),
}


def grade(c, P):
    x = np.clip(c, 0.0, 1.0)
    lift, gain = np.array(P["lift"]), np.array(P["gain"])
    gamma = np.array(P["gamma"], float)
    x = x + lift * (1.0 - x)
    x = x * gain
    x = np.clip(x, 0.0, 1.0) ** (1.0 / gamma)
    x = (x - P["pivot"]) * P["contrast"] + P["pivot"]
    k = P["knee"]
    hi = x > k
    x = np.where(hi, k + (1.0 - k) * np.tanh((x - k) / (1.0 - k)), x)
    x = np.clip(x, 0.0, 1.0)
    luma = (x * REC709).sum(-1, keepdims=True)
    x = luma + (x - luma) * P["sat"]
    if P.get("tone"):
        sh = np.array(P["sh_tint"]); hit = np.array(P["hi_tint"]); amt = P["tone"]
        ws = (1.0 - np.clip(luma / 0.5, 0, 1)) ** 2 * amt
        wh = (luma ** 2) * amt
        x = x * (1 - ws) + x * sh * ws
        x = x * (1 - wh) + x * hit * wh
    return np.clip(x, 0.0, 1.0)


def write_cube(path, size, P, title="Conquest grade"):
    g = np.linspace(0.0, 1.0, size)
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")
    grid = np.stack([r, gg, b], axis=-1).reshape(-1, 3)  # .cube: red fastest
    out = grade(grid, P)
    lines = [f"# {title} — tools/make_grade.py", f'TITLE "{title}"', f"LUT_3D_SIZE {size}",
             "DOMAIN_MIN 0.0 0.0 0.0", "DOMAIN_MAX 1.0 1.0 1.0", ""]
    lines += [f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}" for v in out]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _apply(frame, cube, dst, width=None):
    vf = f"lut3d={Path(cube).resolve().relative_to(ROOT).as_posix()}"
    if width:
        vf = f"scale={width}:-2," + vf
    r = subprocess.run([FFMPEG, "-y", "-i", str(frame), "-vf", vf, str(dst)],
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        sys.exit("ffmpeg lut3d falló:\n" + "\n".join(r.stderr.strip().splitlines()[-6:]))


def _font(sz):
    for n in ("consola.ttf", "cour.ttf", "DejaVuSansMono.ttf", "arial.ttf"):
        for d in (Path("C:/Windows/Fonts"), Path("/usr/share/fonts")):
            for p in ([d / n] + list(d.rglob(n)) if d.is_dir() else []):
                try:
                    return ImageFont.truetype(str(p), sz)
                except Exception:
                    pass
    return ImageFont.load_default()


def explore(frame, only=None):
    frame = Path(frame).resolve()
    names = only or list(PRESETS)
    tw = 900
    tiles = []
    with tempfile.TemporaryDirectory(dir=ROOT) as td:
        raw = Path(td) / "raw.png"
        subprocess.run([FFMPEG, "-y", "-i", str(frame), "-vf", f"scale={tw}:-2", str(raw)],
                       capture_output=True, cwd=ROOT)
        tiles.append(("RAW", Image.open(raw).convert("RGB")))
        for name in names:
            P = PRESETS[name]
            cube = Path(td) / f"{name}.cube"
            write_cube(cube, 33, P, name)
            g = Path(td) / f"{name}.png"
            _apply(frame, cube, g, width=tw)
            tiles.append((name, Image.open(g).convert("RGB")))
    tw2, th2 = tiles[0][1].size
    cols = 2
    rows = (len(tiles) + cols - 1) // cols
    lab = 46
    W, H = cols * tw2, rows * (th2 + lab)
    sheet = Image.new("RGB", (W, H), (16, 13, 9))
    d = ImageDraw.Draw(sheet)
    f = _font(30)
    for i, (name, im) in enumerate(tiles):
        x, y = (i % cols) * tw2, (i // cols) * (th2 + lab)
        d.rectangle((x, y, x + tw2, y + lab), fill=(16, 13, 9))
        d.text((x + 16, y + 8), name, font=f, fill=(201, 161, 90) if name != "RAW" else (150, 138, 118))
        sheet.paste(im, (x, y + lab))
    out = frame.with_suffix(".explore" + frame.suffix)
    sheet.save(out)
    print(f"escrito  {out}")
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--explore" in a:
        only = a[a.index("--only") + 1].split(",") if "--only" in a else None
        explore(a[a.index("--explore") + 1], only)
        sys.exit(0)
    preset = a[a.index("--preset") + 1] if "--preset" in a else "cool-forensic"  # channel default
    if preset not in PRESETS:
        sys.exit(f"preset desconocido: {preset}\ndisponibles: {', '.join(PRESETS)}")
    size = int(a[a.index("--size") + 1]) if "--size" in a else 33
    write_cube(OUT, size, PRESETS[preset], f"Conquest · {preset}")
    print(f"escrito  {OUT.relative_to(ROOT)}  ({size}^3 · preset «{preset}»)")
    if "--preview" in a:
        fr = Path(a[a.index("--preview") + 1]).resolve()
        _apply(fr, OUT, fr.with_suffix(".graded" + fr.suffix))
        g = fr.with_suffix(".graded" + fr.suffix)
        subprocess.run([FFMPEG, "-y", "-i", str(fr), "-i", str(g), "-filter_complex",
                        "[0]crop=iw/2:ih:0:0[l];[1]crop=iw/2:ih:iw/2:0[r];[l][r]hstack",
                        str(fr.with_suffix(".split" + fr.suffix))],
                       capture_output=True, cwd=ROOT)
        print(f"escrito  {g.name} · {fr.with_suffix('.split' + fr.suffix).name}")
