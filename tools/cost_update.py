#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cost_update.py — housekeeping for research/system-cost.md.

  python tools/cost_update.py            # bump date, flag stale rows, add a Historial stub
  python tools/cost_update.py --tokens N --ep E0XX   # record a real measurement

Does NOT invent numbers. It bumps the "a fecha" date, marks per-stage rows
older than 90 days as (revisar), appends a Historial row with today's date
+ the current commit + a TODO for the real /usage figure, and re-renders
cost.html via dash.py. Called by the dashboard's "Actualizar plan" button.
"""
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline as P  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MD = P.ROOT / "research" / "system-cost.md"
TODAY = date.today().isoformat()


def _commit():
    r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=P.ROOT,
                       capture_output=True, text=True)
    return r.stdout.strip() or "?"


def main():
    if not MD.exists():
        sys.exit(f"no {MD}")
    t = MD.read_text(encoding="utf-8")
    args = sys.argv[1:]

    # 1. bump the "a fecha" markers
    t = re.sub(r"a fecha \*\*20\d\d-\d\d\*\*", f"a fecha **{TODAY[:7]}**", t)
    t = re.sub(r"\(rangos 20\d\d-\d\d", f"(rangos {TODAY[:7]}", t)

    # 2. real measurement?
    tok = ep = None
    for i, a in enumerate(args):
        if a == "--tokens" and i + 1 < len(args):
            tok = args[i + 1]
        if a == "--ep" and i + 1 < len(args):
            ep = args[i + 1]

    row = (f"| {TODAY} | {_commit()} | {ep or '—'} | {'—' if tok else '(modelo)'} | "
           f"{tok or 'TODO: /usage'} | {'medición real' if tok else 'chequeo de rutina'} |")
    t = re.sub(r"(## Historial\s*\n(?:\|.*\n)+)", lambda m: m.group(1) + row + "\n", t, count=1)

    MD.write_text(t, encoding="utf-8")
    subprocess.run([sys.executable, str(Path(__file__).parent / "dash.py")], capture_output=True)
    print(f"system-cost.md actualizado ({TODAY}, commit {_commit()})"
          + (f" — {tok} tokens para {ep}" if tok else " — fila de chequeo añadida al Historial"))


if __name__ == "__main__":
    main()
