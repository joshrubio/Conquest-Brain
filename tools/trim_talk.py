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

  2b. soft   ·  python tools/trim_talk.py TAKE.mp4 --soft
       what «Aplicar corte» and the edit room's audio cuts actually run: the
       cheap half of --apply. Rewrites <take>.words.json and the edit room's
       09-vo.m4a (audio only, cut from <take>.review.m4a — seconds, no video),
       and leaves <take>.render.pending so the 4K render is QUEUED, not run.
       --apply (run on «Finalizar», or «Renderizar recorte» in the room, or
       inside assemble.py --rough/--final) does the heavy render once for all
       the queued cuts and clears the marker.

  --proxy          build <take>.proxy.mp4 (540p, muted, of the ORIGINAL take; once per
                   take, minutes). The edit room plays the face from it + 09-cuts-map.json
                   and skips the cuts live, so cutting never re-renders video. Started
                   automatically by the review pass and by --soft.
  --map            rewrite 09-cuts-map.json from cuts.json (no audio, no render).

  --apply-now      both phases with the auto proposal, no review (advance.py / CI).
  --rebuild-page   regenerate the trim room from an existing transcription (no
                   whisper). Keeps any autosaved edits; --reset-cuts discards them.

A gap under 0.45 s is never cut. --keep MM:SS protects a span in phase 1.
With --script, the trim room lists script lines no surviving span covers, and
writes <take>.pickups.json (full sentence text, match confidence, an
original-take-second anchor) — the re-record candidate list pickup_room.py
turns into the pickup UI.
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
from mediabin import FFMPEG, FFPROBE, keep_awake  # noqa: E402

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
    blocks, tables, headings, the appendix. Returns [(raw_text, norm_words), ...] —
    raw_text keeps punctuation/casing so a missed sentence can be read back verbatim
    for a pickup."""
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
                out.append((sent.strip(), ws))
    return out


def check_script(words, spans, script_sents, sim=0.62):
    """After cuts: which script sentences does no surviving span cover well?
    script_sents = [(raw_text, norm_words), ...] from _spoken_script. Returns
    [(raw_text, score, anchor_t), ...] for sentences below `sim` — anchor_t is
    the ORIGINAL-take second (same clock as <take>.review.m4a and the `spans`
    render() splices) of the closest-matching (if weak) window: a rough point
    to sample "how it was said" and to splice a pickup near. None if the take
    has no surviving words at all."""
    surv = [(s, w) for (s, _e, w) in words if remap(s, spans) is not None]
    surv_norm = [norm(w) for _, w in surv]
    missing = []
    for raw, ws in script_sents:
        L = len(ws)
        best, best_k = 0.0, None
        for k in range(0, max(1, len(surv_norm) - L + 1), 2):
            r = SequenceMatcher(None, ws, surv_norm[k:k + L]).ratio()
            if r > best:
                best, best_k = r, k
            if best >= sim:
                break
        if best < sim:
            anchor = surv[best_k][0] if best_k is not None and surv else None
            missing.append((raw, best, anchor))
    return missing


def write_pickups_json(take, missing):
    """<take>.pickups.json — sentence-level re-record candidates for
    pickup_room.py: full script text verbatim (so the operator reads back
    exactly what's written, not a word or two — keeps the delivery's tone
    consistent with the rest of the take), match confidence, and a rough
    original-take-timeline anchor (`anchor_t`, same clock as <take>.review.m4a)
    to sample the flub and splice the pickup near. One row per script sentence
    `check_script` couldn't match well."""
    import json as _j
    out = [{"text": t, "score": round(sc, 3),
            "anchor_t": round(a, 3) if a is not None else None}
           for t, sc, a in missing]
    p = take.with_suffix(".pickups.json")
    p.write_text(_j.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  escrito  {p.name}  ({len(out)} candidatos a pickup)")


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
                "para recuperar una toma, o vuelve a grabar el pickup — lista completa en "
                f"`{take.with_suffix('.pickups.json').name}`.", ""]
        out += [f"- ({sc:.0%}) {txt[:90]}…" for txt, sc, _a in missing]
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


def load_accepted_pickups(take):
    """Accepted pickups (pickup_room.py / serve.py's /pickup-accept) for this
    take, `audio` resolved to an absolute path. Each replaces a span — fold
    `(orig_start, orig_end, "pickup")` into the cut list before `keep_spans()`
    (same as any other cut), then pass the result to `write_words_json()` /
    `render()` so it's spliced back in at that point. Shared by both --apply
    and --apply-now so neither can silently render a take that drops a pickup
    the other would have included."""
    import json as _j
    acc_f = take.with_suffix(".pickups.accepted.json")
    if not acc_f.is_file():
        return []
    pickups = []
    for p in _j.loads(acc_f.read_text(encoding="utf-8")).get("pickups", []):
        p = dict(p)
        p["audio"] = take.parent / p["audio"]
        pickups.append(p)
    return pickups


def build_timeline(spans, pickups):
    """Interleave kept original-take `spans` with accepted `pickups`
    (each {"orig_start","dur",...}) in original-timeline order, and give each
    item its trimmed-timeline start `t0` (cumulative). With no pickups this is
    just `spans` in order — the same trimmed clock `remap()` computes alone;
    with pickups, everything from the first pickup onward shifts, which is
    exactly why `remap()` alone can't be reused once a pickup is spliced in."""
    items = [{"kind": "orig", "s": s, "e": e} for s, e in spans]
    items += [{"kind": "pickup", "pk": pk, "s": pk["orig_start"]} for pk in (pickups or [])]
    items.sort(key=lambda it: it["s"])
    t = 0.0
    for it in items:
        it["t0"] = t
        t += (it["e"] - it["s"]) if it["kind"] == "orig" else it["pk"]["dur"]
    return items, t


