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
COST_MD = P.ROOT / "research" / "system-cost.md"
COST_HTML = P.ROOT / "cost.html"


def md_to_html(md):
    e = _h.escape
    out, i, lines = [], 0, md.splitlines()
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("|"):
            tbl = []
            while i < len(lines) and lines[i].startswith("|"):
                tbl.append(lines[i]); i += 1
            rows = [[c.strip() for c in r.strip("|").split("|")] for r in tbl]
            rows = [r for r in rows if not set("".join(r)) <= set("-: ")]
            if rows:
                th = "".join(f"<th>{fmt(c)}</th>" for c in rows[0])
                tb = "".join("<tr>" + "".join(f"<td>{fmt(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
                out.append(f'<table class="kpi"><tr>{th}</tr>{tb}</table>')
            continue
        if ln.startswith("### "):
            out.append(f"<h3>{fmt(ln[4:])}</h3>")
        elif ln.startswith("## "):
            out.append(f"<h2>{fmt(ln[3:])}</h2>")
        elif ln.startswith("# "):
            out.append(f"<h1>{fmt(ln[2:])}</h1>")
        elif ln.startswith("> "):
            out.append(f'<blockquote>{fmt(ln[2:])}</blockquote>')
        elif ln.strip().startswith(("- ", "* ")):
            items = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                items.append(f"<li>{fmt(lines[i].strip()[2:])}</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif ln.strip():
            out.append(f"<p>{fmt(ln)}</p>")
        i += 1
    return "".join(out)


def fmt(s):
    s = _h.escape(s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


_VIEW_CSS = (
    "<style>main{max-width:880px;margin:0 auto;padding:1.5rem}"
    "blockquote{border-left:2px solid var(--gold);margin:1rem 0;padding:.5rem .9rem;color:var(--muted);font-size:.85rem}"
    "h1,h2,h3{border:0}h2{margin-top:1.8rem}li{margin:.2rem 0}"
    "table.kpi{width:100%;border-collapse:collapse;font-size:.8rem;margin:.6rem 0}"
    "table.kpi td,table.kpi th{border-top:1px solid var(--line);padding:.35rem .5rem;text-align:left;vertical-align:top}"
    "table.kpi th{color:var(--muted)}"
    ".hbtn{font:inherit;font-size:.8rem;padding:.4rem .8rem;border:1px solid var(--line);border-radius:8px;"
    "background:var(--surface-2);color:var(--fg);text-decoration:none;cursor:pointer;display:inline-block}"
    "</style>")


def view_page(title, inner, assets_url=None, extra_head="", extra_script=""):
    e = _h.escape
    ab = (f'<a class="hbtn" href="{e(assets_url)}" target="_blank">📁 Recursos</a>' if assets_url else "")
    return ("<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{e(title)}</title>" + STYLE + _VIEW_CSS + extra_head + "</head><body>"
            f"<header><h1>{e(title)}</h1>{ab}"
            "<a class=\"hbtn\" href=\"/\" style=\"margin-left:auto\">← dashboard</a></header>"
            "<main>" + inner + "</main>" + extra_script + "</body></html>\n")


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


def strip(epid, slug, cur, gate):
    e = _h.escape
    dots = []
    for n in range(13):
        sm = P.STAGE[n]
        cls = "d"
        if n < cur:
            cls = "d done"
        elif n == cur:
            cls = "d cur " + gate
        tgt = P.OPEN.get(n, "")
        href = ""
        if n <= cur and tgt:
            if tgt.endswith(".html"):
                href = (P.SERVED + tgt) if tgt.startswith("ideas/") else f"{P.SERVED}episodes/{slug}/{tgt}"
                # only link if the html plausibly exists (review pages are per-episode / ideas)
            else:
                href = f"{P.SERVED}view?ep={epid}&f={tgt}"
        tip = f"Stage {n} · {e(sm['name'])} — {e(P.HELP.get(n, ''))}"
        if href:
            dots.append(f'<a class="{cls}" href="{href}" target="_blank" data-tip="{tip}">{n}</a>')
        else:
            dots.append(f'<span class="{cls}" data-tip="{tip}">{n}</span>')
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
        if cur >= 2:
            try: P.ensure_assets(epid)
            except Exception: pass
        sm = P.STAGE.get(cur, {})
        rev = sm.get("review_html")
        slug = d["slug"]
        btns = []
        if rev:
            href = served + rev if rev.startswith("ideas/") else f"{served}episodes/{slug}/{rev}"
            btns.append(f'<a class="btn" href="{e(href)}" target="_blank" '
                        f'data-tip="Abre la página de revisión de este stage: repasas lo generado, apruebas o dejas notas, y el botón Finalizar cierra el gate.">'
                        f'Abrir revisión · Stage {cur}</a>')
        elif cur in (1, 3, 5, 6):
            btns.append(f'<a class="btn" href="{served}view?ep={epid}&f={e(P.OPEN[cur])}" target="_blank" '
                        f'data-tip="Abre lo que Claude escribió en este stage para que lo leas.">Ver lo generado</a>')
        assets_btn = (f'<a class="btn" href="{served}episodes/{slug}/assets/" target="_blank" '
                      f'data-tip="La carpeta donde viven las imágenes, clips, música y tomas de este episodio.">📁 Recursos</a>')
        if cur >= 6:
            btns.append(assets_btn)
        if sm.get("fold") == "human":
            btns.append(f'<button class="btn" data-human="{epid}:{cur}" '
                        f'data-tip="Marca este stage offline como terminado (grabación, subida). Cierra el gate y pasa al siguiente.">'
                        f'Marcar Stage {cur} hecho</button>')
        if d["gate"] == "firmado":
            btns.append(f'<button class="btn primary" data-adv="{epid}" '
                        f'data-tip="El gate está cerrado. Este botón mueve el episodio al siguiente stage y prepara lo que haga falta.">'
                        f'▶ Avanzar a Stage {sm.get("next","?")}</button>')
        elif d["gate"] == "exportado":
            btns.append('<span class="tag warn" data-tip="Tomaste las decisiones pero falta aplicarlas al fichero. El server o Claude lo harán.">exportado — falta plegar</span>')
        reads = sm.get("reads", [])
        rules = sm.get("rules", [])
        manifest = ""
        if sm.get("fold") == "claude" and (reads or rules):
            manifest = ('<details class="man"><summary>Contexto que leerá Claude en este stage</summary>'
                        + "<div>" + " · ".join(f"<code>{e(x)}</code>" for x in reads + rules)
                        + " — <b>y nada más</b></div></details>")
        cards.append(
            f'<div class="epc">'
            f'<div class="epch"><b>{e(epid)}</b> · {e(d["title"] or d["slug"])} '
            f'<span class="tag">{e(d["track"])}</span> '
            f'<span class="tag">narra {e(d["narrator"])}</span></div>'
            + strip(epid, d["slug"], cur, d["gate"])
            + f'<div class="now">Stage <b>{cur} · {e(sm.get("name","?"))}</b> — gate <b>{e(d["gate"])}</b>'
            + (f' · auto-avance hasta {d["auto"]}' if d["auto"] < 12 else "")
            + '</div>'
            + (f'<div class="notes">{e(d["notes"])}</div>' if d["notes"] else "")
            + manifest
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
document.querySelectorAll('[data-loop]').forEach(b=>b.onclick=async()=>{{
  await post('/loop',{{state:b.dataset.loop}});}});
"""
    loop_state = P.read_loop().get("state", "run")
    lbadge = {"run": "activa", "pause": "pausada", "stop": "cerrada"}.get(loop_state, loop_state)
    if loop_state == "run":
        loopbtns = ('<button class="btn" data-loop="pause" data-tip="Detiene el trabajo automático un rato, sin cerrar la sesión. Para pausas cortas — cada rato sigue costando un poco.">⏸ Pausar</button>'
                    '<button class="btn" data-loop="stop" data-tip="Termina la sesión automática. Claude deja de trabajar solo. El progreso NO se pierde. Para retomar hay que relanzar el /loop en la terminal.">⏹ Cerrar sesión</button>')
    elif loop_state == "pause":
        loopbtns = ('<button class="btn" data-loop="run" data-tip="Vuelve a activar el trabajo automático.">▶ Reanudar</button>'
                    '<button class="btn" data-loop="stop" data-tip="Termina la sesión automática. El progreso NO se pierde.">⏹ Cerrar sesión</button>')
    else:  # stop
        loopbtns = ('<button class="btn" data-loop="run" data-tip="Reactiva la señal. Después, relanza  /loop atiende el dashboard  en la terminal del chat.">▶ Reanudar sesión</button>'
                    '<span class="count" style="opacity:.7">sesión cerrada — relanza <code>/loop</code> en la terminal</span>')
    tips = (
        '<details class="tips"><summary>💡 Cómo no gastar tokens</summary>'
        '<h4>El <code>/loop</code> y la sesión</h4>'
        '<p>El <code>/loop atiende el dashboard</code> son turnos míos recurrentes en tu terminal de Claude Code. '
        'Cada tick cuesta algo (poco, va cacheado) aunque no haya trabajo. Para cerrarlo:</p>'
        '<ul>'
        '<li><b>⏹ Cerrar sesión</b> (arriba) — la forma limpia: el loop termina en su próximo tick y no se reprograma.</li>'
        '<li>o <b>dime</b> «para el loop».  o <b>Esc</b> en la terminal del chat (más brusco).</li>'
        '<li><b>⏸ Pausar</b> detiene el trabajo pero el tick sigue costando — úsalo para pausas cortas, no largas.</li>'
        '<li>El estado (<code>_STATUS.md</code>, <code>_queue.json</code>) <b>no se pierde</b> al cerrar. Al retomar: reabre el dashboard, y para re-automatizar vuelve a lanzar <code>/loop atiende el dashboard</code>.</li>'
        '<li>El <b>server</b> (<code>serve.py</code>) es python puro — <b>no gasta tokens</b>. Ciérralo cuando quieras (su ventana «Exodo server»).</li>'
        '</ul>'
        '<h4>Flujo eficiente</h4><ul>'
        '<li><b>Reparte</b> research (Stage 2) y guion (Stage 4) en sesiones distintas de 5 h — juntas rozan el límite de la ventana.</li>'
        '<li>Deja que el server plegue los gates <b>mecánicos</b> (0·2·7·9·10) — no le pidas a Claude que lo haga.</li>'
        '<li>Una frase corta basta: «sigue». No repitas el contexto ni el estado — ya está en los ficheros.</li>'
        '<li><b>Nunca</b> «revisa el proyecto» / «lee los docs». El manifiesto de cada card dice exactamente qué se lee.</li>'
        '<li>Un episodio de una sola tirada roza el tope de 5 h — <b>párate tras el guion</b> y retoma en otra sesión.</li>'
        '<li>Fija el <b>auto-avance</b> en <code>_STATUS.md</code> bajo el stage donde quieres revisar, para que el loop pare ahí.</li>'
        '</ul></details>')
    body = (
        tips
        + '<section><h2>En producción</h2>'
        + ("".join(cards) if cards else '<p class="muted">Ningún capítulo en producción. '
           'Añade una fila a <code>episodes/_STATUS.md</code> o aprueba una idea.</p>')
        + '</section>'
        '<section><h2>Publicados</h2>' + hist + '</section>')
    extra = ('<style>'
             '.epc{border:1px solid var(--line);border-radius:12px;background:var(--surface);padding:1.1rem;margin:0 0 1.1rem}'
             '.epch{font-size:.95rem;margin-bottom:.7rem}'
             '.strip{display:flex;gap:.3rem;margin:.4rem 0 .7rem;flex-wrap:wrap}'
             '.d{width:1.8rem;height:1.8rem;display:grid;place-items:center;border-radius:6px;'
             'font-size:.72rem;background:var(--surface-2);color:var(--muted);border:1px solid var(--line);'
             'text-decoration:none}'
             'a.d{cursor:pointer}a.d:hover{border-color:var(--bone);transform:translateY(-1px)}'
             '.d.done{background:var(--gold-soft);color:var(--gold);border-color:var(--gold)}'
             '.d.cur{border-color:var(--bone);color:var(--bone);font-weight:700}'
             '.d.cur.firmado{background:var(--gold);color:#1a1610}'
             '.d.cur.exportado{background:#6b5a2a;color:var(--bone)}'
             # themed hover tooltip (replaces native title=)
             '[data-tip]{position:relative}'
             '[data-tip]:hover::after{content:attr(data-tip);position:absolute;left:0;top:calc(100% + 6px);'
             'z-index:50;width:max-content;max-width:22rem;white-space:normal;'
             'background:var(--surface-2);color:var(--fg);border:1px solid var(--gold);border-radius:8px;'
             'padding:.5rem .7rem;font-size:.78rem;line-height:1.4;font-weight:400;'
             'box-shadow:0 8px 24px #0008;pointer-events:none}'
             '[data-tip]:hover::before{content:"";position:absolute;left:10px;top:calc(100% + 1px);'
             'border:5px solid transparent;border-bottom-color:var(--gold);z-index:51}'
             'header [data-tip]:hover::after{max-width:26rem}'
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
             'details.tips{border:1px solid var(--gold);border-radius:10px;background:var(--gold-soft);'
             'padding:.6rem .9rem;margin:0 0 1.5rem}'
             'details.tips summary{cursor:pointer;font-weight:600;color:var(--bone)}'
             'details.tips ul{margin:.4rem 0 .6rem;font-size:.85rem}details.tips li{margin:.35rem 0}'
             'details.tips h4{margin:.9rem 0 .2rem;font-size:.82rem;color:var(--gold)}'
             'details.tips p{font-size:.83rem;margin:.3rem 0}'
             'details.man{font-size:.78rem;color:var(--muted);margin:.4rem 0}'
             'details.man summary{cursor:pointer}details.man code{font-size:.72rem}'
             'header .btn{font-size:.78rem;padding:.35rem .6rem}'
             '</style>')
    hd = ('<h1>Exodo · dashboard</h1>'
          f'<span class="count">sesión: <b>{lbadge}</b></span>'
          + loopbtns
          + ('<a class="btn" href="cost.html" style="margin-left:auto" '
             'data-tip="Cuántos tokens consume el sistema y qué fracción de tu plan. Con consejos para no gastar de más.">Consumo</a>'
             if COST_MD.exists() else ''))
    return ("<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>Exodo · dashboard</title>" + STYLE + extra + "</head><body>\n"
            "<header>" + hd + "</header>\n<main>" + body + "</main>\n"
            "<script>" + script + "</script>\n</body></html>\n")


def build_cost():
    inner = md_to_html(COST_MD.read_text(encoding="utf-8"))
    head = ("<style>#upd{border-color:var(--gold);color:var(--gold)}"
            "[data-tip]{position:relative}"
            "[data-tip]:hover::after{content:attr(data-tip);position:absolute;right:0;top:calc(100% + 6px);"
            "z-index:50;width:max-content;max-width:24rem;white-space:normal;background:var(--surface-2);"
            "color:var(--fg);border:1px solid var(--gold);border-radius:8px;padding:.5rem .7rem;font-size:.78rem;"
            "line-height:1.4;box-shadow:0 8px 24px #0008;pointer-events:none}</style>")
    updbtn = ('<button class="hbtn" id="upd" data-tip="Pone la fecha de hoy, marca las filas con más de 3 meses para revisar, '
              'añade una línea al historial con la versión actual y un hueco para el dato real de consumo, y refresca esta página. '
              'No se inventa ningún número.">Actualizar</button>')
    script = ("<script>document.getElementById('upd').onclick=async()=>{"
              "try{const r=await fetch('http://localhost:8765/cost-update',{method:'POST',"
              "headers:{'content-type':'application/json'},body:'{}'});"
              "if(r.ok){const j=await r.json();alert(j.msg||'actualizado');location.reload();}"
              "else alert('server respondió '+r.status);}"
              "catch(e){alert('El server no está corriendo. Abre Exodo-Dashboard.bat, o corre  python tools/cost_update.py');}};"
              "</script>")
    p = view_page("Consumo del sistema", inner, None, head, script)
    return p.replace('<a class="hbtn" href="/" style="margin-left:auto">← dashboard</a>',
                     updbtn + '<a class="hbtn" href="/" style="margin-left:auto">← dashboard</a>')


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    msg = ""
    if COST_MD.exists():
        COST_HTML.write_text(build_cost(), encoding="utf-8")
        msg = " + cost.html"
    n = len(P.read_status())
    print(f"escrito  dashboard.html{msg}  ({n} episodios en _STATUS.md)")
