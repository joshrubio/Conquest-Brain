#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dash.py — regenerate dashboard.html from episodes/_STATUS.md + the folders
+ the KPI log in brain/07. Pure python, no agent, cheap.

Run by hand (`python tools/dash.py`), at the end of every advance.py, and
served live by serve.py (which re-runs it on every /finish).

All styling lives in tools/theme.py — this file only builds structure.
"""
import html as _h
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme as T  # noqa: E402
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
            rows = [[c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", r.strip("|"))] for r in tbl]
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


def view_page(title, inner, assets_url=None, extra_head="", extra_script=""):
    """Rendered markdown view (serve.py /view). Chrome from theme.shell."""
    e = _h.escape
    ab = (f'<a class="btn ghost" href="{e(assets_url)}" target="_blank">Recursos</a>' if assets_url else "")
    header = (f'<h1>{e(title)}</h1>{ab}'
              '<a class="btn ghost spacer" href="/">Volver al panel</a>')
    return T.shell(e(title), header, f'<div class="doc">{inner}</div>',
                   extra_css=extra_head, head_extra="", script_html=extra_script or " ")


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
    epp = P.EP_DIR / slug
    cards = []
    for n in range(1, 13):
        sm = P.STAGE[n]
        cls = "sc"
        if n < cur:
            cls = "sc done"
        elif n == cur:
            cls = "sc cur " + gate
        tgt = P.OPEN.get(n, "")
        href = ""
        if n <= cur and tgt:
            if tgt.startswith("ideas/"):
                href = P.SERVED + tgt if (P.ROOT / tgt).exists() else ""
            elif tgt.endswith(".html"):
                href = f"{P.SERVED}episodes/{slug}/{tgt}" if (epp / tgt).exists() else ""
            else:
                href = f"{P.SERVED}view?ep={epid}&f={tgt}" if (epp / tgt).exists() else ""
        inner = (f'<span class="scn">{n}</span> <b>{e(sm["name"])}</b>'
                 f'<span class="scd">{e(P.CARD.get(n, ""))}</span>')
        if n == 8 and n <= cur:
            # Stage 8 (Grabación) has no doc to read — «Ver más» opens the
            # upload dialog (pick the take -> sube a assets/ -> pliega el gate)
            # instead of pointing at 06-shotlist.md (OPEN[8], meant for while
            # you're filming, not as this card's target).
            cards.append(f'<button type="button" class="{cls}" data-rec-open="{epid}">{inner}'
                         f'<span class="scpill">Ver más</span></button>')
        elif href:
            cards.append(f'<a class="{cls}" href="{href}" target="_blank">{inner}'
                         f'<span class="scpill">Ver más</span></a>')
        else:
            cards.append(f'<div class="{cls}">{inner}'
                         f'<span class="scpill pend">Pendiente</span></div>')
    return f'<div class="strip">{"".join(cards)}</div>'


def _episode_card(epid, d, qentry=None):
    e = _h.escape
    cur = max(d["stage"], 0)
    if cur >= 2:
        try: P.ensure_assets(epid)
        except Exception: pass
    sm = P.STAGE.get(cur, {})
    rev = sm.get("review_html")
    slug = d["slug"]
    served = P.SERVED
    btns = []
    if rev:
        href = served + rev if rev.startswith("ideas/") else f"{served}episodes/{slug}/{rev}"
        btns.append(f'<a class="btn primary" href="{e(href)}" target="_blank" '
                    'data-tip="Abre la página de revisión de este stage: repasas lo generado, apruebas o dejas notas, y Finalizar cierra el gate.">'
                    f'Revisar · Stage {cur}</a>')
    elif cur in (1, 3, 5, 6):
        btns.append(f'<a class="btn" href="{served}view?ep={epid}&f={e(P.OPEN[cur])}" target="_blank" '
                    'data-tip="Abre lo que Claude escribió en este stage para que lo leas.">Ver lo generado</a>')
    if cur >= 6:
        btns.append(f'<a class="btn ghost" href="{served}episodes/{slug}/assets/" target="_blank" '
                    'data-tip="La carpeta donde viven las imágenes, clips, música y tomas de este episodio.">Recursos</a>')
    if cur in (8, 9):
        try:
            revs = sorted((P.ep_path(epid) / "assets").glob("*.review.html"))
        except Exception:
            revs = []
        for rv in revs:
            done = (rv.parent / (rv.name.split(".")[0] + ".trimmed.mp4")).exists()
            btns.append(
                f'<a class="btn{"" if done else " primary"}" target="_blank" '
                f'href="{served}episodes/{slug}/assets/{e(rv.name)}" '
                'data-tip="Sala de recorte: la forma de onda de la toma con cada silencio/retoma como un bloque '
                'que arrastras. «Aplicar corte» recorta la toma y re-alinea el timeline.">'
                f'{"✓ " if done else ""}Recortar la voz · {e(rv.name.split(".")[0])}</a>')
    if sm.get("fold") == "human":
        btns.append(f'<button class="btn" data-human="{epid}:{cur}" '
                    'data-tip="Marca este stage offline como terminado (grabación, subida). Cierra el gate y pasa al siguiente.">'
                    f'Marcar hecho</button>')
    # stages Claude writes that have NO review page (brief, outline, fact-check,
    # shotlist) — one button to fold + advance. Stages with a review page
    # (research, script) go through «Revisar», not this shortcut.
    is_draft_stage = (sm.get("fold") == "claude" or cur in P.DRAFT_STAGES) and not rev
    if d["gate"] == "abierto" and is_draft_stage and cur > 0:
        doc = P.PRIMARY_DOC.get(cur, "")
        written = doc and not P.pristine(epid, doc)
        nxt = sm.get("next", "?")
        if written:
            btns.append(f'<button class="btn accent" data-done="{epid}" '
                        f'data-tip="Confirmas que {e(doc)} está escrito y aprobado. Cierra el gate y avanza a Stage {nxt} '
                        f'(equivale a: python tools/advance.py {epid}).">'
                        f'{e(sm.get("name","?"))} listo → avanzar a Stage {nxt}</button>')
        else:
            btns.append(f'<button class="btn" data-nudge="{epid}" '
                        'data-tip="Este stage lo escribe Claude, no el panel (que no gasta tokens). Marca prioridad para el '
                        '/loop (baja su cadencia a ~1 min con trabajo en cola). Instantáneo: «sigue» en la terminal del /loop, '
                        'o pídemelo en el chat.">▶ Pedir generación del ' + e(sm.get("name","?")).lower() + '</button>')
    if d["gate"] == "firmado":
        btns.append(f'<button class="btn accent" data-adv="{epid}" '
                    'data-tip="El gate está cerrado. Mueve el episodio al siguiente stage y prepara lo que haga falta.">'
                    f'Avanzar a Stage {sm.get("next","?")}</button>')
    elif d["gate"] == "exportado":
        btns.append('<span class="pill warn" data-tip="Tomaste las decisiones pero falta aplicarlas al fichero. El server o Claude lo harán."><span class="dot"></span>exportado — falta plegar</span>')

    reads = sm.get("reads", [])
    rules = sm.get("rules", [])
    manifest = ""
    if (sm.get("fold") == "claude" or sm.get("key") == "script") and (reads or rules):
        manifest = ('<details class="man"><summary>Contexto que leerá Claude en este stage</summary>'
                    + "<div>" + " · ".join(f"<code>{e(x)}</code>" for x in reads + rules)
                    + " — <b>y nada más</b></div></details>")

    qline = ""
    if qentry:
        act = "escribir" if qentry.get("action") == "generate" else "plegar"
        qline = ('<div class="qline" data-tip="Esta fase la trabaja Claude, no el panel (que no gasta tokens). '
                 'La recoge el /loop en su próximo tick, o pídesela en el chat: «haz la tarea en cola de '
                 f'{e(epid)}»."><span class="dot"></span>En cola para Claude · '
                 f'{e(act)} {e(qentry.get("produces") or P.STAGE.get(qentry.get("stage",cur),{}).get("name","?"))}</div>')

    gate_cls = {"abierto": "", "exportado": "warn", "firmado": "on"}.get(d["gate"], "")
    auto = f' · auto-avance hasta Stage {d["auto"]}' if d["auto"] < 12 else ""
    return (
        '<div class="epc">'
        f'<div class="epch"><span class="id">{e(epid)}</span> <b>{e(d["title"] or d["slug"])}</b> '
        f'<span class="tag">{e(d["track"])}</span> '
        f'<span class="tag">narra {e(d["narrator"])}</span></div>'
        + strip(epid, slug, cur, d["gate"])
        + f'<div class="now">Stage <b>{cur} · {e(sm.get("name","?"))}</b> '
          f'<span class="pill {gate_cls}"><span class="dot"></span>{e(d["gate"])}</span>{auto}</div>'
        + (f'<div class="notes">{e(d["notes"])}</div>' if d["notes"] else "")
        + qline
        + manifest
        + f'<div class="btns">{"".join(btns)}</div>'
        '</div>')


def _header():
    e = _h.escape
    served = P.SERVED
    import time
    lp = P.read_loop()
    loop_state = lp.get("state", "run")
    badge = {"run": ('on', 'Sesión activa'), "pause": ('warn', 'Sesión pausada'),
             "stop": ('off', 'Sesión cerrada')}.get(loop_state, ('off', loop_state))
    hb_tip = ('data-tip="Cuándo trabajó por última vez el /loop. Si está viejo o no aparece, el /loop no está '
              'corriendo: lánzalo con  /loop atiende  en la terminal del chat, o pide el trabajo directamente en el chat."')
    if lp.get("last_tick_ts"):
        m = int((time.time() - lp["last_tick_ts"]) / 60)
        cls = "on" if m < 5 else "warn"
        label = "/loop: tick ahora" if m < 1 else f"/loop: tick hace {m} min"
        heartbeat = f'<span class="pill {cls}" {hb_tip}><span class="dot"></span>{label}</span>'
    else:
        heartbeat = f'<span class="pill off" {hb_tip}><span class="dot"></span>/loop sin señal</span>'
    if loop_state == "run":
        loopbtns = ('<button class="btn ghost" data-loop="pause" data-tip="Detiene el trabajo automático un rato, sin cerrar la sesión. Para pausas cortas — cada rato sigue costando un poco.">Pausar</button>'
                    '<button class="btn ghost" data-loop="stop" data-tip="Termina la sesión automática. Claude deja de trabajar solo. El progreso NO se pierde. Para retomar hay que relanzar el /loop en la terminal.">Cerrar sesión</button>')
    elif loop_state == "pause":
        loopbtns = ('<button class="btn ghost" data-loop="run" data-tip="Vuelve a activar el trabajo automático.">Reanudar</button>'
                    '<button class="btn ghost" data-loop="stop" data-tip="Termina la sesión automática. El progreso NO se pierde.">Cerrar sesión</button>')
    else:
        loopbtns = ('<button class="btn ghost" data-loop="run" data-tip="Reactiva la señal. Después, relanza  /loop atiende el dashboard  en la terminal del chat.">Reanudar sesión</button>')
    cost = ('<a class="btn ghost spacer" href="cost.html" data-tipr '
            'data-tip="Cuántos tokens consume el sistema y qué fracción de tu plan. Con consejos para no gastar de más.">Consumo</a>'
            if COST_MD.exists() else '')
    return ('<h1 class="brand">Conquest<span class="of">Oficial</span></h1>'
            '<span class="count">panel de producción</span>'
            f'<span class="pill {badge[0]}"><span class="dot"></span>{badge[1]}</span>'
            + heartbeat
            + loopbtns
            + f'<a class="btn ghost" href="{served}ideas/idea-review.html" target="_blank" '
              'data-tip="El pool de ideas: puntúa, aprueba o descarta, pide ideas nuevas, y en una idea aprobada crea su episodio (Stage 0).">Ideas</a>'
            + cost)


def _tips():
    return (
        '<details class="tips"><summary>Cómo no gastar tokens</summary>'
        '<h4>El loop y la sesión</h4>'
        '<p>El <code>/loop atiende el dashboard</code> son turnos míos recurrentes en tu terminal de Claude Code. '
        'Cada tick cuesta algo (poco, va cacheado) aunque no haya trabajo. Para cerrarlo:</p>'
        '<ul>'
        '<li><b>Cerrar sesión</b> (arriba) — la forma limpia: el loop termina en su próximo tick y no se reprograma.</li>'
        '<li>o <b>dime</b> «para el loop». o <b>Esc</b> en la terminal del chat (más brusco).</li>'
        '<li><b>Pausar</b> detiene el trabajo pero el tick sigue costando — úsalo para pausas cortas, no largas.</li>'
        '<li>El estado (<code>_STATUS.md</code>, <code>_queue.json</code>) <b>no se pierde</b> al cerrar. Al retomar: reabre el panel, y para re-automatizar vuelve a lanzar <code>/loop atiende el dashboard</code>.</li>'
        '<li>El <b>server</b> (<code>serve.py</code>) es python puro — <b>no gasta tokens</b>. Ciérralo cuando quieras (su ventana «Conquest server»).</li>'
        '</ul>'
        '<h4>Flujo eficiente</h4><ul>'
        '<li><b>Reparte</b> research (Stage 2) y guion (Stage 4) en sesiones distintas de 5 h — juntas rozan el límite de la ventana.</li>'
        '<li>Deja que el server plegue los gates <b>mecánicos</b> (0·2·7·9·10) — no le pidas a Claude que lo haga.</li>'
        '<li>Una frase corta basta: «sigue». No repitas el contexto ni el estado — ya está en los ficheros.</li>'
        '<li><b>Nunca</b> «revisa el proyecto» / «lee los docs». El manifiesto de cada card dice exactamente qué se lee.</li>'
        '<li>Un episodio de una sola tirada roza el tope de 5 h — <b>párate tras el guion</b> y retoma en otra sesión.</li>'
        '<li>Fija el <b>auto-avance</b> en <code>_STATUS.md</code> bajo el stage donde quieres revisar, para que el loop pare ahí.</li>'
        '</ul></details>')


def build():
    e = _h.escape
    st = P.read_status()
    q = {}
    for x in P.read_queue():
        q.setdefault(x["ep"], {})[x["stage"]] = x
    cards = [_episode_card(epid, d, q.get(epid, {}).get(max(d["stage"], 0)))
             for epid, d in sorted(st.items())
             if not (d["slug"].startswith(epid) and "EXAMPLE" in d["slug"])]

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
  catch(e){{alert('El server no está corriendo. Abre Conquest-Dashboard.bat, o corre  python tools/serve.py');}}
}}
document.querySelectorAll('[data-adv]').forEach(b=>b.onclick=()=>post('/advance',{{ep:b.dataset.adv}}));
document.querySelectorAll('[data-done]').forEach(b=>b.onclick=()=>{{
  if(confirm('¿El contenido de este stage está escrito y aprobado?\\n\\nCierra el gate y avanza al siguiente stage.'))
    post('/stage-done',{{ep:b.dataset.done}});}});
document.querySelectorAll('[data-nudge]').forEach(b=>b.onclick=async()=>{{
  try{{const r=await fetch('http://localhost:{P.PORT}/nudge',{{method:'POST',
    headers:{{'content-type':'application/json'}},body:JSON.stringify({{ep:b.dataset.nudge}})}});
    const j=await r.json(); alert(j.msg||'marcado');}}
  catch(e){{alert('El server no está corriendo.');}}}});
document.querySelectorAll('[data-human]').forEach(b=>b.onclick=()=>{{
  const [ep,st]=b.dataset.human.split(':'); post('/human',{{ep,stage:+st}});}});
document.querySelectorAll('[data-loop]').forEach(b=>b.onclick=async()=>{{
  await post('/loop',{{state:b.dataset.loop}});}});

// Stage 8 — «Ver más» opens this instead of a page: pick the take, «Subir»
// copies it into assets/ (renamed) and pliega el gate + avanza a Edición.
const recDlg=document.getElementById('recmodal'), recFile=document.getElementById('recfile'),
      recBtn=document.getElementById('recupload'), recSt=document.getElementById('recstatus');
let recEp='';
document.querySelectorAll('[data-rec-open]').forEach(b=>b.onclick=()=>{{
  recEp=b.dataset.recOpen;
  document.getElementById('recep').textContent=recEp;
  recFile.value=''; recSt.textContent=''; recBtn.disabled=true;
  recDlg.showModal();
}});
document.getElementById('reccancel').onclick=()=>recDlg.close();
recFile.onchange=()=>{{ recBtn.disabled=!recFile.files.length; }};
recBtn.onclick=async()=>{{
  const f=recFile.files[0]; if(!f)return;
  recBtn.disabled=true; recSt.textContent='subiendo… ('+(f.size/1048576).toFixed(0)+' MB)';
  try{{
    const url='http://localhost:{P.PORT}/record-upload?ep='+encodeURIComponent(recEp)
      +'&name='+encodeURIComponent(f.name);
    const r=await fetch(url,{{method:'POST',body:f}});
    const j=await r.json().catch(()=>({{}}));
    if(r.ok){{alert('Toma subida.\\n'+(j.msg||'')+'\\nPanel actualizado.');location.reload();return;}}
    recSt.textContent=j.error||('server '+r.status); recBtn.disabled=false;
  }}catch(e){{recSt.textContent='El server no está corriendo (tools/serve.py).'; recBtn.disabled=false;}}
}};
"""
    welcome = (
        '<div class="welcome"><h2>Bienvenido a <b>Conquest</b></h2>'
        '<p>El panel de producción — de la idea a la publicación en 12 fases. '
        'Cada tarjeta es un capítulo: abre la revisión de su fase, aprueba o deja notas, '
        'y el gate se cierra solo. Nada aquí gasta tokens hasta que Claude trabaja.</p></div>')
    grid = ('<div class="epgrid">' + "".join(cards) + '</div>') if cards else (
        '<p class="muted">Ningún capítulo en producción. '
        'Añade una fila a <code>episodes/_STATUS.md</code> o aprueba una idea.</p>')
    recmodal = (
        '<dialog id="recmodal" class="recmodal"><form method="dialog">'
        '<h3>Subir la toma — <span id="recep"></span></h3>'
        '<p class="muted small">Elige el vídeo grabado (talking-head, Stage 8). Se copia a '
        '<code>assets/&lt;EPID&gt;-vo.&lt;ext&gt;</code>, cierra el gate y avanza a Stage 9 (Edición) — '
        'sin esperar al /loop.</p>'
        '<input type="file" id="recfile" accept="video/*">'
        '<p id="recstatus" class="muted small"></p>'
        '<div class="row" style="justify-content:flex-end;gap:.5rem;margin-top:.6rem">'
        '<button type="button" class="btn ghost" id="reccancel">Cancelar</button>'
        '<button type="button" class="btn primary" id="recupload" disabled>Subir</button>'
        '</div></form></dialog>')
    body = (
        welcome + _tips()
        + '<section><h2>En producción</h2>' + grid + '</section>'
        '<section><h2>Publicados</h2>' + hist + '</section>' + recmodal)
    return T.shell("Conquest · panel", _header(), body, script)


