#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
script_review.py — Stage 4 review surface (the script pass).

Renders `05-script.md` as a clean two-column editor:

- **Main column** — only what gets *said*: NARRACIÓN, EXPLICADOR, and the
  PROMISE/PAY foreshadowing beats, flowing as plain prose you read and edit
  in place. No technical notes cluttering the read.
- **Sidebar** — one card per section, holding what doesn't get said: the
  section's **duration** (editable — e.g. trim the Bumper to 3 s) and its
  `[EN PANTALLA]` / `[NOTA]` / `[HOOK VISUAL]` production notes, each its
  own editable box. A section with neither is skipped — no empty cards.

Every beat still carries its stamp bar (cue pill → explainer on click,
PROMISE/PAY/source badges, a "revisado" toggle) exactly where it lives,
main column or sidebar.

"Finalizar Stage 4" walks both columns, re-sorts every beat back into its
original sequence (by section, then by its original position within the
section), and POSTs the reassembled `05-script.md` straight to the local
server, which writes it verbatim (the cabecera/table above the first `---`
is passed through untouched). The gate only firms once "aprobado" is
ticked with a reviewer name; until then the file still saves on every
"Finalizar" so no edit is ever lost waiting on a signature.

Reads  episodes/E0XX-slug/05-script.md
Writes episodes/E0XX-slug/05-script.html   (browser — gitignored)
       (reviewer exports)  05-script-pass.txt  (tracked audit note)
       -> server writes the edited body straight back into 05-script.md

Usage
  python tools/script_review.py E0XX-slug
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
    "PROMISE": ("Foreshadowing: se promete un detalle ('quiero que recuerdes esto') que se pagará más adelante.",
                "3–6 por episodio, TODOS pagados. En el montaje, el plano del PROMISE y el del PAY son el mismo.", "brain/02 §2, brain/11 §2.1"),
    "PAY": ("El pago de un PROMISE: '¿recuerdas lo que dije sobre X? Aquí es donde importa.'",
            "Si un PROMISE no tiene PAY, sobra el PROMISE.", "brain/02 §2"),
    "S..": ("Etiqueta de fuente al final de una frase factual.",
            "Resuelve contra 03-source-log.csv. Toda afirmación de carga necesita ≥1 fuente Tier A/B. El fact-check (Stage 5) lo comprueba.", "brain/01, brain/14"),
}
SECTIONS = {
    "COLD OPEN": "Los primeros 20–40 s. Empieza DENTRO de la historia, sin intro de canal. Termina anunciando qué hará el vídeo. Es el momento de más cortes del episodio.",
    "BUMPER": "3–6 s en negro: wordmark 'Conquest' + 'Soy [nombre]'. El único momento de marca dentro del vídeo, y va DESPUÉS del hook, nunca antes.",
    "PIVOTE": "La frase bisagra que sale del hook hacia el trasfondo. Aquí suele ir el primer explicador. 10–20% del metraje.",
    "CONTEXTO": "El mundo en el que pasa la historia: época, institución, personas, lo que estaba en juego.",
    "NARRATIVA": "La espina dorsal, 55–70%. Cronológica. Personas: nacimiento → detalle que prefigura → ascenso → cima → giro/caída → desenlace.",
    "TEORÍAS": "Módulo opcional: solo si el caso está genuinamente en disputa. Cada posición se presenta, se pesa y se cierra con un veredicto honesto ('no hay pruebas concluyentes').",
    "CIERRE": "8–20%. Convierte 'una cosa que pasó' en 'una cosa sobre cómo funcionan las personas — o sobre qué significa'. Forma A/B/C × registro (psicológico / práctico / filosófico / religioso). Los registros filosófico y religioso van SIEMPRE atribuidos + [S..], como una idea, no como la verdad. Sin sermón.",
    "CTA": "Beat separado, DESPUÉS de que el cierre aterrice. CTA suave del canal. Sin pitch ni enlace de terceros.",
}
# cues that never get spoken — production/technical notes, sidebar material.
# everything else (NARRACIÓN, EXPLICADOR, PROMISE, PAY, unrecognized cues)
# is something the narrator says, so it stays in the main reading column.
SIDEBAR_CUES = {"EN PANTALLA", "NOTA", "HOOK VISUAL"}
CUE_RE = re.compile(r"^\[([A-ZÑÁÉÍÓÚ][A-ZÑÁÉÍÓÚ .]*?)\]")
DUR_RE = re.compile(r"^(.*?)\s*\(([^()]*)\)\s*$")
CTA_RE = re.compile(r"Tipo de CTA:\s*(.+)", re.I)


