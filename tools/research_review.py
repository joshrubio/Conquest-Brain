#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
research_review.py — Stage 2 review surface.

Claude drafts `02-research-dossier.md` + `03-source-log.csv` from public
sources; this turns them into one page where a reviewer — Usuario 001 or
Usuario 002, doesn't matter — walks the dossier section by section and the
source-log row by row, ticks OK / revisar, leaves notes, and approves.

Reads  episodes/E0XX-slug/02-research-dossier.md
       episodes/E0XX-slug/03-source-log.csv
Writes episodes/E0XX-slug/02-research.html  (browser — gitignored)
       (reviewer exports)  02-research.txt  (tracked) -> Claude folds back

Usage
  python tools/research_review.py E0XX-slug
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
DOSSIER_F = "02-research-dossier.md"
LOG_F = "03-source-log.csv"
REVIEW_HTML = "02-research.html"
REVIEW_TXT = "02-research.txt"

GATE = [
    ("carga-tier-ab", "Cada afirmación de carga tiene ≥1 fuente Tier A/B"),
    ("disputados", "Los puntos disputados están identificados y marcados como tales"),
    ("sin-cd", "Nada de la narrativa depende solo de Tier C/D"),
    ("derechos", "El estado de derechos de cada visual está anotado"),
    ("coi", "Independencia/COI: contable desde documentación pública (brain/05)"),
]
WEAK = re.compile(r"verificar|a completar|d[ée]bil|an[eé]cdota|buscar 2a|tradici[oó]n|"
                  r"origen d[eé]bil|pendiente|sin confirmar|apócrifa", re.I)


def md_sections(txt):
    """-> [(title, body_html)]  for each ## section."""
    out = []
    for m in re.finditer(r"^##\s+(.+?)\s*\n(.*?)(?=^## |\Z)", txt, re.M | re.S):
        out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def md_to_html(md):
    e = _h.escape
    lines = md.splitlines()
    html, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        if ln.strip().startswith("|"):
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                tbl.append(lines[i]); i += 1
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in tbl]
            rows = [r for r in rows if not set("".join(r)) <= set("-: ")]
            if rows:
                head = "".join(f"<th>{e(c)}</th>" for c in rows[0])
                body = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>"
                               for r in rows[1:])
                html.append(f'<table class="mini"><tr>{head}</tr>{body}</table>')
            continue
        if ln.startswith(">"):
            html.append(f'<blockquote class="hint">{e(ln.lstrip("> ").rstrip())}</blockquote>')
        elif ln.strip():
            html.append(f'<p>{e(ln.strip())}</p>')
        i += 1
    return "".join(html) or '<p class="empty">— vacío —</p>'