def build_cost():
    inner = md_to_html(COST_MD.read_text(encoding="utf-8"))
    updbtn = ('<button class="btn ghost" id="upd" '
              'data-tip="Pone la fecha de hoy, marca las filas con más de 3 meses para revisar, '
              'añade una línea al historial con la versión actual y un hueco para el dato real de '
              'consumo, y refresca esta página. No se inventa ningún número.">Actualizar</button>')
    header = ('<h1>Consumo del sistema</h1>' + updbtn
              + '<a class="btn ghost spacer" href="/">Volver al panel</a>')
    script = ("document.getElementById('upd').onclick=async()=>{"
              "try{const r=await fetch('http://localhost:8765/cost-update',{method:'POST',"
              "headers:{'content-type':'application/json'},body:'{}'});"
              "if(r.ok){const j=await r.json();alert(j.msg||'actualizado');location.reload();}"
              "else alert('server respondió '+r.status);}"
              "catch(e){alert('El server no está corriendo. Abre Conquest-Dashboard.bat, o corre  python tools/cost_update.py');}};")
    return T.shell("Consumo del sistema", header, f'<div class="doc">{inner}</div>', script)


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    msg = ""
    if COST_MD.exists():
        COST_HTML.write_text(build_cost(), encoding="utf-8")
        msg = " + cost.html"
    n = len(P.read_status())
    print(f"escrito  dashboard.html{msg}  ({n} episodios en _STATUS.md)")