def remap_with_pickups(t, items):
    """Like `remap()`, but timeline-aware of spliced-in pickups (see
    `build_timeline`). None if `t` falls inside a cut — pickup-replaced spans
    included, same as any other cut."""
    for it in items:
        if it["kind"] != "orig":
            continue
        if t < it["s"]:
            return None
        if t <= it["e"]:
            return it["t0"] + (t - it["s"])
    return None


def orig_range_for_cut(take, t0, t1):
    """Inverse of remap()/remap_with_pickups(): map a [t0,t1) range on the
    ALREADY-TRIMMED take's own clock back to the ORIGINAL take's clock, so a
    further cut made downstream (the edit room's audio micro-trims) can be
    appended to <take>.cuts.json in the coordinates --apply already expects.
    Raises if either end lands inside a spliced-in pickup — that's
    re-recorded audio with no original-take position to cut from; the pickup
    room, not this, is where that gets trimmed."""
    import json as _j
    raw_f = take.with_suffix(".words.raw.json")
    if not raw_f.is_file():
        raise SystemExit(f"falta {raw_f.name} — corre antes el pase de revisión (sin --apply)")
    rw = _j.loads(raw_f.read_text(encoding="utf-8"))
    if not rw:
        raise SystemExit(f"{raw_f.name} está vacío")
    total = rw[-1]["e"] + 1.0
    cuts_f = take.with_suffix(".cuts.json")
    cd = _j.loads(cuts_f.read_text(encoding="utf-8")) if cuts_f.is_file() else {"cuts": []}
    cl = [(float(c[0]), float(c[1]), (c[2] if len(c) > 2 else "corte")) for c in cd.get("cuts", [])]
    pickups = load_accepted_pickups(take)
    items, _total = build_timeline(keep_spans(_merge(cl), total), pickups)

    def inv(t):
        for it in items:
            length = (it["e"] - it["s"]) if it["kind"] == "orig" else it["pk"]["dur"]
            if t < it["t0"] + length + 1e-6:
                if it["kind"] != "orig":
                    return None
                return it["s"] + (t - it["t0"])
        return None

    s, e = inv(t0), inv(t1)
    if s is None or e is None:
        raise SystemExit("ese tramo cae sobre un pickup regrabado — recórtalo desde la sala de pickups")
    return round(s, 3), round(e, 3)


def write_words_json(take, words, spans, pickups=None):
    import json
    if not pickups:
        out = []
        for s, _e, w in words:
            ts = remap(s, spans)
            if ts is not None:
                out.append({"w": w.strip(), "t": round(ts, 3)})
        take.with_suffix(".words.json").write_text(
            json.dumps(out, ensure_ascii=False), encoding="utf-8")
        print(f"  escrito  {take.with_suffix('.words.json').name}  ({len(out)} palabras)")
        return
    items, _total = build_timeline(spans, pickups)
    out = []
    for s, _e, w in words:
        ts = remap_with_pickups(s, items)
        if ts is not None:
            out.append({"w": w.strip(), "t": round(ts, 3)})
    for it in items:
        if it["kind"] != "pickup":
            continue
        pk, toks = it["pk"], it["pk"]["text"].split()
        if not toks:
            continue
        # no per-word whisper timing inside a pickup — evenly spread across its
        # duration. align() matches by text first; sub-word precision here
        # isn't what it needs, the sentence-level splice point is.
        step = pk["dur"] / len(toks)
        for k, tok in enumerate(toks):
            out.append({"w": tok, "t": round(it["t0"] + k * step, 3)})
    out.sort(key=lambda w: w["t"])
    take.with_suffix(".words.json").write_text(
        json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"  escrito  {take.with_suffix('.words.json').name}  ({len(out)} palabras, "
          f"{len(pickups)} pickup(s) integrados)")


def _probe_video_info(take):
    r = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height,r_frame_rate",
                        "-of", "csv=p=0", str(take)], capture_output=True, text=True)
    parts = r.stdout.strip().split(",")
    if len(parts) < 3:
        raise RuntimeError(f"ffprobe no pudo leer vídeo de {take}: {r.stderr[-300:]}")
    num, _, den = parts[2].partition("/")
    den_f = float(den) if den else 0.0
    fps = float(num) / den_f if den_f else 25.0   # "0/0" (unknown/VFR) — sane fallback, not a crash
    return int(parts[0]), int(parts[1]), fps


def _grab_frame(take, t, out_png):
    r = subprocess.run([FFMPEG, "-y", "-ss", f"{max(0.0, t):.3f}", "-i", str(take),
                        "-vframes", "1", str(out_png)], capture_output=True, text=True)
    if r.returncode != 0 or not Path(out_png).exists():
        raise RuntimeError(f"no se pudo capturar el frame en {t:.2f}s: {r.stderr[-300:]}")


GATE_ATTACK_MS = 5      # fixed — this is an experimental single-knob control,
GATE_RELEASE_MS = 150   # brain/16: only threshold is user-adjustable (review.html)
GATE_RATIO = 20         # strong enough to read as "muted", not just quieter


