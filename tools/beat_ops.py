#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""beat_ops.py — first-class structural edits on the schema-2 timeline.

Operates directly on `episodes/<slug>/09-timeline.json`, keyed by the stable
beat `id`. Never touches the shotlist spine. Every op rewrites the authored
beats, then `assemble.rebuild_timeline` re-derives in/out on the VO backbone
and re-resolves files. Adding or splitting a beat needs no verbatim `frag` —
the timeline owns its own structure now (brain/16 «timeline canónica»).

  python tools/beat_ops.py E0XX-slug --add --after b7 --kind stock [--section "acto 1"] [--dur 4]
  python tools/beat_ops.py E0XX-slug --split b9 --at 128.4
  python tools/beat_ops.py E0XX-slug --merge b9 --into prev|next
  python tools/beat_ops.py E0XX-slug --del b9 [--absorb ripple|prev]
  python tools/beat_ops.py E0XX-slug --setdur b9 --dur 7.5
  python tools/beat_ops.py E0XX-slug --dup b9
  python tools/beat_ops.py E0XX-slug --reorder b3,b1,b2,...
  python tools/beat_ops.py E0XX-slug --tidy [--merge-same-file]
"""
import contextlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assemble as A  # noqa: E402

DEFAULT_DUR = {"archivo": 4.0, "stock": 4.0, "kb": 5.0, "ia": 6.0,
               "gráfico": 12.0, "grafico": 12.0, "acamara": 6.0, "negro": 3.0}


def _floor(kind):
    if kind in A.ACAMARA:
        return A.MIN_ACAMARA
    if kind in A.GRAPHIC:
        return A.MIN_GRAPHIC
    return A.MIN_BEAT


def _load(slug):
    ep = A.EP_DIR / slug
    tj = ep / "09-timeline.json"
    if not tj.exists():
        raise SystemExit(f"no existe {tj} — siembra la línea primero")
    data = json.loads(tj.read_text(encoding="utf-8"))
    if data.get("schema", 1) < 2:
        raise SystemExit(
            f"{tj.name} es schema 1 — migra antes de editar por beat:\n"
            f"  python tools/migrate_timeline.py {slug}")
    return ep, tj, data


def _finish(slug, tj, data):
    tj.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):    # keep assemble's chatter off our JSON
        return A.rebuild_timeline(slug)


def _idx(beats, bid):
    for i, b in enumerate(beats):
        if b.get("id") == bid:
            return i
    raise SystemExit(f"no hay beat con id {bid}")


def _mint(data):
    bid = f"b{data.get('next_id', 1)}"
    data["next_id"] = data.get("next_id", 1) + 1
    return bid


# ── ops ───────────────────────────────────────────────────────────────────

def add(slug, after=None, kind="stock", section=None, dur=None, marker=None,
        vo_anchor="", asset=None):
    ep, tj, data = _load(slug)
    beats = data["beats"]
    at = (_idx(beats, after) + 1) if after else len(beats)
    ref = beats[min(at, len(beats) - 1)] if beats else {}
    nb = {
        "id": _mint(data),
        "dur": float(dur) if dur else DEFAULT_DUR.get(kind, 4.0),
        "section": section or ref.get("section", ""),
        "kind": kind,
        "asset": asset or "",
        "motion": "cut" if kind in A.ACAMARA or kind == "negro" else "push",
        "marker": (marker or "").upper(),
        "vo_anchor": vo_anchor or "",
    }
    beats.insert(at, nb)
    return _finish(slug, tj, data)


def split(slug, bid, at):
    ep, tj, data = _load(slug)
    beats = data["beats"]
    i = _idx(beats, bid)
    b = beats[i]
    b_in, b_out = b["in"], b["out"]
    at = float(at)
    fl = _floor(b["kind"])
    if not (b_in + fl <= at <= b_out - fl):
        raise SystemExit(
            f"el corte debe caer entre {b_in + fl:.1f}s y {b_out - fl:.1f}s "
            f"(cada mitad ≥ {fl:g}s)")
    # optional: snap to the nearest spoken word inside the beat
    words = [w for w in A.load_words(ep) if b_in <= w["t"] < b_out]
    if words:
        at = min(words, key=lambda w: abs(w["t"] - at))["t"]
        at = min(max(at, b_in + fl), b_out - fl)
    head = round(at - b_in, 3)
    tail = {
        "id": _mint(data), "dur": round(b_out - at, 3),
        "section": b["section"], "kind": b["kind"], "asset": b.get("asset", ""),
        "motion": b.get("motion", "push"), "marker": "SPLIT",
        "vo_anchor": " ".join(w["w"] for w in words if w["t"] >= at)[:120],
    }
    b["dur"] = head
    b["vo_anchor"] = " ".join(w["w"] for w in words if w["t"] < at)[:120] or b.get("vo_anchor", "")
    beats.insert(i + 1, tail)
    return _finish(slug, tj, data)


def merge(slug, bid, into="prev"):
    ep, tj, data = _load(slug)
    beats = data["beats"]
    i = _idx(beats, bid)
    j = i - 1 if into == "prev" else i + 1
    if not (0 <= j < len(beats)):
        raise SystemExit(f"no hay beat {into} de {bid} para fusionar")
    keep, drop = beats[j], beats[i]
    keep["dur"] = round(keep["dur"] + drop["dur"], 3)
    for k in ("asset", "marker", "vo_anchor", "label"):
        if not keep.get(k) and drop.get(k):
            keep[k] = drop[k]
    beats.pop(i)
    return _finish(slug, tj, data)


def delete(slug, bid, absorb="ripple"):
    ep, tj, data = _load(slug)
    beats = data["beats"]
    i = _idx(beats, bid)
    gone = beats.pop(i)
    if absorb == "prev" and i - 1 >= 0:
        beats[i - 1]["dur"] = round(beats[i - 1]["dur"] + gone["dur"], 3)
    # "ripple": everything downstream shifts up; the last beat's derived out
    # stays on vo_end (it grows) — flag_rhythm warns if that overstretches it
    if not beats:
        raise SystemExit("no puedes borrar el último beat de la línea")
    return _finish(slug, tj, data)


def set_dur(slug, bid, dur):
    ep, tj, data = _load(slug)
    beats = data["beats"]
    b = beats[_idx(beats, bid)]
    b["dur"] = round(float(dur), 3)
    b["dur_edited"] = True
    return _finish(slug, tj, data)


def duplicate(slug, bid):
    ep, tj, data = _load(slug)
    beats = data["beats"]
    i = _idx(beats, bid)
    clone = dict(beats[i])
    clone["id"] = _mint(data)
    clone.pop("marker", None)
    clone.pop("approved", None)
    clone.pop("fix", None)
    beats.insert(i + 1, clone)
    return _finish(slug, tj, data)


def reorder(slug, order):
    ep, tj, data = _load(slug)
    beats = data["beats"]
    by_id = {b["id"]: b for b in beats}
    if set(order) != set(by_id):
        raise SystemExit("el nuevo orden debe listar exactamente los mismos ids")
    data["beats"] = [by_id[i] for i in order]
    return _finish(slug, tj, data)


def reseed(slug, confirm=False):
    """«Re-sembrar desde shotlist» — discard every sala edit and rebuild the
    timeline from the spine + VO. Backs the current file up first."""
    if not confirm:
        raise SystemExit("reseed necesita confirm=true — descarta TODAS las ediciones de sala")
    import shutil
    import time
    f = A.EP_DIR / slug / "09-timeline.json"
    if f.exists():
        shutil.copy2(f, f.with_name(f"09-timeline.{int(time.time())}.bak.json"))
    with contextlib.redirect_stdout(io.StringIO()):
        return A.seed_timeline(slug, force=True)


def tidy(slug, merge_same_file=False):
    ep, tj, data = _load(slug)
    beats = data["beats"]
    before = len(beats)
    kept = A.tidy_subfloor([dict(b) for b in beats], data.get("total", 0),
                           merge_same_file=merge_same_file)
    for b in kept:
        b["dur"] = round(b["out"] - b["in"], 3)
    data["beats"] = [A._authored_beat(b) for b in kept]
    out = _finish(slug, tj, data)
    out["tidied"] = before - len(data["beats"])
    return out


# ── dispatch (used by serve.py /beat-op) ──────────────────────────────────

def run(slug, action, **kw):
    if "id" in kw:                       # the client keys beats by `id`; ops call it `bid`
        kw["bid"] = kw.pop("id")
    fn = {"add": add, "split": split, "merge": merge, "delete": delete,
          "del": delete, "setdur": set_dur, "set_dur": set_dur,
          "duplicate": duplicate, "dup": duplicate, "reorder": reorder,
          "tidy": tidy, "reseed": reseed}.get(action)
    if not fn:
        raise SystemExit(f"acción desconocida: {action}")
    return fn(slug, **kw)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    slug = a[0]

    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default

    if "--json" in a:                       # serve.py /beat-op: {"action": ..., ...}
        try:
            payload = json.loads(opt("--json") or "{}")
            action = payload.pop("action", "")
            tl = run(slug, action, **payload)
            resp = {"ok": True, "timeline": tl}
            if isinstance(tl, dict) and "tidied" in tl:
                resp["note"] = f"fusionados {tl.pop('tidied')} beats sub-mínimo"
            print(json.dumps(resp, ensure_ascii=False))
        except SystemExit as ex:
            print(json.dumps({"error": ex.code if isinstance(ex.code, str) else "error"},
                             ensure_ascii=False))
            sys.exit(1)
        sys.exit(0)

    if "--add" in a:
        add(slug, after=opt("--after"), kind=opt("--kind", "stock"),
            section=opt("--section"), dur=opt("--dur"), marker=opt("--marker"),
            asset=opt("--asset"))
    elif "--split" in a:
        split(slug, opt("--split"), opt("--at"))
    elif "--merge" in a:
        merge(slug, opt("--merge"), into=opt("--into", "prev"))
    elif "--del" in a:
        delete(slug, opt("--del"), absorb=opt("--absorb", "ripple"))
    elif "--setdur" in a:
        set_dur(slug, opt("--setdur"), opt("--dur"))
    elif "--dup" in a:
        duplicate(slug, opt("--dup"))
    elif "--reorder" in a:
        reorder(slug, opt("--reorder").split(","))
    elif "--tidy" in a:
        tidy(slug, merge_same_file="--merge-same-file" in a)
    else:
        print(__doc__)
        sys.exit(2)
