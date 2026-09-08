#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_graphics.py — the episode's own graphics, in the house style (brain/03).

Reads the **Gráficos / motion** table of `06-shotlist.md` and renders one 4K PNG
per row into `assets/graphic/<id>.png` (id = the `asset` the shotlist names).

Seven ids have a bespoke renderer — a real drawn graphic, not a text card:
  *pipeline*  the print workshop chain          *age_ladder*   the preface's age scale
  *names_timeline*  the ~30 art-names on a life  *mastery_curve* ego vs. maestría curves
  *prussian_blue*  pigment + trade route         *death_card*    the closing text card
  *signature_manji*  the late signature + gloss
Each pulls its content from the row's own "Qué muestra" / "Datos" text where it
can (the arrows, the «quotes», the pairs); a few constants (the name list from
S05, the kanji) live at the top of this file. Any id without a renderer falls
back to a plain titled card carrying the "Qué muestra" text.

These are **stills** — enough for the Stage-9 rough cut to have every gráfico
beat covered. A designer turns the load-bearing ones into motion later; re-run
`assemble.py` afterwards. Won't overwrite an existing PNG unless --force.

A contact sheet (`assets/graphic/_index.html`) is written on every run — open it
at `http://127.0.0.1:8765/episodes/E0XX-slug/assets/graphic/_index.html` to
preview every card with its id, "qué muestra", rótulo and the beats that use it.

Usage
  python tools/make_graphics.py E0XX-slug [--force] [--id G4_age_ladder ...]
  python tools/make_graphics.py E0XX-slug --contact-only   # just rebuild the sheet