def load_gate(take):
    """<take>.gate.json → threshold_db, or None (no file / null threshold —
    identical behavior to before this existed). Experimental, review.html
    only: written by its own autosave, read only here at --apply time."""
    import json as _j
    p = take.with_suffix(".gate.json")
    if not p.is_file():
        return None
    try:
        v = _j.loads(p.read_text(encoding="utf-8")).get("threshold_db")
    except Exception:
        return None
    return float(v) if v is not None else None


def _gate_filter(threshold_db):
    """ffmpeg `agate` filter string for a fixed attack/release/ratio, given
    only a threshold in dB (agate's own `threshold` is linear 0-1)."""
    lin = 10 ** (float(threshold_db) / 20)
    return f"agate=threshold={lin:.6f}:attack={GATE_ATTACK_MS}:release={GATE_RELEASE_MS}:ratio={GATE_RATIO}"


def _part(out_path):
    """Where render() writes before swapping into place. `x.trimmed.mp4` ->
    `x.trimmed.part.mp4` — deliberately NOT matched by the `*.trimmed.mp4` globs
    the rest of the pipeline uses, so a killed/crashed render can never leave a
    half-written file that looks like a finished take."""
    return out_path.with_name(out_path.stem + ".part" + out_path.suffix)


def _swap_in(tmp, out_path):
    """Atomic replace. On Windows this fails with a sharing violation while
    serve.py is streaming the old file to the room, so retry for a few seconds."""
    import time
    for k in range(10):
        try:
            tmp.replace(out_path)
            return True
        except OSError as ex:
            if k == 9:
                print(f"  FALLO al colocar {out_path.name}: {ex}")
                return False
            time.sleep(0.5)
    return False


