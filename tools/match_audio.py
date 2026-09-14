#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
match_audio.py — condition a pickup recording to sit next to the original take.

Not full acoustic room-matching (that's a much harder DSP problem — reverb,
noise-floor, mic coloring). What this actually does, honestly:

  1. Two-pass `loudnorm` so the pickup's overall loudness lands on the
     REFERENCE clip's own measured loudness (not a fixed broadcast target) —
     covers "same mic/room, different day/level", the common case.
  2. A gentle highpass (default 80 Hz) to knock down room rumble / handling
     noise the mic picked up that the original doesn't have.
  3. The operator's manual gain nudge from the pickup-room slider (dB),
     applied on top — automatic matching gets you close, the ear finishes it.
  4. A short fade in/out at the clip edges so the splice has no click.

Usage:
    python tools/match_audio.py --pickup rec.wav --ref clip.wav --out matched.wav
        [--gain -2.5] [--highpass 80] [--fade 0.03]

    python tools/match_audio.py --pickup rec.wav --ref TAKE.mp4 \\
        --ref-start 123.4 --ref-dur 5 --out matched.wav
        extracts the reference window from a bigger file (a take, or its
        .review.m4a proxy) first, at --ref-start for --ref-dur seconds.

Importable: match_and_render(pickup, ref, out, gain_db=0.0, ...) -> bool.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mediabin import FFMPEG, FFPROBE  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def probe_duration(path):
    """Container-level duration first; a webm straight out of the browser's
    MediaRecorder often has none (it's a live-recorded stream, not a properly
    finalised file with a duration in its header) — fall back to the audio
    stream's own duration, then to ffmpeg's own decode-time progress readout
    as a last resort, before giving up."""
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                        capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        pass
    r2 = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "a:0",
                        "-show_entries", "stream=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                        capture_output=True, text=True)
    try:
        return float(r2.stdout.strip())
    except ValueError:
        pass
    r3 = subprocess.run([FFMPEG, "-i", str(path), "-f", "null", "-"],
                        capture_output=True, text=True)
    times = re.findall(r"time=(\d+):(\d+):(\d+\.\d+)", r3.stderr)
    if times:
        h, m, s = times[-1]
        return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"ffprobe/ffmpeg no pudieron leer la duración de {path}:\n"
                        f"{r.stderr[-300:]}")


def extract_segment(src, start, dur, out_wav):
    """A short reference window from a bigger file (a take or its .review.m4a
    proxy) as mono 48k wav, ready to measure."""
    cmd = [FFMPEG, "-y", "-ss", f"{max(0.0, start):.3f}", "-t", f"{dur:.3f}",
           "-i", str(src), "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(out_wav)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not Path(out_wav).exists():
        raise RuntimeError(f"no se pudo extraer el segmento de referencia: {r.stderr[-400:]}")
    return out_wav


_LN_RE = re.compile(r"\{[^{}]*\"input_i\"[^{}]*\}", re.S)


def measure_loudness(path, I=-16.0, TP=-1.5, LRA=11.0):
    """Pass-1 loudnorm measurement — input_i/input_tp/input_lra/input_thresh
    for `path`, against the given target (only matters for `input_thresh`,
    which loudnorm derives relative to I)."""
    cmd = [FFMPEG, "-i", str(path), "-af",
           f"loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    m = _LN_RE.search(r.stderr)
    if not m:
        raise RuntimeError(f"loudnorm no pudo medir {path}:\n" + r.stderr[-500:])
    return json.loads(m.group(0))


def match_and_render(pickup, ref, out, gain_db=0.0, highpass_hz=80, fade=0.03):
    """Loudness-match `pickup` to `ref`'s own measured loudness, apply a
    highpass + the operator's manual gain, fade the edges, write `out` (wav).
    Returns True on success."""
    ref_m = measure_loudness(ref)
    I, TP, LRA = float(ref_m["input_i"]), float(ref_m["input_tp"]), float(ref_m["input_lra"])
    # loudnorm's own defaults reject a wildly quiet/loud target; clamp to its
    # accepted ranges rather than let ffmpeg silently fall back to -16 LUFS.
    I = max(-70.0, min(-5.0, I))
    LRA = max(1.0, min(20.0, LRA))
    TP = max(-9.0, min(0.0, TP))
    pk_m = measure_loudness(pickup, I=I, TP=TP, LRA=LRA)
    dur = probe_duration(pickup)
    fo = max(0.0, dur - fade)
    ln = (f"loudnorm=I={I}:TP={TP}:LRA={LRA}:"
          f"measured_I={pk_m['input_i']}:measured_TP={pk_m['input_tp']}:"
          f"measured_LRA={pk_m['input_lra']}:measured_thresh={pk_m['input_thresh']}:"
          f"linear=true")
    af = (f"highpass=f={highpass_hz},{ln},volume={gain_db}dB,"
          f"afade=t=in:st=0:d={fade},afade=t=out:st={fo:.3f}:d={fade}")
    cmd = [FFMPEG, "-y", "-i", str(pickup), "-af", af,
           "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not Path(out).exists():
        print("  FALLO ffmpeg (match_audio):\n" + "\n".join(r.stderr.strip().splitlines()[-6:]))
        return False
    print(f"  escrito  {Path(out).name}  (ref {I:.1f} LUFS · pickup medido {pk_m['input_i']} → ajustado"
          f"{f' {gain_db:+.1f} dB manual' if gain_db else ''})")
    return True


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or "-h" in a or "--help" in a:
        print(__doc__)
        sys.exit(0 if a else 2)

    def opt(name, d=None):
        return a[a.index(name) + 1] if name in a else d

    pickup = opt("--pickup")
    ref = opt("--ref")
    out = opt("--out")
    if not (pickup and ref and out):
        sys.exit("hacen falta --pickup, --ref y --out")
    gain = float(opt("--gain", "0"))
    highpass = float(opt("--highpass", "80"))
    fade = float(opt("--fade", "0.03"))

    ref_path = Path(ref)
    tmp_ref = None
    if opt("--ref-start") is not None:
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        tmp_ref = Path(tmp.name)
        extract_segment(ref_path, float(opt("--ref-start")), float(opt("--ref-dur", "5")), tmp_ref)
        ref_path = tmp_ref

    try:
        ok = match_and_render(Path(pickup), ref_path, Path(out), gain_db=gain,
                               highpass_hz=highpass, fade=fade)
    finally:
        if tmp_ref is not None:
            tmp_ref.unlink(missing_ok=True)
    sys.exit(0 if ok else 1)