"""
import math
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
W, H = 3840, 2160
GROUND = (16, 13, 9)
SURFACE = (30, 26, 20)
SURFACE2 = (44, 38, 29)
BONE = (236, 227, 206)
GOLD = (201, 161, 90)
MUTED = (150, 138, 118)
FAINT = (78, 69, 53)
BLUE = (17, 46, 82)          # azul de Prusia (bero-ai), aproximado

SERIF = ("georgia.ttf", "times.ttf", "DejaVuSerif.ttf")
SERIF_B = ("georgiab.ttf", "timesbd.ttf", "DejaVuSerif-Bold.ttf")
SERIF_I = ("georgiai.ttf", "timesi.ttf", "DejaVuSerif-Italic.ttf")
MONO = ("cour.ttf", "consola.ttf", "DejaVuSansMono.ttf")
CJK = ("YuGothM.ttc", "YuGothB.ttc", "msgothic.ttc", "meiryo.ttc", "msmincho.ttc")
FONT_DIRS = [Path("C:/Windows/Fonts"), Path("/usr/share/fonts"), Path("/Library/Fonts"),
             ROOT / "brand" / "assets" / "fonts"]

# S05 (Beyond the Great Wave, 2017): "unos treinta nombres … Shunro, Sori, Hokusai,
# Taito, Iitsu, Gakyo Rojin, Manji, entre otros". Years are the commonly cited
# adoption dates — shown as "≈", not as hard on-screen data.
NAMES = [
    ("Shunrō", "春朗", "≈1779"),
    ("Sōri", "宗理", "≈1795"),
    ("Hokusai", "北斎", "≈1805"),
    ("Taito", "戴斗", "≈1810"),
    ("Iitsu", "為一", "≈1820"),
    ("Manji", "卍", "≈1834"),
]
MANJI_KANJI = "画狂老人卍"

_FCACHE = {}


def _font(names, size):
    key = (names, size)
    if key in _FCACHE:
        return _FCACHE[key]
    for d in FONT_DIRS:
        if not d.is_dir():
            continue
        for n in names:
            for p in [d / n] + list(d.rglob(n)):
                try:
                    f = ImageFont.truetype(str(p), size)
                    _FCACHE[key] = f
                    return f
                except Exception:
                    pass
    f = ImageFont.load_default()
    _FCACHE[key] = f
    return f


# ---------- drawing helpers ----------

def _new():
    im = Image.new("RGB", (W, H), GROUND)
    return im, ImageDraw.Draw(im)


def _wrap(d, text, font, maxw):
    out, line = [], ""
    for word in text.split():
        t = (line + " " + word).strip()
        if d.textlength(t, font=font) <= maxw:
            line = t
        else:
            if line:
                out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def ctext(d, cx, y, text, font, fill):
    d.text((cx - d.textlength(text, font=font) / 2, y), text, font=font, fill=fill)


def rtext(d, rx, y, text, font, fill):
    d.text((rx - d.textlength(text, font=font), y), text, font=font, fill=fill)


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def arrow(d, p0, p1, color=GOLD, width=5, head=34):
    x0, y0 = p0
    x1, y1 = p1
    d.line([p0, p1], fill=color, width=width)
    ang = math.atan2(y1 - y0, x1 - x0)
    for s in (0.5, -0.5):
        d.line([p1, (x1 - head * math.cos(ang - s), y1 - head * math.sin(ang - s))],
               fill=color, width=width)


def dashed(d, p0, p1, color=MUTED, width=3, dash=26, gap=18):
    x0, y0 = p0
    x1, y1 = p1
    total = math.hypot(x1 - x0, y1 - y0)
    if total == 0:
        return
    ux, uy = (x1 - x0) / total, (y1 - y0) / total
    t = 0.0
    while t < total:
        a = (x0 + ux * t, y0 + uy * t)
        b = (x0 + ux * min(t + dash, total), y0 + uy * min(t + dash, total))
        d.line([a, b], fill=color, width=width)
        t += dash + gap


def _clean(s):
    return re.sub(r"[`*]+", "", s or "").strip()


def _salvedad(s):
    """The rótulo column doubles as a note-to-self ('— (proceso, no cifra)',
    '— (cita en la descripción)'). Only a real on-screen salvedad is drawn."""
    s = _clean(s)
    low = s.lower()
    if (not s or s in ("—", "-") or low.lstrip("—-（( ").startswith(("(", "—"))
            or "cita en la desc" in low or "source card" in low or "no cifra" in low
            or low.startswith("proceso")):
        return ""
    return s


def frame(d, title, rotulo=None):
    m = 210
    d.line([(m, 196), (W - m, 196)], fill=GOLD, width=3)
    d.line([(m, 196), (m, 250)], fill=GOLD, width=3)
    d.line([(W - m, 196), (W - m, 142)], fill=GOLD, width=3)
    d.text((m, 118), title.upper(), font=_font(MONO, 46), fill=GOLD)
    sv = _salvedad(rotulo)
    if sv:
        f = _font(SERIF_I, 46)
        d.line([(m, H - 214), (m + 96, H - 214)], fill=GOLD, width=3)
        for i, ln in enumerate(_wrap(d, sv, f, W - 2 * m)):
            d.text((m, H - 176 + i * 58), ln, font=f, fill=MUTED)


# ---------- text extraction from the shotlist row ----------

def quotes(s):
    return re.findall(r"[«\"“]([^»\"”]+)[»\"”]", s)


def arrow_seq(s):
    s = re.split(r"[:：]", s, 1)[-1]
    s = re.sub(r"\([^)]*\)", "", s)
    parts = re.split(r"\s*(?:→|->|›|—>|>)\s*", s)
    return [p.strip(" .,;") for p in parts if p.strip(" .,;")]


def pair_vs(s):
    m = re.split(r"\s*(?:vs\.?|↔|frente a)\s*", s, 1)
    if len(m) == 2:
        a = re.split(r"[;,]", m[0])[-1].strip()
        b = re.split(r"[;,]", m[1])[0].strip()
        return a, b
    return None


# ---------- bespoke renderers ----------

def g_pipeline(row):
    im, d = _new()
    frame(d, "el grabado — cadena de manos", row["label"])
    raw = arrow_seq(row["shows"]) or ["dibujante", "tallador", "impresor", "editor"]
    stations = [re.split(r"[;·]", s)[0].strip() for s in raw][:4]
    kanji = {"dibujante": "絵師", "tallador": "彫師", "impresor": "摺師", "editor": "版元"}
    n = len(stations)
    m = 280
    bw, bh = 660, 440
    gapx = (W - 2 * m - n * bw) / (n - 1)
    cy = 560
    cxs = []
    for i, st in enumerate(stations):
        x = m + i * (bw + gapx)
        cx = x + bw / 2
        cxs.append(cx)
        rrect(d, (x, cy, x + bw, cy + bh), 18, fill=SURFACE, outline=FAINT, width=2)
        ctext(d, cx, cy + 40, f"0{i + 1}", _font(MONO, 40), GOLD)
        k = kanji.get(st.lower(), "")
        if k:
            ctext(d, cx, cy + 108, k, _font(CJK, 150), BONE)
        ctext(d, cx, cy + 320, st, _font(SERIF, 58), MUTED)
        if i < n - 1:
            arrow(d, (x + bw + 26, cy + bh / 2), (x + bw + gapx - 26, cy + bh / 2))

    # the signed name belongs to station 1; it "rides" to the finished print
    ry = cy + bh + 280
    d.line([(cxs[0], cy + bh + 24), (cxs[0], ry)], fill=GOLD, width=3)
    dashed(d, (cxs[0] + 140, ry), (cxs[-1] - 220, ry), color=GOLD, width=3)
    ss = 190
    d.rectangle((cxs[0] - ss / 2, ry - ss / 2, cxs[0] + ss / 2, ry + ss / 2),
                outline=(176, 62, 48), width=7)
    d.text((cxs[0], ry), "落款", font=_font(CJK, 66), fill=(176, 62, 48), anchor="mm")
    # the finished print at the end
    pw, ph = 360, 250
    px, py = cxs[-1] - pw / 2, ry - ph / 2
    rrect(d, (px, py, px + pw, py + ph), 10, fill=SURFACE2, outline=GOLD, width=3)
    d.arc((px + 40, py + 60, px + pw - 40, py + ph + 140), 180, 360, fill=BLUE, width=14)
    d.rectangle((px + pw - 54, py + ph - 40, px + pw - 24, py + ph - 14),
                outline=(176, 62, 48), width=5)

    big = _font(SERIF, 78)
    for j, ln in enumerate(["El nombre firmado es del dibujante.",
                            "La madera la tocan otros tres."]):
        ctext(d, W / 2, ry + 180 + j * 104, ln, big, BONE)
    return im


def g_names(row):
    im, d = _new()
    frame(d, "los nombres — una vida, treinta firmas", row["label"])
    m = 320
    y = 1150
    d.line([(m, y), (W - m, y)], fill=MUTED, width=4)
    for i in range(31):
        x = m + (W - 2 * m) * i / 30
        d.line([(x, y - 14), (x, y + 14)], fill=FAINT, width=2)
    rtext(d, m + 70, y + 40, "≈1760", _font(MONO, 38), MUTED)
    d.text((W - m - 70, y + 40), "1849", font=_font(MONO, 38), fill=MUTED)

    span = 1849 - 1760
    for i, (rom, kj, yr) in enumerate(NAMES):
        year = int(re.sub(r"\D", "", yr))
        x = m + (W - 2 * m) * (year - 1760) / span
        up = (i % 2 == 0)
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=GOLD)
        stem = 250
        ny = y - stem if up else y + stem
        d.line([(x, y + (-16 if up else 16)), (x, ny)], fill=GOLD, width=3)
        if up:
            ctext(d, x, ny - 250, kj, _font(CJK, 118), BONE)
            ctext(d, x, ny - 108, rom, _font(SERIF, 54), BONE)
            ctext(d, x, ny - 44, yr, _font(MONO, 34), MUTED)
        else:
            ctext(d, x, ny + 24, kj, _font(CJK, 118), BONE)
            ctext(d, x, ny + 166, rom, _font(SERIF, 54), BONE)
            ctext(d, x, ny + 230, yr, _font(MONO, 34), MUTED)

    ctext(d, W / 2, 300,
          "«A menudo vendía el nombre anterior a un discípulo y tomaba otro.»",
          _font(SERIF_I, 54), MUTED)
    return im


def g_prussian(row):
    im, d = _new()
    frame(d, "el azul de Prusia", row["label"])
    sw = 1120
    sx, sy = 300, (H - sw) / 2 + 60
    d.rectangle((sx, sy, sx + sw, sy + sw), fill=BLUE, outline=FAINT, width=2)
    ctext(d, sx + sw / 2, sy + sw + 44, "«bero-ai» — el azul del taller",
          _font(SERIF_I, 50), MUTED)

    ex = sx + sw + 300
    ax0, ax1 = ex + 40, W - 340
    ay = 620
    d.ellipse((ax0 - 15, ay - 15, ax0 + 15, ay + 15), fill=BONE)
    d.ellipse((ax1 - 15, ay - 15, ax1 + 15, ay + 15), fill=GOLD)
    d.text((ax0 - 10, ay - 92), "EUROPA", font=_font(MONO, 40), fill=MUTED)
    rtext(d, ax1 + 10, ay - 92, "JAPÓN · NAGASAKI", _font(MONO, 40), GOLD)
    pts = [(ax0 + (ax1 - ax0) * t / 60,
            ay + 320 * (t / 60) * (1 - t / 60) * 4) for t in range(61)]
    d.line(pts, fill=GOLD, width=5)
    arrow(d, pts[-3], pts[-1])
    mxp, myp = pts[30]
    d.polygon([(mxp, myp - 26), (mxp + 26, myp), (mxp, myp + 26), (mxp - 26, myp)],
              outline=MUTED, width=4)

    bullets = ["sintetizado en Europa (s. XVIII)",
               "más barato hacia finales de la década de 1820",
               "hace posible la lámina entera en azul — aizuri-e"]
    for j, s in enumerate(bullets):
        yy = ay + 520 + j * 190
        d.ellipse((ex - 4, yy + 26, ex + 12, yy + 42), fill=GOLD)
        for k, ln in enumerate(_wrap(d, s, _font(SERIF, 54), W - ex - 300)):
            d.text((ex + 48, yy + k * 62), ln, font=_font(SERIF, 54), fill=BONE)
    return im


def g_signature(row):
    im, d = _new()
    frame(d, "la firma tardía", row["label"])
    qs = quotes(row["shows"])
    rom = qs[0] if qs else "Gakyō Rōjin Manji"
    gloss = qs[1] if len(qs) > 1 else "el viejo loco por la pintura"
    ctext(d, W / 2, 540, MANJI_KANJI, _font(CJK, 360), BONE)
    arrow(d, (W / 2, 1010), (W / 2, 1190), width=5)
    ctext(d, W / 2, 1220, rom, _font(SERIF, 100), GOLD)
    ctext(d, W / 2, 1440, f"«{gloss}»", _font(SERIF_I, 96), BONE)
    ctext(d, W / 2, 1680, "«manji» — el signo sánscrito que tomó como nombre",
          _font(SERIF_I, 46), MUTED)
    return im


def g_ladder(row):
    im, d = _new()
    frame(d, "la escala del prefacio (1834)", row["label"])
    nums = [int(x) for x in re.findall(r"\b(\d{2,3})\b", row["shows"])]
    if not nums:
        nums = [73, 80, 90, 100, 110]
    qs = quotes(row["shows"])
    top_note = qs[-1] if qs else "cada punto y cada línea, vivos"
    n = len(nums)
    m = 340
    base_y = H - 380
    top_y = 640
    step_w = (W - 2 * m) / n
    for i, val in enumerate(nums):
        x = m + i * step_w
        h = top_y + (base_y - top_y) * (1 - (i + 1) / n)
        hot = (val == max(nums))
        d.rectangle((x + 34, h, x + step_w - 34, base_y),
                    fill=GOLD if hot else SURFACE, outline=GOLD if hot else FAINT,
                    width=4 if hot else 2)
        ctext(d, x + step_w / 2, h - 128, str(val),
              _font(SERIF_B, 150 if hot else 108), BONE if hot else MUTED)
    d.line([(m, base_y), (W - m, base_y)], fill=MUTED, width=4)
    ctext(d, W / 2, 340, f"«… a los {max(nums)}, {top_note}.»", _font(SERIF_I, 64), BONE)
    return im


def g_mastery(row):
    im, d = _new()
    frame(d, "dos metas", row["label"])
    pv = pair_vs(row["shows"])
    a_lbl = re.sub(r"^metas de\s+", "", (pv[0] if pv else "demostrar (ego)"))
    b_lbl = re.sub(r"^metas de\s+", "", (pv[1] if pv else "aprender (maestría)"))
    px0, py0 = 380, 340
    px1, py1 = W - 420, H - 400
    d.line([(px0, py1), (px1 + 40, py1)], fill=MUTED, width=4)
    d.line([(px0, py0 - 40), (px0, py1)], fill=MUTED, width=4)
    d.text((px0 - 24, py0 - 130), "lo que alcanzas", font=_font(SERIF, 46), fill=MUTED)
    rtext(d, px1 + 40, py1 + 34, "tiempo · práctica", _font(SERIF, 46), MUTED)

    def poly(fn, cap=None):
        pts = []
        for k in range(241):
            t = k / 240
            y = fn(t)
            if cap is not None and y >= cap:
                pts.append((px0 + (px1 - px0) * t, py1 - (py1 - py0) * cap))
                return pts, True
            pts.append((px0 + (px1 - px0) * t, py1 - (py1 - py0) * max(0.0, y)))
        return pts, False

    ceil = 0.5
    ego, _ = poly(lambda t: ceil * (1 - math.exp(-5.5 * t)))
    dashed(d, (px0, py1 - (py1 - py0) * ceil), (px1, py1 - (py1 - py0) * ceil),
           color=FAINT, width=3)
    d.line(ego, fill=MUTED, width=9)
    mastery, hit = poly(lambda t: 0.12 + 1.15 * t ** 0.92, cap=0.98)
    d.line(mastery, fill=GOLD, width=12)
    if hit:
        arrow(d, mastery[-2], (mastery[-1][0] + 60, mastery[-1][1] - 60), color=GOLD, width=12)

    d.text((px0 + 24, py1 - (py1 - py0) * ceil - 64), "techo", font=_font(MONO, 34), fill=FAINT)
    ex, ey = ego[-1]
    rtext(d, px1 + 20, ey + 24, a_lbl, _font(SERIF, 54), MUTED)
    mx, my = mastery[-1]
    d.text((mx - d.textlength(b_lbl, font=_font(SERIF, 60)) - 40, my - 20),
           b_lbl, font=_font(SERIF, 60), fill=GOLD)
    return im


def g_death(row):
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    qs = quotes(row["shows"]) or quotes(row["label"])
    main = qs[0] if qs else "Edo, 1849 · ~88 años"
    parts = re.split(r"\s*[·|]\s*", main)
    d.line([(W / 2 - 90, 780), (W / 2 + 90, 780)], fill=GOLD, width=3)
    ctext(d, W / 2, 900, parts[0], _font(SERIF, 200), BONE)
    if len(parts) > 1:
        ctext(d, W / 2, 1200, " · ".join(parts[1:]), _font(SERIF_I, 110), MUTED)
    if row["label"] and row["label"] not in ("—", "-"):
        ctext(d, W / 2, 1520, row["label"], _font(SERIF_I, 52), FAINT)
    return im


RENDERERS = [
    ("pipeline", g_pipeline),
    ("names", g_names),
    ("prussian", g_prussian),
    ("signature", g_signature),
    ("manji", g_signature),
    ("ladder", g_ladder),
    ("mastery", g_mastery),
    ("curve", g_mastery),
    ("death", g_death),
]


def generic_card(row):
    im, d = _new()
    frame(d, row["id"].replace("_", " "), row["label"])
    body = _font(SERIF, 104)
    lines = _wrap(d, row["shows"], body, W - 620)
    y = H // 2 - len(lines) * 66
    for ln in lines:
        d.text((310, y), ln, font=body, fill=BONE)
        y += 132
    return im


def render_row(row):
    key = row["id"].lower()
    for tag, fn in RENDERERS:
        if tag in key:
            return fn(row)
    return generic_card(row)


# ---------- shotlist parsing ----------

def parse_graphics(md):
    m = re.search(r"##\s*Gr[aá]ficos?\s*/\s*motion.*?\n(\|.*?)(?:\n\n|\n##|\Z)", md, re.S | re.I)
    if not m:
        return []
    rows = [r for r in m.group(1).splitlines() if r.strip().startswith("|")]
    out = []
    for r in rows:
        c = [x.strip() for x in r.strip().strip("|").split("|")]
        if len(c) < 3 or c[0].lower() in ("id", "") or set("".join(c)) <= set("-: "):
            continue
        out.append({
            "id": c[0].strip("`"),
            "beats": c[1] if len(c) > 1 else "",
            "shows": c[2] if len(c) > 2 else "",
            "datos": c[3] if len(c) > 3 else "",
            "label": c[4] if len(c) > 4 else "",
            "style": c[5] if len(c) > 5 else "",
        })
    return out


def _beats_using(md):
    """gid -> [beat numbers] from the shotlist timeline (tipo 'gráfico' rows)."""
    use = {}
    for ln in md.splitlines():
        if not ln.strip().startswith("|"):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 6 or not c[0].isdigit():
            continue
        asset = c[5].strip("`").split()[-1] if c[5] else ""
        if re.match(r"G\d", asset):
            use.setdefault(asset, []).append(c[0])
    return use


def write_contact(d, rows, md):
    use = _beats_using(md)
    esc = lambda s: (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    cards = []
    for row in rows:
        gid = row["id"]
        png = f"{gid}.png"
        exists = (d / png).exists()
        beats = ", ".join(use.get(gid, [])) or "—"
        tag = "" if exists else '<span class="miss">falta el PNG</span>'
        inner = (f'<img loading="lazy" src="{png}">' if exists else '<div class="ph">—</div>')
        cards.append(f"""      <figure>
        <div class="fr">{inner}</div>
        <figcaption><b>{esc(gid)}</b> {tag}<br><span class="sh">{esc(row['shows'])}</span>
        <br><span class="lb">rótulo: {esc(row['label']) or '—'}</span>
        <br><span class="bt">beats: {beats}</span></figcaption>
      </figure>""")
    html = f"""<!doctype html><meta charset="utf-8"><title>Gráficos — contact sheet</title>
