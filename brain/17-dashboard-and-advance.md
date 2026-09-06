---
doc: 17-dashboard-and-advance
summary: "The dashboard (dash.py), the local server (serve.py), and the gate engine (advance.py). How a chapter moves from stage to stage with one click."
stage: all
read_when: "running the pipeline day to day; a gate won't close; setting up the /loop"
pairs_with: [06-production-workflow, 07-publishing-seo-metrics]
tools: [dash.py, serve.py, advance.py, pipeline.py, metrics.py, theme.py, assemble.py, edit_timeline.py]
authority: canonical
---

# 17 — Dashboard & the Advance Engine

One screen for every chapter, and a one-click hand-off between stages.
`tools/pipeline.py` holds the 12-stage manifest that all of this reads.

## The pieces

| File | What |
|------|------|
| `tools/pipeline.py` | the stage manifest (produces / review page / fold kind / next / what to read to *generate* each stage) + readers/writers for `_STATUS.md` and `_queue.json`. Not a CLI. |
| `tools/theme.py` | **the whole design system** — every CSS token, component and the HTML wrapper, in one file. Presentation only, no logic or data. `dash.py` + the review tools import `CSS` / `HELPERS` / `FAVICON` / `shell` from here — `FAVICON` (the channel avatar, `brand/assets/favicon.ico` + `-32.png`) is baked into every page's `<head>` via `shell()`. Read it *only* to restyle pages; folding gates and draining the queue never touches it. |
| `tools/dash.py` | regenerates `dashboard.html` + `cost.html` from `_STATUS.md` + the folders + the KPI log. Structure only — look comes from `theme.py`. Pure python, cheap. |
| `tools/serve.py` | `127.0.0.1:8765`. Serves the dashboard + every review page + episode files. Turns each review page's finish button into: stash decisions → fold the gate → regenerate the dashboard. |
| `tools/advance.py` | the gate engine — `fold` (apply a stage's decisions) and `next` (bump to the next stage). Mechanical only; anything needing an agent goes on `_queue.json`. |
| `tools/metrics.py` | Stage 12 review page — paste YouTube numbers → KPI-log row + retro block. |
| `Conquest-Dashboard.bat` | double-click: starts `serve.py` + opens the browser. |
| `Conquest-Dashboard.lnk` | a Windows shortcut to the `.bat` with the channel avatar as its icon (a `.bat` can't carry an icon itself) — gitignored, machine-local; copy/pin it to the Desktop or taskbar. Regenerate with PowerShell if it's ever missing: `$s=(New-Object -COM WScript.Shell).CreateShortcut("Conquest-Dashboard.lnk"); $s.TargetPath="Conquest-Dashboard.bat"; $s.IconLocation="brand\assets\favicon.ico"; $s.Save()` (run from the repo root). |

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

**Stage 9 (edit)** is special: entering it, `advance.py` runs `assemble.py` +
`edit_timeline.py` (python — builds the first-cut timeline + `09-edit.html`).
Finalising it POSTs `09-timeline.json`; the fold queues one agent task: apply the
per-beat regen notes (`kenburns.py`) then `assemble.py --final` for the 4K master.

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

- **⏹ Cerrar sesión** → `stop` → el tick reporta y no reprograma → el loop termina. El botón **solo aparece mientras la sesión está activa o pausada**; tras cerrar, queda «▶ Reanudar sesión». Para pararlo **ya**: dímelo ("para el loop") o **Esc** en la terminal.
- **⏸ Pausar** → noop + sleep largo. Cada tick sigue costando el overhead (cacheado) → solo para pausas cortas.
- **▶ Reanudar** → `run`.

`serve.py` pone `run` al arrancar (server nuevo = sesión nueva). Retomar la automatización tras cerrar = reabrir el dashboard + volver a lanzar `/loop atiende el dashboard`; el estado (`_STATUS.md`, `_queue.json`) no se pierde.

El **server** (`serve.py`) es aparte y no gasta tokens; ciérralo cuando quieras.

## Ahorro de tokens

El dashboard incluye la burbuja «Cómo no gastar tokens» y, por card, el **manifiesto de contexto** (los `reads` + `rules` del stage — lo único que el agente debe abrir).

**El diseño está en cuarentena.** Todo el CSS/HTML vive en `tools/theme.py` y en ningún otro sitio. Los datos que consume el agente (`_STATUS.md`, `_queue.json`, `_exports/*.json`, `*.txt`) son texto plano sin marcado, y `dashboard.html`/`cost.html` están gitignored. Plegar un gate o drenar la cola nunca abre un fichero con estilos → el rediseño no entra en el contexto. `theme.py` solo se abre para "cambiar cómo se ven las páginas". El reporte vive en `research/system-cost.md` (tracked) → botón «Consumo» del dashboard abre su render `cost.html`. Dentro, el botón **«Actualizar»** (con tooltip) corre `tools/cost_update.py`: bumpea la fecha, marca como *revisar* las filas > 90 días, añade una fila al Historial con el commit actual y un hueco para el `/usage` real, y re-renderiza. No inventa cifras.

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

## La tira de stages (dashboard)

Cada card de episodio tiene una tira de 13 chips (0–12). Al hover, cada uno explica su stage en lenguaje llano. Clic → abre lo que ese stage produjo:

- stage con review page → su `.html`
- stage sin review page (brief · outline · fact-check · shotlist · publicación) → su `.md` **renderizado** (`serve.py /view` lo convierte al vuelo, con el estilo del dashboard)
- stage 8 grabación → el shotlist renderizado, con botón **Recursos**
- stage 9 edición → **`09-edit.html`**, la timeline (waveform + un bloque por beat + inspector)
- stage futuro (aún sin fichero) → solo el tooltip

Todos los botones del dashboard y de `cost.html` llevan tooltip temático (no el nativo) en lenguaje no-técnico.

**Carpeta de recursos:** `pipeline.ensure_assets(epid)` crea `<ep>/assets/` con sus subcarpetas (`intro stock video archive ai kb thumb`) + README — al crear el episodio, al entrar en stage ≥ 6, y defensivamente en `dash.py`. El server lista la carpeta en `/episodes/<slug>/assets/`. El HTML del pase de estilo y la vista del shotlist enlazan a ella.

## El pool de ideas

Botón **💡 Ideas** del dashboard → `ideas/idea-review.html` (regenerada por `idea_review.py`). Es gestión del pool, no un gate lineal:

- por idea: veredicto (aprobar / incubar / descartar) + hook + /21 + nota
- **«Aplicar cambios»** → `POST /ideas` → escribe los estados en `idea-pool.md` al momento (descartar → `descartada`, incubar → `incubando`); las `aprobar` se listan para crear su episodio
- **«＋ Generar 3 ideas»** → `POST /ideas-new` → encola una tarea `ideas` para el agente (añade ideas al pool, sin avanzar stages)
- **← dashboard** para volver

## Adding an episode

Approve an idea in `idea-review.html` → Stage 0 fold copies
`_TEMPLATE-episode-folder/` → `episodes/E0XX-slug/`, marks the idea-pool row,
sets Stage 1. Or add a row to `_STATUS.md` by hand and `python tools/dash.py`.
