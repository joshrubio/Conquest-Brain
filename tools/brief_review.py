#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brief_review.py — Stage 1 review surface (the brief).

Renders `01-brief.md` as an editable document:

- The **cabecera** (`| Campo | Valor |`) table — one labeled text input per
  row (ID episodio, Slug carpeta, Fecha del brief, Autor del brief, Track,
  Modo, Hook-title elegido, Guionista, Narrador asignado, Forma del cierre,
  Estado). A cell's value can contain a literal `|` (e.g. a hook-title like
  `... | Tulipomanía | Documental`, escaped in the .md as `\\|`) — it's
  unescaped for editing and re-escaped on save so the table never breaks.
- The rest of the document — Sujeto, Elegibilidad, Tesis de trabajo,
  Estructura, Por qué ahora, Top 3 fuentes, Cross-check, Riesgos,
  Estimación, Decisión — as one big editable `<textarea>` per `##`-level
  section (heading line included in the box, simplest way to reconstruct
  the file byte-faithfully for whatever the reviewer didn't touch).

"Guardar" autosaves to localStorage (fingerprinted against the doc's
current content via `freshLocal` — theme.py's HELPERS — so a stale browser
draft can never silently clobber a doc that changed on disk since).
"Finalizar Stage 1" POSTs the full reconstructed markdown to the local
server's /finish, which writes it verbatim back into 01-brief.md.

Reads  episodes/E0XX-slug/01-brief.md
Writes episodes/E0XX-slug/01-brief.html   (browser — gitignored)
       -> server writes the edited body straight back into 01-brief.md

Usage
  python tools/brief_review.py E0XX-slug
"""
import hashlib
import html as _h
import json
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
BRIEF_F = "01-brief.md"
REVIEW_HTML = "01-brief.html"

# same escaped-pipe-aware split as dash.py's md_to_html table parser — a
# cell can hold a literal "|" (a hook-title's " | " separators) escaped as
# "\|" in the markdown source; that must not be treated as a column break.
_ROW_SPLIT = re.compile(r"(?<!\\)\|")


def _split_row(line):
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.strip() for c in _ROW_SPLIT.split(inner)]


def parse(md):
    """-> (before, fields, mid, sections)
    before   — raw text up to (not including) the cabecera table, untouched
    fields   — [(label, value), ...] value already un-escaped ("\\|" -> "|")
    mid      — raw text between the table and the first "## " heading
    sections — [raw section text, ...] each starting with its own "## " line
    """
    m = re.search(r"(?:^\|.*(?:\n|\Z))+", md, re.M)
    if not m:
        # no table found (shouldn't happen for a real brief) — treat the
        # whole document as a single trailing blob so nothing is lost.
        return md, [], "", []
    before, table_text, after = md[:m.start()], m.group(0), md[m.end():]

    fields = []
    for ln in table_text.split("\n"):
        if not ln.strip():
            continue
        cells = _split_row(ln)
        if not cells:
            continue
        if set("".join(cells)) <= set("-: "):
            continue                       # separator row
        if cells[0].strip().lower() == "campo":
            continue                       # header row
        label = cells[0]
        value = "|".join(cells[1:]) if len(cells) > 2 else (cells[1] if len(cells) > 1 else "")
        fields.append((label, value.replace("\\|", "|")))

    parts = re.split(r"(?=^## )", after, flags=re.M)
    mid = parts[0] if parts else after
    sections = parts[1:] if len(parts) > 1 else []
    return before, fields, mid, sections


def _fmt_label(label):
    s = _h.escape(label)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def build(slug, before, fields, mid, sections):
    e = _h.escape

    hdr_rows = "".join(
        f'<tr><td>{_fmt_label(lab)}</td>'
        f'<td><input type="text" class="fld" data-idx="{i}" value="{e(val)}"></td></tr>'
        for i, (lab, val) in enumerate(fields)
    )

    sec_html = "".join(
        f'<div class="secwrap"><textarea class="sec" data-idx="{i}" rows="6" '
        f'spellcheck="false">{e(sec)}</textarea></div>'
        for i, sec in enumerate(sections)
    )

    body = (
        '<section><h2>Cabecera</h2>'
        '<p class="hint">Un campo por fila — incluido el hook-title, aunque contenga « | » literales '
        '(se guardan escapados en la tabla, se editan aquí sin escapar).</p>'
        '<table class="mini"><tr><th>Campo</th><th>Valor</th></tr>' + hdr_rows + '</table>'
        '</section>'
        '<section><h2>Documento</h2>'
        '<p class="hint">Cada bloque es una sección completa del brief (con su título <code>##</code> '
        'incluido) — edítala como texto libre. Al «Finalizar» se reconstruye el <code>01-brief.md</code> '
        'entero; lo que no toques se guarda exactamente igual.</p>'
        f'{sec_html}'
        '</section>'
    )

    fp_src = repr((before, [(l, v) for l, v in fields], mid, sections))
    fp = hashlib.sha1(fp_src.encode("utf-8")).hexdigest()[:12]

    script = f"""
const EPID={slug[:4]!r}; const STAGE=1;
const LS="conquest-brief:{slug}";
const HASH={json.dumps(fp)};
const BEFORE={json.dumps(before)};
const MID={json.dumps(mid)};
const LABELS={json.dumps([lab for lab, _ in fields])};
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const cnt=$('.count');
const secs=$$('.sec');
function autosize(el){{el.style.height='auto';el.style.height=(el.scrollHeight+2)+'px';}}
secs.forEach(autosize);

function state(){{
  return {{
    fields: $$('.fld').map(el=>el.value),
    sections: secs.map(el=>el.value),
  }};
}}
function sync(){{
  const s=state();
  localStorage.setItem(LS, JSON.stringify(Object.assign({{__h:HASH}}, s)));
  cnt.textContent = LABELS.length+' campos · '+secs.length+' secciones · guardado en este navegador';
}}
const {{fresh:init,hadStale}}=freshLocal(LS,HASH);
if(hadStale){{
  const note=document.createElement('p'); note.className='muted small';
  note.textContent='⚠ Se descartó un borrador local de una versión anterior de este brief (el documento cambió en disco desde tu última visita) — esto es lo recién generado.';
  document.querySelector('main').prepend(note);
}}
if(init){{
  $$('.fld').forEach((el,i)=>{{if(init.fields&&init.fields[i]!==undefined)el.value=init.fields[i];}});
  secs.forEach((el,i)=>{{if(init.sections&&init.sections[i]!==undefined){{el.value=init.sections[i];autosize(el);}}}});
}}
$$('.fld').forEach(el=>el.addEventListener('input',sync));
secs.forEach(el=>el.addEventListener('input',()=>{{autosize(el);sync();}}));
sync();

$('#save').onclick=()=>{{sync();alert('Guardado en este navegador (no cierra el gate).');}};
$('#clr').onclick=()=>{{localStorage.removeItem(LS);location.reload()}};
$('#exp').onclick=()=>{{
  const vals=$$('.fld').map(el=>el.value);
  let tbl='| Campo | Valor |\\n|---|---|\\n';
  LABELS.forEach((lab,i)=>{{
    const v=(vals[i]||'').replace(/\\|/g,'\\\\|');
    tbl+='| '+lab+' | '+v+' |\\n';
  }});
  const briefMd=BEFORE+tbl+MID+secs.map(el=>el.value).join('');
  finishStage('01-brief.txt', briefMd, EPID, STAGE,
    'Brief guardado en 01-brief.md.', {{brief_md: briefMd}});
}};
"""
    hd = (f'<h1>Brief · {e(slug)}</h1><span class="count"></span>'
          '<button id="save">Guardar</button>'
          '<button class="primary" id="exp">Finalizar Stage 1</button>'
          '<button id="clr">Limpiar</button>'
          '<a class="btn ghost spacer" href="http://localhost:8765/">Volver al panel</a>')
    extra = ('<style>'
             'table.mini{width:100%;border-collapse:collapse;font-size:.85rem;margin:.3rem 0}'
             'table.mini th{text-align:left;color:var(--muted);font-weight:600;padding:.35rem .6rem}'
             'table.mini td{border-top:1px solid var(--line);padding:.5rem .6rem;vertical-align:top}'
             'table.mini td:first-child{width:30%;color:var(--muted);font-size:.82rem}'
             'table.mini input{width:100%}'
             '.secwrap{margin:0 0 1.1rem}'
             '.sec{display:block;width:100%;min-height:6rem;font-family:var(--mono);font-size:.82rem;'
             'line-height:1.55;resize:vertical;overflow:hidden;background:var(--bg-2);'
             'border:1px solid var(--line-2);border-radius:8px;padding:.7rem .8rem;color:var(--fg)}'
             '.sec:focus{outline:1px dashed var(--gold-line)}'
             '</style>')
    return page(f"Brief · {e(slug)}", hd, body + extra, script)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: python tools/brief_review.py E0XX-slug")
    slug = sys.argv[1].strip("/\\")
    ep = ROOT / "episodes" / slug
    f = ep / BRIEF_F
    if not f.exists():
        sys.exit(f"no {f.relative_to(ROOT)}")
    before, fields, mid, sections = parse(f.read_text(encoding="utf-8"))
    (ep / REVIEW_HTML).write_text(build(slug, before, fields, mid, sections), encoding="utf-8")
    print(f"escrito  episodes/{slug}/{REVIEW_HTML}  ({len(fields)} campos, {len(sections)} secciones)")
    print("siguiente: ábrelo, edita, «Finalizar Stage 1»")
