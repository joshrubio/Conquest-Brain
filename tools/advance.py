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

def _gen_note(epid, nxt, nm):
    if nxt == 1:
        return (f"completar el 01-brief.md ya prellenado de {epid} (ID/slug/track/hook/narrador puestos "
                f"en Stage 0 desde la idea) — rellenar sujeto, tesis, estructura, fuentes y riesgos")
    return f"escribir {nm['produces']} para {epid}"


def _dash():
    subprocess.run([sys.executable, str(Path(__file__).parent / "dash.py")],
                   capture_output=True)


def _exp(epid, stage):
    return P.ep_path(epid) / "_exports" / f"stage{stage:02d}.json"


# ---------- folds (mechanical) ----------

def fold_idea(epid, d, payload):
    """Stage 0: create the episode folder from template, prefill the brief, mark the idea-pool row."""
    ep = P.EP_DIR / f"{epid}-{d['slug']}" if not d["slug"].startswith(epid) else P.EP_DIR / d["slug"]
    # dirs_exist_ok: the produce endpoint pre-creates <ep>/_exports/ to stash
    # stage00.json before calling this fold — merge the template in around it.
    shutil.copytree(TEMPLATE, ep, dirs_exist_ok=True)
    P.ensure_assets(epid)
    _prefill_brief(ep / "01-brief.md", epid, d, payload)
    _mark_pool(payload.get("idea_id"), f"en producción ({epid})")
    return True, "carpeta creada + brief prellenado"


def _idea_id_of(epid):
    """The idea-pool id an episode came from — stashed in _exports/stage00.json at Stage 0."""
    f = P.ep_path(epid) / "_exports" / "stage00.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8")).get("idea_id")
        except json.JSONDecodeError:
            pass
    return None


def _mark_pool(idea_id, state):
    """Set the Estado cell of an idea-pool summary row (no-op if the id isn't found)."""
    pool = P.ROOT / "ideas" / "idea-pool.md"
    if not (idea_id and pool.exists()):
        return
    t = pool.read_text(encoding="utf-8")
    nt = re.sub(rf"(\|\s*{re.escape(idea_id)}\s*\|.*?\|)([^|]*)(\|\s*)$",
                lambda m: m.group(1) + f" {state} " + m.group(3), t, flags=re.M, count=1)
    if nt != t:
        pool.write_text(nt, encoding="utf-8")


def _prefill_brief(brief, epid, d, payload):
    """Drop the knowns from Stage 0 into the fresh 01-brief.md — the author fills the rest."""
    if not brief.exists():
        return
    cell = lambda s: s.replace("|", r"\|").strip()          # safe inside a md table cell
    title = (d.get("title") or payload.get("working_title") or epid).strip("«».")
    slug = d.get("slug") or f"{epid}-{P.slugify(title)}"
    hook = payload.get("hook") or ""
    track = d.get("track") or "…"
    narr = d.get("narrator") or "…"
    t = brief.read_text(encoding="utf-8")
    subs = [
        (r"^# Brief de episodio — E0XX «[^»]*»", f"# Brief de episodio — {epid} «{title}»"),
        (r"(\|\s*ID episodio\s*\|\s*)E0XX(\s*\|)", epid),
        (r"(\|\s*Slug carpeta\s*\|\s*)E0XX-<slug>(\s*\|)", cell(slug)),
        (r"(\|\s*Track\s*\|\s*)[^|]*(\|)", cell(track) + " "),
        (r"(\|\s*Narrador asignado\s*\|\s*)[^|]*(\|)", cell(narr) + " "),
    ]
    if hook:
        subs.append((r"(\|\s*Hook-title elegido \(`brain/13`\)\s*\|\s*)[^|]*(\|)", cell(hook) + " "))
    for pat, rep in subs:
        if pat.startswith("^# "):
            t = re.sub(pat, lambda m, r=rep: r, t, count=1, flags=re.M)
        else:
            t = re.sub(pat, lambda m, r=rep: m.group(1) + r + m.group(2), t, count=1, flags=re.M)
    brief.write_text(t, encoding="utf-8")


