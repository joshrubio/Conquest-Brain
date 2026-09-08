---
description: Drena la cola del dashboard (episodes/_queue.json) — hazlo pendiente, avanza gates, respeta el techo de auto-avance. Úsalo con /loop.
---

Atiende el dashboard de Conquest. **Lee SOLO `episodes/_loop.json` y `episodes/_queue.json`** — no explores el repo.

0. Lee `episodes/_loop.json`:
   - `{"state":"stop"}` → responde «loop cerrado» y **NO reprogrames** (el loop termina aquí).
   - `{"state":"pause"}` → responde «pausado» en una línea, marca noop, y programa el próximo tick a 300 s. No hagas trabajo.
   - `{"state":"run"}` o ausente → continúa.
   - Anota si hay `"wake": true` (el usuario pulsó «Pedir generación» en el panel) — lo usas en el paso 3.
1. **Heartbeat:** `python -c "import sys,time;sys.path.insert(0,'tools');import pipeline as P;P.touch_loop(last_tick_ts=int(time.time()), wake=False)"` — marca que el loop está vivo y limpia el flag `wake`.
2. Si la cola está vacía: dilo en una línea y programa el próximo tick según la **cadencia** de abajo.
3. Por cada entrada `{ep, stage, action, reads, rules, produces, note}`:
   - Lee **únicamente** los ficheros de `reads` + los docs de `rules`. Nada más. Nunca abras `tools/*.py` (y menos `tools/theme.py`, que es solo CSS) — no los necesitas para generar ni plegar.
   - `action: "generate"` → escribe `produces` para ese episodio siguiendo `rules`. Si el stage tiene página de revisión (research = 2, guion = 4), genera además la página: `python tools/research_review.py <slug>` / `python tools/script_review.py <slug>`.
   - `action: "ideas"` (ep = `POOL`) → añade las ideas nuevas a `ideas/idea-pool.md` siguiendo la `note` (no crees carpetas, no avances stages). Luego `python tools/idea_review.py` para regenerar la página, y borra la entrada de la cola.
   - `action: "fold"` → aplica las decisiones de `<ep>/_exports/stage<NN>.json` (o el `.txt` canónico) al fichero fuente del stage.
   - Cuando termines: `python tools/advance.py fold <ep>` y luego, si el stage ≤ `Auto-avance` de ese episodio en `_STATUS.md`, `python tools/advance.py next <ep>`. Si el stage == el techo, para ahí y anótalo en el reporte.
   - Quita la entrada de la cola (`advance.py next` la borra al avanzar; si no avanzaste, bórrala tú con `python -c "...P.dequeue('<ep>', <stage>)"`).
4. Reporta en 3–6 líneas: qué hiciste, qué queda, qué necesita mi visto.

**Cadencia** (programa el próximo tick con este `delaySeconds`, clamped 60–3600):
- Cola con entradas al terminar, o `wake` estaba activo → **60 s**.
- Cola vacía: 1º–2º tick vacío seguido → **120 s**; 3º–5º → **300 s**; a partir del 6º → **900 s**. (Lleva la cuenta en `_loop.json` como `idle_streak` vía `P.touch_loop(idle_streak=N)`; resetea a 0 en cuanto haya trabajo.)

No toques stages `human` (grabación, publicación) ni pidas permiso para los `mech`. Para los gates de alto riesgo (tras research = stage 2, tras guion = stage 4) **para y espera mi "sigue"** aunque el techo lo permita, salvo que el techo esté explícitamente por encima.
