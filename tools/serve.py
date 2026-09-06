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
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline as P  # noqa: E402


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
        ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".mp4": "video/mp4",
        ".ico": "image/x-icon"}


def _run(args):
    r = subprocess.run([sys.executable, str(TOOLS / args[0])] + args[1:],
                       capture_output=True, text=True)
    return (r.stdout or r.stderr).strip()


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

    def do_OPTIONS(self):
        self._send(204, b"", "text/plain")

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
        if path == "/view":
            return self._view(qs.get("ep", [""])[0], qs.get("f", [""])[0])
        f = (P.ROOT / path.lstrip("/")).resolve()
        if P.ROOT in f.parents:
            if f.is_dir():
                return self._send(200, _dir_html(f), MIME[".html"])
            if f.is_file():
                return self._send(200, f.read_bytes(), MIME.get(f.suffix, "application/octet-stream"))
        self._send(404, json.dumps({"error": "not found", "path": path}))

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
        n = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, json.dumps({"error": "bad json"}))
        path = self.path.split("?")[0]
        ep = data.get("ep")

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

        if path == "/advance":
            return self._send(200, json.dumps({"ok": True, "msg": _run(["advance.py", "next", ep])}))

        if path == "/timeline":                       # Stage 9 — save the cutting-room timeline
            slug = data.get("slug") or ep
            tl = data.get("timeline") or {}
            epp = P.ep_path(ep)
            (epp / "09-timeline.json").write_text(
                json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
            beats = tl.get("beats", [])
            dec = ["# 09-decisions.txt — desde 09-edit.html", ""]
            for b in beats:
                bits = []
                if b.get("fix"):
                    bits.append("FIX: " + b["fix"])
                if b.get("approved"):
                    bits.append("APROBADO")
                if b.get("nudge"):
                    bits.append(f"nudge {b['nudge']:+d}f")
                if bits:
                    dec.append(f"beat {b['n']:>2}  {b.get('asset') or '—'}  " + " · ".join(bits))
            (epp / "09-decisions.txt").write_text("\n".join(dec) + "\n", encoding="utf-8")
            P.set_ep(ep, stage=9, gate="exportado")
            _run(["edit_timeline.py", slug])          # re-render the page with saved state
            msg = _run(["advance.py", "fold", ep])
            return self._send(200, json.dumps({"ok": True, "msg": msg}))

        if path == "/tl-preview":                     # Stage 9 — re-render a region of the proxy
            slug = data.get("slug") or ep
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

        if path == "/cost-update":
            return self._send(200, json.dumps({"ok": True, "msg": _run(["cost_update.py"])}))

        if path == "/ideas-new":
            n = int(data.get("n", 3))
            P.enqueue("POOL", 0, "ideas",
                      note=f"Añade {n} ideas nuevas a ideas/idea-pool.md — alterna T01/T02, 3 hook-titles "
                           f"estilo Dieck cada una, /21 estimada. No crees carpetas ni avances stages. "
                           f"Reglas: brain/12, brain/13, ideas/idea-rubric.md")
            _run(["dash.py"])
            return self._send(200, json.dumps({"ok": True, "reload": False,
                              "msg": f"{n} ideas en cola — el /loop o Claude las escribe en el pool"}))

        if path == "/ideas":
            pool = P.ROOT / "ideas" / "idea-pool.md"
            approved, t = [], (pool.read_text(encoding="utf-8") if pool.exists() else "")
            for iid, x in (data.get("verdicts") or {}).items():
                v = x.get("v")
                if v == "aprobar":
                    approved.append(iid)
                elif v in ("descartar", "incubar"):
                    new = "descartada" if v == "descartar" else "incubando"
                    t = re.sub(rf"(\|\s*{re.escape(iid)}\s*\|(?:[^|\n]*\|){{5}})\s*[^|\n]*(\|)",
                               rf"\1 {new} \2", t, count=1)
            if pool.exists():
                pool.write_text(t, encoding="utf-8")
            _run(["idea_review.py"]); _run(["dash.py"])
            tail = (f" · aprobadas (crea episodio): {', '.join(approved)}" if approved else "")
            return self._send(200, json.dumps({"ok": True, "msg": "Pool actualizado" + tail}))

        self._send(404, json.dumps({"error": "unknown endpoint", "path": path}))


if __name__ == "__main__":
    P.write_loop("run")          # fresh server = fresh session
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
