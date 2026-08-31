---
description: Drena la cola del dashboard (episodes/_queue.json) — hazlo pendiente, avanza gates, respeta el techo de auto-avance. Úsalo con /loop.
---

Atiende el dashboard de Exodo. **Lee SOLO `episodes/_loop.json` y `episodes/_queue.json`** — no explores el repo.

0. Lee `episodes/_loop.json`:
   - `{"state":"stop"}` → responde «loop cerrado» y **NO reprogrames** (el loop termina aquí).
   - `{"state":"pause"}` → responde «pausado» en una línea, marca noop, y programa el próximo tick largo (20 min). No hagas trabajo.
   - `{"state":"run"}` o ausente → continúa.
1. Si la cola está vacía: dilo en una línea y termina (el /loop dormirá).
2. Por cada entrada `{ep, stage, action, reads, rules, produces, note}`:
   - Lee **únicamente** los ficheros de `reads` + los docs de `rules`. Nada más.
   - `action: "generate"` → escribe `produces` para ese episodio siguiendo `rules`.
   - `action: "fold"` → aplica las decisiones de `<ep>/_exports/stage<NN>.json` (o el `.txt` canónico) al fichero fuente del stage.
   - Cuando termines: `python tools/advance.py fold <ep>` y luego, si el stage ≤ `Auto-avance` de ese episodio en `_STATUS.md`, `python tools/advance.py next <ep>`. Si el stage == el techo, para ahí y anótalo en el reporte.
   - Quita la entrada de la cola (`advance.py` no la borra por ti si fue `generate`: bórrala tú con un pequeño edit a `_queue.json`, o usa `pipeline.dequeue`).
3. Reporta en 3–6 líneas: qué hiciste, qué queda, qué necesita mi visto.

No toques stages `human` (grabación, publicación) ni pidas permiso para los `mech`. Para los gates de alto riesgo (tras research = stage 2, tras guion = stage 4) **para y espera mi "sigue"** aunque el techo lo permita, salvo que el techo esté explícitamente por encima.
