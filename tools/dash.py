#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dash.py — regenerate dashboard.html from episodes/_STATUS.md + the folders
+ the KPI log in brain/07. Pure python, no agent, cheap.

Run by hand (`python tools/dash.py`), at the end of every advance.py, and
served live by serve.py (which re-runs it on every /finish).
"""
import html as _h
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_ui import STYLE  # noqa: E402
import pipeline as P  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT = P.ROOT / "dashboard.html"
KPI_DOC = P.ROOT / "brain" / "07-publishing-seo-metrics.md"


def kpi_rows():
    if not KPI_DOC.exists():
        return []
    txt = KPI_DOC.read_text(encoding="utf-8")
    m = re.search(r"## KPI log\s*\n(.*?)(?=\n## |\Z)", txt, re.S)
    if not m:
        return []
    rows = []
    for ln in m.group(1).splitlines():
        if not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if not cells or set("".join(cells)) <= set("-: ") or cells[0].lower() in ("episode", "episodio"):
            continue
        if "EXAMPLE" in cells[0]:
            continue
        rows.append(cells)
    return rows


def strip(ep, cur, gate, auto):
    dots = []
    for n in range(13):
        cls = "d"
        if n < cur:
            cls = "d done"
        elif n == cur:
            cls = "d cur " + gate
        dots.append(f'<span class="{cls}" title="Stage {n} · {_h.escape(P.STAGE[n]["name"])}">{n}</span>')
    return f'<div class="strip">{"".join(dots)}</div>'


def build():
    e = _h.escape
    st = P.read_status()
    served = "http://localhost:%d/" % P.PORT

    cards = []
    for epid in sorted(st):
        d = st[epid]
        if d["slug"].startswith(epid) and "EXAMPLE" in d["slug"]:
            continue
        cur = max(d["stage"], 0)
        sm = P.STAGE.get(cur, {})
        rev = sm.get("review_html")
        btns = []
        if rev:
            href = (served + rev) if not rev.startswith("ideas/") else (served + rev)
            btns.append(f'<a class="btn" href="{e(href)}" target="_blank">Abrir revisión · Stage {cur}</a>')
        if sm.get("fold") == "human":
            btns.append(f'<button class="btn" data-human="{epid}:{cur}">Marcar Stage {cur} hecho</button>')
        if d["gate"] == "firmado":
            btns.append(f'<button class="btn primary" data-adv="{epid}">▶ Avanzar a Stage {sm.get("next","?")}</button>')
        elif d["gate"] == "exportado":
            btns.append('<span class="tag warn">exportado — falta plegar</span>')
        cards.append(
            f'<div class="epc">'
            f'<div class="epch"><b>{e(epid)}</b> · {e(d["title"] or d["slug"])} '
            f'<span class="tag">{e(d["track"])}</span> '
            f'<span class="tag">narra {e(d["narrator"])}</span></div>'
            + strip(epid, cur, d["gate"], d["auto"])
            + f'<div class="now">Stage <b>{cur} · {e(sm.get("name","?"))}</b> — gate <b>{e(d["gate"])}</b>'
            + (f' · auto-avance hasta {d["auto"]}' if d["auto"] < 12 else "")
            + '</div>'
            + (f'<div class="notes">{e(d["notes"])}</div>' if d["notes"] else "")
            + f'<div class="btns">{"".join(btns)}</div>'
            '</div>')

    krows = kpi_rows()
    if krows:
        head = "".join(f"<th>{e(c)}</th>" for c in
                       ["Episodio", "Pub", "Duración", "Views 30d", "AVD %", "CTR %", "Subs", "Notas"][:len(krows[0])])
        kbody = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in krows)
        hist = f'<table class="kpi"><tr>{head}</tr>{kbody}</table>'
    else:
        hist = '<p class="muted">Sin episodios publicados todavía.</p>'

    script = f"""
async function post(path,body){{
  try{{const r=await fetch('http://localhost:{P.PORT}'+path,{{method:'POST',
    headers:{{'content-type':'application/json'}},body:JSON.stringify(body)}});
    if(r.ok){{location.reload();return}} alert('server respondió '+r.status);}}
  catch(e){{alert('El server no está corriendo. Abre Exodo-Dashboard.bat, o corre  python tools/serve.py');}}
}}
document.querySelectorAll('[data-adv]').forEach(b=>b.onclick=()=>post('/advance',{{ep:b.dataset.adv}}));
document.querySelectorAll('[data-human]').forEach(b=>b.onclick=()=>{{
  const [ep,st]=b.dataset.human.split(':'); post('/human',{{ep,stage:+st}});}});
"""
    body = (
        '<section><h2>En producción</h2>'
        + ("".join(cards) if cards else '<p class="muted">Ningún capítulo en producción. '
           'Añade una fila a <code>episodes/_STATUS.md</code> o aprueba una idea.</p>')
        + '</section>'
        '<section><h2>Publicados</h2>' + hist + '</section>')
    extra = ('<style>'
             '.epc{border:1px solid var(--line);border-radius:12px;background:var(--surface);padding:1.1rem;margin:0 0 1.1rem}'
             '.epch{font-size:.95rem;margin-bottom:.7rem}'
             '.strip{display:flex;gap:.25rem;margin:.4rem 0 .7rem}'
             '.d{width:1.7rem;height:1.7rem;display:grid;place-items:center;border-radius:6px;'
             'font-size:.7rem;background:var(--surface-2);color:var(--muted);border:1px solid var(--line)}'
             '.d.done{background:var(--gold-soft);color:var(--gold);border-color:var(--gold)}'
             '.d.cur{border-color:var(--bone);color:var(--bone);font-weight:700}'
             '.d.cur.firmado{background:var(--gold);color:#1a1610}'
             '.d.cur.exportado{background:#6b5a2a;color:var(--bone)}'
             '.now{font-size:.85rem}.notes{font-size:.8rem;color:var(--muted);margin:.4rem 0}'
             '.btns{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.7rem}'
             '.btn{font:inherit;font-size:.8rem;padding:.4rem .8rem;border:1px solid var(--line);border-radius:8px;'
             'background:var(--surface-2);color:var(--fg);cursor:pointer;text-decoration:none;display:inline-block}'
             '.btn.primary{background:var(--gold);color:#1a1610;border-color:var(--gold);font-weight:600}'
             '.tag.warn{background:#6b5a2a;color:var(--bone)}'
             '.muted{color:var(--muted)}'
             'table.kpi{width:100%;border-collapse:collapse;font-size:.82rem}'
             'table.kpi td,table.kpi th{border-top:1px solid var(--line);padding:.4rem .55rem;text-align:left}'
             'table.kpi th{color:var(--muted)}'
             '</style>')
    hd = ('<h1>Exodo · dashboard</h1>'
          '<span class="count">estado de cada capítulo · se regenera al cerrar cada gate</span>')
    return ("<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>Exodo · dashboard</title>" + STYLE + extra + "</head><body>\n"
            "<header>" + hd + "</header>\n<main>" + body + "</main>\n"
            "<script>" + script + "</script>\n</body></html>\n")


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    n = len(P.read_status())
    print(f"escrito  dashboard.html  ({n} episodios en _STATUS.md)")