def section_key(title):
    t = title.upper()
    for k in SECTIONS:
        if k in t:
            return k
    if "ACTO" in t:
        return "NARRATIVA"
    return None


def parse(md):
    # header table (kept only for display — the raw header block is
    # threaded through verbatim so we never have to reconstruct the table)
    header = {}
    for m in re.finditer(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", md, re.M):
        k = m.group(1).strip()
        if k and k.lower() not in ("campo", "valor") and set(k) != {"-"}:
            header[k] = re.sub(r"\*+", "", m.group(2)).strip()

    header_raw, sep, body = md.partition("\n---\n")
    if not sep:
        header_raw, body = "", md

    # Everything from the first heading that isn't a recognized script section
    # onward — source-log index, foreshadowing/explainer registers, self-review
    # checklist — is reference material, not the script. Split it off *before*
    # parsing beats, so it's never mis-treated as one and never rendered as
    # editable prose; it's carried through to output byte-for-byte.
    appendix_raw, seen_real_section = "", False
    for hm0 in re.finditer(r"^#{2,3} (.+)$", body, re.M):
        title0 = re.sub(r"\s*\(.*?\)\s*$", "", hm0.group(1)).strip()
        if section_key(title0) is None:
            if seen_real_section:  # never treat the whole doc as appendix —
                body, appendix_raw = body[:hm0.start()], body[hm0.start():].rstrip("\n")
                break
        else:
            seen_real_section = True

    nodes, cur_sec, cur_raw, cur_level, sec_idx, n = [], "—", None, 2, -1, 0
    blocks = re.split(r"(?=^#{2,3} )", body, flags=re.M)
    for blk in blocks:
        hm = re.match(r"^(#{2,3}) (.+)", blk)
        if hm:
            cur_raw = hm.group(0)
            cur_level = len(hm.group(1))
            cur_sec = re.sub(r"\s*\(.*?\)\s*$", "", hm.group(2)).strip()
            sec_idx += 1
            rest = blk[hm.end():].strip()
        else:
            rest = blk.strip()
            if cur_raw is None:
                # stray whitespace before the first heading (the header/body
                # split above always leaves some) — not a section, skip it
                # entirely rather than counting it as beat/section zero.
                continue
        dm = DUR_RE.match(cur_raw or "")
        base, dur = (dm.group(1), dm.group(2)) if dm else (cur_raw or "", "")
        nodes.append({"kind": "sec", "idx": sec_idx, "sec": cur_sec, "seckey": section_key(cur_sec),
                      "base": base, "dur": dur, "level": cur_level})
        if not rest:
            continue
        parts = re.split(r"(?=^\[[A-ZÑÁÉÍÓÚ])", rest, flags=re.M)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            cm = CUE_RE.match(part)
            if cm:
                cue, explicit = cm.group(1).strip(), True
                text = part[cm.end():].lstrip("] ").strip()
            else:
                cue, text, explicit = "NARRACIÓN", part, False
            # a lone "---" divider before the next heading has nothing to do
            # with this beat's text — it's swallowed in here because it isn't
            # a heading itself. Strip it so it never leaks into a textarea.
            text = re.sub(r"\n+-{3,}\s*$", "", text).rstrip()
            cue_norm = cue if cue in NOTES else (cue.split()[0] if cue else "NARRACIÓN")
            if cue_norm == "PLANT":  # legacy tag from before the promise/pay rename
                cue_norm = "PROMISE"
            n += 1
            nodes.append({
                "kind": "beat", "n": n, "sec_idx": sec_idx, "sec": cur_sec, "seckey": section_key(cur_sec),
                "cue": cue, "cue_norm": cue_norm, "explicit": explicit, "text": text,
                "side": cue_norm in SIDEBAR_CUES,
                "src": sorted(set(re.findall(r"\[S\d+\]", text))),
                "promise": "[PROMISE]" in part or "[PLANT]" in part or cue_norm in ("PROMISE", "PLANT"),
                "pay": "[PAY]" in part or cue_norm == "PAY",
            })
    return header, header_raw, nodes, appendix_raw


def _beat_html(b, e):
    note = NOTES.get(b["cue_norm"])
    badges = ""
    if b["promise"]:
        badges += '<span class="badge promise">PROMISE</span>'
    if b["pay"]:
        badges += '<span class="badge pay">PAY</span>'
    for s in b["src"]:
        badges += f'<span class="badge s">{e(s)}</span>'
    expl = ""
    if note:
        expl = (f'<div class="expl" hidden><b>{e(b["cue_norm"])}</b> — {e(note[0])} '
                f'<i>{e(note[1])}</i> <code>{e(note[2])}</code></div>')
    return (
        f'<div class="node beat" data-n="{b["n"]}" data-sec="{b["sec_idx"]}" data-cue="{e(b["cue"])}" '
        f'data-explicit="{1 if b["explicit"] else 0}">'
        '<div class="stampbar">'
        f'<button type="button" class="pill cue" data-cue-btn>{e(b["cue"] or "NARRACIÓN")}</button>'
        f'{badges}'
        '<span class="spacer"></span>'
        f'<button type="button" class="pill rev" data-rev data-k="{b["n"]}">revisado</button>'
        '</div>'
        f'{expl}'
        f'<textarea class="beattxt" data-k="{b["n"]}" rows="1" spellcheck="false">{e(b["text"])}</textarea>'
        '</div>')


def build(slug, header, header_raw, nodes, appendix_raw=""):
    e = _h.escape
    real_beats = [b for b in nodes if b["kind"] == "beat"]
    nbeats = len(real_beats)
    n_promise = sum(1 for b in real_beats if b["promise"])
    n_pay = sum(1 for b in real_beats if b["pay"])
    # a pay beat can resolve more than one promise at once, so pay < promise is
    # normal — only flag the case that can never be right (a pay with nothing
    # promised, or promises but zero pays at all).
    pp_bad = n_pay > n_promise or (n_promise > 0 and n_pay == 0)
    pp_note = f"{n_promise} promise · {n_pay} pay" + (" ⚠ revisa — no debería pasar" if pp_bad else "")

    # each `[NOTA] Tipo de CTA: …` anywhere in the script is one CTA moment;
    # brain/02 §4 caps an episode at two "audience" asks (closing always,
    # mid-episode optional) — a product/sponsor plug (§4c) takes the mid slot
    # instead of adding a third, and never counts against the type-variety check.
    cta_tags = []
    for b in real_beats:
        if b["cue_norm"] != "NOTA":
            continue
        m = CTA_RE.match(b["text"])
        if m:
            t = m.group(1).strip()
            cta_tags.append((t, b["seckey"] == "CTA", bool(re.match(r"(?i)producto|patrocinio", t))))
    audience = [(t, closing) for t, closing, prod in cta_tags if not prod]
    product = [t for t, closing, prod in cta_tags if prod]
    cta_bad = len(audience) > 2 or (len(audience) == 2 and audience[0][0].lower() == audience[1][0].lower())
    cta_parts = [f"{t} ({'cierre' if closing else 'mid-episodio'})" for t, closing in audience]
    cta_parts += [f"{t} (patrocinio/producto)" for t in product]
    cta_note = (" + ".join(cta_parts) if cta_parts else
                "⚠ sin tag — añade [NOTA] Tipo de CTA: … en el closing ask")
    if cta_bad:
        cta_note += " ⚠ revisa brain/02 §4 — máx. 2, sin repetir tipo"

    hdr_rows = "".join(f"<tr><td>{e(k)}</td><td>{e(v)}</td></tr>" for k, v in header.items())
    hdr_rows += (f'<tr><td>Promise / Pay</td>'
                 f'<td class="{"warn" if pp_bad else ""}">{e(pp_note)}</td></tr>')
    hdr_rows += (f'<tr><td>Tipo de CTA</td>'
                 f'<td class="{"warn" if (cta_bad or not cta_parts) else ""}">{e(cta_note)}</td></tr>')

    leg = "".join(
        f'<tr><td><code>{e("[S..]" if k=="S.." else "["+k+"]")}</code></td>'
        f'<td>{e(d[0])}</td><td>{e(d[1])}</td><td><code>{e(d[2])}</code></td></tr>'
        for k, d in NOTES.items())
    secleg = "".join(f'<tr><td><b>{e(k.title())}</b></td><td>{e(v)}</td></tr>' for k, v in SECTIONS.items())

    orig = {}       # n -> original text, for the "edited" diff in the audit export
    main_parts = []
    side_by_sec = {}   # sec_idx -> [beat html, ...]
    sec_meta = []      # [{idx, sec, base, dur}] in order, for the sidebar cards

    for b in nodes:
        if b["kind"] == "sec":
            sec_meta.append({"idx": b["idx"], "sec": b["sec"], "base": b["base"], "dur": b["dur"]})
            note = SECTIONS.get(b["seckey"], "")
            main_parts.append(
                f'<div class="node sech" data-sec="{b["idx"]}" data-level="{b["level"]}" '
                f'data-base="{e(b["base"])}" data-dur="{e(b["dur"])}">'
                f'<h2 class="sech">{e(b["sec"])}</h2>'
                + (f'<p class="hint sechint">{e(note)}</p>' if note else "")
                + '</div>')
            continue
        orig[b["n"]] = b["text"]
        if b["side"]:
            side_by_sec.setdefault(b["sec_idx"], []).append(_beat_html(b, e))
        else:
            main_parts.append(_beat_html(b, e))

    side_cards = []
    for sm in sec_meta:
        beats = side_by_sec.get(sm["idx"], [])
        if not sm["dur"] and not beats:
            continue    # nothing to show for this section — skip the card
        sec_idx, sec_dur = sm["idx"], sm["dur"]
        dur_field = (
            '<div class="durfield"><label>Duración</label>'
            f'<input type="text" class="dur" data-sec-dur="{sec_idx}" value="{e(sec_dur)}" '
            'placeholder="p. ej. 0:38–0:43"></div>')
        side_cards.append(
            f'<div class="sidecard" data-sidecard="{sm["idx"]}">'
            f'<h3>{e(sm["sec"])}</h3>'
            f'{dur_field}'
            + "".join(beats) +
            '</div>')

    body = (
        '<section><h2>Cabecera</h2><table class="mini">' + hdr_rows + '</table></section>'
        '<section><details><summary><b>Leyenda</b> — las notas técnicas del modelo narrativo (léela una vez)</summary>'
        '<table class="mini"><tr><th>Marca</th><th>Qué es</th><th>La regla</th><th>brain/</th></tr>'
        + leg + '</table>'
        '<table class="mini"><tr><th>Sección</th><th>Qué hace</th></tr>' + secleg + '</table>'
        '</details></section>'
        f'<section><h2>El guion — {nbeats} beats</h2>'
        '<p class="hint">La columna principal es solo lo que se dice — narración, explicadores, promise/pay. '
        'A la derecha, por sección: su duración (editable) y sus notas de producción '
        '(<code>[EN PANTALLA]</code>, <code>[NOTA]</code>, <code>[HOOK VISUAL]</code>) — también editables ahí. '
        'Pulsa una etiqueta para ver qué significa. '
        '<b>«Finalizar Stage 4»</b> guarda el guion tal cual está en el editor; el gate solo pasa a '
        'Stage 5 cuando esté aprobado y firmado.</p>'
        '<div class="layout">'
        f'<div id="editor">{"".join(main_parts)}</div>'
        f'<aside id="sidebar">{"".join(side_cards)}</aside>'
        '</div>'
        '</section>'
        + (('<section><details id="appendix"><summary><b>Material de referencia</b> — '
            'índice de fuentes, registros de foreshadowing/explicadores, autorrevisión… '
            'no es guion, no se narra, de solo lectura aquí (edítalo en el .md si hace falta)</summary>'
            f'<pre>{e(appendix_raw)}</pre></details></section>') if appendix_raw else "")
        + '<section><h2>Nota global y firma</h2>'
        '<textarea id="global" placeholder="nota general (ritmo, arco, el cierre, lo que falta…)"></textarea>'
        '<div class="row" style="margin-top:.7rem">'
        '<input type="text" id="firma" placeholder="revisor (Usuario 001 o Usuario 002)">'
        '</div>'
        '<label class="ap" style="margin-top:.6rem"><input type="checkbox" id="ok"> '
        'Guion aprobado — pasa a fact-check (Stage 5)</label>'
        '</section>')

    header_ver = json.dumps(header.get("Versión", header.get("Version", "?")))
    # Fingerprint of *this* parse's shape — beat numbers and section indices are
    # just positional counters, so if the underlying 05-script.md is edited
    # outside the browser (a beat inserted/removed/reordered) between visits,
    # those numbers get reused for different content. Saved edits keyed by
    # them would then land on the wrong beat on restore. Comparing this
    # fingerprint against the one stored alongside old localStorage state is
    # what lets us tell "same document, safe to restore" from "reshaped
    # document, discard the stale state" instead of silently corrupting the
    # reconstruction on the next Finalizar.
    fp_src = json.dumps([header_raw, appendix_raw, orig,
                         [(m["idx"], m["dur"]) for m in sec_meta]], sort_keys=True, ensure_ascii=False)
    fp = hashlib.sha1(fp_src.encode("utf-8")).hexdigest()[:12]
    script = f"""
const EPID={slug[:4]!r}; const STAGE=4;
const LS="conquest-scriptpass-{slug}";
const FP={json.dumps(fp)};
const HEADER_RAW={json.dumps(header_raw)};
const APPENDIX_RAW={json.dumps(appendix_raw)};
const ORIG={json.dumps(orig)};
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const cnt=$('.count');
const boxes=$$('.beattxt');
function autosize(el){{el.style.height='auto';el.style.height=(el.scrollHeight+2)+'px';}}
boxes.forEach(autosize);
function save(){{
  const c={{fp:FP,edit:{{}},rev:{{}},dur:{{}}}};
  boxes.forEach(el=>c.edit[el.dataset.k]=el.value);
  $$('.pill.rev').forEach(el=>c.rev[el.dataset.k]=el.classList.contains('on'));
  $$('.dur').forEach(el=>c.dur[el.dataset.secDur]=el.value);
  c.g=$('#global').value; c.f=$('#firma').value; c.ok=$('#ok').checked;
  localStorage.setItem(LS,JSON.stringify(c));
}}
function sync(){{
  save();
  const tot={nbeats};
  const rev=$$('.pill.rev.on').length;
  const edited=boxes.filter(el=>el.value.trim()!==(ORIG[el.dataset.k]||'').trim()).length;
  cnt.textContent=rev+' / '+tot+' revisados · '+edited+' editados';
}}
let init=JSON.parse(localStorage.getItem(LS)||'null');
if(init&&init.fp!==FP){{
  // 05-script.md changed shape since this was saved (a beat moved/added/removed
  // outside the browser) — beat numbers now point at different content, so
  // applying this saved state would silently scramble the reconstruction.
  // Discard it rather than guess.
  localStorage.removeItem(LS);
  init=null;
  alert('El guion cambió desde tu última sesión en esta página (se reordenaron o añadieron beats) — se descartó el progreso guardado en este navegador para no mezclar texto de un beat con otro. El .md en disco no se tocó.');
}}
if(init){{
  boxes.forEach(el=>{{const v=init.edit&&init.edit[el.dataset.k]; if(v!==undefined){{el.value=v;autosize(el);}}}});
  $$('.pill.rev').forEach(el=>{{if(init.rev&&init.rev[el.dataset.k])el.classList.add('on');}});
  $$('.dur').forEach(el=>{{const v=init.dur&&init.dur[el.dataset.secDur]; if(v!==undefined)el.value=v;}});
  $('#global').value=init.g||''; $('#firma').value=init.f||''; $('#ok').checked=!!init.ok;
}}
boxes.forEach(el=>el.addEventListener('input',()=>{{autosize(el);sync();}}));
$$('.dur').forEach(el=>el.addEventListener('input',sync));
$('#global').addEventListener('input',sync);
$('#firma').addEventListener('input',sync);
$('#ok').addEventListener('change',sync);
$$('.pill.rev').forEach(b=>b.addEventListener('click',()=>{{b.classList.toggle('on');sync();}}));
$$('[data-cue-btn]').forEach(b=>b.addEventListener('click',()=>{{
  const x=b.closest('.node').querySelector('.expl'); if(x)x.hidden=!x.hidden;
}}));
// clicking a section heading jumps the sidebar to its card, and back
$$('.node.sech').forEach(h=>h.addEventListener('click',()=>{{
  const c=$('.sidecard[data-sidecard="'+h.dataset.sec+'"]'); if(c)c.scrollIntoView({{behavior:'smooth',block:'start'}});
}}));
$$('.sidecard').forEach(c=>c.querySelector('h3').addEventListener('click',()=>{{
  const h=$('.node.sech[data-sec="'+c.dataset.sidecard+'"]'); if(h)h.scrollIntoView({{behavior:'smooth',block:'start'}});
}}));
sync();
$('#exp').onclick=()=>{{
  const firma=$('#firma').value.trim(), ok=$('#ok').checked;
  if(ok&&!firma){{alert('Falta el nombre del revisor para poder firmar el gate (el guion se guarda igual).');}}
  const secs=$$('.node.sech').map(h=>({{
    idx:h.dataset.sec, base:h.dataset.base, level:+h.dataset.level,
    dur:(($('.dur[data-sec-dur="'+h.dataset.sec+'"]')||{{}}).value ?? h.dataset.dur),
  }}));
  // a "---" divider sat before every top-level (##) section in the source;
  // ### sub-sections (the Acto beats inside Narrativa) never had one. Put
  // them back so the reconstructed .md reads the same as it did on disk.
  let body='';
  secs.forEach((s,i)=>{{
    const raw=s.base+(s.dur.trim()?(' ('+s.dur.trim()+')'):'');
    const beats=$$('.node.beat[data-sec="'+s.idx+'"]')
      .sort((a,b)=>(+a.dataset.n)-(+b.dataset.n))
      .map(node=>{{
        const explicit=node.dataset.explicit==='1', cue=node.dataset.cue;
        const txt=node.querySelector('.beattxt').value.replace(/\\s+$/,'').replace(/^\\s+/,'');
        return explicit?('['+cue+'] '+txt):txt;
      }});
    if(i>0) body+=(s.level===2?'\\n\\n---\\n\\n':'\\n\\n');
    body+=[raw,...beats].join('\\n\\n');
  }});
  const scriptMd=HEADER_RAW+'\\n---\\n'+body+(APPENDIX_RAW?('\\n\\n---\\n\\n'+APPENDIX_RAW):'')+'\\n';
  const L=['# {REVIEW_TXT} — 05-script.html','episodio\\t{slug}',
    'version\\t'+({header_ver}),
    'revisor\\t'+(firma||'(sin firmar)'),
    'aprobado\\t'+((ok&&firma)?'si':'NO'),
    '','---BEATS---'];
  $$('.node.beat').forEach(node=>{{
    const k=node.dataset.n, cue=node.dataset.cue;
    const txt=node.querySelector('.beattxt').value.trim();
    const edited=txt!==(ORIG[k]||'').trim();
    const rev=node.querySelector('.pill.rev').classList.contains('on');
    if(!edited&&!rev)return;
    L.push([k,cue,(edited?'EDITADO':'')+(edited&&rev?' · ':'')+(rev?'revisado':'')].join('\\t'));
  }});
  $$('.dur').forEach(el=>{{
    const h=$('.node.sech[data-sec="'+el.dataset.secDur+'"]');
    if(h&&el.value.trim()!==(h.dataset.dur||'').trim())
      L.push(['sec:'+el.dataset.secDur,'duración',(h.dataset.dur||'—')+' → '+el.value.trim()].join('\\t'));
  }});
  const g=$('#global').value.trim();
  if(g)L.push('','---GLOBAL---',g);
  finishStage('{REVIEW_TXT}', L.join('\\n')+'\\n', EPID, STAGE,
    'Guion guardado en 05-script.md. El gate a Stage 5 solo se firma con «aprobado» + revisor.',
    {{script_md:scriptMd, ok:ok, firma:firma}});
}};
$('#clr').onclick=()=>{{localStorage.removeItem(LS);location.reload()}};
"""
    hd = (f'<h1>Script pass · {e(slug)}</h1><span class="count"></span>'
          f'<button class="primary" id="exp">Finalizar Stage 4</button>'
          '<button id="clr">Limpiar</button>'
          '<a class="btn ghost spacer" href="http://localhost:8765/">Volver al panel</a>')
    extra = ('<style>'
             'table.mini{width:100%;border-collapse:collapse;font-size:.8rem;margin:.3rem 0}'
             'table.mini th{text-align:left;color:var(--muted);font-weight:600}'
             'table.mini td,table.mini th{border-top:1px solid var(--line);padding:.35rem .5rem;vertical-align:top}'
             'table.mini td.warn{color:var(--gold);font-weight:600}'
             '.layout{display:grid;grid-template-columns:1fr 19rem;gap:1.75rem;align-items:start}'
             '@media (max-width:900px){.layout{grid-template-columns:1fr}}'
             '#editor{min-width:0}'
             '.node{margin:0 0 .15rem}'
             '.node.sech{margin:2rem 0 .2rem;cursor:pointer}'
             'h2.sech{margin:0;font-size:.95rem;color:var(--gold);border:0}'
             'p.sechint{margin:.1rem 0 1rem}'
             '.node.beat{padding:.55rem .2rem;border-radius:8px;transition:background .15s}'
             '.node.beat:focus-within{background:var(--surface-2)}'
             '.stampbar{display:flex;gap:.4rem;align-items:center;flex-wrap:wrap;margin-bottom:.3rem}'
             '.pill{font:inherit;font-size:.68rem;letter-spacing:.03em;padding:.15rem .5rem;border-radius:999px;'
             'background:var(--surface-2);color:var(--muted);border:1px solid var(--line);cursor:pointer}'
             '.pill.cue{color:var(--gold);cursor:help}'
             '.pill.rev{margin-left:auto}'
             '.pill.rev.on{color:var(--lime,#7dbb6a);border-color:var(--lime,#7dbb6a)}'
             '.stampbar .spacer{flex:1}'
             '.badge{font-size:.64rem;padding:.1rem .35rem;border-radius:4px;background:var(--surface-2);color:var(--muted)}'
             '.badge.promise{color:#c9a24a}.badge.pay{color:#7dbb6a}.badge.s{color:var(--muted)}'
             '.expl{font-size:.78rem;color:var(--muted);background:var(--surface-2);padding:.5rem .6rem;'
             'border-radius:7px;margin-bottom:.4rem;border-left:2px solid var(--gold)}'
             '.beattxt{display:block;width:100%;border:0;background:transparent;color:inherit;font:inherit;'
             'font-size:.9rem;line-height:1.55;resize:none;overflow:hidden;padding:.1rem .2rem;outline:none}'
             '.beattxt:focus{outline:1px dashed var(--gold-line)}'
             'label.ap{display:flex;gap:.4rem;align-items:center;font-size:.82rem;cursor:pointer}'
             'summary{cursor:pointer}'
             '#sidebar{position:sticky;top:1rem;display:flex;flex-direction:column;gap:1rem;'
             'max-height:calc(100vh - 2rem);overflow:auto}'
             '.sidecard{border:1px solid var(--line);border-radius:10px;padding:.7rem .8rem;background:var(--surface)}'
             '.sidecard h3{margin:0 0 .5rem;font-size:.78rem;color:var(--gold);cursor:pointer;font-weight:600}'
             '.durfield{display:flex;align-items:center;gap:.5rem;margin-bottom:.5rem}'
             '.durfield label{font-size:.68rem;color:var(--muted);flex:none}'
             '.durfield input{flex:1;font-size:.78rem;padding:.25rem .45rem;border-radius:6px;'
             'border:1px solid var(--line);background:var(--surface-2);color:inherit}'
             '.sidecard .node.beat{padding:.4rem 0;border-top:1px solid var(--line);border-radius:0}'
             '.sidecard .node.beat:first-of-type{border-top:0}'
             '.sidecard .beattxt{font-size:.8rem}'
             '#appendix{background:var(--surface-2);border:1px dashed var(--line-2);border-radius:10px;'
             'padding:.9rem 1.1rem;margin-top:.5rem}'
             '#appendix summary{color:var(--muted);font-size:.85rem}'
             '#appendix summary b{color:var(--fg)}'
             '#appendix pre{margin:.8rem 0 0;color:var(--muted);font-size:.74rem;font-family:var(--mono);'
             'white-space:pre-wrap;word-break:break-word;max-height:28rem;overflow:auto}'
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
    header, header_raw, nodes, appendix_raw = parse(f.read_text(encoding="utf-8"))
    (ep / REVIEW_HTML).write_text(build(slug, header, header_raw, nodes, appendix_raw), encoding="utf-8")
    nb = sum(1 for b in nodes if b["kind"] == "beat")
    print(f"escrito  episodes/{slug}/{REVIEW_HTML}  ({nb} beats)")
    print("siguiente: ábrelo, edita directamente cada beat, «Finalizar Stage 4»")
