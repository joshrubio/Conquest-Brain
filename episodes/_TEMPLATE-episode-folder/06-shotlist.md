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
2. Todo `[EN PANTALLA]` del guion = beat, literal.
2b. **Cold open:** el bloque `[HOOK VISUAL]` del guion = 2–5 beats, corte seco, **vídeo stock preferido**; el último es el «giro». **Bumper:** 1 beat = negro + marca `Conquest`, 3–6 s, sin motion.
3. Toda persona / lugar / documento / institución / cifra nombrada → imagen o gráfico propio.
4. `[EXPLICADOR]` → una secuencia motion-graphic / diagrama. Sin talking-head. Es el bloque visual más largo (~60–140 s).
5. `[PROMISE]` y `[PAY]` → **mismo plano** las dos veces (rima visual).
6. Cierre / reflexión → reusar imágenes ya vistas; sin archivo nuevo. Opción: único plano de narrador a cámara, en el "para llevar".
7. Toda cifra → gráfico propio con rótulo de fuente en pantalla.
8. Afirmación disputada o aproximada → rótulo de salvedad en pantalla.

**Ritmo objetivo (v1, calibrar en `brain/11 §4`):** cold open 10–12 beats/min (2–5 planos en 20–40 s) · bumper 1 plano 3–6 s · contexto 6–8 · narrativa 7–9 · explicador 3–5 · módulo teorías 8–10 · cierre 4–6 · CTA 1–2. Episodio de 20 min ≈ 150–180 beats (con reutilización).

## A cámara (narrador del episodio: Usuario 002 / Usuario 001)

| Beat / sección | Encuadre | Fondo / luz | Guion (referencia) | Notas |
|----------------|----------|-------------|--------------------|-------|
| (Opción) Para llevar | Plano medio | Fondo neutro de serie | Sección 3 | Único momento a cámara; refuerza que es idea propia |

## Timeline — la espina (una fila por beat, en orden de emisión)

**Esta tabla la parsean `tools/assemble.py` y `tools/edit_timeline.py`. Formato fijo** (ver `templates/shotlist-broll.md` para la definición de cada columna):

- `#` de corrido · `in` `m:ss` (estimación; se re-alinea en Stage 9) · `dur` segundos enteros
- `sección`: `cold open`·`bumper`·`pivote`·`contexto`·`acto N`·`explicador`·`teorías`·`cierre`·`cta`
- `tipo`: `archivo`·`stock`·`kb`·`ia`·`gráfico`·`negro`
- `asset`: id que resuelve contra `07-selection.md` (`—` si aún no elegido)
- `motion`: `push`·`pan-h`·`pan-v`·`static`·`zoom`·`cut`
- `marcador`: `HOOK`·`PROMISE n`·`PAY n`·`EXPLICADOR n`·`—` (PROMISE n y PAY n → mismo `asset` y `motion`)

| # | in | dur | sección | tipo | asset | rótulo | motion | marcador | guion (frag.) |
|---|----|-----|---------|------|-------|--------|--------|----------|---------------|
| 1 | 0:00 | 12 | cold open | ia | E0XX_ai01_… | Ilustración — Conquest | static | HOOK | «…» |
| 2 | 0:12 | 10 | cold open | stock | INTRO2 | — | cut | — | «…» |
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

- [ ] La tabla **Timeline — la espina** está completa y parsea sin errores
- [ ] Todo visual con estado de derechos en `03-source-log.csv`
- [ ] Todo dato en gráfico con fuente [ID] y, si aplica, rótulo de salvedad
- [ ] `PROMISE n` y `PAY n` usan el mismo `asset` y el mismo `motion`
- [ ] Sin clip de película dramatizada como registro histórico
- [ ] Reenactments / IA / colorizado marcados para rótulo en pantalla
- [ ] Cold open: 2–5 planos de hook (vídeo preferido) + bumper en negro; hook+bumper ≤ 50 s
- [ ] Nº de beats coherente con el ritmo objetivo para la duración