def fold_assets(epid, d, payload):
    """Stage 7: the picker already wrote 07-picks.txt; run the download."""
    picks = P.ep_path(epid) / "07-picks.txt"
    if not picks.exists():
        return False, "no 07-picks.txt"
    r = subprocess.run([sys.executable, str(Path(__file__).parent / "pull_assets.py"),
                        d["slug"] if d["slug"].startswith(epid) else f"{epid}-{d['slug']}", "--download"],
                       capture_output=True, text=True)
    return (r.returncode == 0), (r.stdout or r.stderr).strip().splitlines()[-1:][0] if (r.stdout or r.stderr) else "descargado"


def fold_script(epid, d, payload):
    """Stage 4: 05-script.html's editor already POSTed the edited script and
    serve.py wrote it straight into 05-script.md. Nothing to fold — the gate
    just needs the reviewer's tick + name before it can firm."""
    if not (payload.get("ok") and str(payload.get("firma", "")).strip()):
        return False, "guion guardado en 05-script.md, falta aprobar + firmar en 05-script.html"
    return True, "guion actualizado directamente en 05-script.md"


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
    """Formats that vary (research / package): stash the export, queue the fold for the agent."""
    st = d["stage"]
    P.enqueue(epid, st, "fold", note=f"aplicar las decisiones de {P.STAGE[st]['name']} "
              f"(en {_exp(epid, st).relative_to(P.ROOT)}) al fichero fuente")
    return "queued", "decisiones en cola para plegar"


def fold_edit(epid, d, payload):
    """Stage 9: the timeline is saved as 09-timeline.json. Queue: apply the FIX
    notes (regen KB clips) then assemble.py --final for the 4K master —
    UNLESS that master already exists and is newer than the timeline (i.e.
    nothing changed since it rendered), in which case the fold is actually
    done: firm the gate instead of re-queuing the same render forever."""
    epp = P.ep_path(epid)
    tj = epp / "09-timeline.json"
    fixes = []
    if tj.exists():
        try:
            for i, b in enumerate(json.loads(tj.read_text(encoding="utf-8")).get("beats", []), 1):
                if b.get("fix"):
                    tag = b.get("id") or b.get("n") or f"#{i}"
                    fixes.append(f"beat {i} ({tag}, {b.get('asset') or 'sin asset'}): {b['fix']}")
        except json.JSONDecodeError:
            pass
    masters = sorted(epp.glob(f"{epid}-*-v*.mp4"), key=lambda f: f.stat().st_mtime)
    hf = epp / "_exports" / "09-final-hash.txt"
    # the timeline's mtime alone is a bad staleness signal — opening 09-edit.html
    # autosaves it even with no real change. Prefer a content hash (stamped by
    # assemble.py --final on success): if it still matches the current timeline,
    # or there's no hash yet to compare (a master rendered before this check
    # existed) and there are no pending fixes, the render already covers it.
    stale = False
    if masters and hf.exists() and tj.exists():
        try:
            current = P.timeline_content_hash(json.loads(tj.read_text(encoding="utf-8")))
            stale = current != hf.read_text(encoding="utf-8").strip()
        except json.JSONDecodeError:
            stale = True
    if masters and not fixes and not stale:
        return True, f"render 4K ya hecho ({masters[-1].name}) · 0 correcciones pendientes"
    note = ("Stage 9 — la timeline canónica está en 09-timeline.json (schema 2). "
            + (f"Aplica las {len(fixes)} correcciones re-corriendo kenburns.py por beat:\n  - "
               + "\n  - ".join(fixes) + "\n" if fixes else "Sin correcciones pendientes. ")
            + "Luego: `python tools/assemble.py " + (d.get("slug") or epid)
            + " --final` para el render 4K. 09-timeline.json es el artefacto autorado — editarlo "
            + "a mano (dur, orden, asset de un beat) está bien; lo que NO debes hacer es re-sembrarlo.")
    P.enqueue(epid, 9, "fold", note=note)
    return "queued", f"timeline guardada · {len(fixes)} correcciones + render 4K en cola"