def build(slug, sections, sources, tier_counts):
    e = _h.escape

    sec_cards = []
    for si, (title, body) in enumerate(sections):
        sec_cards.append(
            f'<div class="card" data-kind="sec" data-k="sec:{si}">'
            f'<h3>{e(title)}</h3>'
            f'<div class="body">{md_to_html(body)}</div>'
            '<div class="verdict">'
            f'<label><input type="radio" name="s{si}" class="st" data-k="sec:{si}" value="ok" checked> ok</label>'
            f'<label><input type="radio" name="s{si}" class="st" data-k="sec:{si}" value="revisar"> revisar</label>'
            '</div>'
            f'<textarea class="nt" data-k="sec:{si}" placeholder="nota (qué falta / qué corregir)"></textarea>'
            '</div>')

    rows = []
    for s in sources:
        sid = s.get("id", "?")
        weak = bool(WEAK.search(s.get("notes", "") + " " + s.get("rights_status", "")))
        tier = s.get("tier", "?")
        rows.append(
            f'<div class="card{" need" if weak else ""}" data-kind="src" data-k="src:{e(sid)}">'
            f'<div class="meta"><span class="tag">{e(sid)}</span> '
            f'<span class="tag">Tier {e(tier)}</span> '
            + (f'<span class="tag">{e(s.get("date",""))}</span>' if s.get("date") else "")
            + '</div>'
            f'<div style="font-size:.82rem"><b>{e(s.get("source_title",""))}</b>'
            + (f' — {e(s.get("author",""))}' if s.get("author") else "") + '</div>'
            f'<div style="font-size:.8rem;color:var(--muted)">{e(s.get("claim_or_use","")[:280])}</div>'
            + (f'<div style="font-size:.78rem;color:var(--muted)"><i>{e(s.get("notes","")[:220])}</i></div>'
               if s.get("notes") else "")
            + '<div class="row">'
            f'<select class="st" data-k="src:{e(sid)}">'
            '<option value="ok">fuente ok</option>'
            '<option value="tier">revisar tier</option>'
            '<option value="2a">falta 2ª fuente</option>'
            '<option value="completar">completar ref (ISBN/pág.)</option>'
            '<option value="abierto">abierto</option></select></div>'
            f'<textarea class="nt" data-k="src:{e(sid)}" placeholder="nota"></textarea>'
            '</div>')

    gate = "".join(
        f'<label class="opt"><input type="checkbox" class="ck" data-k="gate:{k}"><span>{e(v)}</span></label>'
        for k, v in GATE)

    body = (
        f'<section><h2>Fuentes <span>· {len(sources)} — '
        + " / ".join(f"{t}:{tier_counts.get(t,0)}" for t in "ABCD") + '</span></h2>'
        '<p class="hint">Marcadas en oro: la nota pide verificar algo (fecha, ISBN, 2ª fuente, anécdota de tradición).</p>'
        '<div class="grid">' + "\n".join(rows) + '</div></section>'
        f'<section><h2>Dossier <span>· {len(sections)} secciones</span></h2>'
        '<div class="grid wide">' + "\n".join(sec_cards) + '</div></section>'
        f'<section><h2>Gate Stage 2 y firma</h2>{gate}'
        '<div class="row" style="margin-top:.8rem">'
        '<input type="text" id="firma" placeholder="firma (Usuario 001 o Usuario 002)">'
        '<input type="text" id="fecha" placeholder="fecha AAAA-MM-DD">'
        '</div>'
        '<label class="opt" style="margin-top:.6rem"><input type="checkbox" id="aprob">'
        '<span>Dossier + source-log aprobados, pasa a guion</span></label>'
        '<textarea class="nt" data-k="firma:nota" placeholder="nota de cierre / qué queda pendiente"></textarea>'
        '</section>')

    script = f"""
const EPID={slug[:4]!r}; const STAGE=2;
const LS="conquest-research-{slug}";
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const cnt=$('.count');
const inp=$$('.st,.nt,.ck');
const K=el=>(el.classList.contains('st')?'st:':el.classList.contains('ck')?'ck:':'nt:')+el.dataset.k+':'+(el.name||'');
function save(){{
  const c={{}}; inp.forEach(el=>c[K(el)]=el.type==='checkbox'||el.type==='radio'?el.checked:el.value);
  c['#firma']=$('#firma').value; c['#fecha']=$('#fecha').value; c['#aprob']=$('#aprob').checked;
  localStorage.setItem(LS,JSON.stringify(c));
}}
function sync(){{
  save();
  const w=$$('.card.need').length;
  const wr=$$('[data-kind]').filter(r=>{{const s=r.querySelector('.st:checked')||r.querySelector('select.st');
    return s&&s.value!=='ok';}}).length;
  cnt.textContent=w+' fuentes a verificar · '+wr+' marcadas';
}}
const init=JSON.parse(localStorage.getItem(LS)||'null');
if(init){{
  inp.forEach(el=>{{const v=init[K(el)]; if(v===undefined)return;
    if(el.type==='checkbox'||el.type==='radio')el.checked=v; else el.value=v;}});
  $('#firma').value=init['#firma']||''; $('#fecha').value=init['#fecha']||'';
  $('#aprob').checked=!!init['#aprob'];
}}
$$('input,textarea,select').forEach(el=>el.addEventListener('input',sync));
sync();
$('#exp').onclick=()=>{{
  const L=['# {REVIEW_TXT} — 02-research.html','episodio\\t{slug}',
    'revisor\\t'+($('#firma').value.trim()||'(sin firmar)'),
    'fecha\\t'+($('#fecha').value.trim()||'?'),
    'aprobado\\t'+(($('#aprob').checked&&$('#firma').value.trim())?'si':'NO'),
    '','---FUENTES---'];
  $$('.card[data-kind="src"]').forEach(c=>{{
    const s=c.querySelector('select.st'), n=c.querySelector('.nt');
    const nt=n&&n.value?n.value.replace(/\\s+/g,' ').trim():'';
    if(s.value==='ok'&&!nt)return;
    L.push([c.dataset.k.slice(4),s.value,nt].join('\\t'));
  }});
  L.push('','---DOSSIER---');
  $$('.card[data-kind="sec"]').forEach(c=>{{
    const s=c.querySelector('.st:checked'), n=c.querySelector('.nt');
    const nt=n&&n.value?n.value.replace(/\\s+/g,' ').trim():'';
    if((!s||s.value==='ok')&&!nt)return;
    L.push([c.querySelector('h3').textContent,(s?s.value:'ok'),nt].join('\\t'));
  }});
  L.push('','---GATE---');
  $$('.ck[data-k^="gate:"]').forEach(c=>L.push(c.dataset.k.slice(5)+'\\t'+(c.checked?'ok':'NO')));
  const nf=$('.nt[data-k="firma:nota"]');
  if(nf&&nf.value.trim())L.push('','---NOTA---',nf.value.trim());
  finishStage('{REVIEW_TXT}', L.join('\\n')+'\\n', EPID, STAGE,
    'Guardado en la carpeta del episodio. Pásaselo a Claude para plegar en 02-research-dossier.md.');
}};
$('#clr').onclick=()=>{{localStorage.removeItem(LS);location.reload()}};
"""
    header = (f'<h1>Research · {e(slug)}</h1><span class="count"></span>'
              f'<button class="primary" id="exp">Exportar {REVIEW_TXT}</button>'
              '<button id="clr">Limpiar</button>')
    extra = ('<style>'
             '.card.need{border-color:var(--gold)}'
             '.grid.wide{grid-template-columns:1fr}'
             '.card .body{max-height:22rem;overflow:auto}'
             'table.mini{width:100%;border-collapse:collapse;font-size:.78rem;margin:.3rem 0}'
             'table.mini th{text-align:left;color:var(--muted);font-weight:600}'
             'table.mini td,table.mini th{border-top:1px solid var(--line);padding:.3rem .45rem;vertical-align:top}'
             'blockquote.hint{border-left:2px solid var(--line);margin:.4rem 0;padding-left:.7rem}'
             '.card .body p{margin:.35rem 0;font-size:.82rem}'
             '</style>')
    return page(f"Research · {slug}", header, body + extra, script)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: python tools/research_review.py E0XX-slug")
    slug = sys.argv[1].strip("/\\")
    ep = ROOT / "episodes" / slug
    dossier = ep / DOSSIER_F
    log = ep / LOG_F
    if not dossier.exists():
        sys.exit(f"no {dossier.relative_to(ROOT)}")
    sections = md_sections(dossier.read_text(encoding="utf-8"))
    sources, counts = [], {}
    if log.exists():
        with log.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                sources.append(row)
                counts[row.get("tier", "?")] = counts.get(row.get("tier", "?"), 0) + 1
    (ep / REVIEW_HTML).write_text(build(slug, sections, sources, counts), encoding="utf-8")
    print(f"escrito  episodes/{slug}/{REVIEW_HTML}  ({len(sections)} secciones, {len(sources)} fuentes)")
    print("siguiente: ábrelo, revisa fuentes + dossier, marca el gate, firma, «Exportar 02-research.txt»")
