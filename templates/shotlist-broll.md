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

1. Un beat visual cada ~2–3 frases, o cuando cambia el sujeto de la frase.
2. Todo `[EN PANTALLA]` del guion = beat, literal (B-roll).
2b. **Cold open:** narración **a cámara** (`acamara`); el bloque `[HOOK VISUAL]` = 2–5 beats de B-roll cortados encima, corte seco, **vídeo stock preferido**, el último es el «giro». **Bumper:** 1 beat `acamara` = wordmark `Conquest` + presentador, 3–6 s.
2c. **A-roll vs B-roll** (`brain/11 §1b`): `acamara` en cold open, bisagras/pivotes, beats de opinión y 1ª persona («yo creo…», «me llama la atención…»), **todo el cierre** y el CTA. B-roll en los tramos de archivo (fechas, cronología, obra, evento) y **todo `[EXPLICADOR]`**. ~30–45 % a cámara.
3. Toda persona / lugar / documento / institución / cifra nombrada → imagen o gráfico propio (B-roll).
4. `[EXPLICADOR]` → una secuencia motion-graphic / diagrama. Sin talking-head. Es el bloque visual más largo (~60–140 s).
5. `[PROMISE]` y `[PAY]` → **mismo plano** las dos veces (B-roll, aunque caigan en un tramo a cámara).
6. Cierre / reflexión → **a cámara**, cortando a imágenes **ya vistas** como ilustración; sin archivo nuevo.
7. Toda cifra → gráfico propio con rótulo de fuente en pantalla.
8. Afirmación disputada o aproximada → rótulo de salvedad en pantalla.

**Ritmo objetivo (v1, calibrar en `brain/11 §4`):** cold open 10–12 beats/min · bumper 1 plano 3–6 s · contexto 6–8 · narrativa 7–9 (a cámara en las bisagras) · explicador 3–5 · cierre 3–5 a cámara · CTA 1–2. Episodio de 20 min ≈ 150–180 beats (con reutilización). Los tramos a cámara cortan más lento (mantener la cara 4–8 s).

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
- **`motion`** — token canónico: `push` (empuje 1.00→1.10) · `pan-h` · `pan-v` · `static` · `zoom` (a un detalle) · `cut` (clip de vídeo, sin move).
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
