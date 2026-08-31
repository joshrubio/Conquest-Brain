#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
script_review.py — Stage 4 review surface (the script pass).

Turns `05-script.md` into one page: every beat as a card you can approve
or comment on, with a short explainer for each narrative technical note
(`[EXPLICADOR]`, `[PLANT]`, `[HOOK VISUAL]`, `[S..]`, the close forms /
registers…) so the reviewer learns the model while correcting the script.

Reads  episodes/E0XX-slug/05-script.md
Writes episodes/E0XX-slug/05-script.html   (browser — gitignored)
       (reviewer exports)  05-script-pass.txt  (tracked) -> Claude folds edits into 05-script.md

Usage
  python tools/script_review.py E0XX-slug
"""
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
SCRIPT_F = "05-script.md"
REVIEW_HTML = "05-script.html"
REVIEW_TXT = "05-script-pass.txt"

# --- the teaching layer: one explainer per marker / structural element ---
NOTES = {
    "NARRACIÓN": ("Lo que dice el narrador, palabra por palabra.",
                  "Voz de investigador en 1ª persona ('investigando, descubrí que…'); todo 'descubrí' corresponde a una fuente real.", "brain/08 §2"),
    "EN PANTALLA": ("Qué se ve: documento, foto, dato, rótulo.",
                    "Lleva fuente [S..] + estado de derechos. En pantalla NO van tarjetas de fuente — las citas viven en la descripción.", "brain/03, brain/06 Stage 6"),
    "NOTA": ("Indicación de tono / pausa / música / edición para producción.",
             "No se narra. Es una acotación.", "brain/02"),
    "EXPLICADOR": ("Mini-cátedra: la historia se pausa para enseñar un concepto que el espectador necesita.",
                   "Señalizado al entrar ('por si no sabes qué es…') y al salir ('ahora que tienes esto, volvamos'). Todo dato dentro lleva [S..]. 2–4 por episodio.", "brain/02 §2"),
    "HOOK VISUAL": ("2–5 planos del cold open, corte seco al ritmo de la voz; cada uno ilustra una imagen concreta que la narración nombra.",
                    "Vídeo stock preferido sobre un empuje en una fija. El último plano es el 'giro' y aguanta ½ s antes del corte a negro.", "brain/02 §0, brain/11"),
    "PLANT": ("Foreshadowing: se planta un detalle ('quiero que recuerdes esto') que se pagará más adelante.",
              "3–6 por episodio, TODOS pagados. En el montaje, el plano del PLANT y el del PAY son el mismo.", "brain/02 §2, brain/11 §2.1"),
    "PAY": ("El pago de un PLANT: '¿recuerdas lo que dije sobre X? Aquí es donde importa.'",
            "Si un PLANT no tiene PAY, sobra el PLANT.", "brain/02 §2"),
    "S..": ("Etiqueta de fuente al final de una frase factual.",
            "Resuelve contra 03-source-log.csv. Toda afirmación de carga necesita ≥1 fuente Tier A/B. El fact-check (Stage 5) lo comprueba.", "brain/01, brain/14"),
}
SECTIONS = {
    "COLD OPEN": "Los primeros 20–40 s. Empieza DENTRO de la historia, sin intro de canal. Termina anunciando qué hará el vídeo. Es el momento de más cortes del episodio.",
    "BUMPER": "3–6 s en negro: wordmark 'Exodo' + 'Soy [nombre]'. El único momento de marca dentro del vídeo, y va DESPUÉS del hook, nunca antes.",
    "PIVOTE": "La frase bisagra que sale del hook hacia el trasfondo. Aquí suele ir el primer explicador. 10–20% del metraje.",
    "CONTEXTO": "El mundo en el que pasa la historia: época, institución, personas, lo que estaba en juego.",
    "NARRATIVA": "La espina dorsal, 55–70%. Cronológica. Personas: nacimiento → detalle que prefigura → ascenso → cima → giro/caída → desenlace.",
    "TEORÍAS": "Módulo opcional: solo si el caso está genuinamente en disputa. Cada posición se presenta, se pesa y se cierra con un veredicto honesto ('no hay pruebas concluyentes').",
    "CIERRE": "8–20%. Convierte 'una cosa que pasó' en 'una cosa sobre cómo funcionan las personas — o sobre qué significa'. Forma A/B/C × registro (psicológico / práctico / filosófico / religioso). Los registros filosófico y religioso van SIEMPRE atribuidos + [S..], como una idea, no como la verdad. Sin sermón.",
    "CTA": "Beat separado, DESPUÉS de que el cierre aterrice. CTA suave del canal. Sin pitch ni enlace de terceros.",
}
CUE_RE = re.compile(r"^\[([A-ZÑÁÉÍÓÚ][A-ZÑÁÉÍÓÚ .]*?)\]")


def section_key(title):
    t = title.upper()
    for k in SECTIONS:
        if k in t:
            return k
    if "ACTO" in t:
        return "NARRATIVA"
    return None


def parse(md):
    # header table
    header = {}
    for m in re.finditer(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", md, re.M):
        k = m.group(1).strip()
        if k and k.lower() not in ("campo", "valor") and set(k) != {"-"}:
            header[k] = re.sub(r"\*+", "", m.group(2)).strip()

    body = md.split("\n---\n", 1)[-1]
    beats, cur_sec, n = [], "—", 0
    blocks = re.split(r"(?=^#{2,3} )", body, flags=re.M)
    for blk in blocks:
        hm = re.match(r"^(#{2,3}) (.+)", blk)
        if hm:
            cur_sec = re.sub(r"\s*\(.*?\)\s*$", "", hm.group(2)).strip()
            rest = blk[hm.end():].strip()
        else:
            rest = blk.strip()
        if not rest:
            beats.append({"kind": "sec", "sec": cur_sec, "seckey": section_key(cur_sec)})
            continue
        beats.append({"kind": "sec", "sec": cur_sec, "seckey": section_key(cur_sec)})
        # split section body at cue markers
        parts = re.split(r"(?=^\[[A-ZÑÁÉÍÓÚ])", rest, flags=re.M)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            cm = CUE_RE.match(part)
            if cm:
                cue = cm.group(1).strip()
                text = part[cm.end():].lstrip("] ").strip()
            else:
                cue, text = "NARRACIÓN", part
            cue_norm = cue.strip() if cue.strip() in NOTES else (cue.split()[0] if cue else "NARRACIÓN")
            n += 1
            beats.append({
                "kind": "beat", "n": n, "sec": cur_sec, "cue": cue, "cue_norm": cue_norm,
                "text": text,
                "src": sorted(set(re.findall(r"\[S\d+\]", text))),
                "plant": "[PLANT]" in part or cue_norm == "PLANT",
                "pay": "[PAY]" in part or cue_norm == "PAY",
            })
    return header, beats


def build(slug, header, beats):
    e = _h.escape
    nbeats = sum(1 for b in beats if b["kind"] == "beat")

    hdr_rows = "".join(f"<tr><td>{e(k)}</td><td>{e(v)}</td></tr>" for k, v in header.items())

    leg = "".join(
        f'<tr><td><code>{e("[S..]" if k=="S.." else "["+k+"]")}</code></td>'
        f'<td>{e(d[0])}</td><td>{e(d[1])}</td><td><code>{e(d[2])}</code></td></tr>'
        for k, d in NOTES.items())
    secleg = "".join(f'<tr><td><b>{e(k.title())}</b></td><td>{e(v)}</td></tr>' for k, v in SECTIONS.items())

    cards = []
    for b in beats:
        if b["kind"] == "sec":
            note = SECTIONS.get(b["seckey"], "")
            cards.append(
                f'<h2 class="sech">{e(b["sec"])}</h2>'
                + (f'<p class="hint sechint">{e(note)}</p>' if note else ""))
            continue
        note = NOTES.get(b["cue_norm"])
        txt = e(b["text"])
        txt = re.sub(r"\[S\d+\]", lambda m: f'<span class="s">{m.group(0)}</span>', txt)
        txt = txt.replace("\n\n", "</p><p>").replace("\n", "<br>")
        badges = ""
        if b["plant"]:
            badges += '<span class="badge plant">PLANT</span>'
        if b["pay"]:
            badges += '<span class="badge pay">PAY</span>'
        for s in b["src"]:
            badges += f'<span class="badge s">{e(s)}</span>'
        expl = ""
        if note:
            expl = (f'<div class="expl" hidden><b>{e(b["cue_norm"])}</b> — {e(note[0])} '
                    f'<i>{e(note[1])}</i> <code>{e(note[2])}</code></div>')
        cards.append(
            f'<div class="card" data-kind="beat" data-k="{b["n"]}">'
            f'<div class="meta"><button class="cue" data-cue>{e(b["cue"] or "NARRACIÓN")}</button>'
            f'<span class="secname">{e(b["sec"])}</span> {badges}</div>'
            f'{expl}'
            f'<div class="txt"><p>{txt}</p></div>'
            '<div class="row">'
            f'<label class="ap"><input type="checkbox" class="ck" data-k="{b["n"]}"> aprobado</label></div>'
            f'<textarea class="nt" data-k="{b["n"]}" placeholder="qué editar en este beat (vacío = sin cambios)"></textarea>'
            '</div>')

    body = (
        '<section><h2>Cabecera</h2><table class="mini">' + hdr_rows + '</table></section>'
        '<section><details open><summary><b>Leyenda</b> — las notas técnicas del modelo narrativo (léela una vez)</summary>'
        '<table class="mini"><tr><th>Marca</th><th>Qué es</th><th>La regla</th><th>brain/</th></tr>'
        + leg + '</table>'
        '<table class="mini"><tr><th>Sección</th><th>Qué hace</th></tr>' + secleg + '</table>'
        '</details></section>'
        f'<section><h2>El guion — {nbeats} beats</h2>'
        '<p class="hint">Por beat: márcalo <b>aprobado</b>, o escribe qué editar. Pulsa la etiqueta '
        '(<code>[NARRACIÓN]</code>, <code>[EXPLICADOR]</code>…) para ver qué significa. '
        '«Exportar» → Claude aplica tus notas a <code>05-script.md</code>.</p>'
        + "\n".join(cards) + '</section>'
        '<section><h2>Nota global y firma</h2>'
        '<textarea id="global" placeholder="nota general (ritmo, arco, el cierre, lo que falta…)"></textarea>'
        '<div class="row" style="margin-top:.7rem">'
        '<input type="text" id="firma" placeholder="revisor (Usuario 001 o Usuario 002)">'
        '</div>'
        '<label class="ap" style="margin-top:.6rem"><input type="checkbox" id="ok"> '
        'Guion aprobado — pasa a fact-check (Stage 5)</label>'
        '</section>')

    header_ver = json.dumps(header.get("Versión", header.get("Version", "?")))
    script = f"""
