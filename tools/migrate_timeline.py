#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""migrate_timeline.py — one-shot: 09-timeline.json schema 1 → schema 2.

Schema 1 is the *derived* timeline (parse_spine + align rebuilt it every save).
Schema 2 is the *authored* timeline (brain/16 «timeline canónica»): each beat
owns its `dur`, align() only seeds. The migration freezes the current cut —
every beat's authored `dur` is its present on-screen length, so the first
schema-2 rebuild reproduces the same timeline to within a frame.

  python tools/migrate_timeline.py E0XX-slug          # migrate in place (+ .v1.bak)
  python tools/migrate_timeline.py E0XX-slug --check   # report only, write nothing

Non-regression checks (any failure → auto-rollback, non-zero exit):
  1. rebuild_timeline() reloads it: same beat count, unique ids, order kept
  2. every beat's derived in/out within 1 frame of the v1 file
  3. total within 1 frame of the v1 total
  4. asset coverage identical — no beat flips ok → uncovered; music unchanged
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import assemble as A  # noqa: E402

FRAME = 1.0 / A.FPS


def migrate(slug, check_only=False):
    ep = A.EP_DIR / slug
    tj = ep / "09-timeline.json"
    if not tj.exists():
        raise SystemExit(f"no existe {tj}")
    v1 = json.loads(tj.read_text(encoding="utf-8"))
    if v1.get("schema", 1) >= 2:
        raise SystemExit(f"{tj.name} ya es schema {v1['schema']} — nada que migrar")

    old = v1.get("beats", [])
    if not old:
        raise SystemExit("la timeline v1 no tiene beats")
    ns = [b["n"] for b in old]
    if len(ns) != len(set(ns)):
        raise SystemExit(f"hay `n` duplicados en la timeline v1: {sorted(ns)}")

    words = A.load_words(ep)
    vo_end_words = A._vo_end_from_words(words) if words else 0.0
    vo_end = round(v1.get("total") or old[-1]["out"], 2)
    if vo_end_words and abs(vo_end_words - vo_end) > 0.5:
        print(f"  ⚠ total v1 {vo_end:.2f}s vs voz {vo_end_words:.2f}s difieren "
              f"{abs(vo_end_words - vo_end):.2f}s — uso el total v1 (el corte manda)")

    # freeze: authored dur = current on-screen length; ids from the spine rows
    src = [dict(b) for b in old]
    ab = A.to_authored_beats(src, vo_end)
    doc = A.authored_doc(
        slug, ab, vo_end=vo_end, total=vo_end,
        words_sig=A._words_sig(words), aligned=bool(v1.get("aligned")),
        music=dict(v1.get("music", {})),
    )
    doc["generated"] = v1.get("generated", doc["generated"])
    doc["seeded"] = v1.get("generated") or doc["seeded"]

    old_io = {b["n"]: (b["in"], b["out"]) for b in old}
    old_cov = {b["n"]: b.get("state") for b in old}

    if check_only:
        _report_plan(old, ab, vo_end)
        _verify(ep, tj, doc, old_io, old_cov, v1, write=False)
        return

    bak = ep / "09-timeline.v1.bak.json"
    shutil.copy2(tj, bak)
    tj.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"escrito  {tj.relative_to(A.ROOT)}  (schema 2, {len(ab)} beats)  ·  respaldo {bak.name}")

    try:
        _verify(ep, tj, doc, old_io, old_cov, v1, write=True)
    except AssertionError as e:
        shutil.copy2(bak, tj)
        raise SystemExit(f"\n✗ chequeo falló: {e}\n  timeline restaurada desde {bak.name}")
    print("\n✓ migración verificada — el corte se reproduce dentro de 1 frame")
    print(f"  render de control:  python tools/assemble.py {slug} --rough   (compara con 09-rough.mp4)")


def _report_plan(old, ab, vo_end):
    print(f"  {len(old)} beats  ·  vo_end {vo_end:.2f}s")
    print(f"  ids: b{old[0]['n']} … b{old[-1]['n']}")
    dl = sum(1 for b in old if b.get("dur_lock"))
    sl = sum(1 for b in old if isinstance(b.get("slot"), (int, float)))
    mg = sum(1 for b in old if b.get("merged"))
    print(f"  overrides horneados: {dl} dur_lock → dur · {sl} slot → orden · {mg} merged")


def _verify(ep, tj, doc, old_io, old_cov, v1, write):
    # 1. reload through the real rebuild path
    if write:
        rebuilt = A.rebuild_timeline(doc["slug"])
    else:
        # simulate without touching disk
        beats = [dict(b) for b in doc["beats"]]
        A.resolve(ep, beats)
        A._derive_motion(beats)
        A.derive_times(beats, A.get_vo_end(ep, doc["vo_end"]))
        A.flag_rhythm(beats)
        rebuilt = {**doc, "beats": [A._authored_beat(b) for b in beats],
                   "total": round(beats[-1]["out"], 2)}
    rb = rebuilt["beats"]
    assert len(rb) == len(v1["beats"]), f"beat count {len(rb)} != {len(v1['beats'])}"
    ids = [b["id"] for b in rb]
    assert len(ids) == len(set(ids)), "ids no únicos tras rebuild"
    assert ids == [f"b{b['n']}" for b in v1["beats"]], "el orden de los beats cambió"

    # 2. timing within a frame
    worst = 0.0
    for b in rb:
        n = A._idn(b["id"])
        oi, oo = old_io[n]
        d = max(abs(oi - b["in"]), abs(oo - b["out"]))
        worst = max(worst, d)
        assert d <= FRAME + 1e-6, f"beat b{n}: in/out se movió {d*1000:.0f} ms (>1 frame)"
    print(f"  timing: desviación máx {worst*1000:.0f} ms  (1 frame = {FRAME*1000:.0f} ms)")

    # 3. total
    assert abs(rebuilt["total"] - (v1.get("total") or 0)) <= FRAME + 1e-6, \
        f"total {rebuilt['total']} vs {v1.get('total')}"

    # 4. coverage + music
    flipped = [A._idn(b["id"]) for b in rb
               if old_cov.get(A._idn(b["id"])) == "ok" and b.get("state") == "uncovered"]
    assert not flipped, f"beats que perdieron su asset: {flipped}"
    assert rebuilt["music"].get("bed") == v1.get("music", {}).get("bed"), "music.bed cambió"
    for k in ("bed_db", "vo_gain_db", "duck_db"):
        assert rebuilt["music"].get(k) == v1["music"].get(k), f"music.{k} cambió"
    print(f"  cobertura: {sum(1 for b in rb if b.get('state')=='ok')}/{len(rb)} ok  ·  music intacta")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    migrate(args[0], check_only="--check" in args)
