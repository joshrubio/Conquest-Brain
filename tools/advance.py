#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
advance.py — the gate engine. Folds a stage's exported decisions and moves
the episode to the next stage. Mechanical work only; anything that needs an
agent is put on episodes/_queue.json instead.

  python tools/advance.py fold E0XX     # fold the current stage's export -> gate 'firmado'
  python tools/advance.py next E0XX     # gate must be 'firmado' -> bump to next stage
  python tools/advance.py E0XX          # fold + next (as far as it can)
  python tools/advance.py --drain       # every episode: fold what's 'exportado', advance what's 'firmado' (<= auto)

serve.py calls `fold` on /finish and `next` on the dashboard's ▶ button.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline as P  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TEMPLATE = P.EP_DIR / "_TEMPLATE-episode-folder"


def _dash():
    subprocess.run([sys.executable, str(Path(__file__).parent / "dash.py")],
                   capture_output=True)


def _exp(epid, stage):
    return P.ep_path(epid) / "_exports" / f"stage{stage:02d}.json"


# ---------- folds (mechanical) ----------

def fold_idea(epid, d, payload):
    """Stage 0: create the episode folder from template, mark the idea-pool row."""
    ep = P.EP_DIR / f"{epid}-{d['slug']}" if not d["slug"].startswith(epid) else P.EP_DIR / d["slug"]
    if not ep.exists():
        shutil.copytree(TEMPLATE, ep)
    P.ensure_assets(epid)
    pool = P.ROOT / "ideas" / "idea-pool.md"
    if pool.exists() and payload.get("idea_id"):
        t = pool.read_text(encoding="utf-8")
        t = re.sub(rf"(\|\s*{re.escape(payload['idea_id'])}\s*\|.*?\|)([^|]*)(\|\s*)$",
                   rf"\1 en producción ({epid}) \3", t, flags=re.M)
        pool.write_text(t, encoding="utf-8")
    return True, "carpeta creada"


def fold_assets(epid, d, payload):
    """Stage 7: the picker already wrote 07-picks.txt; run the download."""
    picks = P.ep_path(epid) / "07-picks.txt"
    if not picks.exists():
        return False, "no 07-picks.txt"
    r = subprocess.run([sys.executable, str(Path(__file__).parent / "pull_assets.py"),
                        d["slug"] if d["slug"].startswith(epid) else f"{epid}-{d['slug']}", "--download"],
                       capture_output=True, text=True)
    return (r.returncode == 0), (r.stdout or r.stderr).strip().splitlines()[-1:][0] if (r.stdout or r.stderr) else "descargado"


def fold_retro(epid, d, payload):
    """Stage 12: append a KPI-log row to brain/07."""
    doc = P.ROOT / "brain" / "07-publishing-seo-metrics.md"
    if not doc.exists():
        return False, "no brain/07"
    t = doc.read_text(encoding="utf-8")
    m = payload.get("metrics", {})
    row = (f"| {epid} {d['title']} | {m.get('pub','—')} | {m.get('len','—')} | {m.get('views','—')} | "
           f"{m.get('avd','—')} | {m.get('ctr','—')} | {m.get('subs','—')} | {m.get('notes','')} |")
    t = re.sub(r"(## KPI log\s*\n(?:\|.*\n)+)", lambda mm: mm.group(1) + row + "\n", t, count=1)
    doc.write_text(t, encoding="utf-8")
    return True, "KPI log actualizado"


def fold_stash(epid, d, payload):
    """Formats that vary (research / edit / package): stash the export, queue the fold for the agent."""
    st = d["stage"]
    P.enqueue(epid, st, "fold", note=f"aplicar las decisiones de {P.STAGE[st]['name']} "
              f"(en {_exp(epid, st).relative_to(P.ROOT)}) al fichero fuente")
    return "queued", "decisiones en cola para plegar"


FOLDS = {"idea": fold_idea, "assets": fold_assets, "retro": fold_retro,
         "research": fold_stash, "edit": fold_stash, "package": fold_stash}


def do_fold(epid):
    data = P.read_status()
    if epid not in data:
        return f"{epid}: no está en _STATUS.md"
    d = data[epid]
    st = d["stage"]
    sm = P.STAGE.get(st)
    if not sm:
        return f"{epid}: stage {st} inválido"
    payload = {}
    ef = _exp(epid, st)
    if ef.exists():
        payload = json.loads(ef.read_text(encoding="utf-8"))
    fold = sm["fold"]
    if fold in ("human", "claude", "verify"):
        # nothing to fold mechanically; a claude/human stage is 'done' when its file exists / user marks it
        P.set_ep(epid, gate="firmado")
        _dash()
        return f"{epid}: stage {st} ({sm['name']}) — gate firmado"
    fn = FOLDS.get(sm["key"])
    if not fn:
        P.set_ep(epid, gate="firmado")
        _dash()
        return f"{epid}: stage {st} — sin fold definido, gate firmado"
    ok, msg = fn(epid, d, payload)
    if ok == "queued":
        P.set_ep(epid, gate="exportado", notes=msg)
        _dash()
        return f"{epid}: {msg} — mira el /loop o dile a Claude 'plega el Stage {st} de {epid}'"
    if ok:
        P.set_ep(epid, gate="firmado", notes=msg)
        _dash()
        return f"{epid}: stage {st} plegado ({msg}) — gate firmado"
    P.set_ep(epid, gate="exportado", notes=f"FOLD FALLÓ: {msg}")
    _dash()
    return f"{epid}: fold falló — {msg}"


# ---------- next ----------

def do_next(epid, force=False):
    data = P.read_status()
    if epid not in data:
        return f"{epid}: no está en _STATUS.md"
    d = data[epid]
    if d["gate"] != "firmado" and not force:
        return f"{epid}: gate '{d['gate']}', no 'firmado' — no avanza"
    st = d["stage"]
    nxt = P.STAGE[st]["next"]
    if nxt is None:
        return f"{epid}: stage {st} es el último"
    nm = P.STAGE[nxt]
    if nxt >= 6:
        P.ensure_assets(epid)
    d = P.set_ep(epid, stage=nxt, gate="abierto")
    if nm["fold"] == "claude":
        P.enqueue(epid, nxt, "generate",
                  note=f"escribir {nm['produces']} para {epid}")
        tail = f" · en cola: escribir {nm['produces']}"
    elif nm["fold"] == "human":
        tail = " · offline (marca 'hecho' en el dashboard cuando termines)"
    else:
        tail = f" · abre la revisión de Stage {nxt}"
    _dash()
    return f"{epid}: → Stage {nxt} ({nm['name']}){tail}"


def drain():
    data = P.read_status()
    out = []
    for epid in sorted(data):
        d = data[epid]
        if d["gate"] == "exportado":
            out.append(do_fold(epid))
            d = P.read_status()[epid]
        if d["gate"] == "firmado" and d["stage"] < d.get("auto", 12):
            out.append(do_next(epid))
    return "\n".join(out) or "nada pendiente"


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit("uso: advance.py [fold|next] E0XX  |  advance.py E0XX  |  advance.py --drain")
    if a[0] == "--drain":
        print(drain())
    elif a[0] == "fold" and len(a) > 1:
        print(do_fold(a[1]))
    elif a[0] == "next" and len(a) > 1:
        print(do_next(a[1], force="--force" in a))
    else:
        epid = a[0]
        print(do_fold(epid))
        print(do_next(epid))
