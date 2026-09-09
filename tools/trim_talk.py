#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trim_talk.py — trim silences + fillers + retakes from a recorded take (Stage 9, brain/16 move 1).

**Two phases** — the transcription drives every cut, so you review it before the cut is baked:

  1. review  ·  python tools/trim_talk.py TAKE.mp4 --script 05-script.md
       faster-whisper transcribes with word timestamps, then PROPOSES cuts:
         - the lead-in and tail-out silence
         - inter-word pauses longer than --gap (asymmetric pad: more room after
           a word than before the next, because whisper word-ends run short)
         - standalone Spanish fillers (unless --no-fillers)
         - retakes / false starts (unless --no-retakes): a run of >= 4 words
           re-said within --retake-window s — the earlier attempt is cut
       Writes  <take>.words.raw.json  <take>.cuts.json (the proposal, then whatever
               the trim room autosaves)  <take>.cuts.md  <take>.review.m4a
               <take>.peaks.json (waveform)  <take>.review.html  ← the TRIM ROOM:
                 the take as a waveform, every cut a red block — drag to move,
                 drag edges to resize, ✕ to delete, «✂ corte aquí» or drag on
                 empty wave to add one. Autosaves to serve.py /trim-save (and on
                 unload). «Aplicar corte» → serve.py /trim → phase 2.
       Renders nothing.

  2. apply   ·  python tools/trim_talk.py TAKE.mp4 --apply
       reads <take>.words.raw.json + <take>.cuts.json and writes
         <take>.words.json    surviving words on the trimmed timeline (assemble.py reads this)
         <take>.trimmed.mp4   the cut take (H.264 / AAC), 10 ms fade at each join

  --apply-now      both phases with the auto proposal, no review (advance.py / CI).
  --rebuild-page   regenerate the trim room from an existing transcription (no
                   whisper). Keeps any autosaved edits; --reset-cuts discards them.

