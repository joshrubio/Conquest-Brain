#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
delete_episode.py — discard an episode's production entirely (the idea isn't
wanted anymore). Moves episodes/<slug>/ to episodes/_trash/<slug>-<ts>/ rather
than a true rm -rf: gone from _STATUS.md, the dashboard, the queue and the
idea-pool either way, but a misclick has a way back instead of being final.

Removes the episode's row from _STATUS.md, drops any queued /_queue.json
tasks for it, and marks its idea-pool row (traced via _exports/stage00.json's
idea_id, same lookup Stage-11 publish uses) as "descartada" — so the idea
doesn't sit forever as "en producción" for a project that no longer exists.

Usage:
    python tools/delete_episode.py E0XX --confirm
        --confirm is required — without it this refuses to touch anything.
"""
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import advance as A  # noqa: E402
import pipeline as P  # noqa: E402


def delete_episode(epid, confirm=False):
    if not confirm:
        sys.exit("delete_episode necesita --confirm — esto saca el episodio de producción")
    data = P.read_status()
    if epid not in data:
        sys.exit(f"{epid} no está en _STATUS.md")
    epp = P.ep_path(epid)
    if not epp.is_dir():
        sys.exit(f"no existe {epp}")

    idea_id = A._idea_id_of(epid)

    trash = P.EP_DIR / "_trash"
    trash.mkdir(exist_ok=True)
    dest = trash / f"{epp.name}-{int(time.time())}"
    shutil.move(str(epp), str(dest))

    data.pop(epid, None)
    P.write_status(data)
    P.write_queue([x for x in P.read_queue() if x["ep"] != epid])
    A._mark_pool(idea_id, f"descartada ({epid} borrado)")

    return dest


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit("uso: python tools/delete_episode.py E0XX --confirm")
    epid = a[0].strip()
    dest = delete_episode(epid, confirm="--confirm" in a)
    print(f"{epid} movido a {dest.relative_to(P.ROOT).as_posix()} — quitado de _STATUS.md, "
          f"de la cola, y su idea (si se rastreó) marcada como descartada")
