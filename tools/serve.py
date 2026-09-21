#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
serve.py — the local dashboard server. 127.0.0.1 only, no auth, your machine.

  python tools/serve.py          # http://localhost:8765

Serves the dashboard + every review page + the episode files, and turns
each review page's "Finalizar" button into: stash decisions -> fold the
gate (advance.py) -> regenerate the dashboard. No copy-paste, no chat.

Started by Conquest-Dashboard.bat, or by Claude in the background, or by you
in its own terminal (survives across sessions).
"""
import html as _h
import json
import os
import re
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline as P  # noqa: E402
import match_audio as MA  # noqa: E402
import pickup_room as PR  # noqa: E402


def _dir_html(d):
    import theme as T
    rel = d.relative_to(P.ROOT).as_posix()
    rows = []
    for p in sorted(d.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        name = p.name + ("/" if p.is_dir() else "")
        size = f"{p.stat().st_size:,} B" if p.is_file() else ""
        rows.append(f'<tr><td><a href="/{rel}/{p.name}">{name}</a></td>'
                    f'<td class="muted">{size}</td></tr>')
    body = ('<div class="doc"><table>'
            + ("".join(rows) or '<tr><td class="muted">carpeta vacía</td></tr>')
            + "</table></div>")
    header = f'<h1>{rel}</h1><a class="btn ghost spacer" href="/">Volver al panel</a>'
    return T.shell(rel, header, body).encode("utf-8")

TOOLS = Path(__file__).resolve().parent
MIME = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
        ".json": "application/json", ".txt": "text/plain; charset=utf-8",
        ".md": "text/plain; charset=utf-8", ".csv": "text/plain; charset=utf-8",
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
        ".gif": "image/gif", ".mp4": "video/mp4", ".webm": "video/webm", ".mov": "video/quicktime",
        ".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".ogg": "audio/ogg", ".wav": "audio/wav",
        ".ico": "image/x-icon"}


# child tools print unicode (→ « » é); force UTF-8 so a cp1252 console never
# crashes them, and decode their output the same way.
_ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}

# ThreadingHTTPServer runs each request in its own thread — two /pickup-accept
# calls landing close together must not race on the same accepted.json's
# read-modify-write (one accept's row silently clobbering the other's).
_PICKUP_ACCEPT_LOCK = threading.Lock()

# same hazard for 09-timeline.json: /beat-asset and /beat-op each write the
# client's full timeline snapshot, then shell out to a tool that does its own
# read-modify-write (beat_ops.py's _mint() included) — two edit-room clicks
# landing close together raced and minted the same beat id twice (E002, 2026-09-15).
class EditBusy(Exception):
    """Another timeline edit has held the lock too long for this one to wait."""


class _TimedLock:
    """The timeline-edit lock, but a waiter gives up after `wait` seconds and says what is
    holding it — instead of every later edit hanging silently behind one stuck operation
    (E002, 2026-09-20: a runaway asset change left «no acepta ningún cambio»)."""

    def __init__(self, wait=45.0):
        self._lock = threading.Lock()
        self.wait, self.what, self.since = wait, "", 0.0

    def __call__(self, what="edición"):
        outer = self

        class _Ctx:
            def __enter__(self):
                if not outer._lock.acquire(timeout=outer.wait):
                    held = int(time.time() - outer.since) if outer.since else 0
                    raise EditBusy(f"otra edición sigue en curso ({outer.what or 'desconocida'}, desde hace "
                                   f"{held} s) — reinténtalo en un momento")
                outer.what, outer.since = what, time.time()
                return self

            def __exit__(self, *exc):
                outer.what, outer.since = "", 0.0
                outer._lock.release()

        return _Ctx()


_TIMELINE_EDIT_LOCK = _TimedLock()
# an operation run while holding the lock must finish (or be killed) in bounded time
EDIT_OP_TIMEOUT = 120         # beat_ops / timeline rebuilds
ASSET_OP_TIMEOUT = 300        # beat_asset may download a stock video


BELOW_NORMAL = 0x00004000 if os.name == "nt" else 0       # BELOW_NORMAL_PRIORITY_CLASS, inherited by ffmpeg children
_HEAVY_TOOLS = {"kenburns.py", "make_graphics.py", "pull_assets.py", "trim_talk.py", "edit_review.py", "find_music.py"}


def _run(args, timeout=None):
    try:
        r = subprocess.run([sys.executable, str(TOOLS / args[0])] + args[1:],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=_ENV, timeout=timeout,
                           creationflags=BELOW_NORMAL if args[0] in _HEAVY_TOOLS else 0)
    except subprocess.TimeoutExpired:          # the child is killed by subprocess.run
        return json.dumps({"error": f"{args[0]} tardó más de {timeout:.0f} s y se canceló"},
                          ensure_ascii=False)
    return (r.stdout or r.stderr).strip()


def _spawn_chain(steps, done_flag=None, log=None, lock_file=None):
    """Run a list of [tool.py, *args] in sequence, detached — the HTTP response
    returns now, the work (a multi-minute render) continues in the background.
    On success writes `done_flag`; if a step exits non-zero (or is killed) it
    stops and writes `<done_flag>.fail` instead, so the UI can tell a crash from
    a completion. `log` (a Path) captures stdout+stderr of every step.
    `lock_file`, if given, is removed once the chain finishes either way — the
    caller creates it before spawning so a second request for the same take
    can refuse itself instead of racing this one's re-render."""
    py = (
        "import subprocess,sys,pathlib\n"
        f"S={steps!r}\n"
        f"T={str(TOOLS)!r}\n"
        f"LOG={str(log)!r} if {log is not None} else None\n"
        "fh=open(LOG,'w',encoding='utf-8',errors='replace') if LOG else subprocess.DEVNULL\n"
        "ok=True\n"
        "for s in S:\n"
        "    r=subprocess.run([sys.executable, str(pathlib.Path(T)/s[0]), *s[1:]],"
        " stdout=fh, stderr=subprocess.STDOUT)\n"
        "    if r.returncode != 0: ok=False; break\n"
        "if LOG: fh.close()\n"
        + (f"pathlib.Path({str(done_flag)!r} + ('' if ok else '.fail')).write_text('ok' if ok else 'fail')\n"
           if done_flag else "")
        + (f"pathlib.Path({str(lock_file)!r}).unlink(missing_ok=True)\n" if lock_file else "")
    )
    # Detached from serve.py: a chain used to be its CHILD, so restarting the server (Ctrl+C in its console,
    # closing the window) killed an hours-long render with it (E002's 4K master).
    flags = (0x00000008 | 0x00000200 | BELOW_NORMAL) if os.name == "nt" else 0   # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | below normal
    return subprocess.Popen([sys.executable, "-c", py], cwd=str(TOOLS.parent), env=_ENV, creationflags=flags,
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ── queued trim: cuts are cheap to save, the 4K render runs once ──────────
# «Aplicar corte» / an edit-room audio cut only queue their cuts: trim_talk.py
# --soft (≈30 s, audio only) refreshes words.json + the room's 09-vo.m4a and
# leaves <take>.render.pending. The heavy trim_talk --apply runs once, on
# «Finalizar» (/timeline) or the room's «Renderizar ahora» (/trim-render), and
# assemble.py --rough/--final run it themselves if it's still pending.
_SOFT = {"lock": threading.Lock(), "dirty": False, "running": False}


def _take_of(epp):
    """The ORIGINAL take — the one with a transcript. The trimmed 4K can be stale
    or absent while cuts are queued, so it can't be used to find the take."""
    raws = sorted((epp / "assets").glob("*.words.raw.json"))
    return epp / "assets" / raws[0].name.replace(".words.raw.json", ".mp4") if raws else None


def _soft_apply_async(epp, take, slug, resync=False):
    """Queue a refresh of words.json + 09-vo.m4a for the take's CURRENT
    cuts.json. Runs in a thread; requests arriving while it runs are coalesced
    (the job loops once more and reads the latest cuts.json)."""
    with _SOFT["lock"]:
        _SOFT["dirty"] = True
        if _SOFT["running"]:
            return
        _SOFT["running"] = True

    def work():
        while True:
            with _SOFT["lock"]:
                if not _SOFT["dirty"]:
                    _SOFT["running"] = False
                    return
                _SOFT["dirty"] = False
            try:
                r = subprocess.run([sys.executable, str(TOOLS / "trim_talk.py"), str(take), "--soft"],
                                   capture_output=True, text=True, encoding="utf-8",
                                   errors="replace", env=_ENV)
                if r.returncode == 0:
                    if resync:
                        (epp / "09-resync.flag").write_text("re-trim", encoding="utf-8")
                    _run(["assemble.py", slug, "--wave"])
                    try:
                        with _TIMELINE_EDIT_LOCK("regenerar la sala"):
                            _run(["edit_timeline.py", slug], timeout=EDIT_OP_TIMEOUT)
                    except EditBusy:
                        pass                       # only the page copy is stale; the next edit regenerates it
                    _run(["dash.py"])
            except Exception:                 # never leave "running" stuck on a crash
                pass

    threading.Thread(target=work, daemon=True).start()


def _soft_wait(timeout=240):
    """Block until the audio refresh (and anything coalesced behind it) is done.
    Only call this OUTSIDE _TIMELINE_EDIT_LOCK — the job takes that lock itself."""
    import time
    end = time.time() + timeout
    while time.time() < end:
        with _SOFT["lock"]:
            if not _SOFT["running"] and not _SOFT["dirty"]:
                return True
        time.sleep(0.4)
    return False


def _start_hard_render(epp, take, slug):
    """Start the queued 4K trim (+ proxy refresh) in the background. Returns
    'none' (nothing pending), 'running' (already going), 'busy' (the audio
    refresh is still writing — retry in a moment) or 'started'."""
    lock_f = take.with_suffix(".apply.lock")
    if P.lock_alive(lock_f):
        return "running"
    if not take.with_suffix(".render.pending").exists():
        return "none"
    if _SOFT["running"]:
        return "busy"
    flag = take.with_suffix(".apply.done")
    flag.unlink(missing_ok=True)
    lock_f.write_text("1", encoding="utf-8")
    proc = _spawn_chain([["trim_talk.py", str(take), "--apply"],
                         ["assemble.py", slug], ["edit_timeline.py", slug],
                         ["dash.py"]], done_flag=flag, lock_file=lock_f)
    lock_f.write_text(str(proc.pid), encoding="utf-8")     # so a stale lock can be told from a live one
    return "started"


_HARD_MSG = {
    "started": "renderizando la toma recortada en segundo plano (varios minutos)",
    "running": "la toma recortada ya se está renderizando en segundo plano",
    "busy": "el audio de la sala aún se está actualizando — inténtalo en unos segundos",
    "none": "no hay cortes pendientes de renderizar",
}


def _pool_detail(txt, iid):
    """The `### T0X-YY …` detail block for an idea, or ''."""
    m = re.search(rf"(?sm)^### {re.escape(iid)}\b.*?(?=^### |\Z)", txt)
    return m.group(0) if m else ""


def _pool_hooks(txt, iid):
    return re.findall(r"^-\s+`([^`]+)`", _pool_detail(txt, iid), re.M)


def _pool_set_status(txt, iid, new):
    """Rewrite the Estado cell of the summary-table row for iid."""
    return re.sub(rf"(\|\s*{re.escape(iid)}\s*\|(?:[^|\n]*\|){{5}})\s*[^|\n]*(\|)",
                  rf"\1 {new} \2", txt, count=1)


def _pool_set_hook(txt, iid, idx):
    """Record the chosen hook-title as a `- **Hook elegido:** ...` line in the detail block."""
    try:
        chosen = _pool_hooks(txt, iid)[int(idx) - 1]
    except (ValueError, IndexError, TypeError):
        return txt
    block = _pool_detail(txt, iid)
    if not block:
        return txt
    line = f"- **Hook elegido:** `{chosen}`"
    if re.search(r"(?m)^-\s+\*\*Hook elegido:\*\*.*$", block):
        nb = re.sub(r"(?m)^-\s+\*\*Hook elegido:\*\*.*$", line, block, count=1)
    else:
        hk = list(re.finditer(r"(?m)^-\s+`[^`]+`[^\n]*$", block))
        if not hk:
            return txt
        pos = hk[-1].end()
        nb = block[:pos] + "\n" + line + block[pos:]
    return txt.replace(block, nb, 1)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", "*")
        # everything here is regenerated on the fly — never let the browser
        # serve a cached page after a restyle / rebuild
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(b)

    UPLOAD_MAX = 2 * 1024 * 1024 * 1024   # 2 GB — a raw 4K still/clip fits, a mistaken pick doesn't hang the box
    UPLOAD_SUBDIRS = {"custom", "ai", "music"}

    def _upload(self, qs):
        """«Examinar…» buttons in 07-style-pass.html: saves a local file the
        user picked straight into the episode's assets/ (no filesystem path
        ever needed in the browser — that's what makes this necessary; JS
        can't read a real local path from <input type=file>, only its bytes).
        Returns the relative path the style-pass JS drops into that beat's
        «recurso propio» input, same as if it had been typed by hand."""
        ep = (qs.get("ep") or [""])[0]
        name = (qs.get("name") or ["archivo"])[0]
        sub = (qs.get("sub") or ["custom"])[0]
        if sub not in self.UPLOAD_SUBDIRS:
            sub = "custom"
        n = int(self.headers.get("Content-Length", 0) or 0)
        epp = P.ep_path(ep)
        if not ep or not epp.is_dir():
            return self._send(404, json.dumps({"error": f"episodio «{ep}» no encontrado"}))
        if n <= 0 or n > self.UPLOAD_MAX:
            return self._send(400, json.dumps({"error": "tamaño de archivo inválido (0 o > 2 GB)"}))
        body = self.rfile.read(n)
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", unquote(name)).lstrip(".") or "archivo"
        dst_dir = epp / "assets" / sub
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst, i = dst_dir / safe, 1
        while dst.exists():
            dst = dst_dir / f"{Path(safe).stem}_{i}{Path(safe).suffix}"
            i += 1
        dst.write_bytes(body)
        rel = f"assets/{sub}/{dst.name}"
        return self._send(200, json.dumps({"ok": True, "path": rel,
                                           "size_mb": round(len(body) / (1024 * 1024), 1)}))

    RECORD_UPLOAD_MAX = 8 * 1024 * 1024 * 1024   # 8 GB — a raw talking-head take runs bigger than a style-pass asset

    def _record_upload(self, qs):
        """Stage 8's upload dialog («Ver más» on its stage-strip tile): saves
        the picked take straight into the episode's assets/ as <EPID>-vo.<ext>
        — the name every later tool (trim_talk.py, assemble.py --seed) expects
        — then folds the gate the same way «Marcar hecho» (/human) does and
        advances straight to Stage 9. One click, no filesystem path typed."""
        ep = (qs.get("ep") or [""])[0]
        name = (qs.get("name") or ["toma.mp4"])[0]
        n = int(self.headers.get("Content-Length", 0) or 0)
        epp = P.ep_path(ep)
        if not ep or not epp.is_dir():
            return self._send(404, json.dumps({"error": f"episodio «{ep}» no encontrado"}))
        if n <= 0 or n > self.RECORD_UPLOAD_MAX:
            return self._send(400, json.dumps({"error": "tamaño de archivo inválido (0 o > 8 GB)"}))
        body = self.rfile.read(n)
        ext = Path(unquote(name)).suffix.lower()
        if ext not in (".mp4", ".mov", ".webm", ".mkv", ".avi"):
            ext = ".mp4"
        dst_dir = epp / "assets"
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / f"{ep}-vo{ext}"
        replaced = dst.exists()
        dst.write_bytes(body)
        P.set_ep(ep, gate="firmado")
        msg = _run(["advance.py", "next", ep])
        note = f"{dst.name} guardado" + (" (reemplazó una toma anterior)" if replaced else "")
        return self._send(200, json.dumps({"ok": True,
            "msg": f"{note} · {round(len(body) / (1024 * 1024))} MB · {msg}"}))

    PICKUP_UPLOAD_MAX = 500 * 1024 * 1024   # 500 MB — one short pickup line, generous ceiling
    PICKUP_CTYPE_EXT = {"audio/webm": ".webm", "video/webm": ".webm", "audio/wav": ".wav",
                         "audio/x-wav": ".wav", "audio/mp4": ".m4a", "video/mp4": ".mp4",
                         "audio/mpeg": ".mp3", "audio/ogg": ".ogg"}

    def _pickup_accept(self, qs):
        """pickup_room.py's «Aceptar»: saves the raw pickup recording/upload,
        extracts the matching reference window from <take>.review.m4a, runs
        match_audio.py (loudness match to that reference + highpass + the
        operator's manual gain), and records the result in
        <take>.pickups.accepted.json. Doesn't render the take itself — that
        happens next time it's (re)applied: trim_talk.py --apply already
        folds in whatever's in that file (brain/16's existing «Re-sincronizar»
        flow after any re-trim applies here unchanged)."""
        ep = (qs.get("ep") or [""])[0]
        take_name = (qs.get("take") or [""])[0]
        try:
            idx = int((qs.get("idx") or ["-1"])[0])
            start = float((qs.get("start") or ["0"])[0])
            end = float((qs.get("end") or ["0"])[0])
            gain = float((qs.get("gain") or ["0"])[0])
        except ValueError:
            return self._send(400, json.dumps({"error": "start/end/gain/idx inválidos"}))
        text = (qs.get("text") or [""])[0]  # parse_qs already percent-decodes — don't unquote() again
        epp = P.ep_path(ep)
        take = epp / "assets" / take_name
        if not ep or not epp.is_dir() or not take.is_file():
            return self._send(404, json.dumps({"error": f"toma «{take_name}» no encontrada para «{ep}»"}))
        if idx < 0:
            return self._send(400, json.dumps({"error": "falta idx (qué pickup de la lista es)"}))
        if end <= start:
            return self._send(400, json.dumps({"error": "la región (start/end) está vacía o invertida"}))
        ref_proxy = take.with_suffix(".review.m4a")
        if not ref_proxy.is_file():
            return self._send(409, json.dumps({
                "error": "falta el proxy de audio de la toma — corre trim_talk.py --script primero"}))

        n = int(self.headers.get("Content-Length", 0) or 0)
        if n <= 0 or n > self.PICKUP_UPLOAD_MAX:
            return self._send(400, json.dumps({"error": "grabación vacía o demasiado grande (> 500 MB)"}))
        body = self.rfile.read(n)
        ctype = self.headers.get("Content-Type", "").split(";")[0].strip()
        ext = self.PICKUP_CTYPE_EXT.get(ctype, ".webm")

        pick_dir = epp / "assets" / "pickups"
        pick_dir.mkdir(parents=True, exist_ok=True)
        stem = take.stem
        raw = pick_dir / f"{stem}_pick{idx:02d}.raw{ext}"
        raw.write_bytes(body)
        matched = pick_dir / f"{stem}_pick{idx:02d}.matched.wav"
        tmp_ref = pick_dir / f"_ref_pick{idx:02d}.wav"
        try:
            MA.extract_segment(ref_proxy, start, end - start, tmp_ref)
            ok = MA.match_and_render(raw, tmp_ref, matched, gain_db=gain)
        except Exception as e:
            return self._send(500, json.dumps({"error": f"match_audio falló: {e}"}))
        finally:
            tmp_ref.unlink(missing_ok=True)
        if not ok:
            return self._send(500, json.dumps({"error": "ffmpeg no pudo ajustar el audio del pickup"}))

        acc_f = take.with_suffix(".pickups.accepted.json")
        # identity is the sentence TEXT, not `idx` — `idx` is just a position in
        # whatever <take>.pickups.json looked like when this page was built, and
        # a later --script/--rebuild-page re-run can renumber or reorder that
        # list. Keying on text keeps "did we already accept THIS line" correct
        # even after a reorder, and the lock keeps two near-simultaneous accepts
        # (two different lines) from clobbering each other's row.
        with _PICKUP_ACCEPT_LOCK:
            data = json.loads(acc_f.read_text(encoding="utf-8")) if acc_f.is_file() else {"pickups": []}
            rows = [p for p in data.get("pickups", []) if p.get("text", "").strip() != text.strip()]
            rows.append({"idx": idx, "text": text, "orig_start": round(start, 3), "orig_end": round(end, 3),
                         "dur": round(end - start, 3), "audio": f"pickups/{matched.name}",
                         "gain_db": gain, "accepted_ts": int(time.time())})
            rows.sort(key=lambda p: p["idx"])
            acc_f.write_text(json.dumps({"pickups": rows}, ensure_ascii=False, indent=1), encoding="utf-8")

        (epp / "09-resync.flag").write_text("pickup", encoding="utf-8")
        # off the response path — the client already patched its own badge, this
        # is only so a *later* page load (a fresh reload, a different session)
        # shows the accepted state too. A long take's word list makes this slow
        # enough that the operator shouldn't wait on it between accepts.
        threading.Thread(target=PR.build, args=(take,), daemon=True).start()
        return self._send(200, json.dumps({"ok": True,
            "msg": f"pickup {idx + 1} listo — se integra en la próxima «Aplicar corte» de esta toma "
                   f"(trim_talk.py --apply ya lo incluye solo)."}))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        raw = self.path
        path = unquote(raw.split("?")[0])
        qs = parse_qs(raw.split("?")[1]) if "?" in raw else {}
        if path in ("/", "/dashboard.html"):
            _run(["dash.py"])
            f = P.ROOT / "dashboard.html"
            return self._send(200, f.read_bytes(), MIME[".html"])
        if path == "/state":
            return self._send(200, json.dumps(P.read_queue(), ensure_ascii=False))
        if path == "/vo-version":
            # the room's audio file is replaced on disk after a cut / a hard render; the page polls
            # this and swaps its <audio> source itself (an <audio> that loaded part of the old file
            # dies on its next range request — the total size changed). `running` = a refresh is in flight.
            epp = P.ep_path(qs.get("ep", [""])[0])
            f = epp / "09-vo.m4a"
            take = _take_of(epp)
            running = bool(_SOFT["running"] or _SOFT["dirty"]) or \
                bool(take and P.lock_alive(take.with_suffix(".apply.lock")))
            return self._send(200, json.dumps({"ver": str(f.stat().st_mtime_ns) if f.exists() else "",
                                               "running": running}))
        if path == "/timeline-backups":
            epp = P.ep_path(qs.get("ep", [""])[0])
            out = []
            for f in sorted(epp.glob("09-timeline.*.*.bak.json"), reverse=True):
                m = re.match(r"09-timeline\.(\d+)\.(reseed|resync)\.bak\.json$", f.name)
                if not m:
                    continue
                import datetime
                when = datetime.datetime.fromtimestamp(int(m.group(1))).strftime("%d %b %H:%M")
                out.append({"name": f.name, "kind": m.group(2), "when": when})
            return self._send(200, json.dumps(out, ensure_ascii=False))

        if path in ("/rough-progress", "/final-progress"):
            stem = "09-rough" if path == "/rough-progress" else "09-final"
            epp = P.ep_path(qs.get("ep", [""])[0])
            done = (epp / f"{stem}.done").exists()
            failed = (epp / f"{stem}.done.fail").exists()
            prg = epp / f"{stem}.progress"
            pct = 100 if done else 0
            if prg.exists() and not done and not failed:
                try:
                    us = re.findall(r"out_time_us=(\d+)", prg.read_text(encoding="utf-8", errors="replace"))
                    tot = (json.loads((epp / "09-timeline.json").read_text(encoding="utf-8")).get("total") or 1) * 1e6
                    if us:
                        pct = max(1, min(99, round(int(us[-1]) / tot * 100)))
                except Exception:
                    pass
            running = prg.exists() and not done and not failed
            return self._send(200, json.dumps(
                {"pct": pct, "done": done, "running": running, "failed": failed}))
        if path == "/view":
            return self._view(qs.get("ep", [""])[0], qs.get("f", [""])[0])
        f = (P.ROOT / path.lstrip("/")).resolve()
        if P.ROOT in f.parents:
            if f.is_dir():
                return self._send(200, _dir_html(f), MIME[".html"])
            if f.is_file():
                return self._send_file(f)
        self._send(404, json.dumps({"error": "not found", "path": path}))

    def _send_file(self, f):
        """Serve a file, honouring a Range request — <audio>/<video> need
        Accept-Ranges + 206 or the browser makes them unseekable."""
        ctype = MIME.get(f.suffix, "application/octet-stream")
        size = f.stat().st_size
        rng = self.headers.get("Range", "")
        m = re.match(r"bytes=(\d*)-(\d*)", rng) if rng else None
        if m and (m.group(1) or m.group(2)):
            a = int(m.group(1)) if m.group(1) else max(0, size - int(m.group(2)))
            b = int(m.group(2)) if m.group(1) and m.group(2) else size - 1
            b = min(b, size - 1)
            a = min(a, b)
            with open(f, "rb") as fh:
                fh.seek(a)
                chunk = fh.read(b - a + 1)
            self.send_response(206)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Range", f"bytes {a}-{b}/{size}")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(len(chunk)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(chunk)
            return
        b = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(b)

    def _view(self, epid, fname):
        import dash
        ep = P.ep_path(epid)
        target = (ep / fname) if not fname.startswith(("ideas/", "brain/")) else (P.ROOT / fname)
        target = target.resolve()
        if P.ROOT not in target.parents or not target.is_file():
            f, ei = _h.escape(fname), _h.escape(epid)
            inner = (f"<p>El fichero <code>{f}</code> aún no existe para <b>{ei}</b> — "
                     "ese stage todavía no se ha generado. Vuelve cuando el episodio llegue ahí.</p>")
            return self._send(200, dash.view_page(f"{ei} · {f}", inner), MIME[".html"])
        md = target.read_text(encoding="utf-8")
        P.ensure_assets(epid)
        assets_url = f"/episodes/{ep.name}/assets/"
        html = dash.view_page(f"{epid} · {fname}", dash.md_to_html(md), assets_url)
        self._send(200, html, MIME[".html"])

    def do_POST(self):
        try:
            return self._do_POST()
        except EditBusy as e:                  # a stuck edit holds the lock: say so, don't hang
            return self._send(503, json.dumps({"error": str(e)}, ensure_ascii=False))

    def _do_POST(self):
        raw_path = self.path
        path = raw_path.split("?")[0]

        if path in ("/upload", "/record-upload", "/pickup-accept"):
            # a "browse..." button's file picker, or a pickup-room recording:
            # the body IS the file's raw bytes (fetch(url, {method:'POST',
            # body: file/blob})) — not JSON, so this has to be handled before
            # the generic JSON read below.
            qs = parse_qs(raw_path.split("?", 1)[1]) if "?" in raw_path else {}
            if path == "/record-upload":
                return self._record_upload(qs)
            if path == "/pickup-accept":
                return self._pickup_accept(qs)
            return self._upload(qs)

        n = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, json.dumps({"error": "bad json"}))
        ep = data.get("ep")

        if path == "/picks":
            # Stage 7 asset picks aren't a pipeline gate — they're inputs Stage 9
            # consumes. Write 07-picks.txt + run --download, whatever stage the
            # episode is at (re-picking after advancing is normal).
            epp = P.ep_path(ep)
            txt = (data.get("payload") or {}).get("txt") or data.get("txt", "")
            if not txt:
                return self._send(400, json.dumps({"error": "sin picks"}))
            pk = epp / "07-picks.txt"
            if pk.exists():                     # the page rewrites this file from what is ticked in THIS browser
                (epp / "07-picks.previous.txt").write_bytes(pk.read_bytes())   # so keep the last version recoverable
            pk.write_text(txt, encoding="utf-8")
            slug = P.read_status().get(ep, {}).get("slug") or ep
            msg = _run(["pull_assets.py", slug, "--download"], timeout=900)
            _run(["dash.py"])
            return self._send(200, json.dumps({"ok": True,
                "msg": "07-picks.txt guardado · " + (msg.splitlines()[-1] if msg else "descarga hecha")}))

        if path == "/finish":
            stage = int(data.get("stage"))
            payload = data.get("payload", data)
            epp = P.ep_path(ep)
            edir = epp / "_exports"
            edir.mkdir(parents=True, exist_ok=True)
            (edir / f"stage{stage:02d}.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
            # content is always saved, even if the stage/gate bump below gets
            # blocked — an edit is never lost just because this review page
            # turned out to be stale.
            canon = P.STAGE.get(stage, {}).get("export")
            if canon and payload.get("txt"):
                (epp / canon).write_text(payload["txt"], encoding="utf-8")
            if stage == 1 and payload.get("brief_md"):
                (epp / "01-brief.md").write_text(payload["brief_md"], encoding="utf-8")
            if stage == 4 and payload.get("script_md"):
                (epp / "05-script.md").write_text(payload["script_md"], encoding="utf-8")

            # guard against reopening a stage the episode already moved past
            # (e.g. an old 05-script.html tab still open after Stage 5 ran) —
            # that would silently regress _STATUS.md. Require an explicit
            # confirmation (payload.reopen) first; the content above is still
            # saved either way.
            cur_stage = P.read_status().get(ep, {}).get("stage", stage)
            if stage < cur_stage and not payload.get("reopen"):
                return self._send(409, json.dumps({
                    "error": "stage_behind", "cur_stage": cur_stage, "stage": stage,
                    "msg": (f"Guardado. Pero este episodio ya está en Stage {cur_stage} — "
                            f"cerrar el gate aquí reabre el Stage {stage} y falta revisar de nuevo "
                            f"los Stages {stage + 1}–{cur_stage}. ¿Reabrir de todas formas?")}))
            notes = (f"⚠ Stage {stage} reabierto — revisar de nuevo Stage {stage + 1}–{cur_stage}"
                     if stage < cur_stage else None)
            P.set_ep(ep, stage=stage, gate="exportado", **({"notes": notes} if notes else {}))
            msg = _run(["advance.py", "fold", ep])
            return self._send(200, json.dumps({"ok": True, "msg": msg}))

        if path == "/trim-save":
            # autosave from the trim room — write <take>.cuts.json, render nothing.
            epp = P.ep_path(ep)
            take = epp / "assets" / data.get("take", "")
            if not take.is_file():
                return self._send(404, json.dumps({"error": "toma no encontrada"}))
            take.with_suffix(".cuts.json").write_text(
                json.dumps({"cuts": data.get("cuts", [])}, ensure_ascii=False), encoding="utf-8")
            return self._send(200, json.dumps({"ok": True}))

        if path == "/trim":
            # <take>.review.html «Aplicar corte»: write the approved cut list,
            # render the trimmed take + refresh the edit-room proxies. It does
            # NOT re-fit the timeline — the room shows «Re-sincronizar» and the
            # editor chooses when (the schema-2 line is authored, brain/16).
            epp = P.ep_path(ep)
            take_name = data.get("take", "")
            take = epp / "assets" / take_name
            if not take.is_file():
                return self._send(404, json.dumps({"error": f"no existe la toma {take_name}"}))
            if P.lock_alive(take.with_suffix(".apply.lock")):
                return self._send(409, json.dumps({
                    "error": "la toma se está renderizando ahora mismo (Finalizar) — espera a que termine"}))
            cuts = data.get("cuts", [])
            take.with_suffix(".cuts.json").write_text(
                json.dumps({"cuts": cuts}, ensure_ascii=False), encoding="utf-8")
            slug = P.read_status().get(ep, {}).get("slug") or ep
            (epp / "09-cut-journal.json").unlink(missing_ok=True)   # whole list replaced: old undo points no longer apply
            # queue, don't render: the 4K trim runs once when the stage is finalized
            _soft_apply_async(epp, take, slug, resync=True)
            return self._send(200, json.dumps({"ok": True,
                "msg": f"{len(cuts)} cortes guardados en cola.\n\n"
                       f"El audio de la sala se actualiza en ~30 s. La toma 4K se renderiza una sola vez, "
                       f"al Finalizar el stage (o con «Renderizar ahora» en la sala). "
                       f"Después, la sala mostrará «Re-sincronizar» para re-ajustar la línea a la voz nueva."}))

        if path == "/trim-render":                     # the room's «Renderizar ahora»
            epp = P.ep_path(ep)
            slug = data.get("slug") or P.read_status().get(ep, {}).get("slug") or ep
            take = _take_of(epp)
            if not take:
                return self._send(404, json.dumps({"error": "no hay toma con transcripción"}))
            st = _start_hard_render(epp, take, slug)
            return self._send(200 if st != "busy" else 409, json.dumps({
                "ok": st in ("started", "running", "none"), "state": st, "msg": _HARD_MSG[st]}))

        if path == "/script-save":                     # Stage 4 — save WIP, no gate fold
            epp = P.ep_path(ep)
            script_md = data.get("script_md")
            if not script_md:
                return self._send(400, json.dumps({"error": "guion vacío"}))
            (epp / "05-script.md").write_text(script_md, encoding="utf-8")
            return self._send(200, json.dumps({"ok": True}))

        if path == "/tl-save":                         # Stage 9 — save WIP, recompute, no gate fold
            slug = data.get("slug") or ep
            tl = data.get("timeline") or {}
            if not tl.get("beats"):
                return self._send(400, json.dumps({"error": "timeline vacío"}))
            epp = P.ep_path(ep)
            with _TIMELINE_EDIT_LOCK("guardar la línea"):
                (epp / "09-timeline.json").write_text(
                    json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
                # rebuild_timeline re-derives in/out from the authored `dur`s on the
                # VO backbone (schema 2) and re-resolves files — no align — then we
                # hand the recomputed timeline back
                _run(["assemble.py", slug, "--timeline-only"], timeout=EDIT_OP_TIMEOUT)
                _run(["edit_timeline.py", slug])
                fresh = (epp / "09-timeline.json").read_text(encoding="utf-8")
            return self._send(200, json.dumps({"ok": True, "msg": "guardado", "timeline": json.loads(fresh)}))

        if path == "/tl-rough":                        # Stage 9 — (re)render the 720p proxy
            slug = data.get("slug") or ep
            epp = P.ep_path(ep)
            if isinstance(data.get("timeline"), dict) and data["timeline"].get("beats"):
                (epp / "09-timeline.json").write_text(
                    json.dumps(data["timeline"], ensure_ascii=False, indent=1), encoding="utf-8")
            if P.lock_alive(epp / "09-rough.lock") or P.lock_alive(epp / "09-final.lock"):
                return self._send(409, json.dumps({"error": "ya hay un render en marcha para este episodio — espera a que termine"}))
            flag = epp / "09-rough.done"
            flag.unlink(missing_ok=True)
            (epp / "09-rough.done.fail").unlink(missing_ok=True)
            (epp / "09-rough.progress").write_text("out_time_us=0\n", encoding="utf-8")  # bar starts at 0
            _spawn_chain([["assemble.py", slug, "--rough"], ["edit_timeline.py", slug]],
                         done_flag=flag, log=epp / "09-rough.log")
            return self._send(200, json.dumps({"ok": True,
                "msg": "renderizando el borrador 720p en segundo plano — unos minutos."}))

        if path == "/tl-final":                        # Stage 9 — render the 4K master
            slug = data.get("slug") or ep
            epp = P.ep_path(ep)
            if P.lock_alive(epp / "09-final.lock"):    # a second one would race the first on its chunk files
                return self._send(409, json.dumps({"error": "el master 4K ya se está renderizando — espera a que termine"}))
            if isinstance(data.get("timeline"), dict) and data["timeline"].get("beats"):
                (epp / "09-timeline.json").write_text(
                    json.dumps(data["timeline"], ensure_ascii=False, indent=1), encoding="utf-8")
            flag = epp / "09-final.done"
            flag.unlink(missing_ok=True)
            (epp / "09-final.done.fail").unlink(missing_ok=True)
            (epp / "09-final.progress").write_text("out_time_us=0\n", encoding="utf-8")  # bar starts at 0
            _spawn_chain([["assemble.py", slug, "--final"]], done_flag=flag, log=epp / "09-final.log")
            return self._send(200, json.dumps({"ok": True,
                "msg": "renderizando el master 4K en segundo plano — esto tarda bastante."}))

        if path == "/advance":
            return self._send(200, json.dumps({"ok": True, "msg": _run(["advance.py", "next", ep])}))

        if path == "/stage-done":
            # a claude/draft stage with no review page (brief, outline, fact-check):
            # confirm its content is written -> fold the gate + advance in one go.
            return self._send(200, json.dumps({"ok": True, "msg": _run(["advance.py", ep])}))

        if path == "/take-undo":
            # Stage 8's upload dialog, "quitar esta toma": deletes the take and
            # everything trim_talk.py/match_audio.py/assemble.py derived from
            # it, puts the episode back at Stage 8 so a new one can be uploaded.
            msg = _run(["undo_take.py", ep])
            _run(["dash.py"])
            return self._send(200, json.dumps({"ok": True, "msg": msg}))

        if path == "/episode-delete":
            # discards the whole episode (moved to episodes/_trash/, not a
            # true rm -rf — see delete_episode.py). Requires the client to
            # have already confirmed with the user; refuses otherwise.
            if not data.get("confirm"):
                return self._send(400, json.dumps({"error": "falta confirm:true"}))
            msg = _run(["delete_episode.py", ep, "--confirm"])
            _run(["dash.py"])
            return self._send(200, json.dumps({"ok": True, "msg": msg}))

        if path == "/timeline":                       # Stage 9 — save the cutting-room timeline
            slug = data.get("slug") or ep
            tl = data.get("timeline") or {}
            epp = P.ep_path(ep)
            (epp / "09-timeline.json").write_text(
                json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
            beats = tl.get("beats", [])
            dec = ["# 09-decisions.txt — desde 09-edit.html", ""]
            for i, b in enumerate(beats, 1):
                bits = []
                if b.get("fix"):
                    bits.append("FIX: " + b["fix"])
                if b.get("nudge"):
                    bits.append(f"nudge {b['nudge']:+d}f")
                if bits:
                    tag = b.get("id") or b.get("n") or f"#{i}"
                    anchor = (b.get("vo_anchor") or b.get("frag") or "")[:48]
                    dec.append(f"{i:>3} {tag:<5} {b.get('asset') or '—':<28} " + " · ".join(bits)
                               + (f"   « {anchor} »" if anchor else ""))
            (epp / "09-decisions.txt").write_text("\n".join(dec) + "\n", encoding="utf-8")
            P.set_ep(ep, stage=9, gate="exportado")
            _run(["edit_timeline.py", slug])          # re-render the page with saved state
            msg = _run(["advance.py", "fold", ep])
            # the queued cuts get rendered now, once — the 4K render waits for it
            take = _take_of(epp)
            if take and take.with_suffix(".render.pending").exists():
                st = _start_hard_render(epp, take, slug)
                msg = (msg + "\n\n" if msg else "") + "Cortes en cola: " + _HARD_MSG[st] + \
                      (" — el render 4K final esperará a que termine." if st in ("started", "running") else ".")
            return self._send(200, json.dumps({"ok": True, "msg": msg}))

        if path == "/beat-asset":                     # Stage 9 — one beat's visual (swap / clear)
            slug = data.get("slug") or ep
            if data.get("list"):
                return self._send(200, _run(["beat_asset.py", slug, "--list"]) or "[]")
            epp = P.ep_path(ep)
            bid = str(data.get("id") or "")
            if not bid:
                return self._send(400, json.dumps({"error": "falta el id del beat"}))
            # a browsed file arrives as base64 → temp under assets/, passed as --src
            up_tmp, up = None, data.get("upload")
            if isinstance(up, dict) and up.get("data"):
                import base64
                ext = (Path(str(up.get("name", "x"))).suffix or ".bin").lower()
                up_tmp = epp / "assets" / ("_upload" + ext)
                try:
                    (epp / "assets").mkdir(parents=True, exist_ok=True)
                    up_tmp.write_bytes(base64.b64decode(up["data"]))
                    data["src"] = str(up_tmp)
                except Exception as e:
                    return self._send(400, json.dumps({"error": f"subida ilegible: {e}"}))
            if data.get("action") == "clear":
                args = ["beat_asset.py", slug, "--clear", bid]
            else:
                args = ["beat_asset.py", slug, "--set", bid]
                args += ["--src", str(data["src"])] if data.get("src") else ["--asset", str(data.get("asset", ""))]
            with _TIMELINE_EDIT_LOCK("cambiar el asset del beat " + bid):
                # persist the edit room's unsaved dur / nudge / approve edits first
                if isinstance(data.get("timeline"), dict) and data["timeline"].get("beats"):
                    (epp / "09-timeline.json").write_text(
                        json.dumps(data["timeline"], ensure_ascii=False, indent=1), encoding="utf-8")
                out = _run(args, timeout=ASSET_OP_TIMEOUT)
                if not out:
                    res = {"error": "sin respuesta"}
                else:
                    try:
                        res = json.loads(out)
                    except (json.JSONDecodeError, TypeError):
                        res = None
                if res is None:
                    if up_tmp is not None:
                        up_tmp.unlink(missing_ok=True)
                    return self._send(500, json.dumps({"error": (out or "sin respuesta")[-400:]}))
                if not res.get("error"):
                    _run(["edit_timeline.py", slug])
                    res["timeline"] = json.loads((epp / "09-timeline.json").read_text(encoding="utf-8"))
            if up_tmp is not None:
                up_tmp.unlink(missing_ok=True)
            return self._send(200, json.dumps(res, ensure_ascii=False))

        if path == "/beat-op":                        # Stage 9 — structural edit by beat id
            slug = data.get("slug") or ep
            epp = P.ep_path(ep)
            payload = {k: v for k, v in data.items()
                       if k not in ("slug", "ep", "timeline")}
            if payload.get("action") == "reseed" and not payload.get("confirm"):
                return self._send(400, json.dumps({"error": "reseed necesita confirm:true"}))
            # audiocut appends a real cut to the take's cuts.json and needs a
            # multi-minute re-render (trim_talk --apply) — resolve the take and
            # refuse a second one while the first is still in flight, same guard
            # /trim already needs for the exact same race.
            take = None
            action = payload.get("action")
            if action in ("audiocut", "cutundo", "cutredo"):
                take = _take_of(epp)
                if not take or not take.is_file():
                    return self._send(400, json.dumps({"error": "no hay toma trimmeada — nada que recortar"}))
                if P.lock_alive(take.with_suffix(".apply.lock")):
                    return self._send(409, json.dumps({
                        "error": "la toma se está renderizando ahora mismo (Finalizar) — espera a que termine"}))
            with _TIMELINE_EDIT_LOCK("edición «" + str(payload.get("action")) + "»"):
                if isinstance(data.get("timeline"), dict) and data["timeline"].get("beats"):
                    (epp / "09-timeline.json").write_text(
                        json.dumps(data["timeline"], ensure_ascii=False, indent=1), encoding="utf-8")
                out = _run(["beat_ops.py", slug, "--json", json.dumps(payload, ensure_ascii=False)],
                           timeout=EDIT_OP_TIMEOUT)
                try:
                    res = json.loads(out)
                except (json.JSONDecodeError, TypeError):
                    return self._send(500, json.dumps({"error": (out or "sin respuesta")[-400:]}))
                if not res.get("error"):
                    _run(["edit_timeline.py", slug])
                    res["timeline"] = json.loads((epp / "09-timeline.json").read_text(encoding="utf-8"))
                    if take is not None:
                        _soft_apply_async(epp, take, slug)
                        if action == "audiocut":
                            res["note"] = ((res.get("note", "") + " ") if res.get("note") else "") + \
                                "ya se oye el corte; el audio de la sala se refresca en ~30 s."
            if take is not None and action in ("cutundo", "cutredo") and not res.get("error"):
                _soft_wait()          # undo/redo answer only once words + audio + map match the timeline
            return self._send(200, json.dumps(res, ensure_ascii=False))

        if path == "/tl-preview":                     # Stage 9 — re-render a region of the proxy
            slug = data.get("slug") or ep
            if isinstance(data.get("timeline"), dict) and data["timeline"].get("beats"):
                (P.ep_path(ep) / "09-timeline.json").write_text(
                    json.dumps(data["timeline"], ensure_ascii=False, indent=1), encoding="utf-8")
            t0, t1 = str(int(float(data.get("t0", 0)))), str(int(float(data.get("t1", 30))) + 1)
            msg = _run(["assemble.py", slug, "--preview", t0, t1])
            return self._send(200, json.dumps({"ok": True, "msg": msg.splitlines()[-1] if msg else "ok"}))

        if path == "/human":
            P.set_ep(ep, gate="firmado")
            _run(["dash.py"])
            return self._send(200, json.dumps({"ok": True, "msg": _run(["advance.py", "next", ep])}))

        if path == "/loop":
            state = data.get("state", "run")
            P.write_loop(state, data.get("note", ""))
            _run(["dash.py"])
            hint = {"run": "el loop trabajará en el próximo tick",
                    "pause": "el loop no hará nada hasta reanudar (sigue gastando algo por tick — Ctrl+C para ahorro real)",
                    "stop": "el loop terminará en su próximo tick"}.get(state, "")
            return self._send(200, json.dumps({"ok": True, "msg": hint}))

        if path == "/nudge":
            # the panel can't run Claude (no tokens by design). This raises a flag
            # the /loop honours on its next tick (it paces down to ~1 min when
            # there's queued work), un-pauses it, and tells the user the instant path.
            import time
            P.touch_loop(state="run", wake=True, wake_ts=int(time.time()))
            _run(["dash.py"])
            lp = P.read_loop()
            fresh = lp.get("last_tick_ts") and (time.time() - lp["last_tick_ts"] < 300)
            msg = ("Marcado. El /loop lo coge en ≤1–2 min." if fresh else
                   "Marcado — pero el /loop no parece estar corriendo (sin ticks recientes).")
            return self._send(200, json.dumps({"ok": True, "msg":
                msg + "\nInstantáneo: escribe «sigue» en la terminal del /loop, o pídemelo en el chat de Claude Code."}))

        if path == "/cost-update":
            return self._send(200, json.dumps({"ok": True, "msg": _run(["cost_update.py"])}))

        if path == "/ideas-new":
            n = int(data.get("n", 3))
            P.enqueue("POOL", 0, "ideas",
                      note=f"Añade {n} ideas nuevas a ideas/idea-pool.md — mezcla los dos tracks "
                           f"(Documental `DOC-` y Ensayo `ENS-`) según lo que pida cada idea. 3 hook-titles "
                           f"estilo Dieck cada una (cola `| Documental` o `| Ensayo`), /21 estimada. No crees "
                           f"carpetas ni avances stages. Reglas: brain/12, brain/13, brain/20, ideas/idea-rubric.md")
            _run(["dash.py"])
            return self._send(200, json.dumps({"ok": True, "reload": False,
                              "msg": f"{n} ideas en cola — el /loop o Claude las escribe en el pool"}))

        if path == "/ideas":
            pool = P.ROOT / "ideas" / "idea-pool.md"
            approved, t = [], (pool.read_text(encoding="utf-8") if pool.exists() else "")
            STATUS = {"aprobar": "aprobada", "descartar": "descartada", "incubar": "incubando"}
            for iid, x in (data.get("verdicts") or {}).items():
                if x.get("hook"):
                    t = _pool_set_hook(t, iid, x["hook"])
                new = STATUS.get(x.get("v"))
                if new:
                    t = _pool_set_status(t, iid, new)
                if x.get("v") == "aprobar":
                    approved.append(iid)
            if pool.exists():
                pool.write_text(t, encoding="utf-8")
            _run(["idea_review.py"]); _run(["dash.py"])
            tail = (f" · aprobadas (pulsa «Crear episodio»): {', '.join(approved)}" if approved else "")
            return self._send(200, json.dumps({"ok": True, "msg": "Pool actualizado" + tail}))

        if path == "/idea-produce":
            iid = (data.get("id") or "").strip()
            pool = P.ROOT / "ideas" / "idea-pool.md"
            if not iid or not pool.exists():
                return self._send(400, json.dumps({"error": "falta id o ideas/idea-pool.md"}))
            t = pool.read_text(encoding="utf-8")
            row = re.search(
                rf"^\|\s*{re.escape(iid)}\s*\|\s*([^|\n]*?)\s*\|(?:[^|\n]*\|){{4}}\s*([^|\n]*?)\s*\|",
                t, re.M)
            if not row:
                return self._send(404, json.dumps({"error": f"{iid} no está en el pool"}))
            work_title, status = row.group(1), row.group(2)
            if status.startswith(("en producción", "en produccion", "publicada")):
                return self._send(409, json.dumps({"error": f"{iid} ya está en «{status}»"}))
            if status != "aprobada":
                return self._send(409, json.dumps({
                    "error": f"{iid} está «{status}» — apruébala primero (veredicto «aprobar» + «Aplicar cambios»)."}))
            hooks = _pool_hooks(t, iid)
            hook = ""
            if data.get("hook"):
                try:
                    hook = hooks[int(data["hook"]) - 1]
                except (ValueError, IndexError):
                    hook = ""
            if not hook:
                hm = re.search(r"(?m)^-\s+\*\*Hook elegido:\*\*\s*`([^`]+)`", _pool_detail(t, iid))
                hook = hm.group(1) if hm else (hooks[0] if hooks else work_title)
            track = "Ensayo" if iid.startswith("ENS") else "Documental"
            narrator = "—"  # ideación sin dueño: el narrador se asigna en el brief (Stage 1)
            epid = P.next_epid()
            slug = f"{epid}-{P.slugify(work_title)}"
            P.set_ep(epid, slug=slug, title=f"«{work_title}»", track=track, narrator=narrator,
                     stage=0, gate="exportado", notes=f"desde {iid} · hook: {hook}")
            exp = P.EP_DIR / slug / "_exports"
            exp.mkdir(parents=True, exist_ok=True)
            (exp / "stage00.json").write_text(
                json.dumps({"idea_id": iid, "hook": hook, "working_title": work_title},
                           ensure_ascii=False, indent=1), encoding="utf-8")
            msg = _run(["advance.py", "fold", epid])
            _run(["idea_review.py"]); _run(["dash.py"])
            return self._send(200, json.dumps({"ok": True,
                "msg": f"{iid} → {epid} · {slug}\n{msg}"}))

        self._send(404, json.dumps({"error": "unknown endpoint", "path": path}))


if __name__ == "__main__":
    P.write_loop("run", wake=False)   # fresh server = fresh session (keep last_tick_ts if a loop is live)
    _run(["dash.py"])
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", P.PORT), H)
    except OSError:
        print(f"El puerto {P.PORT} ya está en uso — probablemente el server ya corre. "
              f"Abre  http://localhost:{P.PORT}")
        sys.exit(0)
    print(f"Conquest dashboard  ->  http://localhost:{P.PORT}   (Ctrl+C para parar)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