A gap under 0.45 s is never cut. --keep MM:SS protects a span in phase 1.
With --script, the trim room lists script lines no surviving span covers.
"""
import re
import subprocess
import sys
import tempfile
from difflib import SequenceMatcher
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mediabin import FFMPEG  # noqa: E402

MIN_GAP = 0.45           # never cut a pause shorter than this, whatever --gap says
FADE = 0.010             # audio fade at each join, seconds
PAD_IN = 0.10            # room kept *before* the next word starts
PAD_OUT = 0.26           # room kept *after* a word ends — whisper word-end runs
#                          short, so a symmetric pad clips the tail of the word.
#                          The waveform review page is the real control; this is
#                          just a sane default the user then nudges.
HEAD_KEEP = 0.25         # breath before the very first word
TAIL_KEEP = 0.40         # tail after the last word
FILLERS = {
    "eh", "ehh", "ehm", "em", "mmm", "este", "esto", "osea", "o", "sea",
    "bueno", "pues", "digamos", "entonces", "verdad", "no", "vale", "ya",
    "tipo", "como", "que", "asi",
}
# only these are cut when they stand alone between pauses; multi-word fillers:
FILLER_PHRASES = [("o", "sea"), ("es", "decir"), ("por", "asi", "decirlo")]


def secs(mmss):
    p = [float(x) for x in str(mmss).split(":")]
    return p[0] * 60 + p[1] if len(p) == 2 else p[0]


def norm(w):
    return w.strip().strip(".,;:¿?¡!—-…\"'()").lower()


def transcribe(take, model_name, lang):
    from faster_whisper import WhisperModel
    try:
        import torch
        dev = "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        dev = "cpu"
    ct = "float16" if dev == "cuda" else "int8"
    print(f"whisper: {model_name} en {dev} ({ct}) …")
    model = WhisperModel(model_name, device=dev, compute_type=ct)
    segs, _ = model.transcribe(str(take), language=lang, word_timestamps=True,
                               vad_filter=True, vad_parameters={"min_silence_duration_ms": 400})
    words = []
    for s in segs:
        for w in (s.words or []):
            words.append((w.start, w.end, w.word))
    return words


def plan_cuts(words, gap, pad, do_fillers, keeps, total=None):
    """Return cuts = [(start, end, reason)]. Cuts the lead-in and tail-out
    silence, and every inter-word pause longer than `gap`, keeping an
    asymmetric pad (more room after a word than before the next)."""
    cuts = []
    first_s, last_e = words[0][0], words[-1][1]
    # lead-in silence (this is the one that kept surviving)
    if first_s > HEAD_KEEP + 0.15:
        cuts.append((0.0, first_s - HEAD_KEEP, f"silencio inicial {first_s:.1f}s"))
    # tail-out silence
    if total and total - last_e > TAIL_KEEP + 0.15:
        cuts.append((last_e + TAIL_KEEP, total, f"silencio final {total - last_e:.1f}s"))
    # silence between consecutive words
    for (s0, e0, _), (s1, e1, _) in zip(words, words[1:]):
        hole = s1 - e0
        if hole > max(gap, MIN_GAP):
            cut_s, cut_e = e0 + PAD_OUT, s1 - PAD_IN
            if cut_e - cut_s > 0.06:
                cuts.append((cut_s, cut_e, f"silencio {hole:.1f}s"))
    # standalone fillers (word surrounded by pauses on both sides)
    if do_fillers:
        for i, (s, e, w) in enumerate(words):
            n = norm(w)
            if n not in FILLERS:
                continue
            before = s - words[i - 1][1] if i else 99
            after = words[i + 1][0] - e if i + 1 < len(words) else 99
            if before > 0.25 and after > 0.20:
                cuts.append((s - PAD_IN, e + PAD_IN, f"filler «{n}»"))
    # honour --keep: drop any cut within 2 s of a protected timestamp
    if keeps:
        cuts = [c for c in cuts if not any(abs(c[0] - k) < 2 or abs(c[1] - k) < 2 or c[0] <= k <= c[1]
                                           for k in keeps)]
    cuts.sort()
    # merge overlaps
    merged = []
    for c in cuts:
        if merged and c[0] <= merged[-1][1] + 0.05:
            merged[-1] = (merged[-1][0], max(merged[-1][1], c[1]), merged[-1][2] + " + " + c[2])
        else:
            merged.append(list(c))
    return [tuple(c) for c in merged]


def plan_retakes(words, pad, window, min_run=4, sim=0.74):
    """Immediate retakes / false starts. If words[i:i+run] is re-said near-verbatim
    starting within `window` s of its end, cut [start of the first attempt →
    start of the retake] (drops the abandoned take + any fumble between).
    Returns [(start, end, reason)]. Conservative: needs a run of >= min_run words
    at >= sim similarity, and the retake must begin soon after (a real callback
    minutes later never matches)."""
    n = len(words)
    toks = [norm(w) for _, _, w in words]
    cuts, covered, i = [], [False] * n, 0
    while i < n - min_run:
        if covered[i]:
            i += 1
            continue
        hit = None
        for run in range(min(35, n - i), min_run - 1, -1):
            a = toks[i:i + run]
            a_end = words[i + run - 1][1]
            j = i + run
            while j + min_run <= n and words[j][0] - a_end < window:
                b = toks[j:j + run]
                if SequenceMatcher(None, a, b).ratio() >= sim:
                    hit = (i, j, run, SequenceMatcher(None, a, b).ratio())
                    break
                j += 1
            if hit:
                break
        if hit:
            s_i, s_j, run, r = hit
            cs = max(0.0, words[s_i][0] - pad)
            ce = words[s_j][0] - pad
            if ce - cs > 0.05:
                cuts.append((cs, ce, f"retoma ({run}p, {r:.0%})"))
            for k in range(s_i, s_j):
                covered[k] = True
            i = s_j
        else:
            i += 1
    return cuts


def _spoken_script(md):
    """Ordered spoken sentences from 05-script.md — NARRACIÓN/EXPLICADOR/PROMISE/PAY
    text only. Drops cue markers, ‹stage directions›, [EN PANTALLA]/[NOTA]/[HOOK VISUAL]
    blocks, tables, headings, the appendix."""
    _, _, body = md.partition("\n---\n")
    body = body.split("\n## Índice de tags")[0]
    out = []
    for blk in re.split(r"(?=^\[[A-ZÑÁÉÍÓÚ])", body, flags=re.M):
        m = re.match(r"^\[([A-ZÑÁÉÍÓÚ][A-ZÑÁÉÍÓÚ ]*)\]", blk)
        cue = m.group(1).strip() if m else "NARRACIÓN"
        if cue not in ("NARRACIÓN", "EXPLICADOR", "PROMISE", "PAY"):
            continue
        txt = blk[m.end():] if m else blk
        txt = re.sub(r"‹[^›]*›", " ", txt)                 # stage directions
        txt = re.sub(r"`[^`]*`|\*+|\[S\d+\]|\|.*", " ", txt)
        for sent in re.split(r"(?<=[.?!])\s+|\n{2,}", txt):
            ws = [norm(w) for w in sent.split() if norm(w)]
            if len(ws) >= 4:
                out.append(ws)
    return out


def check_script(words, spans, script_sents, sim=0.62):
    """After cuts: which script sentences does no surviving span cover well?"""
    surv = [norm(w) for (s, _e, w) in words if remap(s, spans) is not None]
    missing = []
    for ws in script_sents:
        L = len(ws)
        best = 0.0
        for k in range(0, max(1, len(surv) - L + 1), 2):
            best = max(best, SequenceMatcher(None, ws, surv[k:k + L]).ratio())
            if best >= sim:
                break
        if best < sim:
            missing.append((" ".join(ws)[:90], best))
    return missing


def keep_spans(cuts, total):
    spans, t = [], 0.0
    for cs, ce, _ in cuts:
        if cs > t:
            spans.append((t, cs))
        t = ce
    if t < total:
        spans.append((t, total))
    return spans


def write_cuts_md(take, words, cuts, spans, total, missing=None):
    n_ret = sum(1 for _, _, r in cuts if "retoma" in r)
    out = [f"# Cortes — {take.name}", "",
           f"- cortes: **{len(cuts)}** ({n_ret} retomas)  ·  quitado: **{sum(e - s for s, e, _ in cuts):.1f} s**  "
           f"·  duración final: **{sum(e - s for s, e in spans):.1f} s** (de {total:.1f} s)",
           "- veta un corte malo:  `--keep MM:SS`  (protege ±2 s)  y re-corre", "",
           "---", ""]
    cut_at = {round(s, 2): (e, r) for s, e, r in cuts}
    line, last_e = [], 0.0
    for s, e, w in words:
        for cs in list(cut_at):
            if last_e <= cs <= s + 0.01:
                ce, r = cut_at.pop(cs)
                line.append(f"\n\n> ✂ **{int(cs // 60):02d}:{cs % 60:05.2f} → {int(ce // 60):02d}:{ce % 60:05.2f}**  ({r})\n\n")
        line.append(w)
        last_e = e
    out.append("".join(line).strip())
    if missing:
        out += ["", "---", "",
                f"## ⚠ Líneas del guion sin cobertura clara ({len(missing)})",
                "Ninguna toma superviviente casa bien con estas frases — se cortaron enteras, "
                "se dijeron mal siempre, o whisper las transcribió raro. Revísalas: `--keep MM:SS` "
                "para recuperar una toma, o vuelve a grabar el pickup.", ""]
        out += [f"- ({sc:.0%}) {txt}…" for txt, sc in missing]
    take.with_suffix(".cuts.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"  escrito  {take.with_suffix('.cuts.md').name}")


def remap(t, spans):
    """Original-timeline second -> trimmed-timeline second, or None if it fell in a cut."""
    acc = 0.0
    for s0, s1 in spans:
        if t < s0:
            return None
        if t <= s1:
            return acc + (t - s0)
        acc += s1 - s0
    return acc


def write_words_json(take, words, spans):
    import json
    out = []
    for s, _e, w in words:
        ts = remap(s, spans)
        if ts is not None:
            out.append({"w": w.strip(), "t": round(ts, 3)})
    take.with_suffix(".words.json").write_text(
        json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"  escrito  {take.with_suffix('.words.json').name}  ({len(out)} palabras)")


def render(take, spans, out_path):
    parts, maps = [], []
    for i, (s, e) in enumerate(spans):
        d = e - s
        fo = max(0.0, d - FADE)
        parts.append(
            f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{i}];"
            f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={FADE},afade=t=out:st={fo:.3f}:d={FADE}[a{i}]")
        maps.append(f"[v{i}][a{i}]")
    script = ";\n".join(parts) + ";\n" + "".join(maps) + f"concat=n={len(spans)}:v=1:a=1[v][a]"
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(script)
        sp = f.name
    # intermediate file — favour speed; the Stage-9 export re-encodes anyway
    cmd = [FFMPEG, "-y", "-i", str(take), "-filter_complex_script", sp,
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16",
           "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k",
           str(out_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    Path(sp).unlink(missing_ok=True)
    if r.returncode != 0 or not out_path.exists():
        print("  FALLO ffmpeg:\n" + "\n".join(r.stderr.strip().splitlines()[-4:]))
        return False
    print(f"  escrito  {out_path.name}")
    return True


def _merge(cuts):
    """sorted [(s,e,reason)] -> non-overlapping."""
    out = []
    for c in sorted(cuts):
        if out and c[0] <= out[-1][1] + 0.05:
            out[-1] = (out[-1][0], max(out[-1][1], c[1]), out[-1][2] + " + " + c[2])
        else:
            out.append(tuple(c))
    return out


def audio_proxy(take):
    """A small AAC proxy of the take for the review page to scrub (the take
    itself can be >1 GB). <take>.review.m4a — skipped if newer than the take."""
    out = take.with_suffix(".review.m4a")
    if out.exists() and out.stat().st_mtime >= take.stat().st_mtime:
        return out
    r = subprocess.run([FFMPEG, "-y", "-i", str(take), "-vn", "-ac", "1",
                        "-c:a", "aac", "-b:a", "96k", str(out)], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  escrito  {out.name}")
    return out


def write_peaks(take, total, n=3000):
    """<take>.peaks.json — [total, [p0,p1,…]] where each p is 0-100 RMS-ish
    amplitude for one of n buckets across the take. The review timeline draws
    the waveform from this (no wavesurfer / no CDN — the repo stays offline)."""
    import json as _j
    import struct
    out = take.with_suffix(".peaks.json")
    if out.exists() and out.stat().st_mtime >= take.stat().st_mtime:
        return out
    sr = 8000
    r = subprocess.run([FFMPEG, "-v", "error", "-i", str(take), "-vn", "-ac", "1",
                        "-ar", str(sr), "-f", "s16le", "-"], capture_output=True)
    raw = r.stdout
    if not raw:
        return out
    samp = struct.unpack(f"<{len(raw) // 2}h", raw[: len(raw) // 2 * 2])
    per = max(1, len(samp) // n)
    peaks = []
    for i in range(0, len(samp), per):
        chunk = samp[i:i + per]
        if not chunk:
            break
        peaks.append(round(max(abs(x) for x in chunk) / 328.0, 1))  # 32768/100
    out.write_text(_j.dumps([round(total, 2), peaks]), encoding="utf-8")
    print(f"  escrito  {out.name}  ({len(peaks)} picos)")
    return out


def write_review_html(take, words, cuts, total, missing=None, saved=None):
    """<take>.review.html — a waveform trim room: the take drawn from
    <take>.peaks.json, every cut a red region you drag / resize / delete,
    drag on empty waveform to add one, transcript synced below. Autosaves to
    serve.py /trim-save; «Aplicar corte» POSTs to /trim. Self-contained: no CDN.
    `saved` = the cut list from a previous editing session (loaded in preference
    to the fresh proposal); None if there is none."""
    import html as _h
    import json as _j
    e = _h.escape
    slug = take.parent.parent.name
    pk = take.with_suffix(".peaks.json")
    peaks = pk.read_text(encoding="utf-8") if pk.exists() else f"[{total:.2f},[]]"
    W = _j.dumps([[round(s, 3), round(en, 3), w.strip()] for s, en, w in words], ensure_ascii=False)
    PROP = _j.dumps([[round(c[0], 3), round(c[1], 3)] for c in _merge(cuts)])
    SAVED = _j.dumps([[round(float(c[0]), 3), round(float(c[1]), 3)] for c in saved]) if saved else "null"
    miss = ""
    if missing:
        miss = ('<div class="miss"><b>Líneas del guion sin cobertura clara (' + str(len(missing))
                + ')</b> — revisa por si alguna es un pickup real, no un encabezado:<ul>'
                + "".join(f"<li>({s:.0%}) {e(t)}…</li>" for t, s in missing) + '</ul></div>')
    m4a = e(take.with_suffix(".review.m4a").name)
    html = f"""<!doctype html><meta charset="utf-8"><title>Recorte · {e(take.name)}</title>
