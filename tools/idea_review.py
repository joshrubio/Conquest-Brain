#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
idea_review.py — Stage 0 review surface. Carmen scores + picks a hook-title +
comments on each idea in the pool, in a page instead of a markdown table.

Reads  ideas/idea-pool.md
Writes ideas/idea-review.html   (open in a browser — gitignored)
       (Carmen exports)  ideas/idea-review.txt   (tracked)

Loop: idea_review.py -> Carmen reviews -> exports idea-review.txt ->
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


def parse_pool(txt):
    """-> [{id, track, title, angle, close, material, score, status, hooks[], detail{}}]"""
    ideas = {}
    # summary tables: | T01-01 | Title | Angle | Close | Material | 20 | aprobada |
    for m in re.finditer(r"^\|\s*(T0[12]-\d+)\s*\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|",
                         txt, re.M):
        iid = m.group(1)
        ideas[iid] = {
            "id": iid, "track": "T01" if iid.startswith("T01") else "T02",
            "title": m.group(2).strip(), "angle": m.group(3).strip(),
            "close": m.group(4).strip(), "material": m.group(5).strip(),
            "score": re.sub(r"\D", "", m.group(6)) or "?",
            "status": m.group(7).strip(),
            "hooks": [], "note": "", "cierre": "",
        }
    # detail sections:  ### T01-01 · Coca-Cola
    for m in re.finditer(r"^### (T0[12]-\d+)[^\n]*\n(.*?)(?=^### |\Z)", txt, re.M | re.S):
        iid, block = m.group(1), m.group(2)
        if iid not in ideas:
            continue
        ideas[iid]["hooks"] = re.findall(r"^-\s+`([^`]+)`", block, re.M)
        cm = re.search(r"\*\*Cierre[^.]*\.\*\*\s*(.+)", block)
        nm = re.search(r"\*\*Notas:\*\*\s*(.+)", block)
        ideas[iid]["cierre"] = re.sub(r"\s+", " ", cm.group(1)).strip() if cm else ""
        ideas[iid]["note"] = re.sub(r"\s+", " ", nm.group(1)).strip() if nm else ""
    return [ideas[k] for k in ideas]


def build(ideas):
    e = _h.escape
    total = len(ideas)
    cards = []
    for i in ideas:
        hooks = "".join(
            f'<label class="opt"><input type="radio" name="hk_{e(i["id"])}" value="{n}">'
            f'<span><code>{n}</code> {e(hk)}</span></label>'
            for n, hk in enumerate(i["hooks"], 1)) or '<p class="empty">sin hook-titles en el detalle</p>'
        cards.append(
            f'<div class="card" data-id="{e(i["id"])}">'
            f'<h3>{e(i["id"])} · {e(i["title"])} '
            f'<span class="tag">{e(i["track"])}</span> '
            f'<span class="tag">est. {e(i["score"])}/21</span> '
            f'<span class="tag">{e(i["status"])}</span></h3>'
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
            '<textarea class="cmt" placeholder="comentario de Carmen (qué falla, qué reforzar, por qué el hook elegido…)"></textarea>'
            '</div>')
    body = (
        '<section><h2>Pool de ideas — revisión de Carmen '
        f'<span>({total})</span></h2>'
        '<p class="hint">Por idea: elige el hook-title más fuerte, pon veredicto, tu /21, y comenta. '
        '«Exportar» → Claude lo pliega en <code>idea-pool.md</code> (estado, hook elegido, tu nota).</p>'
        '<div class="grid">' + "\n".join(cards) + '</div></section>')
    script = f"""
const LS="exodo-ideareview";
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
document.getElementById('exp').onclick=()=>{{
  const o=state();
  const L=['# {REVIEW_TXT} — generado por idea-review.html',
           '# id  veredicto  /21|-  hook:N|-  nota: <texto>'];
  Object.entries(o).forEach(([id,x])=>{{
    if(x.v==='igual'&&!x.c&&!x.hk&&!x.s)return;
    L.push([id, x.v, x.s||'-', x.hk?('hook:'+x.hk):'-', x.c?('nota: '+x.c.replace(/\\s+/g,' ')):''].join('  ').trim());
  }});
  saveTxt('{REVIEW_TXT}', L.join('\\n')+'\\n',
    'Guardado en ideas/. Pásaselo a Claude para actualizar idea-pool.md.');
}};
document.getElementById('clr').onclick=()=>{{localStorage.removeItem(LS);location.reload()}};
"""
    header = ('<h1>Pool de ideas · Carmen</h1><span class="count"></span>'
              f'<button class="primary" id="exp">Exportar {REVIEW_TXT}</button>'
              '<button id="clr">Limpiar</button>')
    return page(f"Revisión de ideas", header, body, script)


if __name__ == "__main__":
    if not POOL.exists():
        sys.exit(f"no {POOL.relative_to(ROOT)}")
    ideas = parse_pool(POOL.read_text(encoding="utf-8"))
    if not ideas:
        sys.exit("no se parsearon ideas de idea-pool.md")
    OUT_HTML.write_text(build(ideas), encoding="utf-8")
    print(f"escrito  ideas/idea-review.html  ({len(ideas)} ideas)")
    print("siguiente: Carmen lo abre, revisa, «Exportar idea-review.txt», te lo pasa")
