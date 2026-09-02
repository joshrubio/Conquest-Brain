# Consumo del sistema — tokens vs. plan Claude Pro

> **Estimación, no medición.** Cifras Fermi por etapa, marcadas con su incertidumbre. Recalíbralo con datos reales tras cada episodio (ver §Calibración). Los límites del plan Pro no los publica Anthropic con exactitud y cambian — los rangos de abajo son a fecha **2026-08**; actualízalos.
>
> Se abre desde el botón **«Consumo»** del dashboard (`tools/dash.py` → `cost.html`).

## Qué mide

Cuántos **tokens de Claude** consume producir un episodio de Conquest-Brain, y qué fracción de una suscripción **Claude Pro** representa. No cuenta el tiempo de la persona (grabar, subir) ni el cómputo local (los scripts de `tools/` son llamadas Bash de coste ~0 en tokens).

## Modelo de coste por etapa (por episodio, un pase sin iteración)

| Stage | Trabajo de Claude | Input aprox. | Output aprox. | Tokens (rango) | Notas |
|-------|-------------------|--------------|---------------|----------------|-------|
| 0 idea | ayuda a poblar el pool (amortizado entre varios episodios) | — | — | ~5–15 k | por idea, no por episodio |
| 1 brief | lee fila del pool + `brain/06,13,09`; redacta `01-brief.md` | ~10 k | ~2 k | **15–30 k** | |
| 2 research | **WebSearch/WebFetch** (5–15 consultas), lee páginas, sintetiza dossier + source-log | 80–300 k | ~5 k | **120–400 k** | la etapa más cara, con mucha varianza |
| 3 outline | lee dossier + brief + `brain/02,09`; beat sheet | ~25 k | ~2 k | **30–55 k** | |
| 4 script | lee outline + dossier + source-log + brief + `brain/02,08,09,13`; guion ~3 000 palabras | ~40 k | ~6 k | **60–120 k** | |
| 4 script-pass fold | lee las notas del pase + el guion; aplica | ~15 k | ~4 k | **20–45 k** | único fold que sigue siendo Claude |
| 5 fact-check L2 | lee guion + source-log + `brain/14`; analiza cada claim, produce correcciones | ~25 k | ~5 k | **40–90 k** | |
| 6 shotlist | lee guion bloqueado + `brain/11`; infiere `06-shotlist.md` | ~20 k | ~4 k | **30–55 k** | |
| 7 prompts IA | lee beats del shotlist + `brain/15`; escribe el texto de escena | ~12 k | ~3 k | **15–35 k** | solo si hay beats sin imagen real |
| 9 edición | `assemble.py` monta el primer corte y `edit_timeline.py` la timeline (python, 0 tokens); tú ajustas en el navegador (0 tokens); Claude solo aplica los FIX de KB como flags + lanza el render | ~12 k | ~5 k | **20–45 k** | antes «Claude + ffmpeg iterativo, 40–110 k, sin tope» — la timeline lo acota |
| 10 descripción | lee source-log + pool + `brain/07`; `09-description.md` | ~12 k | ~3 k | **15–35 k** | |
| 12 retro | lee KPI + `brain/07`; fixes de proceso | ~8 k | ~3 k | **10–25 k** | |
| **Suma, un pase** | | | | **~410–1 100 k** | |
| **× iteración real** (feedback → revisión, ×1.5–2) | | | | **~600 k – 2.2 M** | |

**Punto medio de trabajo:** **~1.1 M tokens por episodio.** Dominado por research (Stage 2) y guion (Stage 4).

## Efecto del dashboard centralizado

| | Sin dashboard (antes de 044d753) | Con dashboard | Ahorro |
|---|---|---|---|
| Cruce de gate mecánico (0·2·7·9·10 + fact-check fold) | Claude lee el `.txt` de revisión (~1–3 k) + el `.md` destino (~2–8 k) + edita (~3–5 k) + responde. **~10–25 k/gate × ~6 gates = 80–200 k/episodio** | lo hace `advance.py` en python — **Claude no participa** | **~80–200 k/episodio** |
| Cruce de gate con Claude (Stage 4 fold) | igual | igual (~20–45 k) | 0 |
| Sincronización de estado (`_STATUS.md`) | Claude lo edita a mano cada cambio (~3–6 k × ~10) | `advance.py` lo escribe | **~30–60 k/episodio** |
| **Total ahorrado por episodio** | | | **~110–260 k (~10–20 %)** |
| Coste nuevo — `/loop` en reposo | — | tick = leer `_queue.json` (~0.2 k) + respuesta corta; el grueso (system prompt + defs de tools) va **cacheado** (TTL 1 h). ~2–6 k/tick de coste marginal; sleep 20 min ⇒ ~3 ticks/h ⇒ **~10–20 k/h en reposo** | −(depende de horas con el loop abierto) |

**Neto:** el dashboard **ahorra ~10–20 % por episodio** en el flujo activo. El `/loop` solo cuesta si lo dejas abierto sin trabajar; con sleeps largos y caché, el reposo es del orden de un fact-check por cada 4–8 h ociosas. Recomendación: en pausas largas, **Cerrar sesión** (o dime «para el loop»); pausar no basta.

## El diseño no toca el gasto de tokens

Todo el CSS/HTML de todas las páginas generadas (dashboard, consumo, review pages, vistas de fichero) vive en **un** fichero, `tools/theme.py` — presentación pura, sin lógica ni datos. `dash.py`, `pipeline.py` y las review tools solo construyen estructura e importan el aspecto de ahí.

