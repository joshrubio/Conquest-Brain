---
description: Drena la cola del dashboard (episodes/_queue.json) — hazlo pendiente, avanza gates, respeta el techo de auto-avance. Úsalo con /loop.
---

Atiende el dashboard de Conquest. **Lee SOLO `episodes/_loop.json` y `episodes/_queue.json`** — no explores el repo.

0. Lee `episodes/_loop.json`:
   - `{"state":"stop"}` → responde «loop cerrado» y **NO reprogrames** (el loop termina aquí).
   - `{"state":"pause"}` → responde «pausado» en una línea, marca noop, y programa el próximo tick a 300 s. No hagas trabajo.
   - `{"state":"run"}` o ausente → continúa.
   - Anota si hay `"wake": true` (el usuario pulsó «Pedir generación» en el panel) — lo usas en el paso 4.
1. **Heartbeat:** `python -c "import sys,time;sys.path.insert(0,'tools');import pipeline as P;P.touch_loop(last_tick_ts=int(time.time()), wake=False)"` — marca que el loop está vivo y limpia el flag `wake`.
2. **Drena los gates ya cerrados:** `python tools/advance.py --drain` — pliega cualquier episodio en `gate: exportado` y avanza cualquiera en `gate: firmado` dentro de su propio `Auto-avance` de `_STATUS.md`. Esto es lo que encadena «Finalizar Stage 9» (o cualquier stage) al siguiente automáticamente — sin esto el episodio se queda en `firmado` esperando que alguien pulse «Avanzar» a mano. El propio `Auto-avance` de cada episodio ya es el permiso explícito para los gates de alto riesgo (research=2, guion=4): un episodio con el techo todavía bajo (p. ej. 4) no pasa de ahí aunque su gate esté firmado; uno con el techo ya subido (como E001 en 12) sí sigue solo. Si la salida no es «nada pendiente» ni un error, cuenta como **trabajo real** este tick — anótalo en el reporte igual que una entrada de cola.
3. Si la cola está vacía: dilo en una línea y programa el próximo tick según la **cadencia** de abajo.
4. Por cada entrada `{ep, stage, action, reads, rules, produces, note}`:
   - Lee **únicamente** los ficheros de `reads` + los docs de `rules`. Nada más. Nunca abras `tools/*.py` (y menos `tools/theme.py`, que es solo CSS) — no los necesitas para generar ni plegar.
   - `action: "generate"` → escribe `produces` para ese episodio siguiendo `rules`. Si el stage tiene página de revisión (research = 2, guion = 4, paquete = 10), genera además la página: `python tools/research_review.py <slug>` / `python tools/script_review.py <slug>` / `python tools/package_review.py <slug>`. El Stage 10 en concreto necesita **capítulos reales** en `09-description.md` — calculados desde los tiempos ya alineados de `09-timeline.json` (no desde el plan pre-render, que puede ir desviado varios minutos) — la nota de la entrada de cola lo repite.
   - `action: "ideas"` (ep = `POOL`) → añade las ideas nuevas a `ideas/idea-pool.md` siguiendo la `note` (no crees carpetas, no avances stages). Luego `python tools/idea_review.py` para regenerar la página, y borra la entrada de la cola.
   - `action: "fold"` → aplica las decisiones de `<ep>/_exports/stage<NN>.json` (o el `.txt` canónico) al fichero fuente del stage.
   - Cuando termines: `python tools/advance.py fold <ep>` y luego, si el stage ≤ `Auto-avance` de ese episodio en `_STATUS.md`, `python tools/advance.py next <ep>`. Si el stage == el techo, para ahí y anótalo en el reporte.
   - Quita la entrada de la cola (`advance.py next` la borra al avanzar; si no avanzaste, bórrala tú con `python -c "...P.dequeue('<ep>', <stage>)"`).
   - **Si la entrada no se puede drenar** (herramienta ausente, error, bloqueo externo) **déjala en la cola y trátala como "sin trabajo real"** en la cadencia de abajo, aunque siga técnicamente "en cola". Si el motivo del bloqueo es el mismo que dejaste anotado en el tick anterior, **no reintentes el mismo comando** — confírmalo con esa nota y sigue.
5. Reporta en 3–6 líneas: qué hiciste, qué queda, qué necesita mi visto.

**Cadencia** (programa el próximo tick con este `delaySeconds`, clamped 60–3600). "Trabajo real" = algo cambió de verdad (un stage avanzó, un documento se generó o plegó, se limpió la cola de ideas) — una cola vacía o una entrada que sigue bloqueada por el mismo motivo que antes **no** cuenta:
- Hubo trabajo real este tick, o `wake` estaba activo → **60 s**.
- Sin trabajo real: 1º–2º tick seguido así → **120 s**; 3º–5º → **300 s**; 6º–10º → **900 s**; a partir del 11º → **3600 s** (el techo — no tiene sentido reintentar cada 15 min algo que no va a cambiar solo). Lleva la cuenta en `_loop.json` como `idle_streak` vía `P.touch_loop(idle_streak=N)`; resetea a 0 en cuanto haya trabajo real.

**Auto-cierre por inactividad** (para no dejarlo corriendo toda la noche por accidente). Lleva en `_loop.json` un `idle_since_ts`: la primera vez que un tick no tiene trabajo real, si está vacío, ponlo a la hora actual (`P.touch_loop(idle_since_ts=<epoch>)`); en cuanto haya trabajo real, bórralo (`P.touch_loop(idle_since_ts=None)`). Si `ahora - idle_since_ts ≥ 1800` (**30 minutos seguidos sin trabajo real**), **detén el loop en vez de programar otro tick**: `P.touch_loop(state="stop", note="auto-cierre: sin cambios reales desde <hora de idle_since_ts>")`, responde una línea explicándolo (qué seguía bloqueado, desde cuándo), y **no llames a ScheduleWakeup** — el loop termina aquí, igual que `{"state":"stop"}` del paso 0. El usuario lo reabre a mano con `/loop` cuando quiera.

No toques stages `human` (grabación, publicación) ni pidas permiso para los `mech`. Para los gates de alto riesgo (tras research = stage 2, tras guion = stage 4) **para y espera mi "sigue"** aunque el techo lo permita, salvo que el techo esté explícitamente por encima.
