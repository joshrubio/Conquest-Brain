# -*- coding: utf-8 -*-
"""
pipeline.py — the single source of truth for the 12-stage pipeline.

The stage manifest (what each stage produces, its review page, how its
gate is folded, what an agent must read to *generate* that stage), plus
readers/writers for episodes/_STATUS.md and episodes/_queue.json.

Imported by dash.py, advance.py, serve.py and the review tools.
Not a CLI.
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes"
STATUS_F = EP_DIR / "_STATUS.md"
QUEUE_F = EP_DIR / "_queue.json"          # gitignored — the loop's to-do list
LOOP_F = EP_DIR / "_loop.json"            # gitignored — the loop's run/pause/stop signal
PORT = 8765
SERVED = f"http://localhost:{PORT}/"


def read_loop():
    if LOOP_F.exists():
        try:
            return json.loads(LOOP_F.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"state": "run"}


def write_loop(state, note="", **extra):
    d = read_loop()
    d.update({"state": state, "note": note})
    d.update(extra)
    LOOP_F.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


def touch_loop(**fields):
    """Merge fields into _loop.json without changing state (heartbeat, wake flag, idle streak)."""
    d = read_loop()
    d.update(fields)
    LOOP_F.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

# fold kinds:
#   mech   — advance.py folds it in python, no agent
#   verify — advance.py only checks an artifact exists + marks the gate
#   claude — an agent must generate/apply content; advance.py queues it
#   human  — offline (record, upload); the user marks it done in the dashboard
STAGES = [
    # n  key         name(ES)                     produces                                   review_html                export                fold      nxt  reads_to_generate                                                   rules
    (0,  "idea",     "Ideación",                  "fila en ideas/idea-pool.md",              "ideas/idea-review.html",  "idea-review.txt",    "mech",   1,   ["ideas/idea-pool.md"],                                              ["brain/12", "brain/13", "brain/05"]),
    (1,  "brief",    "Brief",                     "01-brief.md",                             None,                      None,                 "claude", 2,   ["ideas/idea-pool.md"],                                              ["brain/06", "brain/13", "brain/09"]),
    (2,  "research", "Dossier de investigación",  "02-research-dossier.md + 03-source-log.csv", "02-research.html",      "02-research.txt",     "mech",   3,   ["01-brief.md"],                                                     ["brain/01", "brain/05", "brain/12"]),
    (3,  "outline",  "Outline",                   "03-outline.md (beat sheet)",              None,                      None,                 "claude", 4,   ["02-research-dossier.md", "01-brief.md"],                            ["brain/02", "brain/09", "brain/19", "templates/outline-template.md"]),
    (4,  "script",   "Guion",                     "05-script.md",                            "05-script.html",          "05-script-pass.txt", "mech",   5,   ["03-outline.md", "02-research-dossier.md", "03-source-log.csv", "01-brief.md"], ["brain/02", "brain/08", "brain/09", "brain/13", "brain/19"]),
    (5,  "factcheck","Fact-check",                "04-factcheck-auto.md",                    None,                      None,                 "claude", 6,   ["05-script.md", "03-source-log.csv"],                                ["brain/14", "brain/01", "brain/04", "brain/19"]),
    (6,  "shotlist", "Shotlist",                  "06-shotlist.md",                          None,                      None,                 "claude", 7,   ["05-script.md"],                                                    ["brain/11", "brain/06"]),
    (7,  "assets",   "Recursos + pase de estilo", "07-assets.md (+ 07b-ai-prompts.md)",      "07-style-pass.html",      "07-picks.txt",       "mech",   8,   ["06-shotlist.md", "material-search.md"],                             ["brain/12", "brain/15", "brain/03"]),
    (8,  "record",   "Grabación",                 "tomas en assets/",                        None,                      None,                 "human",  9,   [],                                                                  []),
    (9,  "edit",     "Edición",                   "09-edit.html (+ 09-timeline.json)",       "09-edit.html",            "09-timeline.json",   "mech",   10,  [],                                                                  ["brain/16"]),
    (10, "package",  "Paquete",                   "08-thumbnail-title.md + 09-description.md", "10-package.html",       "10-package.txt",     "mech",   11,  ["03-source-log.csv", "ideas/idea-pool.md"],                          ["brain/07", "brain/13", "brain/03"]),
    (11, "publish",  "Publicación",               "10-publish-checklist.md",                 None,                      None,                 "human",  12,  [],                                                                  ["brain/04", "brain/05"]),
    (12, "retro",    "Retro",                     "11-retro.md",                            "12-metrics.html",         "12-metrics.txt",     "mech",   None, [],                                                                  ["brain/07"]),
]

_KEYS = ("n", "key", "name", "produces", "review_html", "export", "fold", "next", "reads", "rules")
STAGE = {s[0]: dict(zip(_KEYS, s)) for s in STAGES}
GATES = ("abierto", "exportado", "firmado")   # firmado = passed, ready to advance

# what clicking a stage's card opens (relative to the episode folder).
# a review .html if it has one; otherwise the file it produced; stage 8 -> the shotlist.
OPEN = {
    0: "ideas/idea-review.html", 1: "01-brief.md", 2: "02-research.html",
    3: "03-outline.md", 4: "05-script.html", 5: "04-factcheck-auto.md",
    6: "06-shotlist.md", 7: "07-style-pass.html", 8: "06-shotlist.md",
    9: "09-edit.html", 10: "10-package.html", 11: "10-publish-checklist.md",
    12: "12-metrics.html",
}

# short scannable label for the stage card
CARD = {
    0: "La idea: título con gancho + hay material + puntúa.",
    1: "Brief: tesis, por qué ahora, cierre, top-3 fuentes, riesgos.",
    2: "Investigación: dossier + registro de fuentes (Claude, fuentes reales).",
    3: "Outline: la lista de beats en orden, antes del guion.",
    4: "Guion completo + el 'script pass' beat a beat.",
    5: "Fact-check automático: cada dato contra su fuente.",
    6: "Shotlist: qué se ve en cada momento.",
    7: "Pase de estilo: eliges imágenes, clips y música.",
    8: "Grabas el vídeo (talking-head) siguiendo el shotlist. Offline.",
    9: "Edición: la timeline — coloca cada beat sobre la voz, ajusta y aprueba.",
    10: "Paquete: título publicado, miniatura, descripción.",
    11: "Publicación: tick legal, subir, programar.",
    12: "Retro: métricas a 48 h y 30 d.",
}

# human-friendly, non-developer explanation shown on hover / in the card
HELP = {
    0: "La idea. Se le busca un buen título con gancho, se comprueba que hay material para ilustrarla y se puntúa. Si pasa, se convierte en carpeta de episodio.",
    1: "El brief: en una frase cada cosa — de qué va, por qué ahora, cómo cierra, las 3 mejores fuentes ya encontradas, los riesgos. Antes de invertir tiempo en investigar.",
    2: "La investigación. Claude busca en fuentes reales y arma el dossier + el registro de fuentes: cronología, personas clave, cada dato con su fuente y su nivel de fiabilidad.",
    3: "El outline: la lista de beats en orden — cold open, contexto, actos, cierre — antes de escribir el guion entero.",
    4: "El guion completo: la narración palabra por palabra, con las notas técnicas y las etiquetas de fuente. Se revisa beat a beat en el 'script pass'.",
    5: "El fact-check. Automático: un script comprueba que cada fuente resuelve, y Claude re-lee cada afirmación contra su fuente y aplica las correcciones al guion.",
    6: "El shotlist: qué se ve en cada momento — un plano por cambio de sujeto, por explicador, por foreshadowing. Se infiere del guion ya bloqueado.",
    7: "El pase de estilo: eliges las imágenes y clips reales de cada beat, los del cold open, y la música. El sistema los descarga a la carpeta de recursos.",
    8: "Grabación. Te grabas en vídeo (talking-head, plano medio, set de serie) leyendo el guion — una toma continua vale, `trim_talk.py` limpia silencios, muletillas y retomas. El shotlist marca qué beats van a cámara (A-roll) y cuáles se cubren con B-roll. Guarda la(s) toma(s) en `<episodio>/assets/` (p. ej. `E0XX-vo.mp4`). Offline — cuando termines, marca 'hecho'.",
    9: "La edición: la sala de montaje. Un primer corte automático coloca cada beat sobre la voz grabada; en la timeline ajustas duración, posición y asset de cada clip, marcas los que hay que regenerar, y apruebas. El render 4K lo hace el sistema.",
    10: "El paquete: eliges el título publicado, la miniatura y repasas la descripción. Las 3 aprobaciones cierran el gate.",
    11: "Publicación. El tick legal/COI final, subir el vídeo, subtítulos, capítulos, comentario fijado, programar.",
    12: "El retro: a las 48 h y a los 30 d pegas las métricas de YouTube. Qué funcionó, qué se corrige en el proceso.",
}


def ensure_assets(epid):
    """Make sure <ep>/assets/ exists with its standard subfolders + README."""
    ep = ep_path(epid)
    ad = ep / "assets"
    for sub in ("", "intro", "stock", "video", "archive", "ai", "kb", "thumb"):
        (ad / sub).mkdir(parents=True, exist_ok=True)
    rd = ad / "README.md"
    tmpl = EP_DIR / "_TEMPLATE-episode-folder" / "assets" / "README.md"
    if not rd.exists() and tmpl.exists():
        rd.write_text(tmpl.read_text(encoding="utf-8"), encoding="utf-8")
    return ad


# ---------- episodes/_STATUS.md ----------

_ROW = re.compile(r"^\|\s*(E\d{3})\s*\|(.+)\|\s*$")


def read_status():
    """-> {epid: {slug,title,track,narrator,stage,gate,auto,notes}}"""
    out = {}
    if not STATUS_F.exists():
        return out
    for line in STATUS_F.read_text(encoding="utf-8").splitlines():
        m = _ROW.match(line)
        if not m:
            continue
        cells = [c.strip() for c in (m.group(1) + "|" + m.group(2)).split("|")]
        # ID | Slug | Título | Track | Narrador | Stage | Gate | Auto-avance | Notas
        if len(cells) < 9:
            continue
        epid = cells[0]
        try:
            stage = int(re.sub(r"\D", "", cells[5]) or -1)
        except ValueError:
            stage = -1
        try:
            auto = int(re.sub(r"\D", "", cells[7]))
        except ValueError:
            auto = 12
        out[epid] = {
            "slug": cells[1], "title": cells[2], "track": cells[3], "narrator": cells[4],
            "stage": stage, "gate": cells[6].lower() if cells[6] in GATES or cells[6].lower() in GATES else "abierto",
            "auto": auto, "notes": cells[8],
        }
    return out


def write_status(data):
    hdr = ("# Índice maestro de episodios\n\n"
           "> Fuente única de verdad del estado de cada episodio. La escriben `tools/advance.py` y `tools/serve.py`; edítala a mano solo para las notas o el techo de auto-avance.\n\n"
           "## Leyenda\n\n"
           "**Stage** 0 idea · 1 brief · 2 investigación · 3 outline · 4 guion · 5 fact-check · 6 shotlist · 7 recursos+estilo · 8 grabación · 9 edición · 10 paquete · 11 publicación · 12 retro\n"
           "**Gate** `abierto` (en curso) · `exportado` (decisiones tomadas, falta plegar) · `firmado` (gate pasado, listo para avanzar)\n"
           "**Auto-avance** el stage máximo hasta el que el loop avanza sin pedirte permiso.\n\n"
           "## Episodios\n\n"
           "| ID | Slug | Título | Track | Narrador | Stage | Gate | Auto-avance | Notas |\n"
           "|----|------|--------|-------|----------|-------|------|-------------|-------|\n")
    rows = []
    for epid in sorted(data):
        d = data[epid]
        rows.append(f"| {epid} | {d['slug']} | {d['title']} | {d.get('track','—')} | "
                    f"{d.get('narrator','—')} | {d['stage']} | {d['gate']} | {d.get('auto',12)} | {d.get('notes','')} |")
    tail = ("\n\n## Reglas\n\n"
            "- Un episodio no avanza de stage sin `Gate = firmado` (`brain/06`, `brain/17`).\n"
            "- Máx. 2 episodios en stages 2–5 a la vez.\n"
            "- Al publicar: `advance.py` mueve la fila al KPI log de `brain/07`.\n")
    STATUS_F.write_text(hdr + "\n".join(rows) + tail, encoding="utf-8")


def set_ep(epid, **fields):
    data = read_status()
    data.setdefault(epid, {"slug": "", "title": "", "track": "—", "narrator": "—",
                           "stage": 0, "gate": "abierto", "auto": 12, "notes": ""})
    data[epid].update(fields)
    write_status(data)
    return data[epid]


# ---------- episodes/_queue.json ----------

def read_queue():
    if QUEUE_F.exists():
        try:
            return json.loads(QUEUE_F.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def write_queue(items):
    QUEUE_F.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")


def enqueue(epid, stage, action, note=""):
    """Add a task for the agent (the /loop) to pick up."""
    st = STAGE.get(stage, {})
    try:
        epdir = ep_path(epid).relative_to(ROOT).as_posix()
    except ValueError:
        epdir = f"episodes/{epid}"
    q = [x for x in read_queue() if not (x["ep"] == epid and x["stage"] == stage)]
    q.append({
        "ep": epid, "stage": stage, "name": st.get("name", "?"), "action": action,
        "reads": [r if r.startswith(("ideas/", "brain/")) else f"{epdir}/{r}"
                  for r in st.get("reads", [])],
        "rules": st.get("rules", []),
        "produces": st.get("produces", ""),
        "note": note,
    })
    write_queue(q)
    return q


def dequeue(epid, stage):
    write_queue([x for x in read_queue() if not (x["ep"] == epid and x["stage"] == stage)])


def ep_path(epid):
    d = read_status().get(epid, {})
    slug = d.get("slug") or epid
    p = EP_DIR / (slug if slug.startswith(epid) else f"{epid}-{slug}")
    return p if p.exists() else EP_DIR / slug


TEMPLATE_DIR = EP_DIR / "_TEMPLATE-episode-folder"

# the document each doc-producing stage owns (Stages 8/9/11 produce takes / a
# timeline / an upload, not a doc — not here).
PRIMARY_DOC = {1: "01-brief.md", 2: "02-research-dossier.md", 3: "03-outline.md",
               4: "05-script.md", 5: "04-factcheck-auto.md", 6: "06-shotlist.md"}
# ...of those, the `mech`-fold ones whose review page is meaningless until a
# Claude draft exists (1/3/5/6 are `claude` folds — already queued on entry).
DRAFT_STAGES = {2: PRIMARY_DOC[2], 4: PRIMARY_DOC[4]}


def pristine(epid, fname):
    """True if the episode's copy of fname is missing or still byte-identical to the template."""
    a = ep_path(epid) / fname
    if not a.exists():
        return True
    b = TEMPLATE_DIR / fname
    return b.exists() and a.read_bytes() == b.read_bytes()


def slugify(s):
    """'Disney / Mickey' -> 'disney-mickey'. ASCII, kebab, safe for a folder name."""
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return s or "ep"


def next_epid():
    """Next free E0XX — max across _STATUS.md, the episode folders, and the KPI log."""
    n = 0
    for epid in read_status():
        m = re.match(r"E(\d+)$", epid)
        if m:
            n = max(n, int(m.group(1)))
    for p in EP_DIR.glob("E[0-9][0-9][0-9]*"):
        m = re.match(r"E(\d+)", p.name)
        if m:
            n = max(n, int(m.group(1)))
    kpi = ROOT / "brain" / "07-publishing-seo-metrics.md"
    if kpi.exists():
        for m in re.finditer(r"\bE(\d{3})\b", kpi.read_text(encoding="utf-8")):
            n = max(n, int(m.group(1)))
    return f"E{n + 1:03d}"
