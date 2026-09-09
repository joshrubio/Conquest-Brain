---
doc: shotlist-broll
summary: "One row per visual beat, inferred from the locked script. Need / archival-vs-graphic / on-screen text / motion / rights."
stage: [6]
fills: "06-shotlist.md"
rule: [11]
authority: template
---

# Shotlist / B-roll — E0XX «<título>»

> Stage 6. Se **infiere del guion bloqueado** (`brain/11-visual-rhythm.md`). Una fila por beat visual. Ningún visual pasa a edición sin estado de derechos.

| Campo | Valor |
|-------|-------|
| ID episodio | E0XX |
| Versión de guion | v__ |
| Narrador del episodio | Usuario 002 / Usuario 001 |
| Responsable | Usuario 001 |
| Fecha | AAAA-MM-DD |

## Heurística de inferencia (proceso A — `brain/11 §2.1`)

1. Un beat visual por frase o cambio de sujeto (persona, lugar, año, objeto) — uno cada ~6–8 s de narración. Nunca sostener un plano más allá del **máximo de §2.2** para esa sección.
2. Todo `[EN PANTALLA]` del guion = beat, literal (B-roll).
2b. **Cold open — siempre esta forma, ~35–45 s en total:** 1 plano contextual (archivo/IA propio del sujeto) sostenido 8–10 s + 3–5 planos de hook (clips seleccionados + archivo, 4–6 s c/u, un pelín más rápido que el cuerpo) + el «giro» (~5 s) + cierre a cámara (~5–8 s) → corte seco a negro → **Bumper:** 1 beat `acamara` = wordmark `Conquest` + presentador, 3–6 s.
2c. **A-roll vs B-roll** (`brain/11 §1b`): `acamara` en cold open, bisagras/pivotes, beats de opinión y 1ª persona, **todo el cierre** y el CTA. B-roll en los tramos de archivo.
3. Toda persona / lugar / documento / institución / cifra nombrada → imagen o gráfico propio (B-roll).
4. `[EXPLICADOR]` — según el **contenido** del gráfico:
   - simple (proceso en 3 cajas, un antes/después) → **secuencia**: gráfico en fases + 2–4 planos de apoyo, ~4–6 sub-beats de ~5 s;
   - **denso** (dato, mapa, línea de tiempo, diagrama que hay que *leer*) → **un beat sostenido de 10–18 s** con movimiento interno (build o push lento) + b-roll antes y después, **nunca intercalado**. Si no se lee en 5 s, no cortes a los 5 s.
4b. **Un `id` de gráfico aparece una vez por vídeo.** Excepción marcada: `PROMISE n`→`PAY n`, o un `eco` en el cierre.
4c. **Un asset de archivo: ≤ 3× por vídeo, ≤ 2× por sección** (salvo pareja `PROMISE`→`PAY`). Un 4º uso lee como que te has quedado sin planos — rota el pool o corta a cámara. `assemble.py` lo avisa.
5. `[PROMISE]` y `[PAY]` → **mismo plano** las dos veces (B-roll). **Corte a cámara justo antes de cada uno** (§2.6).
6. Cierre / reflexión → **a cámara** en tramos de ~10–14 s, cortando a imágenes **ya vistas** (~4–6 s) como ilustración; sin archivo nuevo.
7. Toda cifra → gráfico propio con rótulo de fuente en pantalla.
8. Afirmación disputada o aproximada → rótulo de salvedad en pantalla.
9. **Nunca el mismo asset en dos beats seguidos** (salvo PROMISE→PAY). Ningún `id` de gráfico dos veces sin marcador (regla 4b). Si un tramo tiene pocos assets, cortar a cámara — no repetir plano.

**Cadencia de talking-head (`brain/11 §2.6`):** a cámara en cada **entrada de acto/sección**, cada **`[PROMISE]`** y **`[PAY]`**, **todo el cierre** y el CTA; y en cualquier tramo B-roll de ~60 s+ con pocos assets distintos. Objetivo **~30–40 %** del metraje a cámara.

**Estándar de duración de plano (`brain/11 §2.2` v2) — planifica por duración, no por número de beats:**

| Sección | plano: mín – **objetivo** – máx (s) |
|---|---|
| Cold open (35–45 s total) | 4 – **6** – 10 |
| Contexto / época | 4 – **6** – 10 |
| Actos narrativos (B-roll) | 4 – **7** – 11 |
| A cámara | 8 – **12** – 18 |
| Explicador / gráfico | denso: sostenido 10–**14**–18 · simple: sub-beats 3–**5**–8 |
| N teorías | 3 – **5** – 8 |
| Cierre (a cámara) | 8 – **12** – 18 |
| CTA | 15–25 s total · 1–2 planos |

≈ **8–10 s de media** → ~95–110 beats para 15 min, ~130 para 20, ~70 para 10. `assemble.py` fuerza: ningún plano B-roll < 2,8 s / a-cámara < 2,5 s (fusiona), ningún `gráfico` < 5 s ni un `id` repetido sin marcador (marca ⚠), ninguno no-a-cámara > 20 s / 2,5× su objetivo (⚠), un still nunca estático, vídeo B-roll sin Ken Burns, nunca el mismo asset seguido.

