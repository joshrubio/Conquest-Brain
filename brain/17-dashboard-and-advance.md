---
doc: 17-dashboard-and-advance
summary: "The dashboard (dash.py), the local server (serve.py), and the gate engine (advance.py). How a chapter moves from stage to stage with one click."
stage: all
read_when: "running the pipeline day to day; a gate won't close; setting up the /loop"
pairs_with: [06-production-workflow, 07-publishing-seo-metrics]
tools: [dash.py, serve.py, advance.py, pipeline.py, metrics.py]
authority: canonical
---

# 17 — Dashboard & the Advance Engine

One screen for every chapter, and a one-click hand-off between stages.
`tools/pipeline.py` holds the 12-stage manifest that all of this reads.

## The pieces

| File | What |
|------|------|
| `tools/pipeline.py` | the stage manifest (produces / review page / fold kind / next / what to read to *generate* each stage) + readers/writers for `_STATUS.md` and `_queue.json`. Not a CLI. |
| `tools/dash.py` | regenerates `dashboard.html` from `_STATUS.md` + the folders + the KPI log. Pure python, cheap. |
| `tools/serve.py` | `127.0.0.1:8765`. Serves the dashboard + every review page + episode files. Turns each review page's finish button into: stash decisions → fold the gate → regenerate the dashboard. |
| `tools/advance.py` | the gate engine — `fold` (apply a stage's decisions) and `next` (bump to the next stage). Mechanical only; anything needing an agent goes on `_queue.json`. |
| `tools/metrics.py` | Stage 12 review page — paste YouTube numbers → KPI-log row + retro block. |
| `Exodo-Dashboard.bat` | double-click: starts `serve.py` + opens the browser. |

## State — `episodes/_STATUS.md`

The single source of truth. `advance.py` and `serve.py` write it; you edit it by
hand only for the notes column or the **auto-advance ceiling**.

Per episode: `Stage` (0–12, the one whose gate is next) · `Gate` (`abierto` →
`exportado` → `firmado`) · `Auto-avance` (max stage the `/loop` advances without
asking).

## Fold kinds (per stage, in `pipeline.py`)

| Kind | Stages | Gate closes by |
|------|--------|----------------|
| `mech` | 0 · 7 · (2 · 9 · 10 partly) | `advance.py` folds the decisions in python — **zero chat** |
| `verify` | — | `advance.py` just checks an artifact exists |
| `claude` | 1 · 3 · 4 · 5 · 6 | an agent generates or applies content — queued on `_queue.json` |
| `human` | 8 record · 11 publish | offline; you press "Marcar hecho" in the dashboard |

For `mech` stages whose export format varies (research, edit, package), `advance.py`
stashes the export to `<ep>/_exports/stageNN.json` and queues a `fold` task — an
agent finishes it. Simple ones (idea → creates the folder; assets → runs
`pull_assets --download`; retro → appends the KPI row) fold fully in python.

## The flow

1. Open a review page from the dashboard, correct / approve.
2. Click **Finalizar Stage N** → POST to `serve.py`:
   - writes `<ep>/_exports/stageNN.json` + the canonical `.txt`
   - `Gate → exportado`, runs `advance.py fold`
   - `mech` → folds now, `Gate → firmado`; `claude` → queues the fold
   - regenerates `dashboard.html`
3. Dashboard shows a **▶ Avanzar a Stage N+1** button once `Gate = firmado`.
   Click it (or the `/loop` does it) → `advance.py next`: bump stage, `Gate →
   abierto`, queue the next stage if it's `claude`, regenerate.

Without the server: the finish button downloads the `.txt`; run
`python tools/advance.py fold E0XX` then `python tools/advance.py next E0XX`.

## Controlar la sesión (el `/loop`)

Un **tick** = una iteración del `/loop`: despierto, leo `_loop.json` + `_queue.json`, hago lo pendiente (o nada), reporto, programo el siguiente. En modo auto-pausado los ticks son ~1 min si hay trabajo y ~20 min en reposo (rango 60–3600 s). **No** coinciden con los cambios de stage — son un temporizador; el botón escribe un fichero y el siguiente tick lo ve.

El navegador no puede matar un `/loop` — solo señalarlo. `episodes/_loop.json` (`{state: run|pause|stop}`) lo escriben los botones del dashboard; `atiende` lo lee **antes que nada** cada tick:

- **⏹ Cerrar sesión** → `stop` → el tick reporta y no reprograma → el loop termina. Para pararlo **ya**: dímelo ("para el loop") o **Esc** en la terminal del chat.
- **⏸ Pausar** → noop + sleep largo. Cada tick sigue costando el overhead (cacheado) → solo para pausas cortas.
- **▶ Reanudar** → `run`.

`serve.py` pone `run` al arrancar (server nuevo = sesión nueva). Retomar la automatización tras cerrar = reabrir el dashboard + volver a lanzar `/loop atiende el dashboard`; el estado (`_STATUS.md`, `_queue.json`) no se pierde.

El **server** (`serve.py`) es aparte y no gasta tokens; ciérralo cuando quieras.

## Ahorro de tokens

El dashboard incluye la burbuja «Cómo no gastar tokens» y, por card, el **manifiesto de contexto** (los `reads` + `rules` del stage — lo único que el agente debe abrir). El reporte vive en `research/system-cost.md` → botón «Consumo»; el botón «Actualizar plan» corre `tools/cost_update.py` (bumpea fecha, marca filas viejas, añade una fila de Historial con hueco para el `/usage` real).

## The `/loop` (optional layer)

`/loop atiende el dashboard` — each tick reads **only** `episodes/_queue.json`:
- entries → do them (write the outline, apply the script-pass notes…) per each
  entry's `reads` + `rules` (read nothing else), then `advance.py`, then
  `dequeue`, then report
- empty → sleep long (20 min)

Respects `Auto-avance`: the loop pauses at that stage and waits for your explicit
"sigue". High-stakes gates (after research, after script) are natural ceilings.

**Token discipline:** the loop tick is one small file read when idle. A working
tick reads only what the queue entry names. Never scan the repo.

## Adding an episode

Approve an idea in `idea-review.html` → Stage 0 fold copies
`_TEMPLATE-episode-folder/` → `episodes/E0XX-slug/`, marks the idea-pool row,
sets Stage 1. Or add a row to `_STATUS.md` by hand and `python tools/dash.py`.
