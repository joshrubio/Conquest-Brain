#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clip_finder.py — Stage 7 Ensayo clip / still finder + extractor.
Protocol: brain/20-experimental-clip-protocol.md §4.1 (clips are the main
resource, stills + Ken Burns are the fallback), §4.6 (discovery vs. the
published excerpt), §6 (tooling).

Finds the moment in a work a `cita` beat needs, then cuts it: a short clip
by default, or a still when a beat is marked for the fallback (§4.1). Works
against a large local media file — search restricts itself to a window when
you give one, and extraction seeks before decoding either way, so a 2-hour
file costs the same as a 10-minute one.

Usage
  python tools/clip_finder.py E0XX-slug --init
      Scaffold episodes/E0XX-slug/07-cite.tsv from the `cita` rows of
      06-shotlist.md ("Timeline — la espina", tipo == cita). One row per
      beat: beat, obra, año, distribuidora, texto a buscar (la cita o una
      descripción de la escena), tipo (clip/still), dur (s, clip only),
      ventana (mm:ss-mm:ss, opcional — acota la búsqueda), timecode (opcional
      — si ya lo sabes, se salta la búsqueda para esa fila).

  python tools/clip_finder.py E0XX-slug [--media OBRA.mkv] [--subs OBRA.srt]
                               [--transcribe] [--lang es] [--model small]
                               [--clipcafe]
      Search. For every 07-cite.tsv row without a manual `timecode`:
        - with --subs: matches the row's search text against the subtitle
          file (SubRip .srt / WebVTT .vtt).
        - with --transcribe (no subs, or subs too thin): runs faster-whisper
          over the file — or just the row's `ventana` if it has one, so you
          don't transcribe a whole film for a single line.
        - with --clipcafe (or CLIPCAFE_API_KEY set in tools/.env — see
          --check-keys): also queries the clip.cafe API (transcript search
          over their indexed catalogue) — useful when you don't hold a local
          copy of the work at all. --media becomes optional in that case.
      Writes 07-cite-pass.html: up to 3 candidates per beat (local + clip.cafe
      mixed, each labelled with its source), a thumbnail where one exists,
      plus a manual-timecode field that always wins.

  python tools/clip_finder.py E0XX-slug --extract [--media OBRA.mkv]
      Read 07-cite-picks.txt (the picker's "Finalizar" button downloads it —
      save it into the episode folder). For each picked beat:
        - a **local** pick cuts with ffmpeg from --media: `tipo: clip` ->
          assets/cite/<beat>_<hhmmss>.mp4 (audio stripped, §4.2; capped at
          the row's `dur`); `tipo: still` -> assets/cite/<beat>_<hhmmss>.png.
        - a **clip.cafe** pick downloads the already-cut clip via the API,
          then still applies §4.2 (audio stripped) and the `dur` cap.
      Appends assets/CREDITS.md (noting the source — own copy or clip.cafe),
      writes 07-cite-selection.md.

  python tools/clip_finder.py --check-keys
      Report whether tools/.env has CLIPCAFE_API_KEY set.

Deps: ffmpeg (tools/mediabin.py); requests (only touched if --clipcafe is
used). faster-whisper only for --transcribe — the same engine
tools/trim_talk.py already uses for Stage 8 takes.

Discovery ≠ rights (brain/20 §4.6): whether the excerpt comes from your own
copy or from clip.cafe's API changes nothing about the fair-use analysis —
clip.cafe's own PRO page says as much ("for commercial use... you must ensure
you have proper rights"). A CLIPCAFE_API_KEY requires their paid PRO plan
(rate-limited: see https://clip.cafe/pro).
"""
import re
import subprocess
import sys
import tempfile
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mediabin import FFMPEG  # noqa: E402
from review_ui import page  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes"
ENV = Path(__file__).resolve().parent / ".env"
UA = "ConquestOficial/1.0 (educational documentary; contact joshuerubio@gmail.com)"
CITE_TSV = "07-cite.tsv"
PICKS_F = "07-cite-picks.txt"
PASS_HTML = "07-cite-pass.html"
SELECTION_MD = "07-cite-selection.md"
DEFAULT_CLIP_DUR = 8           # s — inside brain/20 §4.4's ~10 s ceiling
N_CANDIDATES = 3
CLIPCAFE_API = "https://api.clip.cafe/"

TSV_COLS = ["beat", "obra", "año", "distribuidora", "texto", "tipo", "dur",
            "ventana", "timecode"]


# ---------- tools/.env ----------

def load_env():
    keys = {}
    if ENV.exists():
        for line in ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            keys[k.strip()] = v.strip().strip('"').strip("'")
    return keys


def check_keys():
    k = load_env()
    print(f"tools/.env: {'found' if ENV.exists() else 'MISSING'}\n")
    v = k.get("CLIPCAFE_API_KEY", "")
    print(f"  {'OK ' if v else '  ·'} {'CLIPCAFE_API_KEY':22s} {'set' if v else '(not set — get one at https://clip.cafe/api-keys/, requires PRO)'}")


def _ep(slug):
    return EP_DIR / slug


# ---------- time helpers ----------

def parse_ts(s):
    """'1:02:03' | '12:03' | '743' | '12:03.500' -> seconds (float)."""
    s = (s or "").strip()
    if not s:
        return None
    parts = s.split(":")
    try:
        parts = [float(p) for p in parts]
    except ValueError:
        return None
    while len(parts) < 3:
        parts.insert(0, 0.0)
    h, m, sec = parts[-3:]
    return h * 3600 + m * 60 + sec


def fmt_ts(t):
    t = max(0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:05.2f}" if h else f"{int(m):02d}:{s:05.2f}"


def fmt_compact(t):
    """For filenames: 743.2 -> '0012m23s'."""
    t = max(0, int(round(t)))
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}h{m:02d}m{s:02d}s"


# ---------- Stage 6 shotlist -> 07-cite.tsv scaffold ----------

def _shotlist_cita_rows(slug):
    """Beats with tipo == cita in the '# | in | dur | sección | tipo | asset |
    rótulo | motion | marcador | guion (frag.)' spine table."""
    f = _ep(slug) / "06-shotlist.md"
    if not f.exists():
        sys.exit(f"no {f.relative_to(ROOT)} — corre Stage 6 primero")
    rows = []
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 10 or not cells[0].strip("-").isdigit():
            continue
        beat, tipo, frag = cells[0], cells[4], cells[9]
        if tipo.lower() == "cita":
            rows.append((beat, frag))
    return rows


def init_tsv(slug):
    ep = _ep(slug)
    out = ep / CITE_TSV
    rows = _shotlist_cita_rows(slug)
    if not rows:
        print(f"sin beats `tipo: cita` en 06-shotlist.md — nada que escalonar")
        return
    if out.exists():
        print(f"ya existe {out.relative_to(ROOT)} — no lo piso. Bórralo si quieres regenerarlo.")
        return
    lines = ["\t".join(TSV_COLS)]
    for beat, frag in rows:
        lines.append("\t".join([beat, "", "", "", frag.strip("«»"), "clip",
                                 str(DEFAULT_CLIP_DUR), "", ""]))
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"escrito  {out.relative_to(ROOT)}  ({len(rows)} beats)")
    print("rellena obra/año/distribuidora, y ventana si la sabes; luego --media")


def read_tsv(slug):
    f = _ep(slug) / CITE_TSV
    if not f.exists():
        sys.exit(f"no {f.relative_to(ROOT)} — corre --init primero")
    lines = [l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    header = [h.strip() for h in lines[0].split("\t")]
    rows = []
    for l in lines[1:]:
        cells = l.split("\t")
        cells += [""] * (len(header) - len(cells))
        rows.append(dict(zip(header, cells)))
    return rows


# ---------- subtitle parsing (SRT / VTT) ----------

SRT_BLOCK_RE = re.compile(
    r"(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})\n(.*?)(?=\n\n|\Z)",
    re.S)


def parse_subs(path):
    """-> [(start_s, end_s, text)], text = plain (tags/newlines collapsed)."""
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    raw = raw.replace("\r\n", "\n")
    out = []
    for m in SRT_BLOCK_RE.finditer(raw + "\n\n"):
        s, e, txt = m.group(1).replace(",", "."), m.group(2).replace(",", "."), m.group(3)
        txt = re.sub(r"<[^>]+>", "", txt)          # <i> etc.
        txt = re.sub(r"\{[^}]+\}", "", txt)         # {\an8} etc. (ASS-in-SRT)
        txt = " ".join(txt.split())
        if txt:
            out.append((parse_ts(s), parse_ts(e), txt))
    return out


# ---------- faster-whisper transcript (only for --transcribe) ----------

def transcribe_window(media, start, end, lang, model_name):
    """-> [(start_s, end_s, text)] segments, times already absolute (offset by
    `start`). Trims the window with ffmpeg first so a 2h file costs what the
    window costs, not the whole runtime."""
    from faster_whisper import WhisperModel
    tmp = None
    src = str(media)
    if start is not None or end is not None:
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        cmd = [FFMPEG, "-y"]
        if start:
            cmd += ["-ss", fmt_ts(start)]
        cmd += ["-i", str(media)]
        if end is not None:
            cmd += ["-t", fmt_ts(max(0.5, end - (start or 0)))]
        cmd += ["-ac", "1", "-ar", "16000", tmp.name]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("  ffmpeg (ventana) fallo:", r.stderr[-800:])
        else:
            src = tmp.name
    try:
        dev, ct = "cpu", "int8"
        try:
            import torch
            if torch.cuda.is_available():
                dev, ct = "cuda", "float16"
        except Exception:
            pass
        print(f"  whisper: {model_name} en {dev} ({ct}) …")
        model = WhisperModel(model_name, device=dev, compute_type=ct)
        segs, _ = model.transcribe(src, language=lang, word_timestamps=False,
                                    vad_filter=True)
        offset = start or 0
        return [(s.start + offset, s.end + offset, s.text.strip()) for s in segs]
    finally:
        if tmp:
            try:
                Path(tmp.name).unlink()
            except Exception:
                pass


# ---------- fuzzy matching ----------

def best_matches(query, segments, n=N_CANDIDATES):
    """segments = [(start,end,text)] -> top-n (score, start, text) by
    difflib similarity, query normalised (lowercase, no accents/punct)."""
    def norm(s):
        s = s.lower()
        s = re.sub(r"[«»\"'.,;:¡!¿?()\-]", " ", s)
        return " ".join(s.split())

    q = norm(query)
    scored = []
    for start, _end, text in segments:
        t = norm(text)
        if not t:
            continue
        r = SequenceMatcher(None, q, t).ratio()
        # reward a long shared word run even if lengths differ a lot
        common = SequenceMatcher(None, q, t).find_longest_match(0, len(q), 0, len(t))
        if common.size > 6:
            r = max(r, common.size / max(len(q), 1))
        scored.append((r, start, text))
    scored.sort(key=lambda x: -x[0])
    return scored[:n]


# ---------- clip.cafe API (search + download) ----------
# https://github.com/ClipCafe/clipcafe — requires a PRO subscription for the
# key (https://clip.cafe/api-keys/). Rate limits per their PRO plan: 10
# req/min, 2000 req + 1000 downloads/month. NOT wired into pull_assets.py
# (brain/12 §1c / brain/20 §4.6): discovery here is fine, but the download
# still only ever produces a `cita` asset, logged as fair use like any other
# manually-sourced excerpt — clip.cafe's own PRO page is explicit that a
# subscription is not a commercial licence.

def q_clipcafe(key, movie_title=None, transcript=None, n=N_CANDIDATES):
    """-> [dict] search hits, each with at least: title, slug, movie_title,
    movie_year, duration, download_url, transcript, poster. [] on any error
    or missing key — never raises, so a flaky/exhausted key just yields no
    clip.cafe candidates instead of breaking the local search path."""
    if not key:
        return []
    import requests
    params = {"api_key": key, "size": n}
    if movie_title:
        params["movie_title"] = movie_title
    if transcript:
        params["transcript"] = transcript
    try:
        r = requests.get(CLIPCAFE_API, params=params,
                          headers={"User-Agent": UA}, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  aviso: clip.cafe búsqueda falló ({e})")
        return []
    # response shape isn't pinned down against a live key — try the
    # documented Elasticsearch-style wrapper first, then a flat list.
    hits = []
    if isinstance(data, dict):
        hits = (data.get("hits") or {}).get("hits") or data.get("results") or data.get("data") or []
    elif isinstance(data, list):
        hits = data
    out = []
    for h in hits[:n]:
        src = h.get("_source", h) if isinstance(h, dict) else {}
        if not src:
            continue
        out.append({
            "title": src.get("title") or "",
            "slug": src.get("slug") or "",
            "movie_title": src.get("movie_title") or movie_title or "",
            "movie_year": src.get("movie_year") or "",
            "duration": src.get("duration") or "",
            "download_url": src.get("download") or "",
            "transcript": src.get("transcript") or "",
            "poster": src.get("movie_poster") or "",
        })
    return out


def download_clipcafe(hit, out_path):
    """Fetch a clip.cafe search hit's clip to `out_path`. -> (ok, msg)."""
    url = hit.get("download_url")
    if not url:
        return False, "el resultado de búsqueda no trae download_url"
    import requests
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
        r.raise_for_status()
    except Exception as e:
        return False, str(e)
    Path(out_path).write_bytes(r.content)
    return True, ""


# ---------- ffmpeg extraction ----------

def _seek_args(t, lead=2.0):
    """Fast+accurate seek: coarse -ss before -i, small fine -ss after -i."""
    coarse = max(0.0, t - lead)
    fine = t - coarse
    return coarse, fine


def grab_still(media, t, out_png):
    coarse, fine = _seek_args(t)
    cmd = [FFMPEG, "-y", "-ss", f"{coarse:.3f}", "-i", str(media),
           "-ss", f"{fine:.3f}", "-frames:v", "1", "-q:v", "2", str(out_png)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, r.stderr[-500:]


def cut_clip(media, t, dur, out_mp4):
    coarse, fine = _seek_args(t)
    cmd = [FFMPEG, "-y", "-ss", f"{coarse:.3f}", "-i", str(media),
           "-ss", f"{fine:.3f}", "-t", f"{dur:.2f}",
           "-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
           "-pix_fmt", "yuv420p", str(out_mp4)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, r.stderr[-500:]


def postprocess_download(raw_path, dur, out_mp4):
    """A clip.cafe download is already the right excerpt — just enforce §4.2
    (strip audio) and the row's duration cap, from the start of the file."""
    cmd = [FFMPEG, "-y", "-i", str(raw_path), "-t", f"{dur:.2f}",
           "-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
           "-pix_fmt", "yuv420p", str(out_mp4)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, r.stderr[-500:]


# ---------- search pass -> picker HTML ----------

def search(slug, media, subs, transcribe, lang, model_name, clipcafe_key=None):
    ep = _ep(slug)
    rows = read_tsv(slug)
    if not rows:
        sys.exit(f"{CITE_TSV} está vacío")
    if not media and not clipcafe_key:
        sys.exit("nada que buscar: da --media, o --clipcafe con CLIPCAFE_API_KEY en tools/.env")

    segments_full = parse_subs(subs) if subs else None
    if segments_full:
        print(f"subtítulos: {len(segments_full)} bloques")
    if clipcafe_key:
        print("clip.cafe: activado")

    cards = []
    thumb_cache = {}
    for row in rows:
        beat, texto = row["beat"], row["texto"]
        manual = parse_ts(row.get("timecode", ""))
        local_cand = []
        if manual is not None:
            local_cand = [(1.0, manual, "(timecode manual)")]
        elif media:
            win_start = win_end = None
            if row.get("ventana"):
                try:
                    a, b = row["ventana"].split("-")
                    win_start, win_end = parse_ts(a), parse_ts(b)
                except Exception:
                    pass
            segs = None
            if segments_full:
                segs = [s for s in segments_full
                        if win_start is None or (win_start - 5 <= s[0] <= (win_end or 1e9) + 5)]
            elif transcribe:
                segs = transcribe_window(media, win_start, win_end, lang, model_name)
            if segs:
                local_cand = best_matches(texto, segs)
        # thumbnails for each local candidate
        thumbs = []
        for score, t, text in local_cand:
            key = round(t, 1)
            if media and key not in thumb_cache:
                png = ep / "assets" / "cite" / f"_preview_{beat}_{key}.jpg"
                png.parent.mkdir(parents=True, exist_ok=True)
                ok, err = grab_still(media, t, png)
                thumb_cache[key] = png if ok else None
                if not ok:
                    print(f"  aviso: preview beat {beat} @ {fmt_ts(t)} fallo: {err}")
            thumbs.append((score, t, text, thumb_cache.get(key) if media else None))

        cc_hits = []
        if clipcafe_key and manual is None:
            cc_hits = q_clipcafe(clipcafe_key, movie_title=row.get("obra") or None,
                                  transcript=texto)
            if cc_hits:
                print(f"  clip.cafe: {len(cc_hits)} candidato(s) para beat {beat}")

        cards.append((row, thumbs, cc_hits))

    Path(ep / "assets" / "cite").mkdir(parents=True, exist_ok=True)
    (ep / PASS_HTML).write_text(_build_html(slug, cards), encoding="utf-8")
    print(f"escrito  episodes/{slug}/{PASS_HTML}  ({len(cards)} beats)")
    print(f"siguiente: ábrelo, elige o corrige el timecode, «Finalizar» descarga {PICKS_F}")


def _build_html(slug, cards):
    import base64
    import json as _json
    esc = lambda s: (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def thumb_img(png):
        if not png or not Path(png).exists():
            return '<div class="thumb ph">sin preview</div>'
        b64 = base64.b64encode(Path(png).read_bytes()).decode()
        return f'<img class="thumb" src="data:image/jpeg;base64,{b64}">'

    body = ['<section><h2>Búsqueda de citas — Ensayo <span>(' + str(len(cards)) + ')</span></h2>',
            '<p class="hint">Por beat: elige un candidato (local o clip.cafe) o escribe el timecode a mano '
            '(siempre gana — cuenta como local, contra <code>--media</code>). '
            '«tipo» clip/still y «dur» vienen de <code>07-cite.tsv</code>, editables aquí. '
            '<b>«Finalizar»</b> descarga <code>' + PICKS_F + '</code> — guárdalo en la carpeta del episodio '
            'y corre <code>--extract</code>.</p>',
            '<div class="grid wide">']
    for row, thumbs, cc_hits in cards:
        beat = esc(row["beat"])
        cc_json = esc(_json.dumps(cc_hits, ensure_ascii=False))
        body.append(f'<div class="card" data-beat="{beat}" data-clipcafe="{cc_json}">')
        body.append(f'<h3>Beat {beat} <span class="tag">{esc(row.get("tipo") or "clip")}</span></h3>')
        body.append(f'<div class="meta"><b>Obra:</b> {esc(row.get("obra"))} ({esc(row.get("año"))}) — {esc(row.get("distribuidora"))}'
                     f'<br><b>Buscado:</b> «{esc(row["texto"])}»</div>')
        any_cand = bool(thumbs or cc_hits)
        if any_cand:
            body.append('<div class="row" style="flex-wrap:wrap;gap:.5rem">')
            first = True
            for score, t, text, png in thumbs:
                checked = " checked" if first else ""
                first = False
                body.append(
                    f'<label class="opt" style="max-width:220px">'
                    f'<input type="radio" name="pick_{beat}" value="local|{t:.2f}"{checked}>'
                    f'{thumb_img(png)}<br><code>{fmt_ts(t)}</code> · {score:.2f} · local<br>'
                    f'<span style="font-size:.75rem">{esc(text[:80])}</span></label>')
            for i, h in enumerate(cc_hits):
                checked = " checked" if first else ""
                first = False
                poster = h.get("poster")
                thumb = (f'<img class="thumb" src="{esc(poster)}">' if poster
                         else '<div class="thumb ph">clip.cafe</div>')
                dur_lbl = f'{h.get("duration")}s' if h.get("duration") else "?"
                body.append(
                    f'<label class="opt" style="max-width:220px">'
                    f'<input type="radio" name="pick_{beat}" value="clipcafe|{i}"{checked}>'
                    f'{thumb}<br><code>clip.cafe</code> · {dur_lbl}<br>'
                    f'<span style="font-size:.75rem">{esc(h.get("movie_title"))} ({esc(str(h.get("movie_year")))})'
                    f' — «{esc((h.get("transcript") or "")[:80])}»</span></label>')
            body.append('</div>')
        else:
            body.append('<p class="empty">sin candidatos — usa el timecode manual</p>')
        body.append(
            f'<div class="row">'
            f'<label>Timecode manual <input type="text" class="tc" placeholder="mm:ss" value="{esc(row.get("timecode"))}"></label>'
            f'<label>Tipo <select class="tipo"><option{" selected" if row.get("tipo") != "still" else ""}>clip</option>'
            f'<option{" selected" if row.get("tipo") == "still" else ""}>still</option></select></label>'
            f'<label>Dur (s) <input type="number" class="dur" value="{esc(row.get("dur") or str(DEFAULT_CLIP_DUR))}" style="width:4rem"></label>'
            f'</div>')
        body.append('</div>')
    body.append('</div></section>')
    body_html = "\n".join(body)

    script = f"""
const cards=[...document.querySelectorAll('.card')];
document.getElementById('exp').onclick=()=>{{
  const L=['beat\\ttimecode\\ttipo\\tdur\\tfuente\\textra'];
  cards.forEach(c=>{{
    const beat=c.dataset.beat;
    const manual=c.querySelector('.tc').value.trim();
    const picked=(c.querySelector('input[type=radio]:checked')||{{}}).value||'';
    const tipo=c.querySelector('.tipo').value;
    const dur=c.querySelector('.dur').value;
    let tc='', fuente='local', extra='';
    if(manual){{ tc=manual; fuente='local'; }}
    else if(picked.startsWith('local|')){{ tc=picked.slice(6); fuente='local'; }}
    else if(picked.startsWith('clipcafe|')){{
      const idx=parseInt(picked.slice(9),10);
      const hits=JSON.parse(c.dataset.clipcafe||'[]');
      const h=hits[idx];
      if(h){{ tc='0'; fuente='clipcafe'; extra=h.download_url||''; }}
    }}
    if(tc!=='') L.push([beat,tc,tipo,dur,fuente,extra].join('\\t'));
  }});
  saveTxt('{PICKS_F}', L.join('\\n')+'\\n', 'Descargado. Guárdalo en episodes/{slug}/ y corre: python tools/clip_finder.py {slug} --extract');
}};
"""
    header = ('<h1>Citas — Ensayo</h1>'
              f'<button class="primary" id="exp">Finalizar</button>'
              '<a class="btn ghost spacer" href="http://localhost:8765/">Volver al panel</a>')
    return page(f"Citas — {slug}", header, body_html, script)


# ---------- extract ----------

def extract(slug, media=None):
    ep = _ep(slug)
    picks_f = ep / PICKS_F
    if not picks_f.exists():
        sys.exit(f"no {picks_f.relative_to(ROOT)} — corre la búsqueda primero y guarda el export del picker aquí")
    tsv_rows = {r["beat"]: r for r in read_tsv(slug)}
    lines = [l for l in picks_f.read_text(encoding="utf-8").splitlines() if l.strip()]
    header = lines[0].split("\t")
    needs_local = any(
        dict(zip(header, (l.split("\t") + [""] * len(header))[:len(header)])).get("fuente", "local") == "local"
        for l in lines[1:]
    )
    if needs_local and media is None:
        media_str = input("Ruta al archivo de la obra (la misma que usaste en --media): ").strip().strip('"')
        media = Path(media_str)
    if needs_local and not media.exists():
        sys.exit(f"no existe: {media}")

    out_dir = ep / "assets" / "cite"
    out_dir.mkdir(parents=True, exist_ok=True)
    credits, selection = [], []
    for l in lines[1:]:
        cells = l.split("\t")
        cells += [""] * (len(header) - len(cells))
        row = dict(zip(header, cells))
        beat = row["beat"]
        fuente = (row.get("fuente") or "local").strip().lower()
        tipo = (row.get("tipo") or "clip").strip().lower()
        meta = tsv_rows.get(beat, {})
        obra = meta.get("obra") or "(obra)"
        año = meta.get("año") or "?"
        dist = meta.get("distribuidora") or "?"

        if fuente == "clipcafe":
            url = row.get("extra") or ""
            if not url:
                print(f"  beat {beat}: pick de clip.cafe sin download_url — salto")
                continue
            dur = float(row.get("dur") or DEFAULT_CLIP_DUR)
            tmpf = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            tmpf.close()
            tmp = Path(tmpf.name)
            ok, err = download_clipcafe({"download_url": url}, tmp)
            if not ok:
                print(f"  FALLO  beat {beat}  descarga clip.cafe: {err}")
                continue
            out = out_dir / f"beat{beat}_clipcafe.mp4"
            ok, err = postprocess_download(tmp, dur, out)
            tmp.unlink(missing_ok=True)
            loc_label = "clip.cafe"
        else:
            t = parse_ts(row["timecode"])
            if t is None:
                print(f"  beat {beat}: timecode ilegible ({row['timecode']!r}) — salto")
                continue
            stamp = fmt_compact(t)
            if tipo == "still":
                out = out_dir / f"beat{beat}_{stamp}.png"
                ok, err = grab_still(media, t, out)
            else:
                dur = float(row.get("dur") or DEFAULT_CLIP_DUR)
                out = out_dir / f"beat{beat}_{stamp}.mp4"
                ok, err = cut_clip(media, t, dur, out)
            loc_label = fmt_ts(t)
        if not ok:
            print(f"  FALLO  beat {beat}  {err}")
            continue
        rel = f"assets/cite/{out.name}"
        print(f"  OK  beat {beat}  {tipo}  {loc_label}  -> {rel}")
        via = " — vía clip.cafe API (no es licencia, brain/20 §4.6)" if fuente == "clipcafe" else ""
        credits.append(f"- beat {beat}: cita — crítica/comentario (fair use) — "
                        f"«{obra}» ({año}, {dist}), {loc_label}{via} — `{rel}`")
        selection.append((beat, tipo, loc_label, obra, año, dist, rel))

    if credits:
        cf = ep / "assets" / "CREDITS.md"
        cf.parent.mkdir(parents=True, exist_ok=True)
        prev = cf.read_text(encoding="utf-8") if cf.exists() else "# Créditos de recursos\n"
        cf.write_text(prev.rstrip() + "\n" + "\n".join(credits) + "\n", encoding="utf-8")
        print(f"\ncréditos  → episodes/{slug}/assets/CREDITS.md")

    if selection:
        L = [f"# Selección de citas — Stage 7 · {slug}", "",
             f"> Generado por `clip_finder.py --extract` desde `{PICKS_F}`. "
             f"Pliega en `07-assets.md` (`brain/20 §4.7`).", "",
             "| Beat | Tipo | Timecode | Obra | Año | Distribuidora | Archivo |",
             "|------|------|----------|------|-----|----------------|---------|"]
        L += [f"| {b} | {ty} | {tc} | {o} | {a} | {d} | `{p}` |"
              for b, ty, tc, o, a, d, p in selection]
        (ep / SELECTION_MD).write_text("\n".join(L) + "\n", encoding="utf-8")
        print(f"selección → episodes/{slug}/{SELECTION_MD}")


# ---------- CLI ----------

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    if args[0] == "--check-keys":
        check_keys()
        return
    slug = args[0]
    if not (_ep(slug)).exists():
        sys.exit(f"no episodes/{slug}/")

    def opt(name, default=None):
        if name in args:
            i = args.index(name)
            return args[i + 1] if i + 1 < len(args) else default
        return default

    if "--init" in args:
        init_tsv(slug)
    elif "--extract" in args:
        media = opt("--media")
        extract(slug, Path(media) if media else None)
    elif "--media" in args or "--clipcafe" in args:
        media_opt = opt("--media")
        media = Path(media_opt) if media_opt else None
        if media and not media.exists():
            sys.exit(f"no existe: {media}")
        subs = opt("--subs")
        clipcafe_key = load_env().get("CLIPCAFE_API_KEY") if "--clipcafe" in args else None
        if "--clipcafe" in args and not clipcafe_key:
            sys.exit("--clipcafe pedido pero no hay CLIPCAFE_API_KEY en tools/.env (--check-keys)")
        search(slug, media, Path(subs) if subs else None,
               "--transcribe" in args, opt("--lang", "es"), opt("--model", "small"),
               clipcafe_key)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