<style>
 :root{{--bg:#100d09;--fg:#ece3ce;--gold:#c9a15a;--mut:#96876f;--line:#2e2820;--cut:#b53a2f}}
 *{{box-sizing:border-box}}
 body{{background:var(--bg);color:var(--fg);font:15px/1.6 Georgia,serif;margin:0;padding:0 0 4rem}}
 header{{position:sticky;top:0;background:#161109;border-bottom:1px solid var(--line);
   padding:12px 22px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;z-index:9}}
 h1{{font-size:14px;color:var(--gold);font-weight:normal;margin:0;font-family:monospace}}
 #stat{{color:var(--mut);font-size:13px;font-family:monospace}}
 button,.btn{{font:inherit;font-size:13px;padding:.35rem .8rem;border-radius:6px;border:1px solid var(--line);
   background:#1e1a14;color:var(--fg);cursor:pointer;text-decoration:none;display:inline-block;line-height:1.4}}
 button.primary,.btn.primary{{background:var(--gold);color:#161109;border-color:var(--gold);font-weight:bold}}
 .btn.ghost{{background:transparent;color:var(--mut)}}
 button.tog{{color:var(--mut)}}
 button.tog.on{{background:#2a2412;color:var(--gold);border-color:#5a4a22}}
 button.tog::before{{content:"○ "}} button.tog.on::before{{content:"● "}}
 .warn{{background:#2a2412;color:#e2c98a;padding:.55rem 22px;font-size:13px;border-bottom:1px solid var(--line)}}
 .warn b{{color:#f0dca0}}
 #tools{{display:flex;gap:10px;align-items:center;padding:8px 22px;font-family:monospace;font-size:12px;color:var(--mut)}}
 #scroll{{overflow-x:auto;overflow-y:hidden;border-bottom:1px solid var(--line);background:#0b0906;position:relative}}
 #lane{{position:relative;height:190px}}
 #wave{{position:sticky;left:0;top:0;display:block;z-index:1}}
 .tick{{position:absolute;top:0;bottom:0;border-left:1px solid #221d16;z-index:2}}
 .tick span{{position:absolute;top:2px;left:3px;font:10px/1 monospace;color:#5a5040}}
 .rg{{position:absolute;top:24px;height:140px;background:rgba(181,58,47,.30);
   border-left:2px solid var(--cut);border-right:2px solid var(--cut);z-index:3;cursor:grab}}
 .rg.retoma{{background:rgba(90,120,190,.28);border-color:#5a78be}}
 .rg .h{{position:absolute;top:0;bottom:0;width:9px;cursor:ew-resize}}
 .rg .h.l{{left:-5px}} .rg .h.r{{right:-5px}}
 .rg .x{{position:absolute;top:2px;right:3px;width:16px;height:16px;line-height:14px;text-align:center;
   background:#161109;border:1px solid var(--cut);border-radius:3px;color:#e0a89c;font:11px monospace;cursor:pointer;opacity:0}}
 .rg:hover .x{{opacity:1}}
 #ph{{position:absolute;top:0;bottom:0;width:2px;background:var(--gold);z-index:5;pointer-events:none}}
 #tx{{max-width:1000px;margin:1.2rem auto;padding:0 22px}}
 .w{{cursor:pointer;border-radius:3px}} .w:hover{{background:#2e2820}}
 .w.now{{background:var(--gold);color:#161109}}
 .w.gone{{color:#5a5040;text-decoration:line-through}}
 .miss{{max-width:1000px;margin:2rem auto;padding:1rem 22px;color:#e2c98a;font-size:13px;border-top:1px solid var(--line)}}
 .miss li{{font-family:monospace;font-size:12px;color:#b7a98a}}
</style>
<header>
 <h1>{e(take.name)}</h1><span id="stat"></span>
 <span id="sd" style="font:12px/1 monospace;color:var(--mut)"></span>
 <button class="primary" id="apply">Aplicar corte</button>
 <button id="reset">Reset a la propuesta</button>
 <a class="btn ghost" style="margin-left:auto" href="http://localhost:8765/">Volver al panel</a>
</header>
<div class="warn">Cada bloque rojo es un <b>corte</b>. Arrastra el cuerpo para moverlo, los bordes para ajustarlo,
 <b>✕</b> para quitarlo. Para <b>añadir un corte</b>: arrastra sobre la onda vacía, o pulsa
 <b>✂ corte aquí</b> (lo crea en el playhead). Clic en la onda o en una palabra = escuchar desde ahí.
 Se guarda solo.</div>
<div id="tools">
 <button id="play">▶</button><span id="clock">0:00 / {int(total//60)}:{int(total%60):02d}</span>
 <button id="addcut" title="Crea un corte en la posición del playhead — luego ajústalo con los bordes">✂ corte aquí</button>
 zoom <button id="zo">−</button><button id="zi">+</button>
 <button id="snapl" class="tog on" title="Al soltar, los bordes saltan al límite de palabra más cercano">imán a palabra</button>
 <button id="foll" class="tog" title="Desplaza la onda para seguir la reproducción">seguir voz</button>
</div>
<div id="scroll"><div id="lane"><canvas id="wave"></canvas><div id="ph"></div></div></div>
<audio id="au" preload="auto" src="/episodes/{e(slug)}/assets/{m4a}"></audio>
<div id="tx"></div>
{miss}
<script>
const TAKE={_j.dumps(take.name)}, SLUG={_j.dumps(slug)}, TOTAL={total:.3f}, EP=SLUG.slice(0,4);
const PK={peaks}, PEAKS=PK[1], WORDS={W}, PROP={PROP}, SAVED={SAVED};
const LS='trim:'+SLUG+':'+TAKE, API='';   // same-origin — no CORS, works on localhost or 127.0.0.1
const au=document.getElementById('au'), scroll=document.getElementById('scroll'),
      lane=document.getElementById('lane'), cv=document.getElementById('wave'),
      ph=document.getElementById('ph'), tx=document.getElementById('tx'),
      stat=document.getElementById('stat'), clock=document.getElementById('clock'),
      sd=document.getElementById('sd');
const ctx=cv.getContext('2d');
let pps=Math.max(2, Math.min(14, 2200/TOTAL));   // px per second
let snap=true;
// load order: this browser's unsaved work → the server's saved cuts → the fresh proposal
let regions=(JSON.parse(localStorage.getItem(LS)||'null')||{{}}).regions || SAVED || PROP.map(c=>c.slice(0,2));
regions=regions.map(r=>({{s:+r[0],e:+r[1],retoma:!!r[2]}}));

function cutList(){{return merged().map(r=>[r[0],r[1],'corte']);}}
let saveT;
function save(){{
  localStorage.setItem(LS,JSON.stringify({{regions:regions.map(r=>[r.s,r.e,r.retoma?1:0])}}));
  sd.textContent='guardando…'; clearTimeout(saveT);
  saveT=setTimeout(async()=>{{
    try{{await fetch(API+'/trim-save',{{method:'POST',headers:{{'content-type':'application/json'}},
      body:JSON.stringify({{ep:EP,take:TAKE,cuts:cutList()}})}});
      sd.textContent='guardado ✓ '+new Date().toLocaleTimeString().slice(0,5);
    }}catch(e){{sd.textContent='sin server — solo local';}}
  }},1200);
}}
addEventListener('beforeunload',()=>{{
  try{{navigator.sendBeacon(API+'/trim-save',
    new Blob([JSON.stringify({{ep:EP,take:TAKE,cuts:cutList()}})],{{type:'application/json'}}));}}catch(e){{}}
}});
function fmt(t){{t=Math.max(0,t);return (t/60|0)+':'+('0'+Math.floor(t%60)).slice(-2);}}
function bounds(){{const b=[];WORDS.forEach(w=>{{b.push(w[0]);b.push(w[1]);}});return b;}}
const WB=bounds();
function snapT(t){{if(!snap)return t;let best=t,d=0.15;for(const x of WB){{const dd=Math.abs(x-t);if(dd<d){{d=dd;best=x;}}}}return best;}}
function merged(){{
  const s=regions.map(r=>[Math.min(r.s,r.e),Math.max(r.s,r.e)]).filter(r=>r[1]-r[0]>0.04).sort((a,b)=>a[0]-b[0]);
  const o=[];for(const r of s){{if(o.length&&r[0]<=o[o.length-1][1]+0.03)o[o.length-1][1]=Math.max(o[o.length-1][1],r[1]);else o.push(r.slice());}}
  return o;
}}
function laneW(){{return Math.max(scroll.clientWidth, TOTAL*pps);}}

function sizeWave(){{               // only on resize/zoom — setting cv.width is a realloc
  const vw=scroll.clientWidth, dpr=devicePixelRatio||1;
  cv.width=vw*dpr; cv.height=190*dpr; cv.style.width=vw+'px'; cv.style.height='190px';
  ctx.setTransform(dpr,0,0,dpr,0,0);
}}
function drawWave(){{               // cheap — called on every scroll
  const vw=scroll.clientWidth, x0=scroll.scrollLeft, mid=24+70;
  ctx.clearRect(0,0,vw,190);
  ctx.fillStyle='#3a342a'; ctx.beginPath();
  for(let px=0;px<vw;px++){{
    const t=(x0+px)/pps; if(t>TOTAL)break;
    const i=Math.floor(t/TOTAL*PEAKS.length), h=Math.max(1,(PEAKS[i]||0)/100*66);
    ctx.rect(px,mid-h,1,h*2);
  }}
  ctx.fill();
}}
function layout(){{
  lane.style.width=laneW()+'px';
  [...lane.querySelectorAll('.tick')].forEach(t=>t.remove());
  const step= pps>8?5: pps>4?10: pps>2?30:60;
  for(let t=0;t<=TOTAL;t+=step){{
    const d=document.createElement('div');d.className='tick';d.style.left=(t*pps)+'px';
    d.innerHTML='<span>'+fmt(t)+'</span>';lane.appendChild(d);
  }}
  drawRegions(); sizeWave(); drawWave(); movePh();
}}
function drawRegions(){{
  [...lane.querySelectorAll('.rg')].forEach(r=>r.remove());
  regions.forEach((r,idx)=>{{
    const a=Math.min(r.s,r.e), b=Math.max(r.s,r.e);
    const d=document.createElement('div');d.className='rg'+(r.retoma?' retoma':'');
    d.style.left=(a*pps)+'px';d.style.width=Math.max(2,(b-a)*pps)+'px';d.dataset.i=idx;
    d.innerHTML='<div class="h l"></div><div class="h r"></div><div class="x">✕</div>';
    lane.appendChild(d);
  }});
}}
function movePh(){{ph.style.left=(au.currentTime*pps)+'px';
  clock.textContent=fmt(au.currentTime)+' / '+fmt(TOTAL);}}
function statLine(){{                // cheap — safe to call every pointermove
  const m=merged();let rm=0;m.forEach(r=>rm+=r[1]-r[0]);
  stat.textContent=m.length+' cortes · quita '+fmt(rm)+' · queda '+fmt(TOTAL-rm);
  return m;
}}
function syncStats(){{               // full — strikes through cut words (2696 nodes); pointerup only
  const m=statLine();
  const cut=t=>m.some(r=>t>=r[0]&&t<r[1]);
  [...tx.children].forEach(el=>{{const s=+el.dataset.s,e=+el.dataset.e;
    el.classList.toggle('gone', cut((s+e)/2));}});
}}
function buildTx(){{
  tx.innerHTML=WORDS.map(w=>'<span class="w" data-s="'+w[0]+'" data-e="'+w[1]+'">'+
    w[2].replace(/[&<>]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]))+'</span> ').join('');
}}

// ---- interactions ----
let drag=null;
lane.addEventListener('pointerdown',ev=>{{
  const rg=ev.target.closest('.rg');
  if(ev.target.classList.contains('x')){{regions.splice(+rg.dataset.i,1);save();layout();syncStats();return;}}
  const x=ev.clientX-lane.getBoundingClientRect().left, t=x/pps;
  if(rg){{
    const i=+rg.dataset.i, edge=ev.target.classList.contains('h')?(ev.target.classList.contains('l')?'l':'r'):'move';
    drag={{i,edge,t0:t,s0:regions[i].s,e0:regions[i].e}};
  }} else {{
    drag={{i:-1,edge:'new',t0:t}}; regions.push({{s:t,e:t}}); drag.i=regions.length-1;
    drawRegions();
  }}
  lane.setPointerCapture(ev.pointerId);
}});
lane.addEventListener('pointermove',ev=>{{
  if(!drag)return;
  drag.moved=true;
  const x=ev.clientX-lane.getBoundingClientRect().left, t=Math.max(0,Math.min(TOTAL,x/pps));
  const r=regions[drag.i];
  if(drag.edge==='move'){{const w=drag.e0-drag.s0,ns=Math.max(0,Math.min(TOTAL-w,drag.s0+(t-drag.t0)));r.s=ns;r.e=ns+w;}}
  else if(drag.edge==='l')r.s=Math.min(t,r.e-0.06);
  else r.e=Math.max(t,r.s+0.06);
  // update ONLY the dragged region's div + the light stat — no full rebuild
  const el=lane.querySelector('.rg[data-i="'+drag.i+'"]');
  if(el){{const a=Math.min(r.s,r.e),b=Math.max(r.s,r.e);
    el.style.left=(a*pps)+'px'; el.style.width=Math.max(2,(b-a)*pps)+'px';}}
  statLine();
}});
lane.addEventListener('pointerup',ev=>{{
  if(!drag) return;
  const r=regions[drag.i];
  if(!drag.moved){{                              // a click, not a drag → seek there
    if(drag.edge==='new') regions.splice(drag.i,1);
    au.currentTime=drag.t0;
  }} else {{
    r.s=snapT(Math.min(r.s,r.e)); r.e=snapT(Math.max(r.s,r.e));
    if(r.e-r.s<0.06) regions.splice(drag.i,1);
  }}
  drag=null; save(); layout(); syncStats();
}});
tx.addEventListener('click',ev=>{{const w=ev.target.closest('.w');if(!w)return;au.currentTime=+w.dataset.s;au.play();}});

document.getElementById('play').onclick=()=>{{au.paused?au.play():au.pause();}};
au.addEventListener('play',()=>{{document.getElementById('play').textContent='⏸';tick();}});
au.addEventListener('pause',()=>document.getElementById('play').textContent='▶');
let follow=false, nowEl=null;
function setNow(t){{                 // only re-scan when the word actually changes
  if(nowEl){{ if(t>=+nowEl.dataset.s && t<+nowEl.dataset.e) return; nowEl.classList.remove('now'); }}
  nowEl=[...tx.children].find(el=>t>=+el.dataset.s && t<+el.dataset.e)||null;
  if(nowEl) nowEl.classList.add('now');
}}
function tick(){{
  movePh();
  const t=au.currentTime;
  setNow(t);
  // keep the PLAYHEAD in view horizontally — never scroll the page (that was fighting the edit)
  if(follow){{
    const px=t*pps;
    if(px<scroll.scrollLeft||px>scroll.scrollLeft+scroll.clientWidth-40)
      scroll.scrollLeft=px-scroll.clientWidth/3;
  }}
  if(!au.paused)requestAnimationFrame(tick);
}}
au.addEventListener('seeked',()=>{{movePh();syncStats();}});
scroll.addEventListener('scroll',drawWave);
document.getElementById('zi').onclick=()=>{{pps=Math.min(60,pps*1.6);layout();}};
document.getElementById('zo').onclick=()=>{{pps=Math.max(1,pps/1.6);layout();}};
document.getElementById('snapl').onclick=e=>{{snap=!snap;e.target.classList.toggle('on',snap);}};
document.getElementById('foll').onclick=e=>{{follow=!follow;e.target.classList.toggle('on',follow);}};
document.getElementById('addcut').onclick=()=>{{
  const t=au.currentTime||0, a=Math.max(0,t), b=Math.min(TOTAL,a+0.8);
  regions.push({{s:a,e:b}}); save(); layout(); syncStats();
  // scroll so the new cut is visible + flash it
  scroll.scrollLeft=a*pps-scroll.clientWidth/2;
  const el=[...lane.querySelectorAll('.rg')].pop();
  if(el){{el.style.outline='2px solid var(--gold)';setTimeout(()=>el.style.outline='',900);}}
}};
document.getElementById('reset').onclick=()=>{{
  if(!confirm('Descarta tus ajustes y vuelve a la propuesta automática. ¿Seguro?'))return;
  regions=PROP.map(c=>({{s:+c[0],e:+c[1]}}));save();layout();syncStats();}};
document.getElementById('apply').onclick=async()=>{{
  const cuts=cutList();
  if(!confirm(cuts.length+' cortes · quita '+fmt(cuts.reduce((a,c)=>a+c[1]-c[0],0))+'. ¿Renderizar la toma recortada?'))return;
  try{{
    const r=await fetch(API+'/trim',{{method:'POST',headers:{{'content-type':'application/json'}},
      body:JSON.stringify({{ep:EP,take:TAKE,cuts}})}});
    const j=await r.json(); alert(r.ok?(j.msg||'ok'):(j.error||('server '+r.status))); return;
  }}catch(e){{}}
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([JSON.stringify({{cuts}},null,1)],{{type:'application/json'}}));
  a.download=TAKE.replace(/\\.[^.]+$/,'')+'.cuts.json';a.click();
  alert('Server no detectado. Guardado cuts.json — corre:  python tools/trim_talk.py <toma> --apply');
}};
addEventListener('resize',layout);
buildTx(); layout(); syncStats();
</script>
"""
    out = take.with_suffix(".review.html")
    out.write_text(html, encoding="utf-8")
    print(f"  escrito  {out.name}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2)
    take = Path(a[0]).resolve()
    if not take.is_file():
        sys.exit(f"no existe: {take}")
    import json as _json

    def opt(name, d):
        return a[a.index(name) + 1] if name in a else d

    raw_f = take.with_suffix(".words.raw.json")
    cuts_f = take.with_suffix(".cuts.json")

    def opt_f(name, d):
        return float(opt(name, d))

    # ---- rebuild the review page from an existing transcription (no whisper) ----
    if "--rebuild-page" in a:
        if not raw_f.is_file():
            sys.exit(f"falta {raw_f.name} — no hay transcripción que reusar")
        rw = _json.loads(raw_f.read_text(encoding="utf-8"))
        words = [(w["s"], w["e"], w["w"]) for w in rw]
        total = words[-1][1] + 1.0
        gap, pad = opt_f("--gap", "0.45"), opt_f("--pad", "0.15")
        cuts = plan_cuts(words, gap, pad, "--no-fillers" not in a, [], total)
        if "--no-retakes" not in a:
            cuts = _merge(cuts + plan_retakes(words, pad, opt_f("--retake-window", "13")))
        missing = None
        sp = opt("--script", "")
        if sp and Path(sp).is_file():
            missing = check_script(words, keep_spans(cuts, total),
                                   _spoken_script(Path(sp).read_text(encoding="utf-8")))
        # keep the user's saved edits unless --reset-cuts
        saved = None
        if cuts_f.is_file() and "--reset-cuts" not in a:
            try:
                saved = _json.loads(cuts_f.read_text(encoding="utf-8")).get("cuts")
            except Exception:
                saved = None
        if saved is None:
            cuts_f.write_text(_json.dumps(
                {"cuts": [[round(s, 3), round(e, 3), r] for s, e, r in cuts]}, ensure_ascii=False),
                encoding="utf-8")
        audio_proxy(take)
        write_peaks(take, total)
        write_review_html(take, words, cuts, total, missing, saved=saved)
        print(f"  página reconstruida ({len(cuts)} cortes propuestos"
              + (f", {len(saved)} guardados conservados" if saved else "") + ")")
        sys.exit(0)

    # ---- phase B: apply an approved cut list ----
    if "--apply" in a:
        if not raw_f.is_file():
            sys.exit(f"falta {raw_f.name} — corre antes el pase de revisión (sin --apply)")
        rw = _json.loads(raw_f.read_text(encoding="utf-8"))
        words = [(w["s"], w["e"], w["w"]) for w in rw]
        total = words[-1][1] + 1.0
        cd = _json.loads(cuts_f.read_text(encoding="utf-8")) if cuts_f.is_file() else {"cuts": []}
        cl = [(float(c[0]), float(c[1]), (c[2] if len(c) > 2 else "corte")) for c in cd.get("cuts", [])]
        spans = keep_spans(_merge(cl), total)
        print(f"aplicar: {len(cl)} cortes · queda {sum(e - s for s, e in spans):.1f}s de {total:.1f}s")
        write_words_json(take, words, spans)
        ok = render(take, spans, take.with_suffix(".trimmed.mp4"))
        sys.exit(0 if ok else 1)

    gap = float(opt("--gap", "0.45"))
    pad = float(opt("--pad", "0.15"))
    model_name = opt("--model", "medium")
    lang = opt("--lang", "es")
    do_fillers = "--no-fillers" not in a
    do_retakes = "--no-retakes" not in a
    retake_window = float(opt("--retake-window", "13"))
    script_path = opt("--script", "")
    keeps = [secs(a[i + 1]) for i, x in enumerate(a) if x == "--keep"]

    words = transcribe(take, model_name, lang)
    if not words:
        sys.exit("whisper no devolvió palabras (¿audio mudo?)")
    total = words[-1][1] + 1.0
    cuts = plan_cuts(words, gap, pad, do_fillers, keeps, total)
    if do_retakes:
        ret = plan_retakes(words, pad, retake_window)
        ret = [c for c in ret if not any(c[0] <= k <= c[1] or abs(c[0] - k) < 2 for k in keeps)]
        cuts = _merge(cuts + ret)
    spans = keep_spans(cuts, total)
    missing = None
    if script_path and Path(script_path).is_file():
        missing = check_script(words, spans, _spoken_script(Path(script_path).read_text(encoding="utf-8")))

    # raw word timeline (for --apply). Seed cuts.json with the proposal ONLY if
    # there's no saved editing session to preserve (--reset-cuts forces reseed).
    raw_f.write_text(_json.dumps(
        [{"s": round(s, 3), "e": round(e, 3), "w": w.strip()} for s, e, w in words],
        ensure_ascii=False), encoding="utf-8")
    saved = None
    if cuts_f.is_file() and "--reset-cuts" not in a:
        try:
            saved = _json.loads(cuts_f.read_text(encoding="utf-8")).get("cuts")
        except Exception:
            saved = None
    if saved is None:
        cuts_f.write_text(_json.dumps(
            {"cuts": [[round(s, 3), round(e, 3), r] for s, e, r in cuts]}, ensure_ascii=False),
            encoding="utf-8")
    write_cuts_md(take, words, cuts, spans, total, missing)
    audio_proxy(take)
    write_peaks(take, total)
    write_review_html(take, words, cuts, total, missing, saved=saved)

    if "--apply-now" in a:               # skip the review, render the auto plan
        write_words_json(take, words, spans)
        ok = render(take, spans, take.with_suffix(".trimmed.mp4"))
        sys.exit(0 if ok else 1)
    print(f"\n{take.name}: {len(cuts)} cortes propuestos, quita {sum(e - s for s, e, _ in cuts):.1f} s"
          + (f" · {len(missing)} líneas del guion sin cobertura" if missing else ""))
    print(f"  revisa   episodes/{take.parent.parent.name}/assets/{take.with_suffix('.review.html').name}")
    print(f"  y pulsa «Aplicar corte» (o:  python tools/trim_talk.py {take} --apply)")
    sys.exit(0)