def render(take, spans, out_path, pickups=None, gate_db=None):
    """Cut `take` down to `spans` (original-timeline, kept regions). With
    `pickups` ({"orig_start","dur","audio"}, from <take>.pickups.accepted.json)
    also present, each is spliced in at its place in original-timeline order:
    a still frame grabbed from the take at `orig_start` held for `dur` under
    the matched pickup audio. The still is a fallback, not a fix — it's
    invisible for a narration/B-roll beat (only the take's *audio* is used
    downstream there) but a pickup landing inside a planned `acamara` stretch
    needs the shot re-recorded for real, not this freeze (brain/16).

    `gate_db`, if given, runs the concatenated audio through one `agate` pass
    (breath between phrases — below a hard cut, above what loudnorm in
    assemble.py fixes) before mapping. None (the default — no <take>.gate.json,
    or a null threshold in it) skips this entirely: identical output to before
    this existed."""
    if not pickups:
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
        amap = "[a]"
        if gate_db is not None:
            script += f";\n[a]{_gate_filter(gate_db)}[ag]"
            amap = "[ag]"
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(script)
            sp = f.name
        # intermediate file — favour speed; the Stage-9 export re-encodes anyway
        tmp = _part(out_path)
        cmd = [FFMPEG, "-y", "-i", str(take), "-filter_complex_script", sp,
               "-map", "[v]", "-map", amap, "-c:v", "libx264", "-crf", "16",
               "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k",
               str(tmp)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        Path(sp).unlink(missing_ok=True)
        if r.returncode != 0 or not tmp.exists():
            tmp.unlink(missing_ok=True)
            print("  FALLO ffmpeg:\n" + "\n".join(r.stderr.strip().splitlines()[-4:]))
            return False
        if not _swap_in(tmp, out_path):
            return False
        print(f"  escrito  {out_path.name}")
        return True

    items, _total = build_timeline(spans, pickups)
    W, H, FPS = _probe_video_info(take)
    tmp_pngs, extra_inputs, parts, maps = [], [], [], []
    vi = 1  # ffmpeg input index; 0 is the take itself
    try:
        for i, it in enumerate(items):
            if it["kind"] == "orig":
                s, e = it["s"], it["e"]
                d = e - s
                fo = max(0.0, d - FADE)
                parts.append(
                    f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS,format=yuv420p[v{i}];"
                    f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,"
                    f"aformat=sample_rates=48000:channel_layouts=stereo,"
                    f"afade=t=in:st=0:d={FADE},afade=t=out:st={fo:.3f}:d={FADE}[a{i}]")
            else:
                pk = it["pk"]
                png = take.with_suffix(f".pick{i}.tmp.png")
                _grab_frame(take, pk["orig_start"], png)
                tmp_pngs.append(png)
                extra_inputs += ["-loop", "1", "-t", f"{pk['dur']:.3f}", "-i", str(png),
                                  "-i", str(pk["audio"])]
                iv, ia = vi, vi + 1
                vi += 2
                parts.append(
                    f"[{iv}:v]fps={FPS:.3f},scale={W}:{H},format=yuv420p,setpts=PTS-STARTPTS[v{i}];"
                    f"[{ia}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                    f"asetpts=PTS-STARTPTS[a{i}]")
            maps.append(f"[v{i}][a{i}]")
        script = ";\n".join(parts) + ";\n" + "".join(maps) + f"concat=n={len(items)}:v=1:a=1[v][a]"
        amap = "[a]"
        if gate_db is not None:
            script += f";\n[a]{_gate_filter(gate_db)}[ag]"
            amap = "[ag]"
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(script)
            sp = f.name
        tmp = _part(out_path)
        cmd = [FFMPEG, "-y", "-i", str(take)] + extra_inputs + [
               "-filter_complex_script", sp, "-map", "[v]", "-map", amap,
               "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "320k", str(tmp)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        Path(sp).unlink(missing_ok=True)
        if r.returncode != 0 or not tmp.exists():
            tmp.unlink(missing_ok=True)
            print("  FALLO ffmpeg (con pickups):\n" + "\n".join(r.stderr.strip().splitlines()[-8:]))
            return False
        if not _swap_in(tmp, out_path):
            return False
        print(f"  escrito  {out_path.name}  ({len(pickups)} pickup(s) integrados)")
        return True
    finally:
        for p in tmp_pngs:
            p.unlink(missing_ok=True)


def pending_marker(take):
    """<take>.render.pending — exists while <take>.cuts.json holds cuts that the
    4K <take>.trimmed.mp4 doesn't reflect yet (queued by --soft, cleared by a
    successful --apply)."""
    return take.with_suffix(".render.pending")


def _cuts_sig(take):
    """Digest of everything --apply reads besides the raw transcript: the cut
    list, accepted pickups and the gate. A --apply only clears the pending
    marker if this is unchanged since it started — a cut queued while the render
    was running must stay queued."""
    import hashlib
    h = hashlib.sha1()
    for suf in (".cuts.json", ".pickups.accepted.json", ".gate.json"):
        f = take.with_suffix(suf)
        h.update(f.read_bytes() if f.is_file() else b"-")
    return h.hexdigest()


def _plan(take):
    """The approved cut list resolved into what --apply and --soft both need:
    (words, spans, pickups, gate_db, cuts, total)."""
    import json as _j
    raw_f = take.with_suffix(".words.raw.json")
    if not raw_f.is_file():
        sys.exit(f"falta {raw_f.name} — corre antes el pase de revisión (sin --apply)")
    rw = _j.loads(raw_f.read_text(encoding="utf-8"))
    words = [(w["s"], w["e"], w["w"]) for w in rw]
    total = words[-1][1] + 1.0
    cuts_f = take.with_suffix(".cuts.json")
    cd = _j.loads(cuts_f.read_text(encoding="utf-8")) if cuts_f.is_file() else {"cuts": []}
    cl = [(float(c[0]), float(c[1]), (c[2] if len(c) > 2 else "corte")) for c in cd.get("cuts", [])]
    pickups = load_accepted_pickups(take)
    cl += [(p["orig_start"], p["orig_end"], "pickup") for p in pickups]
    return words, keep_spans(_merge(cl), total), pickups, load_gate(take), cl, total


SOFT_SR = 48000


def _pcm(path):
    """`path` decoded to mono 48 kHz int16 (numpy). None on failure."""
    import numpy as np
    r = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-vn", "-ac", "1",
                        "-ar", str(SOFT_SR), "-f", "s16le", "-"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    return np.frombuffer(r.stdout, dtype=np.int16)


def _soft_vo(take, items, gate_db, out_path):
    """The edit room's 09-vo.m4a for the CURRENT cut list, without touching the
    video. Same result as render()'s audio (join fades, pickups, gate) but the
    take's small audio proxy (<take>.review.m4a) is decoded ONCE and sliced in
    memory — a 160-way atrim/concat graph in ffmpeg took minutes (every branch
    buffers the whole stream), this is seconds. Mono AAC like assemble.vo_proxy()."""
    import numpy as np
    src = audio_proxy(take)
    base = _pcm(src) if src.exists() else None
    if base is None:
        print(f"  FALLO: no se pudo leer {src.name}")
        return False
    fade = int(FADE * SOFT_SR)
    chunks, acc = [], 0.0                    # acc: exact trimmed-clock seconds so far
    for it in items:
        if it["kind"] == "orig":
            a, b = round(it["s"] * SOFT_SR), round(it["e"] * SOFT_SR)
            seg = base[a:b].astype(np.float32)
            n = len(seg)
            if n > 2 * fade:                 # 10 ms fade at each join, like render()
                ramp = np.linspace(0.0, 1.0, fade, dtype=np.float32)
                seg[:fade] *= ramp
                seg[-fade:] *= ramp[::-1]
            length = it["e"] - it["s"]
        else:
            pk = _pcm(it["pk"]["audio"])
            if pk is None:
                print(f"  FALLO: no se pudo leer el pickup {it['pk']['audio']}")
                return False
            seg = pk.astype(np.float32)
            length = it["pk"]["dur"]
        # land on the exact cumulative sample so 160 joins can't drift the clock
        want = round((acc + length) * SOFT_SR) - round(acc * SOFT_SR)
        if len(seg) < want:
            seg = np.pad(seg, (0, want - len(seg)))
        chunks.append(seg[:want])
        acc += length
    pcm = np.clip(np.concatenate(chunks), -32768, 32767).astype(np.int16)
    tmp = out_path.with_name(out_path.stem + ".part" + out_path.suffix)
    cmd = [FFMPEG, "-y", "-f", "s16le", "-ar", str(SOFT_SR), "-ac", "1", "-i", "-"]
    if gate_db is not None:
        cmd += ["-af", _gate_filter(gate_db)]
    cmd += ["-c:a", "aac", "-b:a", "128k", str(tmp)]
    r = subprocess.run(cmd, input=pcm.tobytes(), capture_output=True)
    if r.returncode != 0 or not tmp.exists():
        tmp.unlink(missing_ok=True)
        print("  FALLO ffmpeg (audio):\n" + "\n".join(
            r.stderr.decode("utf-8", "replace").strip().splitlines()[-4:]))
        return False
    return _swap_in(tmp, out_path)


def soft_apply(take):
    """The cheap half of --apply, run on every «Aplicar corte» / audio cut: the
    retimed words.json + the room's 09-vo.m4a, then queue the 4K render by
    leaving the pending marker. Seconds, audio only."""
    import json as _j
    import time
    words, spans, pickups, gate_db, cl, total = _plan(take)
    print(f"en cola: {len(cl)} cortes · queda {sum(e - s for s, e in spans):.1f}s de {total:.1f}s"
          + (f" · {len(pickups)} pickup(s)" if pickups else "")
          + (f" · gate {gate_db:g}dB" if gate_db is not None else ""))
    write_words_json(take, words, spans, pickups=pickups)
    items, _t = build_timeline(spans, pickups)
    if not _soft_vo(take, items, gate_db, take.parent.parent / "09-vo.m4a"):
        return False
    print("  escrito  09-vo.m4a  (audio de la sala al día)")
    if write_cuts_map(take, items):
        print("  escrito  09-cuts-map.json  (la cámara de la sala salta los cortes)")
    if spawn_video_proxy(take):
        print(f"  construyendo {take.with_suffix('.proxy.mp4').name} en segundo plano (una vez por toma)")
    pending_marker(take).write_text(_j.dumps({"cuts": len(cl), "ts": int(time.time())}), encoding="utf-8")
    print(f"  render 4K pendiente ({pending_marker(take).name}) — se hace al Finalizar")
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


def video_proxy(take):
    """<take>.proxy.mp4 — a small muted 540p proxy of the ORIGINAL take, built
    once per take. The edit room plays the narrator's face from it and jumps
    over the cuts live (09-cuts-map.json says where), so a cut never has to
    re-render any video. Same encode as assemble.take_proxy(): a keyframe every
    0.5 s so a seek at a join lands fast. Skipped if newer than the take."""
    import os
    out = take.with_suffix(".proxy.mp4")
    if out.exists() and out.stat().st_mtime >= take.stat().st_mtime:
        return out
    lock = take.with_suffix(".proxy.lock")
    import pipeline as P
    try:
        mine = int(lock.read_text(encoding="utf-8").strip() or 0) == os.getpid()
    except (OSError, ValueError):
        mine = False
    if not mine and P.lock_alive(lock):
        print(f"  {out.name}: ya se está construyendo")
        return None
    lock.write_text(str(os.getpid()), encoding="utf-8")
    tmp = out.with_name(out.stem + ".part" + out.suffix)
    try:
        r = subprocess.run([FFMPEG, "-y", "-i", str(take), "-vf", "scale=-2:540,fps=24",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "32", "-g", "12",
                            "-keyint_min", "12", "-sc_threshold", "0", "-an",
                            "-movflags", "+faststart", str(tmp)], capture_output=True, text=True)
        if r.returncode != 0 or not tmp.exists() or not _swap_in(tmp, out):
            tmp.unlink(missing_ok=True)
            print(f"  {out.name} falló: {(r.stderr or '')[-200:]}")
            return None
        print(f"  escrito  {out.name}  ({out.stat().st_size // (1024 * 1024)} MB)")
        return out
    finally:
        lock.unlink(missing_ok=True)


def spawn_video_proxy(take):
    """Build <take>.proxy.mp4 in a detached process (minutes: it decodes the 4K
    original once) unless it exists or is already being built."""
    import os
    out = take.with_suffix(".proxy.mp4")
    if out.exists() and out.stat().st_mtime >= take.stat().st_mtime:
        return False
    import pipeline as P
    lock = take.with_suffix(".proxy.lock")
    if P.lock_alive(lock):
        return False
    flags = (0x00000008 | 0x00000200) if os.name == "nt" else 0     # DETACHED_PROCESS | NEW_PROCESS_GROUP
    proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), str(take), "--proxy"],
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, creationflags=flags)
    lock.write_text(str(proc.pid), encoding="utf-8")
    return True