| | Antes | Ahora |
|---|---|---|
| Sistema de diseño | fragmentado en 7 sitios (`review_ui`, `dash._VIEW_CSS`, `dash.extra` ~50 líneas, `build_cost`, y `edit_review`/`pull_assets` redefiniendo `:root` a mano) | un fichero, `tools/theme.py` |
| Editar la lógica del pipeline | abrir `dash.py` = ~400 líneas de CSS en el contexto | `dash.py` es data→DOM; el CSS ya no está |
| Un rediseño (como este) | tocaba 8 ficheros que también llevan lógica | toca `theme.py` y punto |
| Drenar la cola / plegar un gate | los datos (`_STATUS.md`, `_queue.json`, `_exports/*.json`, `*.txt`) son texto plano sin marcado; `dashboard.html`/`cost.html` gitignored | igual — **el rediseño nunca entra en el contexto de una decisión** |

Barrera de lectura explícita: `theme.py` abre con un banner *PRESENTATION ONLY*; `AGENTS.md`, `brain/17` y `.claude/commands/atiende.md` dicen que solo se abre para "cambiar cómo se ven las páginas". Coste de un rediseño en tokens del flujo de producción: **cero**.

## La sala de montaje (Stage 9) — coste

**Construirla (una vez):** `assemble.py` + `edit_timeline.py` + CSS + wiring ≈ **el coste de ~1 episodio** de tokens, repartido en varias sesiones. La varianza está en el grafo `filter_complex` de `assemble.py` (cada ciclo de debug de render de vídeo cuesta).

**Por episodio, después:** Stage 9 pasa de **40–110 k** (Claude iterando ffmpeg, sin tope) a **20–45 k** (acotado):

| Paso | Tokens |
|------|--------|
| Primer corte + timeline (`assemble.py` → `edit_timeline.py`) | 0 — python |
| Arrastrar / trim / swap / previsualizar (en el navegador) | 0 — como el dashboard |
| Render 4K (`assemble.py --final`) | 0 — python/ffmpeg |
| Claude: aplicar los FIX de KB como flags + revisar el render | ~20–45 k |

**Contexto:** `09-edit.html` lo genera python; su CSS vive en `theme.py` (cuarentena); Claude solo lee `09-timeline.json` / `09-decisions.txt` (texto plano). Cero carga añadida por decisión.

**Fork DaVinci:** si un episodio necesita pulido a frame, se lleva `09-timeline.json` a Resolve — la colocación ya está hecha, Claude no re-coloca 45 clips vía MCP (eso serían ~60–150 k/episodio). La timeline propia se amortiza vs. ese fork a los **~10–15 episodios**.

## Contra el plan Claude Pro (rangos 2026-08 — verificar)

Claude Pro (~20 USD/mes) usa un límite móvil que **se reinicia cada 5 h** más un **tope semanal**. Anthropic no publica el número exacto de tokens; en uso tipo Claude Code, estimaciones de comunidad y observación propia:

| Ventana | Presupuesto Pro estimado | Un episodio (~1.1 M) | Episodios por ventana |
|---------|--------------------------|----------------------|-----------------------|
| Sesión de 5 h | ~2–4 M tokens efectivos (con caché) | ~1.1 M | **~2–3** trozos de episodio, o **~1 episodio completo si cae en una sola ventana** |
| Semana | ~15–30 M tokens efectivos | ~1.1 M/episodio | **~10–20 episodios/semana** de techo teórico |

**Lectura práctica:** a cadencia real (1 episodio / 2–3 semanas, `brain/07`), Conquest-Brain consume **una fracción pequeña** de un plan Pro semanal — el cuello de botella es research + guion en una sola sesión de 5 h, que puede rozar el límite de esa ventana si haces todo el episodio de una tirada. Repartir research y guion en sesiones distintas lo mantiene holgado.

**Para un adoptante futuro:** si produce 1 episodio/semana con iteración pesada (~2 M/episodio), sigue dentro de Pro, pero con menos margen para otro trabajo en paralelo. 2+ episodios/semana → considerar un plan superior.

## Calibración (hazlo tras E002)

1. Al terminar un episodio, corre `/usage` (o el skill `explain-usage`) y anota los tokens reales de la sesión/sesiones dedicadas a ese episodio.
2. Rellena la fila real en §Historial.
3. Ajusta los rangos de la tabla por etapa si la realidad se desvía > ~30 %.
4. Vuelve a estimar el % de Pro con los números reales.

## Historial

| Fecha | Versión (commit) | Episodio | Tokens estimados | Tokens reales | Notas |
|-------|------------------|----------|------------------|---------------|-------|
| 2026-08-31 | rename + theme.py | — | ~1.1 M/episodio (modelo) | — | sin cambio de coste: rename Éxodo→Conquest y consolidación de diseño no tocan el flujo de producción |
| 2026-08 | 044d753 (dashboard) | — | ~1.1 M/episodio (modelo) | — | primera línea base; sin medición real todavía |
| — | pre-044d753 | — | ~1.25 M/episodio (modelo) | — | +10–20 % por folds manuales |

## Cómo se actualiza

Este doc (`.md`) es **tracked**; su render `cost.html` lo regenera `tools/dash.py` (gitignored, como `dashboard.html`). Edítalo a mano cuando:
- cambien los límites del plan Pro → actualiza §Contra el plan
- midas tokens reales → §Historial + recalibra la tabla
- una etapa cambie de coste (nueva herramienta, más/menos lectura) → su fila
El botón **«Actualizar»** (arriba, en esta página) corre `tools/cost_update.py`. `tools/dash.py` lo re-renderiza a `cost.html` en cada regeneración del dashboard.
