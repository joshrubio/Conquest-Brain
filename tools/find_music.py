#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_music.py — pick the channel's background-music beds (Stage 9, brain/16 move 4).

Brief: OMINOUS AMBIENT. Atmosphere, not dread, not a mystery stinger.
Instrumental, low, slow, minimal melody, no vocals, no percussion spikes.
Run once (or in a couple of passes), keep 3–5 tracks, reuse every episode.

Source: Jamendo API (free client_id in tools/.env as JAMENDO_CLIENT_ID; register at
https://devportal.jamendo.com/). No key -> Openverse audio fallback (weak for beds).

LICENCE — read this. A monetised YouTube video is COMMERCIAL use and a sync/derivative.
This tool only keeps tracks under CC-BY / CC-BY-SA / CC0 (NC and ND are filtered out).
CC-BY still REQUIRES crediting the artist + licence in the video description — the tool
logs each to brand/assets/music/LICENSES.md. CC-BY-SA additionally asks that the work
be shareable alike; if that bothers you, stick to CC-BY / CC0.
Jamendo's separate PAID "Jamendo Licensing" service is NOT needed for CC-BY tracks —
it's for a clean no-attribution licence or for tracks the artist kept all-rights.
No-hassle alternatives with zero attribution: YouTube Audio Library (in Studio),
Pixabay Music (pixabay.com/music) — both browse-only, no API.

Usage
  python tools/find_music.py "dark ambient drone cinematic underscore"
      -> brand/assets/music/candidates.md   (title, artist, licence, preview, id)

  python tools/find_music.py --get 1874320 1553019 ...
      download those ids -> brand/assets/music/ + append LICENSES.md
"""
import re
import sys
from pathlib import Path

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
ENV = Path(__file__).resolve().parent / ".env"
MUS = ROOT / "brand" / "assets" / "music"
CAND = MUS / "candidates.md"
UA = "ExodoOficial/1.0 (educational documentary; contact joshuerubio@gmail.com)"
DEFAULT_Q = "dark ambient drone cinematic underscore atmospheric"


def env(name):
    if ENV.exists():
        for ln in ENV.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln.startswith(name + "="):
                return ln.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


# A monetised YouTube video is commercial use + a sync/derivative.
# Reject any CC licence carrying NC (non-commercial) or ND (no-derivatives).
def _lic_slug(ccurl):
    parts = (ccurl or "").rstrip("/").split("/")
    return parts[-2].lower() if len(parts) >= 2 else ""


def commercial_ok(slug):
    """True if the CC licence allows monetised/commercial use. Empty slug -> unknown."""
    if not slug:
        return None                       # can't tell — surface it, flag it
    if slug in ("cc0", "zero", "publicdomain", "mark"):
        return True
    tokens = set(slug.split("-"))          # e.g. {"by","nc","sa"}
    if "nc" in tokens or "nd" in tokens:
        return False
    return tokens <= {"by", "sa"}


# --------------------------------------------------------------------------- search
def jamendo(query, cid, n=40):
    r = requests.get("https://api.jamendo.com/v3.0/tracks/", params={
        "client_id": cid, "format": "json", "limit": n,
        "fuzzytags": query.replace(" ", "+"),
        "include": "musicinfo licenses", "audioformat": "mp32",
        "order": "popularity_total", "vocalinstrumental": "instrumental",
        "ccnd": "false", "cc_nc": "false",       # exclude NoDerivatives + NonCommercial
    }, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    out = []
    for t in r.json().get("results", []):
        if not t.get("audiodownload_allowed"):
            continue
        dur = int(t.get("duration") or 0)
        if dur < 90:
            continue
        slug = _lic_slug(t.get("license_ccurl"))
        ok = commercial_ok(slug)
        if ok is False:                           # NC or ND -> drop (API filter is unreliable)
            continue
        parts = (t.get("license_ccurl") or "").rstrip("/").split("/")[-2:]
        licstr = ("CC " + "-".join(parts).upper()) if slug else "CC (verificar en la page)"
        if ok is None:
            licstr += "  ⚠ sin licencia legible"
        out.append({
            "src": "jamendo", "id": str(t["id"]),
            "title": t.get("name", ""), "artist": t.get("artist_name", ""),
            "dur": dur, "lic": licstr,
            "tags": " ".join((t.get("musicinfo") or {}).get("tags", {}).get("genres", [])),
            "preview": t.get("audio", ""), "download": t.get("audiodownload", ""),
            "page": t.get("shareurl", ""),
        })
    return out


def openverse(query, n=25):
    try:
        r = requests.get("https://api.openverse.org/v1/audio/", params={
            "q": query, "page_size": n, "license": "cc0,by,by-sa",
        }, headers={"User-Agent": UA}, timeout=30)
        r.raise_for_status()
    except requests.HTTPError as e:
        print(f"openverse: HTTP {e.response.status_code} (rate limit anónimo) — sin candidatos")
        return []
    out = []
    for h in r.json().get("results", []):
        dur = round((h.get("duration") or 0) / 1000)
        out.append({
            "src": h.get("source", "openverse"), "id": str(h.get("id", "")),
            "title": h.get("title", ""), "artist": h.get("creator", "") or "",
            "dur": dur,
            "lic": f"CC {h.get('license', '').upper()} {h.get('license_version', '')}".strip(),
            "tags": " ".join(h.get("tags_names", []) if isinstance(h.get("tags_names"), list) else []),
            "preview": h.get("url", ""), "download": h.get("url", ""),
            "page": h.get("foreign_landing_url", ""),
        })
    return out


def search(query):
    cid = env("JAMENDO_CLIENT_ID")
    if cid:
        try:
            hits = jamendo(query, cid)
            if hits:
                return hits, "jamendo"
        except requests.HTTPError as e:
            print(f"jamendo: HTTP {e.response.status_code} — cae a openverse")
    return openverse(query), "openverse (sin JAMENDO_CLIENT_ID — beds flojos)"


HEAD = [
    "# Candidatos de música — pool acumulado",
    "",
    "> Cada `find_music.py \"query\"` AÑADE aquí (dedup por id). Brief: **ominosa ambiental**.",
    "> Solo CC-BY / CC-BY-SA / CC0 (uso comercial OK). **CC-BY exige crédito** — se registra",
    "> en `LICENSES.md` al descargar. Sin líos: YouTube Audio Library (Studio) o pixabay.com/music.",
    "> Escucha, elige 3–5, corre:  `python tools/find_music.py --get <id> <id> ...`",
    "",
]


def run(query):
    hits, src = search(query)
    MUS.mkdir(parents=True, exist_ok=True)
    prev = CAND.read_text(encoding="utf-8") if CAND.exists() else "\n".join(HEAD)
    have = set(re.findall(r"^## `([^`]+)`", prev, re.M))
    new = []
    for h in hits:
        key = f"{h['src']}:{h['id']}"
        if key in have:
            continue
        have.add(key)
        mm, ss = divmod(h["dur"], 60)
        new += [
            f"## `{key}` — {h['title']} · {h['artist']}",
            f"- {mm}:{ss:02d} · {h['lic']} · «{query}»" + (f" · {h['tags']}" if h['tags'] else ""),
            f"- download: {h['download'] or h['preview']}",
        ]
        if h["page"]:
            new.append(f"- page: {h['page']}")
        new.append("")
    if new:
        CAND.write_text(prev.rstrip() + "\n\n" + "\n".join(new) + "\n", encoding="utf-8")
    n_new = sum(1 for x in new if x.startswith("## "))
    print(f"escrito  {CAND.relative_to(ROOT)}  (+{n_new} nuevos, {len(have)} en el pool, fuente: {src})")
    print("siguiente: escucha (page), elige 3–5, `python tools/find_music.py --get <id> ...`")


def get(ids):
    if not CAND.exists():
        sys.exit(f"no {CAND.relative_to(ROOT)} — corre la búsqueda primero")
    txt = CAND.read_text(encoding="utf-8")
    MUS.mkdir(parents=True, exist_ok=True)
    lic_lines = []
    for want in ids:
        m = re.search(rf"^## `([a-z_]+):{re.escape(want)}` — (.+)$", txt, re.M)
        if not m:
            print(f"  ?  {want} no está en candidates.md")
            continue
        src, titleartist = m.group(1), m.group(2)
        block = txt[m.end():txt.find("\n## ", m.end()) if "\n## " in txt[m.end():] else len(txt)]
        dl = re.search(r"download: (\S+)", block) or re.search(r"preview: (\S+)", block)
        lic = re.search(r"·\s*(CC[^\n·]*)", block)
        if not dl:
            print(f"  ?  {want} sin URL")
            continue
        try:
            r = requests.get(dl.group(1), headers={"User-Agent": UA}, timeout=120)
            r.raise_for_status()
        except Exception as e:
            print(f"  FALLO  {want}  {e}")
            continue
        safe = re.sub(r"[^A-Za-z0-9]+", "-", titleartist.split(" · ")[0]).strip("-").lower()[:40]
        head = r.content[:4]
        if head[:3] == b"ID3" or head[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xfa", b"\xff\xf2"):
            ext = ".mp3"
        elif head == b"OggS":
            ext = ".ogg"
        elif head == b"fLaC":
            ext = ".flac"
        else:
            ext = ".mp3" if "mp3" in dl.group(1).lower() else ".ogg"
        fn = MUS / f"{src}_{want}_{safe}{ext}"
        fn.write_bytes(r.content)
        print(f"  OK  {fn.name}  ({len(r.content)//1024} KB)")
        lic_lines.append(f"- `{fn.name}` — {titleartist} — {lic.group(1).strip() if lic else 'CC (ver candidates.md)'} "
                         f"— atribución obligatoria en 09-description.md")
    if lic_lines:
        lf = MUS / "LICENSES.md"
        prev = lf.read_text(encoding="utf-8") if lf.exists() else "# Licencias — música de fondo\n\n> CC, no dominio público. Atribuir cada pista (autor + licencia) en la descripción del vídeo.\n"
        lf.write_text(prev.rstrip() + "\n" + "\n".join(lic_lines) + "\n", encoding="utf-8")
        print(f"\nlicencias → {lf.relative_to(ROOT)}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--get":
        if len(a) < 2:
            sys.exit("da al menos un id: --get 1874320 ...")
        get(a[1:])
    else:
        run(" ".join(a) if a else DEFAULT_Q)
