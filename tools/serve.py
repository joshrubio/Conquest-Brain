#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
serve.py — the local dashboard server. 127.0.0.1 only, no auth, your machine.

  python tools/serve.py          # http://localhost:8765

Serves the dashboard + every review page + the episode files, and turns
each review page's "Finalizar" button into: stash decisions -> fold the
gate (advance.py) -> regenerate the dashboard. No copy-paste, no chat.

Started by Exodo-Dashboard.bat, or by Claude in the background, or by you
in its own terminal (survives across sessions).
"""
import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline as P  # noqa: E402

TOOLS = Path(__file__).resolve().parent
MIME = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
        ".json": "application/json", ".txt": "text/plain; charset=utf-8",
        ".md": "text/plain; charset=utf-8", ".csv": "text/plain; charset=utf-8",
        ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".mp4": "video/mp4"}


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
        self.end_headers()
        self.wfile.write(b)

    def do_OPTIONS(self):
        self._send(204, b"", "text/plain")

    def do_GET(self):
        path = unquote(self.path.split("?")[0])
        if path in ("/", "/dashboard.html"):
            _run(["dash.py"])
            f = P.ROOT / "dashboard.html"
            return self._send(200, f.read_bytes(), MIME[".html"])
        if path == "/state":
            return self._send(200, json.dumps(P.read_queue(), ensure_ascii=False))
        f = (P.ROOT / path.lstrip("/")).resolve()
        if P.ROOT in f.parents and f.is_file():
            return self._send(200, f.read_bytes(), MIME.get(f.suffix, "application/octet-stream"))
        self._send(404, json.dumps({"error": "not found", "path": path}))

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
            # also drop the canonical .txt so the existing fold/download paths work
            canon = P.STAGE.get(stage, {}).get("export")
            if canon and payload.get("txt"):
                (epp / canon).write_text(payload["txt"], encoding="utf-8")
            P.set_ep(ep, stage=stage, gate="exportado")
            msg = _run(["advance.py", "fold", ep])
            return self._send(200, json.dumps({"ok": True, "msg": msg}))

        if path == "/advance":
            return self._send(200, json.dumps({"ok": True, "msg": _run(["advance.py", "next", ep])}))

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
    print(f"Exodo dashboard  ->  http://localhost:{P.PORT}   (Ctrl+C para parar)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
