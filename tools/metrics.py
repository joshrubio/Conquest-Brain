#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
metrics.py — Stage 12 review surface. Paste the YouTube Studio numbers at
48 h and 30 d; export → a KPI-log row in brain/07 + a metrics block in
11-retro.md.

  python tools/metrics.py E0XX-slug

Reads  episodes/E0XX-slug/  (title from _STATUS.md)
Writes episodes/E0XX-slug/12-metrics.html  (browser — gitignored)
       (export)  12-metrics.txt  →  fold_retro (advance.py)
"""
import html as _h
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_ui import page  # noqa: E402
import pipeline as P  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FIELDS = [
    ("pub", "Fecha de publicación (AAAA-MM-DD)"),
    ("len", "Duración (mm:ss)"),
    ("views48", "Views a 48 h"), ("avd48", "AVD % a 48 h"), ("ctr48", "CTR % a 48 h"),
    ("views", "Views a 30 d"), ("avd", "AVD % a 30 d"), ("ctr", "CTR % a 30 d"),
    ("ret_refl", "Retención en el marcador «Reflexión» (%)"),
    ("ret_takeaway", "Retención en «Para llevar» (%)"),
    ("subs", "Suscriptores ganados (30 d)"),
    ("returning", "% espectadores que vuelven"),
    ("notes", "Nota cualitativa (comentarios: ¿pensamiento o indignación?)"),
]


def build(slug, title):
    e = _h.escape
    rows = "".join(
        f'<label class="opt" style="flex-direction:column;align-items:stretch">'
        f'<span style="font-size:.8rem;color:var(--muted);margin-bottom:.2rem">{e(lbl)}</span>'
        f'<input type="text" data-k="{k}"></label>' for k, lbl in FIELDS)
    body = (
        f'<section><h2>Métricas · {e(slug)} — {e(title)}</h2>'
        '<p class="hint">Dos pasadas: a las 48 h y a los 30 d (`brain/07`). Rellena lo que tengas y exporta; '
        'la fila del KPI log y el bloque de `11-retro.md` se escriben solos.</p>'
        '<div class="grid">' + rows + '</div></section>'
        '<section><h2>Firma</h2>'
        '<div class="row"><input type="text" id="firma" placeholder="quién (Usuario 001 o Usuario 002)">'
        '<input type="text" id="fecha" placeholder="fecha de esta pasada"></div>'
        '<label class="opt" style="margin-top:.6rem"><input type="checkbox" id="ok"> '
        'Retro cerrada (30 d) — episodio archivado</label></section>')
    script = f"""
const LS="conquest-metrics-{slug}", $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
function save(){{const o={{}};$$('[data-k]').forEach(i=>o[i.dataset.k]=i.value);
  o._f=$('#firma').value;o._d=$('#fecha').value;o._ok=$('#ok').checked;
  localStorage.setItem(LS,JSON.stringify(o));}}
const i=JSON.parse(localStorage.getItem(LS)||'null');
if(i){{$$('[data-k]').forEach(x=>{{if(i[x.dataset.k]!=null)x.value=i[x.dataset.k]}});
  $('#firma').value=i._f||'';$('#fecha').value=i._d||'';$('#ok').checked=!!i._ok;}}
$$('input').forEach(x=>x.addEventListener('input',save));
$('#exp').onclick=()=>{{
  const m={{}};$$('[data-k]').forEach(x=>{{if(x.value.trim())m[x.dataset.k]=x.value.trim();}});
  const L=['# 12-metrics.txt','episodio\\t{slug}','fecha\\t'+($('#fecha').value.trim()||'?'),
    'quien\\t'+($('#firma').value.trim()||'?'),'cerrada\\t'+($('#ok').checked?'si':'NO'),'','---METRICAS---'];
  Object.entries(m).forEach(([k,v])=>L.push(k+'\\t'+v));
  finishStage('12-metrics.txt', L.join('\\n')+'\\n', '{slug}'.slice(0,4), 12,
    'Guardado — pásaselo a Claude o corre  python tools/advance.py fold {slug}',
    {{metrics:m}});
}};
$('#clr').onclick=()=>{{localStorage.removeItem(LS);location.reload()}};
"""
    hd = (f'<h1>Métricas · {e(slug)}</h1><span class="count"></span>'
          '<button class="primary" id="exp">Finalizar Stage 12</button>'
          '<button id="clr">Limpiar</button>')
    return page(f"Métricas · {slug}", hd, body, script)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: python tools/metrics.py E0XX-slug")
    slug = sys.argv[1].strip("/\\")
    ep = P.ROOT / "episodes" / slug
    if not ep.exists():
        sys.exit(f"no {ep}")
    title = P.read_status().get(slug[:4], {}).get("title", "")
    (ep / "12-metrics.html").write_text(build(slug, title), encoding="utf-8")
    print(f"escrito  episodes/{slug}/12-metrics.html")
    print("siguiente: rellena las métricas, «Finalizar Stage 12»")
