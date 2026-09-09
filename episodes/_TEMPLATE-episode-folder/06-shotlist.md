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

1. Un beat visual por frase o cambio de sujeto — uno cada ~6–8 s. Nunca sostener un plano más allá del máximo de §2.2.
2. Todo `[EN PANTALLA]` del guion = beat, literal.
2b. **Cold open — siempre esta forma, ~35–45 s:** 1 plano contextual (archivo/IA propio) 8–10 s + 3–5 planos de hook (4–6 s) + el «giro» (~5 s) + cierre a cámara (~5–8 s) → negro → **Bumper:** 1 beat `acamara`, wordmark + presentador, 3–6 s.
2c. **A-roll vs B-roll** (`brain/11 §1b`): `acamara` en cold open · bumper · bisagras · opinión / 1ª persona · **todo el cierre** · CTA.
3. Toda persona / lugar / documento / institución / cifra nombrada → imagen o gráfico propio (B-roll).
4. `[EXPLICADOR]` — gráfico **simple** → secuencia de sub-beats (~5 s); gráfico **denso** (dato/mapa/diagrama que hay que leer) → **un beat sostenido 10–18 s** con build interno + b-roll antes/después, nunca intercalado.
4b. **Un `id` de gráfico, una aparición** — salvo callback marcado (`PROMISE`/`PAY`/`eco`).
4c. **Un asset de archivo: ≤ 3× por vídeo, ≤ 2× por sección** (pareja `PROMISE`→`PAY` aparte). `assemble.py` avisa del 4º uso.
5. `[PROMISE]` y `[PAY]` → **mismo plano** las dos veces (B-roll). Corte a cámara justo antes de cada uno.
6. Cierre / reflexión → **a cámara** en tramos de ~10–14 s, cortando a imágenes ya vistas (~4–6 s); sin archivo nuevo.
7. Toda cifra → gráfico propio con rótulo de fuente en pantalla.
8. Afirmación disputada o aproximada → rótulo de salvedad en pantalla.
9. **Nunca el mismo asset en dos beats seguidos** (salvo PROMISE→PAY). Ningún `id` de gráfico dos veces sin marcador (regla 4b).

**Duración de plano (`brain/11 §2.2` — planifica por duración, no por número):** cold open 4–**6**–10 s · contexto 4–**6**–10 · narrativa B-roll 4–**7**–11 · a cámara 8–**12**–18 · gráfico denso sostenido 10–**14**–18 · gráfico simple 3–**5**–8 (sub-beats) · teorías 3–**5**–8 · cierre 8–**12**–18 · CTA 15–25 s total. ≈ 8–10 s de media → ~95–110 beats para 15 min. **Talking-head** en cada entrada de acto, cada PROMISE/PAY, todo el cierre, CTA (`brain/11 §2.6`); ~30–40 % a cámara. `assemble.py` fuerza: B-roll < 2,8 s / a-cámara < 2,5 s se fusiona, `gráfico` < 5 s o `id` repetido sin marcador marca ⚠, no-a-cámara > 20 s marca ⚠, still nunca estático, vídeo B-roll sin Ken Burns.

## A cámara (narrador del episodio: Usuario 002 / Usuario 001)

| Beat / sección | Encuadre | Fondo / luz | Guion (referencia) | Notas |
|----------------|----------|-------------|--------------------|-------|
| (Opción) Para llevar | Plano medio | Fondo neutro de serie | Sección 3 | Único momento a cámara; refuerza que es idea propia |

## Timeline — la espina (una fila por beat, en orden de emisión)

**Esta tabla la parsean `tools/assemble.py` y `tools/edit_timeline.py`. Formato fijo** (ver `templates/shotlist-broll.md` para la definición de cada columna):

- `#` de corrido · `in` `m:ss` (estimación; se re-alinea en Stage 9) · `dur` segundos enteros
- `sección`: `cold open`·`bumper`·`pivote`·`contexto`·`acto N`·`explicador`·`teorías`·`cierre`·`cta`
- `tipo`: `acamara` (A-roll: la toma del narrador, `asset` = `—`)·`archivo`·`stock`·`kb`·`ia`·`gráfico`·`negro`
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