<style>
 body{{background:#100d09;color:#ece3ce;font:15px/1.5 Georgia,serif;margin:0;padding:40px}}
 h1{{font-size:20px;color:#c9a15a;font-weight:normal;margin:0 0 6px}}
 p.sub{{color:#96876f;margin:0 0 28px}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:26px}}
 figure{{margin:0;background:#1e1a14;border:1px solid #2e2820;border-radius:8px;overflow:hidden}}
 .fr{{aspect-ratio:16/9;background:#000;display:flex;align-items:center;justify-content:center}}
 .fr img{{width:100%;height:100%;object-fit:contain}}
 .ph{{color:#4a3e2f;font-size:40px}}
 figcaption{{padding:12px 14px 16px}}
 .sh{{color:#ece3ce}} .lb{{color:#96876f;font-size:13px}} .bt{{color:#c9a15a;font-size:13px}}
 .miss{{color:#e2b23a;font-size:12px;border:1px solid #6a5a2f;border-radius:4px;padding:1px 6px;margin-left:6px}}
</style>
<h1>Gráficos propios — {esc(d.parent.parent.name)}</h1>
<p class="sub">Stills para el rough cut. Sube los que importen a motion real y re-corre <code>assemble.py</code>.</p>
<div class="grid">
{chr(10).join(cards)}
</div>
"""
    (d / "_index.html").write_text(html, encoding="utf-8")
    print(f"  escrito  assets/graphic/_index.html  ({len(rows)} tarjetas)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    slug = a[0].strip("/\\")
    ep = ROOT / "episodes" / slug
    sl = ep / "06-shotlist.md"
    if not sl.exists():
        sys.exit(f"no {sl.relative_to(ROOT)}")
    force = "--force" in a
    contact_only = "--contact-only" in a
    only = {a[i + 1] for i, x in enumerate(a) if x == "--id"}
    md = sl.read_text(encoding="utf-8")
    rows = parse_graphics(md)
    if not rows:
        sys.exit("no encuentro la tabla 'Gráficos / motion' en 06-shotlist.md")
    d = ep / "assets" / "graphic"
    d.mkdir(parents=True, exist_ok=True)
    n = 0
    if not contact_only:
        for row in rows:
            if only and row["id"] not in only:
                continue
            out = d / f"{row['id']}.png"
            if out.exists() and not force:
                print(f"  ya existe  {out.name}  (--force para regenerar)")
                continue
            try:
                render_row(row).save(out)
                print(f"  escrito  assets/graphic/{out.name}  «{row['shows'][:56]}»")
                n += 1
            except Exception as e:
                print(f"  FALLO  {row['id']}: {e}")
    write_contact(d, rows, md)
    print(f"\n{n} gráfico(s) generado(s) en episodes/{slug}/assets/graphic/")
    print(f"preview:  http://127.0.0.1:8765/episodes/{slug}/assets/graphic/_index.html")
    if not contact_only:
        print("son stills — sube los que importen a motion real; luego re-corre assemble.py")
