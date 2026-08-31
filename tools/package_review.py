#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
package_review.py — Stage 10 review surface. Pick the title, pick the thumbnail,
review the description — with the editorial reviewer (Usuario 002) — in a page.

Reads  episodes/E0XX-slug/08-thumbnail-title.md   (3 title candidates)
       episodes/E0XX-slug/09-description.md        (assembled description)
       episodes/E0XX-slug/03-source-log.csv        (Fuentes principales, Tier A/B)
       episodes/E0XX-slug/assets/thumb/*           (thumbnail variants, if any)
Writes episodes/E0XX-slug/10-package.html   (browser — gitignored)
       (reviewer exports)  10-package.txt   (tracked) -> Claude folds into 08 + 09

Usage
  python tools/package_review.py E0XX-slug --init   # scaffold 08 + 09 from templates
  python tools/package_review.py E0XX-slug
"""
import csv
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
EP_DIR = ROOT / "episodes"
TPL = ROOT / "templates"
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}


def scaffold(ep, slug):
    for src, dst in (("thumbnail-title-brief.md", "08-thumbnail-title.md"),
                     ("description-and-credits.md", "09-description.md")):
        d = ep / dst
        if d.exists():
            print(f"  ya existe {dst}")
            continue
        t = (TPL / src).read_text(encoding="utf-8")
        if dst.startswith("08"):
            hooks = _hooks_for(slug)
            if hooks:
                for letter, hk in zip("ABC", hooks):
                    t = t.replace(f"> <título {letter}>", f"> {hk}", 1)
                print(f"  {dst}: 3 hook-titles de idea-pool insertados")
        d.write_text(t, encoding="utf-8")
        print(f"  creado {dst}")


def _hooks_for(slug):
    pool = ROOT / "ideas" / "idea-pool.md"
    if not pool.exists():
        return []
    key = slug.split("-", 1)[-1].lower()
    for m in re.finditer(r"^### T0[12]-\d+ · ([^\n]+)\n(.*?)(?=^### |\Z)",
                         pool.read_text(encoding="utf-8"), re.M | re.S):
        if key in m.group(1).lower():
            return re.findall(r"^-\s+`([^`]+)`", m.group(2), re.M)[:3]
    return []


def title_candidates(ep):
    f = ep / "08-thumbnail-title.md"
    if not f.exists():
        return []
    out = []
    for m in re.finditer(r"^### [ABC]\s*\n>\s*(.+)$", f.read_text(encoding="utf-8"), re.M):
        t = m.group(1).strip()
        if t and not t.startswith("<título"):
            out.append(t)
    return out


def description_text(ep):
    f = ep / "09-description.md"
    if not f.exists():
        return ""
    t = f.read_text(encoding="utf-8")
    m = re.search(r"## TEXTO PARA PEGAR EN YOUTUBE\s*\n(.*?)\n---", t, re.S)
    return (m.group(1).strip() if m else t).strip()


def fuentes_block(ep):
    f = ep / "03-source-log.csv"
    if not f.exists():
        return ""
    lines = []
    with f.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if (r.get("tier") or "").strip().upper() not in ("A", "B"):
                continue
            if not (r.get("source_title") or "").strip():
                continue
            bits = [x for x in (r.get("author"), f"«{r['source_title'].strip()}»",
                                r.get("publisher"), r.get("date")) if x and x.strip()]
            ref = (r.get("url_or_reference") or "").strip()
            lines.append("- " + ", ".join(b.strip() for b in bits) + (f". {ref}" if ref else "."))
    return "\n".join(lines)


def build(ep, slug):
    e = _h.escape
    titles = title_candidates(ep)
    desc = description_text(ep)
    fuentes = fuentes_block(ep)
    thumbs = []
    td = ep / "assets" / "thumb"
    if td.is_dir():
        thumbs = [f for f in sorted(td.iterdir()) if f.suffix.lower() in IMG_EXT]

    t_html = "".join(
        f'<label class="opt"><input type="radio" name="titulo" value="{e(t)}">'
        f'<span>{e(t)} <code>{len(t)} car.</code></span></label>' for t in titles
    ) or '<p class="empty">sin candidatos en 08-thumbnail-title.md</p>'

    if thumbs:
        th_html = '<div class="grid">' + "".join(
            f'<label class="card" style="cursor:pointer">'
            f'<img src="assets/thumb/{e(f.name)}" style="width:100%;border-radius:8px;aspect-ratio:16/9;object-fit:cover">'
            f'<label class="opt"><input type="radio" name="thumb" value="assets/thumb/{e(f.name)}"> {e(f.name)}</label>'
            f'</label>' for f in thumbs) + '</div>'
    else:
        th_html = ('<p class="empty">sin variantes en assets/thumb/</p>'
                   '<input type="text" id="thumbpath" placeholder="ruta de la miniatura elegida (opcional)">')

    body = (
        '<section><h2>Título '
        f'<span>({len(titles)} candidatos · ≤ ~70 car. visibles)</span></h2>'
        f'{t_html}'
        '<div class="row" style="margin-top:.6rem"><input type="text" id="titulo_otro" '
        'placeholder="otro título (si ninguno convence)"></div></section>'

        '<section><h2>Miniatura</h2>'
        f'{th_html}</section>'

        '<section><h2>Descripción <span>— edítala aquí, es el texto final</span></h2>'
        f'<textarea id="desc" style="min-height:22rem">{e(desc)}</textarea>'
        + (f'<details style="margin-top:.6rem"><summary>Fuentes principales (Tier A/B de 03-source-log.csv) — para pegar</summary>'
           f'<pre class="box">{e(fuentes)}</pre></details>' if fuentes else "")
        + '</section>'

        '<section><h2>Aprobación editorial</h2>'
        '<div class="verdict">'
        '<label><input type="checkbox" id="ok_t"> título OK</label>'
        '<label><input type="checkbox" id="ok_m"> miniatura OK</label>'
        '<label><input type="checkbox" id="ok_d"> descripción OK</label>'
        '</div>'
        '<textarea id="nota" placeholder="nota de revisión (qué cambiar en título/miniatura/descripción)" '
        'style="margin-top:.6rem"></textarea></section>'
    )

    script = f"""
const LS="exodo-package:{e(slug)}";
const $=s=>document.querySelector(s);
function state(){{
  return {{
    t:(document.querySelector('input[name=titulo]:checked')||{{}}).value||'',
    to:$('#titulo_otro').value.trim(),
    m:(document.querySelector('input[name=thumb]:checked')||{{}}).value||($('#thumbpath')?$('#thumbpath').value.trim():''),
    d:$('#desc').value,
    ok:[$('#ok_t').checked&&'titulo',$('#ok_m').checked&&'miniatura',$('#ok_d').checked&&'descripcion'].filter(Boolean),
    n:$('#nota').value.trim(),
  }};
}}
function sync(){{
  const s=state(); localStorage.setItem(LS,JSON.stringify(s));
  $('.count').textContent=s.ok.length+' / 3 aprobados';
}}
const i=jget(LS,null);
if(i){{
  if(i.t){{const r=document.querySelector('input[name=titulo][value="'+CSS.escape(i.t)+'"]'); if(r)r.checked=true;}}
  if(i.to)$('#titulo_otro').value=i.to;
  if(i.m){{const r=document.querySelector('input[name=thumb][value="'+CSS.escape(i.m)+'"]'); if(r)r.checked=true; else if($('#thumbpath'))$('#thumbpath').value=i.m;}}
  if(i.d)$('#desc').value=i.d;
  (i.ok||[]).forEach(k=>{{const el=$('#ok_'+k[0]); if(el)el.checked=true}});
  if(i.n)$('#nota').value=i.n;
}}
document.querySelectorAll('input,textarea').forEach(x=>x.addEventListener('input',sync));
sync();
$('#exp').onclick=()=>{{
  const s=state(), title=s.to||s.t;
  const L=['# 10-package.txt — generado por 10-package.html',
           'titulo\\t'+title,
           'miniatura\\t'+s.m,
           'aprobado\\t'+s.ok.join(','),
           'nota\\t'+s.n.replace(/\\n/g,' '),
           '---DESCRIPCION---', s.d];
  saveTxt('10-package.txt', L.join('\\n')+'\\n',
    'Guardado en la carpeta del episodio. Pásaselo a Claude para cerrar 08 + 09.');
}};
$('#clr').onclick=()=>{{localStorage.removeItem(LS);location.reload()}};
"""
    header = (f'<h1>Paquete · {e(slug)}</h1><span class="count"></span>'
              '<button class="primary" id="exp">Exportar 10-package.txt</button>'
              '<button id="clr">Limpiar</button>')
    return page(f"Paquete — {e(slug)}", header, body, script)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    slug = a[0]
    ep = EP_DIR / slug
    if not ep.is_dir():
        sys.exit(f"no existe {ep}")
    if "--init" in a:
        scaffold(ep, slug)
        sys.exit(0)
    if not (ep / "08-thumbnail-title.md").exists():
        sys.exit(f"no {slug}/08-thumbnail-title.md — corre:  python tools/package_review.py {slug} --init")
    (ep / "10-package.html").write_text(build(ep, slug), encoding="utf-8")
    print(f"escrito  episodes/{slug}/10-package.html")
    print("siguiente: el revisor lo abre, elige título + miniatura, revisa la descripción, «Exportar 10-package.txt»")