## A cámara (A-roll · narrador: Usuario 002 / Usuario 001)

En la espina, un beat `acamara` = se muestra la toma del narrador para ese hueco (`assemble.py` la recorta a `in`–`out`; sin Ken Burns, `motion` = `cut`). Encuadre y fondo son fijos de serie — no hace falta una fila por beat, solo la nota de estilo general:

| Aspecto | Valor |
|---------|-------|
| Encuadre | Plano medio corto, mirada a cámara |
| Fondo / luz | Set fijo de serie (`brain/03`) |
| Secciones a cámara | cold open · bumper · bisagras entre actos · beats de opinión / 1ª persona · todo el cierre · CTA |
| Toma | `assets/<toma>.trimmed.mp4` (Stage 8) — **una sola toma continua** por ahora |

## Timeline — la espina (una fila por beat, en orden de emisión)

**Esta tabla la parsea `tools/assemble.py` y `tools/edit_timeline.py`. Formato fijo:**

- **`#`** — número de beat, de corrido desde 1.
- **`in`** — inicio previsto, `m:ss` (una estimación; en Stage 9 `assemble.py` lo re-alinea a la voz real).
- **`dur`** — duración objetivo en segundos (entero).
- **`sección`** — una de: `cold open` · `bumper` · `pivote` · `contexto` · `acto N` · `explicador` · `teorías` · `cierre` · `cta`.
- **`tipo`** — `acamara` (A-roll: la toma del narrador) · `archivo` (foto/escaneo real) · `stock` (b-roll de vídeo genérico) · `kb` (Ken Burns sobre una fija) · `ia` (ilustración IA — lleva rótulo) · `gráfico` (motion propio) · `negro` (corte a negro).
- **`asset`** — el id que resuelve contra `07-selection.md` / `07-assets.md` (`E0XX_ai01_…`, `INTRO2`, `S09`, `G1`…). `—` para `acamara` y `negro`, o si aún no elegido.
- **`rótulo`** — texto en pantalla, o `—`. `Ilustración — Conquest` obligatorio para `ia`; salvedad para cifras dudosas.
- **`motion`** — token canónico: `push` (empuje 1.00→1.10) · `pan-h` · `pan-v` · `zoom` (a un detalle) · `cut` (hold seco, sin move). Es una **pista** — `assemble.py` la sobrescribe según el aspecto del asset (retrato → `pan-v`, panorámica → `pan-h`) y **nunca deja un still estático**. No uses `static`.
- **`marcador`** — `HOOK` · `PROMISE n` · `PAY n` · `EXPLICADOR n` · `—`. `PROMISE n` y su `PAY n` **usan el mismo `asset` y el mismo `motion`**.

| # | in | dur | sección | tipo | asset | rótulo | motion | marcador | guion (frag.) |
|---|----|-----|---------|------|-------|--------|--------|----------|---------------|
| 1 | 0:00 | 10 | cold open | acamara | — | — | cut | HOOK | «…» (narración a cámara) |
| 2 | 0:10 | 6 | cold open | stock | INTRO2 | — | cut | — | «…» (B-roll encima) |
| … | | | | | | | | | |

## Detalle por beat (para el humano — no se parsea)

| # | Visual necesario | Fuente / origen | Fuente [ID source-log] | Estado de derechos | Notas |
|---|------------------|-----------------|------------------------|--------------------|-------|
| 1 | | | | dominio público / CC-__ / licencia / cita | |

## Gráficos / motion — guion de cada uno

| id | Beat # | Qué muestra | Datos (fuente [ID]) | Rótulo de fuente/salvedad | Notas de estilo |
|----|--------|-------------|---------------------|---------------------------|-----------------|
| G1 | | | | | |

## Música / sonido

| Cue | Sección | Pista (librería + licencia) | Notas |
|-----|---------|-----------------------------|-------|
| M1 | Cold open | | sin letras |
| M2 | Narrativa | | lecho bajo la voz |
| M3 | Cierre | | entra en el "para llevar" |

## Faltantes / a conseguir

- [ ] …

## Gate Stage 6

- [ ] La tabla **Timeline — la espina** está completa: toda fila con `#`, `in`, `dur`, `sección`, `tipo`, `motion`, `marcador` (parsea sin errores)
- [ ] Reparto A-roll / B-roll marcado: `acamara` en cold open · bumper · bisagras · opinión/1ª persona · cierre · CTA (`brain/11 §1b`); ~30–45 % a cámara
- [ ] Todo visual con estado de derechos en `03-source-log.csv`
- [ ] Todo dato en gráfico con fuente [ID] y, si aplica, rótulo de salvedad
- [ ] `PROMISE n` y `PAY n` usan el mismo `asset` y el mismo `motion`
- [ ] Sin clip de película dramatizada como registro histórico
- [ ] Reenactments / IA / colorizado con `rótulo` en pantalla
- [ ] Cold open: 2–5 planos de hook (vídeo preferido) + bumper en negro; hook+bumper ≤ 50 s
- [ ] Nº de beats coherente con el ritmo objetivo para la duración
