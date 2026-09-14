#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
undo_take.py — undo a Stage 8 take upload: delete the take and everything
Stage 9 generated *from it*, put the episode back at Stage 8 (gate abierto)
so a corrected/different take can be uploaded in its place.

Deletes, under episodes/<slug>/:
  - the take itself: assets/<EPID>-vo.<ext>
  - everything trim_talk.py/match_audio.py derived from it: assets/<EPID>-vo.*
    (words.raw.json, cuts.json/.md, review.html/.m4a, peaks.json, trimmed.mp4,
    words.json, pickups*.json, pickup-room.html, apply.done*)
  - accepted-pickup audio: assets/pickups/<EPID>-vo_pick*, _ref_pick*
  - if Stage 9 had already started (all at the episode root, not assets/):
    09-timeline.json (+ its .bak.json backups), 09-edit.html, 09-decisions.txt,
    09-vo.m4a, 09-take.mp4, 09-rough.mp4, 09-rough.progress/.done(.fail),
    09-final.progress/.done(.fail), 09-resync.flag, any rendered master
    <slug>-v*.mp4, _exports/stage09.json

Never touches: Stage 7 assets, Ken Burns clips (assets/kb/ — those come from
stills, not the take), graphics, or anything from an earlier stage.

Usage:
    python tools/undo_take.py E0XX
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline as P  # noqa: E402


def undo_take(epid):
    epp = P.ep_path(epid)
    if not epp.is_dir():
        sys.exit(f"no existe {epp}")
    assets = epp / "assets"
    removed = []

    def rm(p):
        if p.exists():
            p.unlink()
            removed.append(p.relative_to(epp).as_posix())

    if assets.is_dir():
        # glob's "*" matches dots too, so this one pattern catches the take
        # itself (<EPID>-vo.mp4) AND every multi-suffix file trim_talk.py /
        # match_audio.py derived from it (…-vo.words.raw.json, …-vo.cuts.json,
        # …-vo.review.html, …-vo.trimmed.mp4, …-vo.pickups.accepted.json, …).
        for f in sorted(assets.glob(f"{epid}-vo.*")):
            rm(f)
        pick_dir = assets / "pickups"
        if pick_dir.is_dir():
            for f in list(pick_dir.glob(f"{epid}-vo_pick*")) + list(pick_dir.glob("_ref_pick*")):
                rm(f)

    tl = epp / "09-timeline.json"
    stage9_started = tl.exists()
    if stage9_started:
        rm(tl)
        for f in epp.glob("09-timeline.*.*.bak.json"):
            rm(f)
        for name in ("09-edit.html", "09-decisions.txt", "09-resync.flag",
                     "09-rough.progress", "09-rough.done", "09-rough.done.fail",
                     "09-final.progress", "09-final.done", "09-final.done.fail"):
            rm(epp / name)
        for name in ("09-vo.m4a", "09-take.mp4", "09-rough.mp4"):
            rm(epp / name)
        for f in epp.glob(f"{epp.name}-v*.mp4"):
            rm(f)
        rm(epp / "_exports" / "stage09.json")

    was = P.read_status().get(epid, {})
    P.set_ep(epid, stage=8, gate="abierto",
             notes="toma deshecha (undo_take.py) — pendiente de subir una toma nueva")
    P.dequeue(epid, 9)
    return removed, was.get("stage")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: python tools/undo_take.py E0XX")
    epid = sys.argv[1].strip()
    removed, prev_stage = undo_take(epid)
    if not removed:
        print(f"{epid}: no había toma ni nada derivado de ella que borrar (ya estaba limpio)")
    else:
        print(f"{epid}: {len(removed)} archivo(s) borrados (venía de Stage {prev_stage}):")
        for r in removed:
            print(f"  - {r}")
    print(f"{epid} vuelve a Stage 8, gate abierto — listo para subir una toma nueva")
