#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
idea_review.py — Stage 0 review surface. The editorial reviewer (Usuario 002)
scores + picks a hook-title + comments on each idea in the pool, in a page
instead of a markdown table.

Reads  ideas/idea-pool.md
Writes ideas/idea-review.html   (open in a browser — gitignored)
       (reviewer exports)  ideas/idea-review.txt   (tracked)

Loop: idea_review.py -> reviewer reviews -> exports idea-review.txt ->
Claude folds the verdicts / chosen hooks / notes back into idea-pool.md.

Usage
  python tools/idea_review.py
"""
import html as _h
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_ui import page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
POOL = ROOT / "ideas" / "idea-pool.md"
OUT_HTML = ROOT / "ideas" / "idea-review.html"
REVIEW_TXT = "idea-review.txt"


# statuses that have left the review board — the idea is a folder now, or dead
HIDDEN_STATUS = ("en producción", "en produccion", "publicada", "descartada")


def parse_pool(txt):
    """-> ([idea…], hidden_count).  idea = {id, track, title, angle, close, material,
    score, status, hooks[], chosen_hook, cierre, note, cpm, audience}"""
    ideas = {}
    # summary tables: | DOC-01 | Title | Angle | Close | Material | 20 | aprobada |
    for m in re.finditer(r"^\|\s*((?:DOC|ENS)-\d+)\s*\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|",
                         txt, re.M):
        iid = m.group(1)
        ideas[iid] = {
            "id": iid, "track": "Ensayo" if iid.startswith("ENS") else "Documental",
            "title": m.group(2).strip(), "angle": m.group(3).strip(),
            "close": m.group(4).strip(), "material": m.group(5).strip(),
            "score": re.sub(r"\D", "", m.group(6)) or "?",
            "status": m.group(7).strip(),
            "hooks": [], "chosen_hook": "", "note": "", "cierre": "", "cpm": "", "audience": "",
        }
    # detail sections:  ### DOC-01 · Coca-Cola
    for m in re.finditer(r"^### ((?:DOC|ENS)-\d+)[^\n]*\n(.*?)(?=^### |\Z)", txt, re.M | re.S):
        iid, block = m.group(1), m.group(2)
        if iid not in ideas:
            continue
        ideas[iid]["hooks"] = re.findall(r"^-\s+`([^`]+)`", block, re.M)
        hkm = re.search(r"(?m)^-\s+\*\*Hook elegido:\*\*\s*`([^`]+)`", block)
        ideas[iid]["chosen_hook"] = hkm.group(1) if hkm else ""
        cm = re.search(r"\*\*Cierre[^.]*\.\*\*\s*(.+)", block)
        nm = re.search(r"\*\*Notas:\*\*\s*(.+)", block)
        mm = re.search(r"\*\*Monetización:\*\*\s*Categoría\s+([ABC])\s*·\s*Audiencia\s+(.+)", block)
        ideas[iid]["cierre"] = re.sub(r"\s+", " ", cm.group(1)).strip() if cm else ""
        ideas[iid]["note"] = re.sub(r"\s+", " ", nm.group(1)).strip() if nm else ""
        ideas[iid]["cpm"] = mm.group(1) if mm else ""
        ideas[iid]["audience"] = re.sub(r"\s+", " ", mm.group(2)).strip() if mm else ""
    visible = [ideas[k] for k in ideas
               if not ideas[k]["status"].lower().startswith(HIDDEN_STATUS)]
    return visible, len(ideas) - len(visible)


def build(ideas, hidden=0):
    e = _h.escape
    total = len(ideas)
    cards = []
    for i in ideas:
        hooks = "".join(
            f'<label class="opt"><input type="radio" name="hk_{e(i["id"])}" value="{n}"'
            f'{" checked" if hk == i["chosen_hook"] else ""}>'
            f'<span><code>{n}</code> {e(hk)}</span></label>'
            for n, hk in enumerate(i["hooks"], 1)) or '<p class="empty">sin hook-titles en el detalle</p>'
        produce = (
            f'<button class="accent" data-produce="{e(i["id"])}" '
            'data-tip="Crea la carpeta del episodio desde la plantilla, marca esta idea como «en producción» '
            '(sale del pool) y la pone en el panel en Stage 0.">Crear episodio →</button>'
            if i["status"] == "aprobada" else "")
        cpm_lab = {"A": "CPM alta", "B": "CPM media", "C": "CPM baja"}.get(i["cpm"], "")
        mon = (f'<span class="tag mon mon-{e(i["cpm"].lower())}">{e(cpm_lab)}</span> '
               f'<span class="tag mon">{e(i["audience"])}</span>') if i["cpm"] else ""
        cards.append(
            f'<div class="card" data-id="{e(i["id"])}">'
            f'<h3>{e(i["id"])} · {e(i["title"])} '
            f'<span class="tag">{e(i["track"])}</span> '
            f'<span class="tag">est. {e(i["score"])}/21</span> '
            f'<span class="tag">{e(i["status"])}</span> {mon}</h3>'
            f'<div class="meta"><b>Ángulo:</b> {e(i["angle"])}<br>'
            f'<b>Cierre:</b> {e(i["close"])}'
            + (f' — {e(i["cierre"])}' if i["cierre"] else "")
            + f'<br><b>Material:</b> {e(i["material"])}'
            + (f'<br><b>Notas:</b> {e(i["note"])}' if i["note"] else "")
            + '</div>'
            f'<div><b style="font-size:.8rem">Hook-title preferido:</b>{hooks}</div>'
            '<div class="verdict">'
            f'<label><input type="radio" name="v_{e(i["id"])}" value="aprobar"> aprobar</label>'
            f'<label><input type="radio" name="v_{e(i["id"])}" value="incubar"> incubar</label>'
            f'<label><input type="radio" name="v_{e(i["id"])}" value="descartar"> descartar</label>'
            f'<label><input type="radio" name="v_{e(i["id"])}" value="igual" checked> dejar igual</label>'
            '</div>'
            '<div class="row">'
            f'<input type="number" class="score" min="0" max="21" placeholder="tu /21 (est. {e(i["score"])})">'
            '</div>'
            '<textarea class="cmt" placeholder="comentario de revisión (qué falla, qué reforzar, por qué el hook elegido…)"></textarea>'
            + (f'<div class="prod">{produce}</div>' if produce else "")
            + '</div>')
    hid = (f' · <span class="muted">{hidden} fuera del pool (en producción / publicadas / descartadas) — '
           'en <code>idea-pool.md</code></span>') if hidden else ""
    body = (
        '<section><h2>Pool de ideas — revisión editorial '
        f'<span>({total})</span></h2>'
        '<p class="hint">Por idea: elige el hook-title más fuerte, pon veredicto (aprobar / incubar / descartar), tu /21, y comenta. '
        '<b>«Aplicar cambios»</b> escribe los estados en <code>idea-pool.md</code> al momento (aprobar → <code>aprobada</code>, '
        'incubar → <code>incubando</code>, descartar → <code>descartada</code>) y guarda el hook elegido. '
        'En una idea <code>aprobada</code>, <b>«Crear episodio →»</b> monta su carpeta y la saca del pool. '
        '<b>«Generar 3 ideas»</b> pone a Claude a añadir ideas nuevas al pool, sin avanzar de stage.'
        + hid + '</p>'
        '<div class="grid">' + "\n".join(cards) + '</div></section>'
        '<style>'
        '.prod{margin-top:.7rem;padding-top:.7rem;border-top:1px solid var(--line-2)}'
        '.tag.mon-a{background:var(--lime-soft);color:var(--lime);border-color:var(--lime-line)}'
        '.tag.mon-b{background:var(--gold-soft);color:var(--gold);border-color:var(--gold-line)}'
        '.tag.mon-c{background:var(--surface-2);color:var(--muted)}'
        '</style>')
    script = f"""