def write_cuts_map(take, items):
    """<ep>/09-cuts-map.json — where each stretch of the trimmed clock lives in
    the ORIGINAL take (the clock <take>.proxy.mp4 is on): [t0, src, len, hold].
    `hold` = a spliced-in pickup, shown as the frozen frame at `src`. Written by
    the same step that writes the audio the room plays, so the two always agree."""
    import json as _j
    segs = []
    for it in items:
        if it["kind"] == "orig":
            segs.append([round(it["t0"], 3), round(it["s"], 3), round(it["e"] - it["s"], 3), 0])
        else:
            segs.append([round(it["t0"], 3), round(it["s"], 3), round(it["pk"]["dur"], 3), 1])
    ep = take.parent.parent
    out = ep / "09-cuts-map.json"
    tmp = out.with_name("09-cuts-map.part.json")
    tmp.write_text(_j.dumps({"take": take.name, "proxy": f"assets/{take.with_suffix('.proxy.mp4').name}",
                             "segs": segs}, ensure_ascii=False), encoding="utf-8")
    return _swap_in(tmp, out)


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


def write_review_html(take, words, cuts, total, missing=None, saved=None, gate_db=None):
    """<take>.review.html — a waveform trim room: the take drawn from
    <take>.peaks.json, every cut a red region you drag / resize / delete,
    drag on empty waveform to add one, transcript synced below. Autosaves to
    serve.py /trim-save; «Aplicar corte» POSTs to /trim. Self-contained: no CDN.
    `saved` = the cut list from a previous editing session (loaded in preference
    to the fresh proposal); None if there is none.

    `gate_db` seeds the experimental noise-gate panel (breath between phrases —
    below a hard cut, above what loudnorm fixes later) from a previous session's
    <take>.gate.json; None means the gate has never been touched here, off by
    default. The panel does its own decode+analysis client-side (Web Audio,
    fetch + decodeAudioData on the same .review.m4a proxy already loaded for
    scrubbing) so every threshold nudge previews instantly with no server
    round-trip; only "Aplicar corte" bakes it in, via agate in render()."""
    import html as _h
    import json as _j
    e = _h.escape
    slug = take.parent.parent.name
    pk = take.with_suffix(".peaks.json")
    peaks = pk.read_text(encoding="utf-8") if pk.exists() else f"[{total:.2f},[]]"
    W = _j.dumps([[round(s, 3), round(en, 3), w.strip()] for s, en, w in words], ensure_ascii=False)
    PROP = _j.dumps([[round(c[0], 3), round(c[1], 3)] for c in _merge(cuts)])
    SAVED = _j.dumps([[round(float(c[0]), 3), round(float(c[1]), 3)] for c in saved]) if saved else "null"
    GATE_DB_SAVED = "null" if gate_db is None else f"{float(gate_db):.1f}"
    miss = ""
    if missing:
        miss = ('<div class="miss"><b>Líneas del guion sin cobertura clara (' + str(len(missing))
                + ')</b> — revisa por si alguna es un pickup real, no un encabezado:<ul>'
                + "".join(f"<li>({s:.0%}) {e(t[:90])}…</li>" for t, s, _a in missing) + '</ul></div>')
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
 #gatebar{{display:flex;gap:10px;align-items:center;padding:6px 22px;font-family:monospace;font-size:12px;
   color:var(--mut);border-bottom:1px solid var(--line);background:#0d0a07}}
 #gatebar b{{color:#8db4e0}}
 #gateTh{{width:150px;accent-color:#5a94d8}}
 #gateTh:disabled{{opacity:.35}}
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
 <button id="savebtn" title="Guarda ya (autoguarda solo cada ~1.2s tras cada cambio; este botón lo fuerza al momento).">Guardar</button>
 <button class="primary" id="apply">Aplicar corte</button>
 <button id="reset">Reset a la propuesta</button>
 {f'<a class="btn ghost" target="_blank" href="http://localhost:8765/episodes/{e(slug)}/09-edit.html" title="Abre la sala de montaje en otra pestaña.">Sala de montaje</a>' if (take.parent.parent / "09-edit.html").exists() else ''}
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
<div id="gatebar">
 <button id="gateTog" class="tog" title="EXPERIMENTAL — atenúa automáticamente lo que quede por debajo del umbral (pensado para la respiración entre frases, no reemplaza los cortes duros). Se previsualiza en vivo aquí mismo; no se hornea hasta «Aplicar corte». Umbral en null/desactivado = comportamiento idéntico a hoy.">gate</button>
 <input type="range" id="gateTh" min="-60" max="-10" step="0.5" disabled>
 <span id="gateThV"></span>
 <span id="gateStat"></span>
 <span style="margin-left:auto;color:#5a5040">resaltado azul en la onda = lo que el gate atenuaría</span>
