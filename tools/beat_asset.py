#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beat_asset.py — edit the Stage-9 spine from the cutting room, retroactively.

  --list                         asset library as JSON, for the picker
  --set <n> --asset <id>         point beat <n> at an asset already in assets/
  --set <n> --src "<url|path>"   fetch a new resource, point beat <n> at it
  --clear <n>                    remove beat <n>'s visual (goes 'sin cubrir')
  --merge <n> --into prev|next   fold beat <n> into a neighbour (that shot covers
                                 the combined VO span); the row is removed
  --del <n>                      remove beat <n> outright (align redistributes)
  --split <n> --at <sec>         cut beat <n> in two at VO-time <sec>; both halves
                                 keep the asset (reassign the 2nd in the sala)
  --add --after <n> --frag "<vo>" --kind <k> [--asset <id> | --src <url|path>]
        [--section <s>] [--marker <m>] [--dur <sec>]
                                 insert a new beat after <n>

Every structural op is retroactive:
- `06-shotlist.md` spine is renumbered 1..N; the beat numbers in its prose
  sections and in `07-assets.md` (Manifiesto `Beat(s)` column) are remapped
- `07-picks.txt` beat lines and `09-timeline.json` (`beats[].n`, so the edit
  room's dur_lock / slot / approved survive) are remapped
- before any renumber, every covered beat's `asset → file` is frozen into
  `assets/_index.json` so resolution never depends on the row number
- a new archival asset appends a `07-assets.md` row and an
  `03-source-log.csv` stub (`S## … PENDIENTE`) for you to fill

Prints JSON. serve.py's /beat-asset endpoint dispatches here.
Not for `acamara` / `negro` beats (they carry no asset) — except --merge/--del/--add.
"""
import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import assemble as A  # noqa: E402
import pull_assets as PA  # noqa: E402

EP_DIR = A.EP_DIR
SUBS = ("graphic", "archive", "video", "stock", "kb", "ai", "intro")
SUB_KIND = {"graphic": "gráfico", "archive": "archivo", "video": "stock",
            "stock": "stock", "kb": "kb", "ai": "ia", "intro": "stock"}
VIDEO_EXT = (".mp4", ".mov", ".webm")
NO_ASSET = {"acamara", "a-cámara", "a-camara", "narrador", "negro"}
SECTIONS = ("cold open", "bumper", "pivote", "contexto", "explicador",
            "acto 1", "acto 2", "acto 3", "acto 4", "acto 5", "teorías", "cierre", "cta")


# ─────────────────────────────────────────────────── asset library
def asset_library(slug):
    ep = EP_DIR / slug
    out, seen = [], set()
    for sub in SUBS:
        d = ep / "assets" / sub
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if f.is_file() and f.suffix.lower() in A.MEDIA_EXT and f.stem not in seen:
                seen.add(f.stem)
                out.append({"id": f.stem, "sub": sub,
                            "url": f"/episodes/{slug}/assets/{sub}/{f.name}",
                            "video": f.suffix.lower() in VIDEO_EXT, "kind": SUB_KIND[sub]})
    return out


# ─────────────────────────────────────────────────── spine helpers
def _spine(slug):
    """(lines, first_data_idx, end_idx) for the 'Timeline — la espina' table."""
    f = EP_DIR / slug / "06-shotlist.md"
    lines = f.read_text(encoding="utf-8").splitlines()
    start = end = None
    inb = False
    for i, ln in enumerate(lines):
        if "Timeline" in ln and "la espina" in ln:
            inb = True
            continue
        if inb and ln.startswith("## "):
            end = i
            break
        if inb and ln.lstrip().startswith("|"):
            c = ln.split("|")
            if len(c) > 1 and c[1].strip().isdigit() and start is None:
                start = i
    if start is None:
        raise SystemExit("no encuentro filas de datos en 'Timeline — la espina'")
    if end is None:
        end = len(lines)
    return f, lines, start, end


def _data_rows(lines, start, end):
    """[(line_idx, cells)] for spine data rows (cells = '|'-split)."""
    out = []
    for i in range(start, end):
        ln = lines[i]
        if not ln.lstrip().startswith("|"):
            continue
        c = ln.split("|")
        if len(c) >= 11 and c[1].strip().isdigit():
            out.append((i, c))
    return out


def _row(n, tin, dur, section, tipo, asset, rotulo, motion, marker, frag):
    return (f"| {n} | {tin} | {dur} | {section} | {tipo} | {asset or '—'} | "
            f"{rotulo or '—'} | {motion} | {marker or '—'} | «{frag.strip('«»')}» |")


def beat_row(slug, n):
    _, lines, s, e = _spine(slug)
    for _, c in _data_rows(lines, s, e):
        if int(c[1].strip()) == n:
            return {"n": n, "in": c[2].strip(), "dur": c[3].strip(),
                    "section": c[4].strip(), "tipo": c[5].strip(),
                    "asset": "" if c[6].strip() in ("—", "-", "") else c[6].strip(),
                    "rotulo": c[7].strip(), "motion": c[8].strip(),
                    "marker": "" if c[9].strip() in ("—", "-") else c[9].strip(),
                    "frag": c[10].strip()}
    return None


# ─────────────────────────────────────────────────── resolution freeze
def freeze_resolutions(slug):
    """Pin every covered beat's asset_id -> exact file in assets/_index.json,
    replicating resolve()'s lookup, so renumbering rows can't break resolution."""
    ep = EP_DIR / slug
    idx = A._asset_index(ep)
    pins = {}
    for b in A.parse_spine((ep / "06-shotlist.md").read_text(encoding="utf-8")):
        a = b["asset"]
        if not a or a.startswith("G") or b["kind"] in NO_ASSET:
            continue
        hit = idx.get(a) or idx.get(a.split(".")[0])
        if not hit:
            aid = a.lower()
            hit = next((v for k, v in idx.items()
                        if k.lower() == aid or k.lower().startswith(aid + "_")), None)
        if not hit:
            for k, v in idx.items():
                if k.lower().startswith(f"beat{b['n']:02d}_") or k.lower().startswith(f"beat{b['n']}_"):
                    hit = v
                    break
        if hit:
            try:
                pins[a] = "assets/" + str(hit.relative_to(ep / "assets")).replace("\\", "/")
            except ValueError:
                pass
    f = ep / "assets" / "_index.json"
    cur = {}
    if f.exists():
        try:
            cur = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    cur.update(pins)
    cur = {k: v for k, v in cur.items() if (ep / v).exists()}
    f.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")


# ─────────────────────────────────────────────────── renumber + remap
def _remap_beatlist(txt, m):
    """Remap a comma/range list of beat numbers ('27–28, 41, +G')."""
    def one(tok):
        tok = tok.strip()
        rng = re.match(r"^(\d+)\s*[–-]\s*(\d+)$", tok)
        if rng:
            a, b = m.get(int(rng.group(1))), m.get(int(rng.group(2)))
            if a is None or b is None:
                return None
            return f"{a}–{b}" if a != b else str(a)
        if tok.isdigit():
            return None if int(tok) not in m else str(m[int(tok)])
        return tok        # '+G', notes
    kept = [x for x in (one(t) for t in txt.split(",")) if x]
    return ", ".join(kept)


def renumber(slug, dropped=frozenset()):
    """Renumber the spine 1..N in file order; drop rows whose number is in
    `dropped`. Returns {old_n: new_n} for the survivors. Also remaps 07-picks.txt,
    09-timeline.json, and the beat numbers in 06-shotlist prose + 07-assets.md."""
    f, lines, s, e = _spine(slug)
    rows = _data_rows(lines, s, e)
    m, new_n = {}, 0
    for li, c in rows:
        old = int(c[1].strip())
        if old in dropped:
            lines[li] = None
            continue
        new_n += 1
        m[old] = new_n
        c[1] = f" {new_n} "
        lines[li] = "|".join(c)
    lines = [ln for ln in lines if ln is not None]
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")

    identity = all(k == v for k, v in m.items()) and not dropped
    if identity:
        return m

    _remap_picks(slug, m, dropped)
    _remap_timeline(slug, m, dropped)
    _remap_prose(slug, m, dropped)
    _remap_assets_md(slug, m, dropped)
    return m


def _remap_picks(slug, m, dropped):
    f = EP_DIR / slug / "07-picks.txt"
    if not f.exists():
        return
    out = []
    for ln in f.read_text(encoding="utf-8").splitlines():
        c = ln.split("\t")
        if len(c) >= 3 and c[0].strip().isdigit():
            old = int(c[0].strip())
            if old in dropped:
                continue
            if old in m:
                c[0] = str(m[old])
                c[1] = re.sub(r"custom:\d+", f"custom:{m[old]}", c[1])
                ln = "\t".join(c)
        out.append(ln)
    f.write_text("\n".join(out) + "\n", encoding="utf-8")


def _remap_timeline(slug, m, dropped):
    f = EP_DIR / slug / "09-timeline.json"
    if not f.exists():
        return
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    beats = []
    for b in d.get("beats", []):
        if b.get("n") in dropped:
            continue
        if b.get("n") in m:
            b["n"] = m[b["n"]]
        beats.append(b)
    d["beats"] = beats
    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def _remap_prose(slug, m, dropped):
    """Beat numbers in the 06-shotlist prose *below* the spine table — best
    effort: 'beat N', 'beats N, M', 'bN' tokens (not the table rows themselves)."""
    f = EP_DIR / slug / "06-shotlist.md"
    full = f.read_text(encoding="utf-8")
    cut = full.index("## Detalle") if "## Detalle" in full else full.index("## Gate") if "## Gate" in full else len(full)
    before, after = full[:cut], full[cut:]

    def repl(mo):
        pre, nums = mo.group(1), mo.group(2)
        outn = [str(m[int(t)]) for t in re.split(r"[,\s·]+", nums) if t.isdigit() and int(t) in m]
        return pre + ", ".join(outn) if outn else pre.rstrip()

    after = re.sub(r"\b(beats?\s+)([\d]+(?:[,\s·]+\d+)*)", repl, after, flags=re.I)
    after = re.sub(r"\bb(\d+)\b", lambda x: f"b{m[int(x.group(1))]}" if int(x.group(1)) in m else x.group(0), after)
    f.write_text(before + after, encoding="utf-8")


def _remap_assets_md(slug, m, dropped):
    f = EP_DIR / slug / "07-assets.md"
    if not f.exists():
        return
    out = []
    for ln in f.read_text(encoding="utf-8").splitlines():
        c = ln.split("|")
        # Manifiesto row: | # | Beat(s) | ...  -> col 2 is the beat list
        if len(c) >= 4 and c[1].strip() and c[2].strip() and not c[1].strip().startswith(("#", "-", "Campo", ":")):
            remapped = _remap_beatlist(c[2], m)
            if remapped != c[2].strip():
                c[2] = f" {remapped} "
                ln = "|".join(c)
        out.append(ln)
    f.write_text("\n".join(out) + "\n", encoding="utf-8")


# ─────────────────────────────────────────────────── fetch / pin / picks
def fetch_new(slug, n, src):
    """Fetch a URL / read a local path -> assets/<sub>/swap_<n>_<hash>.<ext>.
    The content-hashed name can't collide with another beat's asset id (the old
    beat<n>_custom_<n> scheme clashed when picks and spine numbering diverged).
    Returns (asset_id, tipo, rel_path)."""
    import hashlib
    keys = PA.load_env()
    url, s = src, "custom"
    if url.lower().startswith("http") and ("pexels.com" in url or "pixabay.com" in url):
        direct, dsrc = PA._resolve_media_page(url, keys)
        if direct:
            url, s = direct, dsrc
    data, final = PA._fetch(url, s)
    if data is None:
        raise SystemExit(f"no se pudo traer el recurso: {final}")
    ext = PA._ext_for(data, final, s)
    sub = "video" if ext in VIDEO_EXT else "archive"
    ass = EP_DIR / slug / "assets"
    h = hashlib.sha1(data).hexdigest()[:8]
    aid = f"swap_{n}_{h}"
    # drop this beat's earlier swap files (a different extension elsewhere would
    # shadow the new one — _asset_index scans video/ before archive/)
    for old in ass.glob(f"*/swap_{n}_*"):
        old.unlink(missing_ok=True)
    (ass / "_proxy").mkdir(exist_ok=True)
    for p in (ass / "_proxy").glob(f"swap_{n}_*"):
        p.unlink(missing_ok=True)
    (ass / sub).mkdir(parents=True, exist_ok=True)
    (ass / sub / f"{aid}{ext}").write_bytes(data)
    return aid, ("stock" if ext in VIDEO_EXT else "archivo"), f"assets/{sub}/{aid}{ext}"


def pin_asset(slug, asset_id, rel_path):
    f = EP_DIR / slug / "assets" / "_index.json"
    idx = {}
    if f.exists():
        try:
            idx = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    idx = {k: v for k, v in idx.items() if (EP_DIR / slug / v).exists()}
    idx[asset_id] = rel_path
    f.write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")


def patch_picks(slug, n, resource):
    f = EP_DIR / slug / "07-picks.txt"
    if not f.exists():
        return
    lines = f.read_text(encoding="utf-8").splitlines()
    row = f"{n}\tcustom:{n}\t{resource}"
    for i, ln in enumerate(lines):
        c = ln.split("\t")
        if len(c) >= 2 and c[0].strip() == str(n) and not c[0].startswith("#"):
            lines[i] = row
            f.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    for i, ln in enumerate(lines):
        if ln.strip().startswith("# --- BEATS"):
            lines.insert(i + 1, row)
            break
    else:
        lines.append(row)
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")


def add_assets_md_row(slug, beat_n, desc, src_note):
    f = EP_DIR / slug / "07-assets.md"
    if not f.exists():
        return
    lines = f.read_text(encoding="utf-8").splitlines()
    # find the last row of the Manifiesto table
    last = None
    inm = False
    for i, ln in enumerate(lines):
        if ln.strip().startswith("## Manifiesto"):
            inm = True
        elif inm and ln.startswith("## "):
            break
        elif inm and ln.lstrip().startswith("|") and not set(ln) <= set("|-: "):
            last = i
    if last is None:
        return
    row = (f"| + | {beat_n} | {desc} | {src_note} | por confirmar | — | por confirmar | "
           f"full-frame | **añadido en la sala** |")
    lines.insert(last + 1, row)
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")


def add_sourcelog_stub(slug, beat_n, claim):
    f = EP_DIR / slug / "03-source-log.csv"
    if not f.exists():
        return None
    rows = list(csv.reader(io.StringIO(f.read_text(encoding="utf-8"))))
    ids = [r[0] for r in rows[1:] if r and re.match(r"S\d+", r[0])]
    nxt = f"S{max((int(x[1:]) for x in ids), default=0) + 1:02d}"
    new = [nxt, claim, "", "", "", "", "C", "", "", "", "PENDIENTE — rellenar",
           f"stub creado en la sala para el beat {beat_n} — completar fuente y derechos antes del render"]
    buf = io.StringIO()
    csv.writer(buf).writerows(rows + [new])
    f.write_text(buf.getvalue(), encoding="utf-8")
    return nxt


# ─────────────────────────────────────────────────── rebuild
def _rebuild(slug):
    r = subprocess.run([sys.executable, str(TOOLS / "assemble.py"), slug, "--timeline-only"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        return "assemble.py falló: " + (r.stderr or r.stdout)[-300:]
    return None


def _beat_json(slug, n):
    d = json.loads((EP_DIR / slug / "09-timeline.json").read_text(encoding="utf-8"))
    b = next((x for x in d["beats"] if x["n"] == n), None)
    if not b:
        return {"n": n, "state": "merged", "note": "el beat se fusionó con un vecino al re-alinear"}
    return {"n": n, "asset": b.get("asset"), "file": b.get("file"), "state": b.get("state"),
            "tipo": b.get("kind"), "motion": b.get("motion")}


# ─────────────────────────────────────────────────── operations
def op_set(slug, n, asset=None, src=None):
    row = beat_row(slug, n)
    if not row:
        return {"error": f"beat {n} no está en la espina"}
    if row["tipo"] in NO_ASSET:
        return {"error": f"el beat {n} es «{row['tipo']}» — no lleva asset que cambiar"}
    tipo = None
    if src:
        asset, tipo, rel = fetch_new(slug, n, src)
        pin_asset(slug, asset, rel)
        patch_picks(slug, n, rel)
    elif asset:
        lib = {a["id"]: a for a in asset_library(slug)}
        if asset not in lib:
            return {"error": f"«{asset}» no está en assets/ — pega una ruta/URL"}
        tipo = lib[asset]["kind"]
    else:
        return {"error": "falta --asset o --src"}
    cells = {"asset": asset, "tipo": tipo} if tipo else {"asset": asset}
    if (row.get("marker") or "").upper() == "SPLIT":
        cells["marker"] = "—"           # 2nd half of a split, now reassigned
    _patch_cells(slug, n, cells)
    err = _rebuild(slug)
    return {"error": err} if err else {**_beat_json(slug, n), "was": row["asset"]}


def op_clear(slug, n):
    row = beat_row(slug, n)
    if not row:
        return {"error": f"beat {n} no está en la espina"}
    if row["tipo"] in NO_ASSET:
        return {"error": f"el beat {n} ya no lleva visual («{row['tipo']}»)"}
    cells = {"asset": "—", "rotulo": "—"}
    if (row.get("marker") or "").upper() == "SPLIT":
        cells["marker"] = "—"
    _patch_cells(slug, n, cells)
    err = _rebuild(slug)
    return {"error": err} if err else {**_beat_json(slug, n), "note": "visual quitado — beat sin cubrir"}


def op_merge(slug, n, into):
    row = beat_row(slug, n)
    if not row:
        return {"error": f"beat {n} no está en la espina"}
    _, lines, s, e = _spine(slug)
    nums = [int(c[1].strip()) for _, c in _data_rows(lines, s, e)]
    if n not in nums:
        return {"error": f"beat {n} no está"}
    i = nums.index(n)
    j = i - 1 if into == "prev" else i + 1
    if j < 0 or j >= len(nums):
        return {"error": f"no hay vecino «{into}»"}
    keep = beat_row(slug, nums[j])
    # the kept neighbour's frag absorbs this beat's frag (align anchors the join)
    a, b = (keep["frag"], row["frag"]) if into == "next" else (row["frag"], keep["frag"])
    merged_frag = f"{a.strip('«»')} {b.strip('«»')}".strip()
    _patch_cells(slug, keep["n"], {"frag": merged_frag})
    freeze_resolutions(slug)
    renumber(slug, dropped={n})
    err = _rebuild(slug)
    if err:
        return {"error": err}
    d = json.loads((EP_DIR / slug / "09-timeline.json").read_text(encoding="utf-8"))
    return {"ok": True, "beats": len(d["beats"]),
            "note": f"beat {n} fusionado en el {'anterior' if into == 'prev' else 'siguiente'}"}


def op_del(slug, n):
    if not beat_row(slug, n):
        return {"error": f"beat {n} no está en la espina"}
    freeze_resolutions(slug)
    renumber(slug, dropped={n})
    err = _rebuild(slug)
    if err:
        return {"error": err}
    d = json.loads((EP_DIR / slug / "09-timeline.json").read_text(encoding="utf-8"))
    return {"ok": True, "beats": len(d["beats"]), "note": f"beat {n} eliminado"}


def _clear_overrides(slug, ns, keys):
    """Drop edit-room geometry overrides (dur_lock / slot) from given beats in
    09-timeline.json — after a split the old lock no longer describes the beat."""
    f = EP_DIR / slug / "09-timeline.json"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    for b in d.get("beats", []):
        if b.get("n") in ns:
            for k in keys:
                b.pop(k, None)
    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def _extend_assetlist(slug, n):
    """After splitting beat n, beat n+1 reuses the same asset — widen the
    07-assets.md Manifiesto 'Beat(s)' entry ('n' -> 'n–n+1', 'x–n' -> 'x–n+1')."""
    f = EP_DIR / slug / "07-assets.md"
    if not f.exists():
        return
    out, changed = [], False
    for ln in f.read_text(encoding="utf-8").splitlines():
        c = ln.split("|")
        if (len(c) >= 4 and c[1].strip() and c[2].strip()
                and not c[1].strip().startswith(("#", "-", "Campo", ":"))):
            toks = [t.strip() for t in c[2].split(",")]
            new = []
            for t in toks:
                if t == str(n):
                    new.append(f"{n}–{n + 1}")
                elif re.match(rf"^\d+\s*[–-]\s*{n}$", t):
                    new.append(re.sub(rf"{n}$", str(n + 1), t))
                else:
                    new.append(t)
            if new != toks:
                c[2] = f" {', '.join(new)} "
                ln = "|".join(c)
                changed = True
        out.append(ln)
    if changed:
        f.write_text("\n".join(out) + "\n", encoding="utf-8")


def op_split(slug, n, at):
    """Split beat <n> into two contiguous beats at VO-time <at> (seconds). Both
    halves keep the same asset — a held shot you then reassign on the 2nd half.
    Timing is taken from the word list, so it doesn't hinge on a frag guess."""
    ep = EP_DIR / slug
    row = beat_row(slug, n)
    if not row:
        return {"error": f"beat {n} no está en la espina"}
    try:
        tj = json.loads((ep / "09-timeline.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"error": "no encuentro 09-timeline.json — reconstruye la línea primero"}
    tb = next((b for b in tj.get("beats", []) if b.get("n") == n), None)
    if not tb:
        return {"error": f"el beat {n} no está en la línea (¿se fusionó al re-alinear?)"}
    vin, vout = float(tb["in"]), float(tb["out"])
    span = vout - vin
    at = float(at)
    if not (vin + 0.2 < at < vout - 0.2):
        return {"error": "el cabezal no está dentro del beat"}

    # snap the cut to the nearest spoken-word boundary inside the beat
    words = A.load_words(ep)
    inside = [w for w in words if vin - 0.05 <= w["t"] < vout]
    cut = at
    if inside:
        cut = min((w["t"] for w in inside), key=lambda t: abs(t - at))
        cut = min(max(cut, vin + 0.2), vout - 0.2)

    floor = (A.MIN_ACAMARA if row["tipo"] in A.ACAMARA
             else A.MIN_GRAPHIC if row["tipo"] in A.GRAPHIC else A.MIN_BEAT)
    if cut - vin < floor or vout - cut < floor:
        return {"error": f"cada mitad debe durar ≥ {floor:g}s — acerca el cabezal al centro del beat"}

    # split the planned dur in the same proportion as the aligned cut
    frac = (cut - vin) / span
    dur_plan = float(re.sub(r"[^\d.]", "", row["dur"]) or span)
    dur1 = max(1, round(dur_plan * frac))
    dur2 = max(1, round(dur_plan) - dur1) or 1

    def _slice(lo, hi, cap=16):
        return " ".join(w["w"] for w in inside if lo <= w["t"] < hi).split()[:cap]
    frag_a = " ".join(_slice(vin - 0.05, cut)) or row["frag"].strip("«»")
    frag_b = " ".join(_slice(cut, vout)) or "(sigue el plano)"

    freeze_resolutions(slug)

    fdst, lines, s, e = _spine(slug)
    col = {"dur": 3, "frag": 10}
    _li = ins_at = None
    for li, c in _data_rows(lines, s, e):
        if int(c[1].strip()) == n:
            c[col["dur"]] = f" {dur1} "
            c[col["frag"]] = f" «{frag_a.strip('«»')}» "
            lines[li] = "|".join(c)
            _li, ins_at = li, li + 1
            break
    if ins_at is None:
        return {"error": f"no encuentro la fila del beat {n}"}
    a_sec = A._secs(row["in"])
    b_in = A._fmt((a_sec if a_sec is not None else vin) + dur1)
    lines.insert(ins_at, _row("0", b_in, dur2, row["section"], row["tipo"],
                              row["asset"], "—", row["motion"] or "cut", "SPLIT", frag_b))
    fdst.write_text("\n".join(lines) + "\n", encoding="utf-8")

    renumber(slug)                                   # placeholder -> n+1, downstream +1
    _clear_overrides(slug, {n}, ("dur_lock", "slot"))
    err = _rebuild(slug)
    if err:
        return {"error": err}
    _extend_assetlist(slug, n)
    d = json.loads((ep / "09-timeline.json").read_text(encoding="utf-8"))
    got = sorted((b for b in d["beats"] if b.get("n") in (n, n + 1)), key=lambda b: b["n"])
    return {"ok": True, "n": n + 1, "beats": len(d["beats"]),
            "note": f"beat {n} partido — 2ª mitad = beat {n + 1}",
            "halves": [{"n": b["n"], "dur": round(b["out"] - b["in"], 1)} for b in got]}


def op_add(slug, after, frag, kind, section=None, marker=None, dur=None, asset=None, src=None):
    ref = beat_row(slug, after)
    if not ref:
        return {"error": f"no hay beat {after} para insertar después"}
    if not (frag or "").strip():
        return {"error": "un beat nuevo necesita un fragmento de la voz (--frag)"}
    kind = (kind or "archivo").lower()
    section = (section or ref["section"]).lower()
    dur = str(int(float(dur))) if dur else ref["dur"]

    freeze_resolutions(slug)
    # insert a placeholder-numbered row right after `after`, then renumber
    f, lines, s, e = _spine(slug)
    ins_at = None
    for li, c in _data_rows(lines, s, e):
        if int(c[1].strip()) == after:
            ins_at = li + 1
            break
    tmp_asset = "—"
    row_txt = _row("0", ref["in"], dur, section, kind, tmp_asset, "—",
                   "push" if kind not in NO_ASSET else "cut", marker or "—", frag)
    lines.insert(ins_at, row_txt)
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    m = renumber(slug)                     # placeholder 0 becomes after+1, rest shift
    new_n = after + 1

    # wire the asset now that the beat has its real number
    src_note = ""
    if src:
        aid, tipo, rel = fetch_new(slug, new_n, src)
        pin_asset(slug, aid, rel)
        patch_picks(slug, new_n, rel)
        _patch_cells(slug, new_n, {"asset": aid, "tipo": tipo})
        src_note = f"traído en la sala: {src}"
    elif asset:
        lib = {x["id"]: x for x in asset_library(slug)}
        if asset in lib:
            _patch_cells(slug, new_n, {"asset": asset, "tipo": lib[asset]["kind"]})
            src_note = f"asset existente: {asset}"

    if kind in ("archivo", "stock", "kb") and src_note:
        add_assets_md_row(slug, new_n, frag.strip("«»")[:70], src_note or "por confirmar")
        stub = add_sourcelog_stub(slug, new_n, f"[beat {new_n}] {frag.strip('«»')[:120]}")
    else:
        stub = None

    err = _rebuild(slug)
    if err:
        return {"error": err}
    d = json.loads((EP_DIR / slug / "09-timeline.json").read_text(encoding="utf-8"))
    return {"ok": True, "n": new_n, "beats": len(d["beats"]),
            "sourcelog": stub, "note": f"beat {new_n} añadido"}


def _patch_cells(slug, n, cells):
    """Set named cells (asset / tipo / rotulo / motion / marker / frag / section /
    dur / in) of beat <n>'s spine row."""
    col = {"in": 2, "dur": 3, "section": 4, "tipo": 5, "asset": 6,
           "rotulo": 7, "motion": 8, "marker": 9, "frag": 10}
    f, lines, s, e = _spine(slug)
    for li, c in _data_rows(lines, s, e):
        if int(c[1].strip()) != n:
            continue
        for k, v in cells.items():
            if k not in col:
                continue
            v = f"«{v.strip('«»')}»" if k == "frag" else (v or "—")
            c[col[k]] = f" {v} "
        lines[li] = "|".join(c)
        f.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    raise SystemExit(f"no encuentro el beat {n}")


# ─────────────────────────────────────────────────── CLI
def _arg(a, name):
    return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else None


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    slug = a[0].strip("/\\")
    try:
        if "--list" in a:
            print(json.dumps(asset_library(slug), ensure_ascii=False))
        elif "--set" in a:
            print(json.dumps(op_set(slug, int(_arg(a, "--set")),
                                    _arg(a, "--asset"), _arg(a, "--src")), ensure_ascii=False))
        elif "--clear" in a:
            print(json.dumps(op_clear(slug, int(_arg(a, "--clear"))), ensure_ascii=False))
        elif "--merge" in a:
            print(json.dumps(op_merge(slug, int(_arg(a, "--merge")),
                                      _arg(a, "--into") or "prev"), ensure_ascii=False))
        elif "--del" in a:
            print(json.dumps(op_del(slug, int(_arg(a, "--del"))), ensure_ascii=False))
        elif "--split" in a:
            print(json.dumps(op_split(slug, int(_arg(a, "--split")),
                                      float(_arg(a, "--at") or 0)), ensure_ascii=False))
        elif "--add" in a:
            print(json.dumps(op_add(slug, int(_arg(a, "--after")), _arg(a, "--frag") or "",
                                    _arg(a, "--kind"), _arg(a, "--section"), _arg(a, "--marker"),
                                    _arg(a, "--dur"), _arg(a, "--asset"), _arg(a, "--src")),
                             ensure_ascii=False))
        else:
            print(__doc__)
            sys.exit(2)
    except SystemExit as ex:
        if isinstance(ex.code, str):
            print(json.dumps({"error": ex.code}, ensure_ascii=False))
            sys.exit(1)
        raise