const LS="conquest-ideareview";
const cards=[...document.querySelectorAll('.card')];
const cnt=document.querySelector('.count');
function state(){{
  const o={{}};
  cards.forEach(c=>{{
    const id=c.dataset.id;
    const v=(c.querySelector('input[name="v_'+id+'"]:checked')||{{}}).value||'igual';
    const hk=(c.querySelector('input[name="hk_'+id+'"]:checked')||{{}}).value||'';
    o[id]={{v,hk,s:c.querySelector('.score').value.trim(),c:c.querySelector('.cmt').value.trim()}};
  }});
  return o;
}}
function sync(){{
  const o=state(); localStorage.setItem(LS,JSON.stringify(o));
  let done=0; Object.values(o).forEach(x=>{{if(x.v!=='igual'||x.c||x.hk||x.s)done++}});
  cnt.textContent=done+' / {total} tocadas';
}}
const init=jget(LS,{{}});
cards.forEach(c=>{{
  const id=c.dataset.id, s=init[id]; if(s){{
    if(s.v){{const r=c.querySelector('input[name="v_'+id+'"][value="'+s.v+'"]'); if(r)r.checked=true;}}
    if(s.hk){{const r=c.querySelector('input[name="hk_'+id+'"][value="'+s.hk+'"]'); if(r)r.checked=true;}}
    if(s.s)c.querySelector('.score').value=s.s;
    if(s.c)c.querySelector('.cmt').value=s.c;
  }}
  c.querySelectorAll('input,textarea').forEach(x=>x.addEventListener('input',sync));
}});
sync();
async function srv(path,body,ok){{
  try{{const r=await fetch(DASH+path,{{method:'POST',headers:{{'content-type':'application/json'}},
    body:JSON.stringify(body)}});
    if(r.ok){{const j=await r.json();alert((j.msg||ok)); if(j.reload!==false)location.reload(); return true;}}
    let j={{}}; try{{j=await r.json()}}catch(e){{}}
    alert(j.error||('server '+r.status));}}catch(e){{return false;}}
}}
document.getElementById('exp').onclick=async()=>{{
  const o=state();
  const verdicts={{}};
  const L=['# {REVIEW_TXT} — generado por idea-review.html',
           '# id  veredicto  /21|-  hook:N|-  nota: <texto>'];
  Object.entries(o).forEach(([id,x])=>{{
    if(x.v==='igual'&&!x.c&&!x.hk&&!x.s)return;
    verdicts[id]={{v:x.v,hook:x.hk,score:x.s,c:x.c}};
    L.push([id, x.v, x.s||'-', x.hk?('hook:'+x.hk):'-', x.c?('nota: '+x.c.replace(/\\s+/g,' ')):''].join('  ').trim());
  }});
  const txt=L.join('\\n')+'\\n';
  if(await srv('/ideas',{{verdicts,txt}},'Pool actualizado.'))return;
  saveTxt('{REVIEW_TXT}', txt, 'Guardado en ideas/ (server no detectado). Pásaselo a Claude.');
}};
const nb=document.getElementById('newideas');
if(nb)nb.onclick=()=>srv('/ideas-new',{{n:3}},'3 ideas en cola.');
document.querySelectorAll('[data-produce]').forEach(b=>b.onclick=async()=>{{
  const id=b.dataset.produce, card=b.closest('.card');
  const hk=(card.querySelector('input[name="hk_'+id+'"]:checked')||{{}}).value||'';
  if(!confirm('¿Crear la carpeta de episodio para '+id+'?\\n\\nLa idea sale del pool y aparece en el panel en Stage 0. '
    +'Si quieres fijar un hook-title como título de trabajo, márcalo antes de continuar.'))return;
  b.disabled=true; b.textContent='creando…';
  if(!await srv('/idea-produce',{{id,hook:hk}},'Episodio creado.')){{b.disabled=false;b.textContent='Crear episodio →';}}
}});
document.getElementById('clr').onclick=()=>{{localStorage.removeItem(LS);location.reload()}};
"""
    header = ('<h1>Pool de ideas</h1><span class="count"></span>'
              f'<button class="primary" id="exp">Aplicar cambios</button>'
              '<button id="newideas">Generar 3 ideas</button>'
              '<button id="clr">Limpiar</button>'
              '<a class="btn ghost spacer" href="http://localhost:8765/">Volver al panel</a>')
    return page(f"Revisión de ideas", header, body, script)


if __name__ == "__main__":
    if not POOL.exists():
        sys.exit(f"no {POOL.relative_to(ROOT)}")
    ideas, hidden = parse_pool(POOL.read_text(encoding="utf-8"))
    if not ideas:
        sys.exit("no se parsearon ideas activas de idea-pool.md")
    OUT_HTML.write_text(build(ideas, hidden), encoding="utf-8")
    print(f"escrito  ideas/idea-review.html  ({len(ideas)} ideas, {hidden} fuera del pool)")
    print("siguiente: el revisor lo abre, revisa, «Aplicar cambios», te lo pasa")