</div>
<div id="scroll"><div id="lane"><canvas id="wave"></canvas><div id="ph"></div></div></div>
<audio id="au" preload="auto" src="/episodes/{e(slug)}/assets/{m4a}"></audio>
<div id="tx"></div>
{miss}
<script>
const TAKE={_j.dumps(take.name)}, SLUG={_j.dumps(slug)}, TOTAL={total:.3f}, EP=SLUG.slice(0,4);
const PK={peaks}, PEAKS=PK[1], WORDS={W}, PROP={PROP}, SAVED={SAVED}, GATE_DB_SAVED={GATE_DB_SAVED};
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
const _ls=(JSON.parse(localStorage.getItem(LS)||'null')||{{}});
let regions=_ls.regions || SAVED || PROP.map(c=>c.slice(0,2));
regions=regions.map(r=>({{s:+r[0],e:+r[1],retoma:!!r[2]}}));

function cutList(){{return merged().map(r=>[r[0],r[1],'corte']);}}
function gateBody(){{return GATE_ON ? {{threshold_db:gateThreshold}} : null;}}
let saveT;
function markLocal(){{
  localStorage.setItem(LS,JSON.stringify({{regions:regions.map(r=>[r.s,r.e,r.retoma?1:0]),gate:gateBody()}}));
}}
async function doSaveNow(){{
  clearTimeout(saveT);
  markLocal();
  sd.textContent='guardando…';
  try{{
    await fetch(API+'/trim-save',{{method:'POST',headers:{{'content-type':'application/json'}},
      body:JSON.stringify({{ep:EP,take:TAKE,cuts:cutList(),gate:gateBody()}})}});
    sd.textContent='guardado ✓ '+new Date().toLocaleTimeString().slice(0,5);
  }}catch(e){{sd.textContent='sin server — solo local';}}
}}
function save(){{                          // autosave path — debounced, coalesces a burst of edits
  markLocal();
  sd.textContent='guardando…'; clearTimeout(saveT);
  saveT=setTimeout(doSaveNow,1200);
}}
document.getElementById('savebtn').onclick=doSaveNow;
addEventListener('beforeunload',()=>{{
  try{{navigator.sendBeacon(API+'/trim-save',
    new Blob([JSON.stringify({{ep:EP,take:TAKE,cuts:cutList(),gate:gateBody()}})],{{type:'application/json'}}));}}catch(e){{}}
}});