FOLDS = {"idea": fold_idea, "assets": fold_assets, "retro": fold_retro,
         "research": fold_stash, "edit": fold_edit, "package": fold_stash,
         "script": fold_script}


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
        # nothing to fold mechanically; a claude/human stage is 'done' when its
        # produced doc actually exists — NOT just because fold was called. A
        # 'claude' stage whose primary doc is still the folder template has not
        # been done: re-queue it and hold the gate, don't wave it through.
        prim = (P.PRIMARY_DOC.get(st) or "").split()[0]
        if fold == "claude" and prim and P.pristine(epid, prim):
            P.enqueue(epid, st, "generate", note=_gen_note(epid, st, sm))
            P.set_ep(epid, gate="abierto")
            _dash()
            return (f"{epid}: stage {st} ({sm['name']}) — {prim} sigue en plantilla, "
                    f"nada que plegar; encolado para escribir. NO avanza.")
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
    P.dequeue(epid, st)                   # the stage we just left is done — drop any stale task
    if st == 11:                          # left publish -> the idea is now live
        _mark_pool(_idea_id_of(epid), f"publicada ({epid})")
    if nxt == 9:
        # Stage 9 (brain/16): Ken Burns on stills → trim each take → first-cut
        # timeline + page. Best-effort: if kenburns/trim can't run (no ffmpeg /
        # faster-whisper on this box) the stage still advances, just less covered.
        slug = d["slug"] if d["slug"].startswith(epid) else f"{epid}-{d['slug']}"
        here = Path(__file__).parent
        ep = P.ep_path(epid)
        steps = []

        gr = subprocess.run([sys.executable, str(here / "make_graphics.py"), slug],
                            capture_output=True, text=True)
        steps.append("gráficos " + ("ok" if gr.returncode == 0 else "falló"))

        kb = subprocess.run([sys.executable, str(here / "kenburns.py"), slug, "--all"],
                            capture_output=True, text=True)
        steps.append("KB " + ("ok" if kb.returncode == 0 else "falló"))

        takes = [t for t in sorted(ep.glob("assets/*.mp4"))
                 if ".trimmed" not in t.name and not t.name.startswith(("09-", "intro"))]
        n_rev = n_done = 0
        for t in takes:
            if t.with_suffix(".trimmed.mp4").exists():
                n_done += 1
                continue
            # phase 1 only: transcribe + propose cuts + review page. The user
            # checks the transcript, vetoes bad cuts, then «Aplicar corte»
            # (serve.py /trim) renders the trimmed take and re-aligns.
            tr = subprocess.run(
                [sys.executable, str(here / "trim_talk.py"), str(t),
                 "--script", str(ep / "05-script.md")],
                capture_output=True, text=True)
            if tr.returncode == 0:
                n_rev += 1
        if takes:
            steps.append(f"trim: {n_done} listas" + (f", {n_rev} a revisar" if n_rev else ""))
        else:
            steps.append("sin tomas")

        # seed the timeline once from the spine + VO. A schema-2 file already
        # here (re-entry / re-drain) is left untouched; a schema-1 file makes
        # --seed refuse and print the migrate command.
        r1 = subprocess.run([sys.executable, str(here / "assemble.py"), slug, "--seed"],
                            capture_output=True, text=True)
        subprocess.run([sys.executable, str(here / "edit_timeline.py"), slug],
                       capture_output=True, text=True)
        last = (r1.stdout or r1.stderr).strip().splitlines()[-1:] or [""]
        rev = ""
        if n_rev:
            rt = next((t for t in takes if not t.with_suffix(".trimmed.mp4").exists()), None)
            if rt:
                rev = f" · revisa la transcripción: assets/{rt.with_suffix('.review.html').name}"
        tail = f" · {' · '.join(steps)} · {last[0][:60]}{rev}"
    elif nm["fold"] == "claude" or (nxt in P.DRAFT_STAGES and P.pristine(epid, P.DRAFT_STAGES[nxt])):
        # a stage that produces a document nobody has drafted yet — queue it for
        # the agent. Covers the `claude` folds (brief/outline/fact-check/shotlist)
        # and the `mech` ones whose doc still has to be written first (research,
        # script, package): without this the dashboard dead-ends on entry.
        P.enqueue(epid, nxt, "generate", note=_gen_note(epid, nxt, nm))
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