const LS="exodo-scriptpass-{slug}";
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const cnt=$('.count');
const inp=$$('.ck,.nt');
function save(){{
  const c={{}}; inp.forEach(el=>c[(el.classList.contains('ck')?'ck:':'nt:')+el.dataset.k]=el.classList.contains('ck')?el.checked:el.value);
  c['#g']=$('#global').value; c['#f']=$('#firma').value; c['#ok']=$('#ok').checked;
  localStorage.setItem(LS,JSON.stringify(c));
}}
function sync(){{
  save();
  const tot={nbeats};
  const done=$$('.card[data-kind=beat]').filter(c=>c.querySelector('.ck').checked||c.querySelector('.nt').value.trim()).length;
  const fix=$$('.card[data-kind=beat]').filter(c=>c.querySelector('.nt').value.trim()).length;
  cnt.textContent=done+' / '+tot+' vistos · '+fix+' con nota';
}}
const init=JSON.parse(localStorage.getItem(LS)||'null');
if(init){{
  inp.forEach(el=>{{const v=init[(el.classList.contains('ck')?'ck:':'nt:')+el.dataset.k];
    if(v===undefined)return; if(el.classList.contains('ck'))el.checked=v; else el.value=v;}});
  $('#global').value=init['#g']||''; $('#firma').value=init['#f']||''; $('#ok').checked=!!init['#ok'];
}}
$$('input,textarea').forEach(el=>el.addEventListener('input',sync));
$$('[data-cue]').forEach(b=>b.addEventListener('click',()=>{{
  const x=b.closest('.card').querySelector('.expl'); if(x)x.hidden=!x.hidden;
}}));
sync();
$('#exp').onclick=()=>{{
  const L=['# {REVIEW_TXT} — 05-script.html','episodio\\t{slug}',
    'version\\t'+({header_ver}),
    'revisor\\t'+($('#firma').value.trim()||'(sin firmar)'),
    'aprobado\\t'+(($('#ok').checked&&$('#firma').value.trim())?'si':'NO'),
    '','---BEATS---'];
  $$('.card[data-kind=beat]').forEach(c=>{{
    const n=c.querySelector('.nt').value.replace(/\\s+/g,' ').trim();
    const ok=c.querySelector('.ck').checked;
    if(!n&&!ok)return;
    const cue=c.querySelector('.cue').textContent.trim();
    L.push([c.dataset.k,cue,(n?('FIX: '+n):'OK')].join('\\t'));
  }});
  const g=$('#global').value.trim();
  if(g)L.push('','---GLOBAL---',g);
  saveTxt('{REVIEW_TXT}', L.join('\\n')+'\\n',
    'Guardado en la carpeta del episodio. Pásaselo a Claude para aplicar las notas a 05-script.md.');
}};
$('#clr').onclick=()=>{{localStorage.removeItem(LS);location.reload()}};
"""
    hd = (f'<h1>Script pass · {e(slug)}</h1><span class="count"></span>'
          f'<button class="primary" id="exp">Exportar {REVIEW_TXT}</button>'
          '<button id="clr">Limpiar</button>')
    extra = ('<style>'
             'table.mini{width:100%;border-collapse:collapse;font-size:.8rem;margin:.3rem 0}'
             'table.mini th{text-align:left;color:var(--muted);font-weight:600}'
             'table.mini td,table.mini th{border-top:1px solid var(--line);padding:.35rem .5rem;vertical-align:top}'
             'h2.sech{margin:2rem 0 .2rem;font-size:.95rem;color:var(--gold);border:0}'
             'p.sechint{margin:.1rem 0 1rem}'
             '.card .meta{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;margin-bottom:.4rem}'
             '.cue{font:inherit;font-size:.7rem;letter-spacing:.04em;padding:.15rem .45rem;border-radius:5px;'
             'background:var(--surface-2);color:var(--gold);border:1px solid var(--line);cursor:help}'
             '.secname{font-size:.72rem;color:var(--muted)}'
             '.badge{font-size:.66rem;padding:.1rem .35rem;border-radius:4px;background:var(--surface-2);color:var(--muted)}'
             '.badge.plant{color:#c9a24a}.badge.pay{color:#7dbb6a}.badge.s{color:var(--muted)}'
             '.expl{font-size:.78rem;color:var(--muted);background:var(--surface-2);padding:.5rem .6rem;'
             'border-radius:7px;margin-bottom:.5rem;border-left:2px solid var(--gold)}'
             '.txt{font-size:.9rem;line-height:1.55;white-space:normal}.txt p{margin:.4rem 0}'
             '.txt .s{color:var(--gold);font-size:.72rem;vertical-align:super}'
             'label.ap{display:flex;gap:.4rem;align-items:center;font-size:.82rem;cursor:pointer}'
             'summary{cursor:pointer}'
             '</style>')
    return page(f"Script pass · {slug}", hd, body + extra, script)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: python tools/script_review.py E0XX-slug")
    slug = sys.argv[1].strip("/\\")
    ep = ROOT / "episodes" / slug
    f = ep / SCRIPT_F
    if not f.exists():
        sys.exit(f"no {f.relative_to(ROOT)}")
    header, beats = parse(f.read_text(encoding="utf-8"))
    (ep / REVIEW_HTML).write_text(build(slug, header, beats), encoding="utf-8")
    nb = sum(1 for b in beats if b["kind"] == "beat")
    print(f"escrito  episodes/{slug}/{REVIEW_HTML}  ({nb} beats)")
    print("siguiente: ábrelo, aprueba / comenta cada beat, «Exportar 05-script-pass.txt»")