/* ---- experimental noise gate (breath between phrases) ----
   Decodes the same .review.m4a proxy via Web Audio (fetch + decodeAudioData,
   a throwaway AudioContext used only for decoding — never routed to
   destination, so it can't affect or be affected by <audio id=au>'s normal
   playback). From the raw samples: a per-10ms-window RMS-dB array, then a
   fixed-attack/release one-pole follower over it -> a 0..1 gain curve. Live
   preview just sets au.volume from that curve every animation frame (tick(),
   below) — no ScriptProcessor/AudioWorklet, no graph rewiring, so with the
   gate off this is 100% inert: same <audio> element, same playback path as
   before this existed. */
let GATE_ON = _ls.gate!==undefined ? !!_ls.gate : (GATE_DB_SAVED!==null);
let gateThreshold = _ls.gate!==undefined ? (_ls.gate?_ls.gate.threshold_db:-34) : (GATE_DB_SAVED!==null?GATE_DB_SAVED:-34);
let gateEnv=null, gateGainCurve=null;
const GATE_HOP=0.01;                        // seconds per analysis window
const gtEl=document.getElementById('gateTog'), thEl=document.getElementById('gateTh'),
      thV=document.getElementById('gateThV'), gStat=document.getElementById('gateStat');
gtEl.classList.toggle('on',GATE_ON); thEl.disabled=!GATE_ON;
thEl.value=gateThreshold; thV.textContent=gateThreshold.toFixed(1)+' dB';
async function ensureGateAnalysis(){{
  if(gateEnv) return gateEnv;
  gStat.textContent='analizando…';
  const Ctx=window.AudioContext||window.webkitAudioContext, ctx=new Ctx();
  try{{
    const buf=await fetch(au.currentSrc||au.src).then(r=>r.arrayBuffer()).then(b=>ctx.decodeAudioData(b));
    const ch=buf.getChannelData(0), hopN=Math.max(1,Math.round(buf.sampleRate*GATE_HOP));
    const n=Math.ceil(ch.length/hopN), dbs=new Float32Array(n);
    for(let i=0;i<n;i++){{
      let sum=0; const a=i*hopN, b2=Math.min(ch.length,a+hopN);
      for(let k=a;k<b2;k++) sum+=ch[k]*ch[k];
      dbs[i]=20*Math.log10(Math.max(1e-6,Math.sqrt(sum/Math.max(1,b2-a))));
    }}
    gateEnv={{dbs,n}};
  }}catch(err){{ gStat.textContent='⚠ no se pudo analizar el audio'; throw err; }}
  finally{{ try{{ctx.close();}}catch(e){{}} }}
  gStat.textContent='';
  return gateEnv;
}}
function gateGains(thresholdDb){{
  // one-pole attack/release follower — fixed 5ms/150ms, matches trim_talk.py's
  // GATE_ATTACK_MS/GATE_RELEASE_MS so the preview matches what --apply bakes in
  const {{dbs,n}}=gateEnv, gains=new Float32Array(n), hopMs=GATE_HOP*1000;
  const aA=Math.exp(-hopMs/5), aR=Math.exp(-hopMs/150), floor=0.03;   // agate ratio=20 ≈ same floor
  let g=1;
  for(let i=0;i<n;i++){{
    const target = dbs[i]>=thresholdDb ? 1 : floor;
    g = target + (g-target)*(target<g?aA:aR);
    gains[i]=g;
  }}
  return gains;
}}
function gateRebuild(){{ if(gateEnv){{ gateGainCurve=gateGains(gateThreshold); drawWave(); }} }}
function gateGainAt(t){{
  if(!gateGainCurve) return 1;
  return gateGainCurve[Math.min(gateGainCurve.length-1,Math.max(0,Math.round(t/GATE_HOP)))];
}}
gtEl.onclick=async()=>{{
  GATE_ON=!GATE_ON; gtEl.classList.toggle('on',GATE_ON); thEl.disabled=!GATE_ON;
  if(GATE_ON){{ try{{await ensureGateAnalysis(); gateRebuild();}}catch(e){{GATE_ON=false;gtEl.classList.remove('on');thEl.disabled=true;}} }}
  else {{ gateGainCurve=null; if(!au.paused) au.volume=1; drawWave(); }}
  save();
}};
thEl.oninput=()=>{{ gateThreshold=+thEl.value; thV.textContent=gateThreshold.toFixed(1)+' dB'; gateRebuild(); }};
thEl.onchange=save;                          // debounced save only once the drag settles
if(GATE_ON) ensureGateAnalysis().then(gateRebuild).catch(()=>{{}});

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
  if(gateGainCurve){{                // gate highlight first, under the waveform
    ctx.fillStyle='rgba(90,150,220,.30)';
    for(let px=0;px<vw;px++){{
      const t=(x0+px)/pps; if(t>TOTAL)break;
      if(gateGainAt(t)<0.5) ctx.fillRect(px,24,1,140);
    }}
  }}
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
  if(GATE_ON && gateGainCurve) au.volume=gateGainAt(t);
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
/* wheel: plain = pan the line (browse ahead without touching playback —
   this is a scroll listener, not a pointerdown one, so it was never at risk
   of the scrollbar-click-seeks bug), Ctrl/Cmd+wheel = zoom at the cursor */
