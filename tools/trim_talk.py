#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trim_talk.py — trim silences + fillers from a recorded take (Stage 9, docs/16 move 1).

faster-whisper transcribes the take with word timestamps, then removes:
  - silence gaps longer than --gap (default 0.6 s), trimmed to ~2x --pad of room
  - standalone filler words from a Spanish list (unless --no-fillers)

Smooth, not aggressive: --pad (0.15 s) is kept around every retained span, a gap
under 0.40 s is never cut, and an 8 ms audio fade sits at each join.

Outputs:
  <take>.cuts.md      transcript with every cut marked + a summary
  <take>.trimmed.mp4  the cut take (re-encoded H.264 / AAC 320k)

Review loop: read <take>.cuts.md, protect any bad cut with --keep MM:SS, re-run.

Usage
  python tools/trim_talk.py TAKE.mp4 [--gap 0.6] [--pad 0.15] [--lang es]
        [--model medium|large-v3] [--no-fillers] [--keep MM:SS ...] [--dry]
"""
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MIN_GAP = 0.40           # never cut a pause shorter than this, whatever --gap says
FADE = 0.008             # audio fade at each join, seconds
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


def plan_cuts(words, gap, pad, do_fillers, keeps):
    """Return (cuts, kept_spans). cuts = [(start, end, reason)]."""
    cuts = []
    # silence between consecutive words
    for (s0, e0, _), (s1, e1, _) in zip(words, words[1:]):
        hole = s1 - e0
        if hole > max(gap, MIN_GAP):
            cut_s, cut_e = e0 + pad, s1 - pad
            if cut_e - cut_s > 0.05:
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
                cuts.append((s - pad / 2, e + pad / 2, f"filler «{n}»"))
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


def keep_spans(cuts, total):
    spans, t = [], 0.0
    for cs, ce, _ in cuts:
        if cs > t:
            spans.append((t, cs))
        t = ce
    if t < total:
        spans.append((t, total))
    return spans


def write_cuts_md(take, words, cuts, spans, total):
    out = [f"# Cortes — {take.name}", "",
           f"- cortes: **{len(cuts)}**  ·  quitado: **{sum(e - s for s, e, _ in cuts):.1f} s**  "
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
    take.with_suffix(".cuts.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"  escrito  {take.with_suffix('.cuts.md').name}")


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
    cmd = ["ffmpeg", "-y", "-i", str(take), "-/filter_complex", sp,
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


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    take = Path(a[0])
    if not take.is_file():
        sys.exit(f"no existe: {take}")

    def opt(name, d):
        return a[a.index(name) + 1] if name in a else d

    gap = float(opt("--gap", "0.6"))
    pad = float(opt("--pad", "0.15"))
    model_name = opt("--model", "medium")
    lang = opt("--lang", "es")
    do_fillers = "--no-fillers" not in a
    keeps = [secs(a[i + 1]) for i, x in enumerate(a) if x == "--keep"]

    words = transcribe(take, model_name, lang)
    if not words:
        sys.exit("whisper no devolvió palabras (¿audio mudo?)")
    total = words[-1][1] + 1.0
    cuts = plan_cuts(words, gap, pad, do_fillers, keeps)
    spans = keep_spans(cuts, total)
    print(f"\n{take.name}: {len(cuts)} cortes, quita {sum(e - s for s, e, _ in cuts):.1f} s\n")
    write_cuts_md(take, words, cuts, spans, total)
    if "--dry" in a:
        print("  --dry: no se renderiza. Revisa el .cuts.md y re-corre sin --dry.")
        sys.exit(0)
    ok = render(take, spans, take.with_suffix(".trimmed.mp4"))
    sys.exit(0 if ok else 1)