scroll.addEventListener('wheel',e=>{{
  if(e.ctrlKey||e.metaKey){{
    e.preventDefault();
    const r=lane.getBoundingClientRect();
    const tAt=(e.clientX-r.left)/pps;
    pps=Math.max(1,Math.min(60,pps*(e.deltaY<0?1.18:1/1.18)));
    layout();
    scroll.scrollLeft=tAt*pps-(e.clientX-scroll.getBoundingClientRect().left);
  }} else {{
    e.preventDefault();
    const d=Math.abs(e.deltaX)>Math.abs(e.deltaY)?e.deltaX:e.deltaY;
    scroll.scrollLeft += d*(e.shiftKey?3:1)*(e.deltaMode===1?16:1);
  }}
}},{{passive:false}});
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
  const cuts=cutList(), gate=gateBody();
  const gateMsg = gate ? (' + gate a '+gate.threshold_db.toFixed(1)+'dB (respiración)') : '';
  if(!confirm(cuts.length+' cortes · quita '+fmt(cuts.reduce((a,c)=>a+c[1]-c[0],0))+gateMsg+'. ¿Guardar en cola? (la toma 4K se renderiza una vez, al Finalizar el stage)'))return;
  try{{
    const r=await fetch(API+'/trim',{{method:'POST',headers:{{'content-type':'application/json'}},
      body:JSON.stringify({{ep:EP,take:TAKE,cuts,gate}})}});
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
        write_review_html(take, words, cuts, total, missing, saved=saved, gate_db=load_gate(take))
        spawn_video_proxy(take)
        if missing is not None:
            write_pickups_json(take, missing)
        print(f"  página reconstruida ({len(cuts)} cortes propuestos"
              + (f", {len(saved)} guardados conservados" if saved else "") + ")")
        sys.exit(0)

    # ---- phase B: apply an approved cut list (+ any accepted pickups) ----
    if "--proxy" in a:
        with keep_awake():                   # decodes the whole 4K original: minutes
            ok = video_proxy(take)
        sys.exit(0 if ok else 1)

    if "--map" in a:                     # (re)write 09-cuts-map.json from cuts.json — no audio, no render
        _w, _sp, _pk, _g, _cl, _t = _plan(take)
        sys.exit(0 if write_cuts_map(take, build_timeline(_sp, _pk)[0]) else 1)

    if "--soft" in a:
        sys.exit(0 if soft_apply(take) else 1)

    if "--apply" in a:
        sig0 = _cuts_sig(take)
        words, spans, pickups, gate_db, cl, total = _plan(take)
        print(f"aplicar: {len(cl)} cortes · queda {sum(e - s for s, e in spans):.1f}s de {total:.1f}s"
              + (f" · {len(pickups)} pickup(s)" if pickups else "")
              + (f" · gate {gate_db:g}dB" if gate_db is not None else ""))
        out = take.with_suffix(".trimmed.mp4")
        _part(out).unlink(missing_ok=True)          # leftover of a killed render
        write_words_json(take, words, spans, pickups=pickups)
        with keep_awake():                   # tens of minutes of 4K: a 3 h idle-sleep stalled one
            ok = render(take, spans, out, pickups=pickups, gate_db=gate_db)
        if ok:
            write_cuts_map(take, build_timeline(spans, pickups)[0])
            if _cuts_sig(take) == sig0:
                pending_marker(take).unlink(missing_ok=True)
                (take.parent.parent / "09-cut-journal.json").unlink(missing_ok=True)   # baked: nothing left to undo
            else:
                print("  llegaron cortes nuevos durante el render — siguen pendientes")
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
    write_review_html(take, words, cuts, total, missing, saved=saved, gate_db=load_gate(take))
    spawn_video_proxy(take)             # ready before the first cut: the room's face plays from it
    if missing is not None:
        write_pickups_json(take, missing)

    if "--apply-now" in a:               # skip the review, render the auto plan
        pickups = load_accepted_pickups(take)
        if pickups:
            spans = keep_spans(_merge(cuts + [(p["orig_start"], p["orig_end"], "pickup") for p in pickups]), total)
        write_words_json(take, words, spans, pickups=pickups)
        ok = render(take, spans, take.with_suffix(".trimmed.mp4"), pickups=pickups, gate_db=load_gate(take))
        sys.exit(0 if ok else 1)
    print(f"\n{take.name}: {len(cuts)} cortes propuestos, quita {sum(e - s for s, e, _ in cuts):.1f} s"
          + (f" · {len(missing)} líneas del guion sin cobertura" if missing else ""))
    print(f"  revisa   episodes/{take.parent.parent.name}/assets/{take.with_suffix('.review.html').name}")
    print(f"  y pulsa «Aplicar corte» (o:  python tools/trim_talk.py {take} --apply)")
    sys.exit(0)
