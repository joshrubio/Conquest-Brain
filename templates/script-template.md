---
doc: script-template
summary: "Full narration + on-screen cues + inline [S..] tags. Header for close form / narrator / version."
stage: [4]
fills: "05-script.md"
rule: [02, 08, 09]
authority: template
---

# Guion — E0XX «<título provisional>»

> Stage 4. Estructura: cold open → pivote a contexto → narrativa cronológica (con interludios explicadores + foreshadowing) → cierre → CTA. Ver `brain/02-content-format.md` (v1).
> Tono: `brain/08-tone-of-voice.md`. Formas de cierre A/B/C: `brain/09-reflection-rules.md`. Menús de frases: `research/dieck-docs/phrasebook.md`.
> Cada afirmación factual lleva un tag `[S..]` que resuelve contra `03-source-log.csv`.

| Campo | Valor |
|-------|-------|
| ID episodio | E0XX |
| Versión | v__ |
| Fecha | AAAA-MM-DD |
| Guionista | Usuario 001 |
| Narrador | Usuario 002 / Usuario 001 |
| **Forma del cierre** | A / B / C — fijada en el brief |
| **Registro(s) del cierre** | psicológico / práctico / filosófico / religioso — máx. 2, fijados en el brief (`brain/09`) |
| Recuento de palabras | … |
| Duración estimada | … min |

---

## Presupuesto por sección

Ritmo de narración objetivo: **~155 palabras/min**. Elegir columna según duración objetivo.

| Sección | % metraje | 15 min (~2.325 pal) | 20 min (~3.100 pal) | 25 min (~3.875 pal) |
|---------|-----------|---------------------|---------------------|---------------------|
| 0. Cold open (hook narrativo + hook visual) | 3–6% | 55–100 pal · 20–40 s | 70–120 pal · 25–42 s | 80–130 pal · 28–45 s |
| 0b. Bumper (presentador + canal, en negro) | — | 6–12 pal · 3–6 s | 6–12 pal · 3–6 s | 6–12 pal · 3–6 s |
| 1. Pivote a contexto + época | 10–20% | 250–460 pal | 350–620 pal | 450–780 pal |
| 2. Narrativa cronológica | 55–70% | 1.300–1.630 pal | 1.700–2.170 pal | 2.150–2.700 pal |
| 3. Cierre (forma A/B/C) | 8–20% | 200–460 pal | 250–620 pal | 320–780 pal |
| 4. CTA coda | ~1% | 20–35 pal · ~10 s | 20–35 pal · ~10 s | 20–35 pal · ~10 s |

**Dentro de la narrativa:**
- **Interludios explicadores:** 2–4 por episodio · ~150–350 palabras cada uno (60–140 s). Cuentan dentro del % de narrativa.
- **Foreshadowing:** 3–6 promises · ~1 frase cada uno · todos pagados.
- **Módulo «las N teorías» (opcional):** 10–20% del metraje cuando se usa; sustituye parte del bloque de cierre/investigación.

---

## Formato de las columnas

```
[NARRACIÓN]  Texto que dice el narrador del episodio (Usuario 001 o Usuario 002), tal cual.
[EN PANTALLA] Documento / foto / dato / rótulo. Fuente [S..] + estado de derechos.
[NOTA]       Indicaciones de tono, pausa, música, edición.
[EXPLICADOR] Interludio didáctico. Señalizar entrada y salida. Todo dato con [S..].
[PROMISE] / [PAY]  Foreshadowing: marca dónde se promete y dónde se paga.
[S..]        Tag de fuente al final de la frase factual.
```

**Cabeceras de sección (`## N. …`):** cada una debe **contener una de estas palabras clave** —
`COLD OPEN` · `BUMPER` · `PIVOTE` · `CONTEXTO` · `NARRATIVA` · `TEORÍAS` · `CIERRE` · `CTA`
(o `Acto N` dentro de la narrativa). `tools/script_review.py` clasifica cada sección por su
título; una cabecera sin palabra clave pierde su ficha de producción y el chequeo del CTA
(y antes del arreglo de 2026-09 se tragaba la sección entera como "apéndice"). Puedes añadir
un subtítulo — `## 2. NARRATIVA — una sola vida` — pero **no quites la palabra clave**.

---

## 0. COLD OPEN / HOOK  —  20–40 s (tope 45 s)

**Hook narrativo** (55–100 pal). Elegir una apertura (adaptar, no copiar — banco en `phrasebook.md §1`):
- Misterio / desaparición · Afirmación en disputa · Escena en acción · Suceso extraño · Pregunta + tesis · Imagen de contraste

**Cerrar el hook anunciando qué hará el video** (`phrasebook.md §2`): "en este episodio reconstruimos…", "aquí van las tres versiones del caso…", "para entenderlo, primero el contexto".

[NARRACIÓN]
…

[HOOK VISUAL]  2–5 planos, corte seco al ritmo de la narración, cada uno ilustra una imagen concreta que la voz nombra. **Vídeo stock preferido** (`tools/pull_assets.py` — beats `stock` traen vídeo primero). ~3–6 s/plano, en escalada; el último es el «giro» y puede aguantar ½ s más antes del corte a negro. Archivo/IA permitido con rótulo (`brain/15`); stock siempre genérico (`brain/12`).
- v1 — …
- v2 — …
- v3 — …

[NOTA] Sin intro de canal antes del hook. No exagerar respecto a lo que prueban las fuentes. Momento de más cortes del episodio (10–12 beats/min).

---

## 0b. BUMPER  —  3–6 s, en negro

El beat de reinicio entre hook e historia (Dieck lo hace así — la marca aparece **después** del hook, nunca antes).

[EN PANTALLA] Corte a **negro**. Aparece la marca **`Conquest`**.

[NARRACIÓN] Una línea del presentador: «Soy [nombre].»

[NOTA] Un tono grave bajo o un beat de silencio. Sin animación de logo, sin sting largo. El pivote a contexto entra en el plano siguiente. Todo hasta aquí (hook + bumper) ≤ 50 s, objetivo ~35 s; el contexto corre para 0:45–0:50.

---

## 1. PIVOTE A CONTEXTO + ÉPOCA

**Frase bisagra** (`phrasebook.md §3`): "pero para saber si esto es cierto, necesitamos contexto" · "imagina que estás en <año>" · "lo que viene nos ayudará a entender <la pregunta del episodio>".

[NARRACIÓN]
Época, institución, personas, lo que estaba en juego. [S..]

[EXPLICADOR] (si el primer concepto va aquí)
- Entrada (`phrasebook.md §4`): "por si no sabes qué es <X>, lo explico en breve" · "si no conoces a <X>, contexto rápido".
- Salida (`phrasebook.md §5`): "ahora que tienes esto, volvamos a la historia" · "con todo esto en mente, nos trasladamos a <año>".
- Todo dato del interludio: [S..].

[EN PANTALLA]
…

---

## 2. NARRATIVA CRONOLÓGICA

> Personas: nacimiento → detalle de infancia que prefigura → ascenso → cima → giro/caída → desenlace.
> Eventos: época → preparación → el hecho beat-by-beat → consecuencias → investigación.

### Acto 1 — …

[NARRACIÓN]
… con atribución sobre la marcha («según los registros…», «en su declaración…»). [S..]

[PROMISE] (`phrasebook.md §6`) "quiero que recuerdes este detalle porque va a importar" — prometer aquí, pagar en Acto __.

### Acto 2 — …

[NARRACIÓN]
… [S..]

[EXPLICADOR] mini-cátedra (concepto necesario). Entrada + salida señalizadas. Cada dato [S..].

### (Opcional) Interludio reflexivo con respuesta diferida

[NARRACIÓN]
Plantear la pregunta universal que abre el caso y **diferir la respuesta** (`phrasebook.md §8`): "esto abre una pregunta interesante: <…>. En un momento te digo qué pienso yo."

### Acto 3 — Punto de giro

[NARRACIÓN]
… [S..]

### Acto 4 — Desenlace

[NARRACIÓN]
… resultado / veredicto / cierre documentado. Nombrar lo que no se sabe. [S..]

[PAY] (`phrasebook.md §7`) pagar aquí los foreshadowings: "¿recuerdas lo que dije sobre <X>? Aquí es donde importa."

### (Opcional) Módulo «las N teorías / los N responsables»

[NARRACIÓN]
Solo si el caso está genuinamente en disputa (`phrasebook.md §13`). Intro: "hay <N> versiones que se sostienen; vamos una por una."
Cada posición: se presenta, se pesa, se cierra honestamente — "no hay pruebas concluyentes de…", "esto sí está documentado…". [S..]

---

## 3. CIERRE  ·  FORMA: ___

### Si FORMA A — Reflexión + para llevar (`phrasebook.md §14`)
[NARRACIÓN]
Transición fuera de la narrativa → nombrar UN ancla → 2-3 observaciones ancladas a escenas ya vistas → ensanchar a lo general → UNA idea aplicable.
- **El ancla** = un mecanismo psicológico, o una idea filosófica/religiosa que el caso plantea (registro fijado en el brief; máx. 2). `brain/09` §"The four registers".
- Marco interpretativo obligatorio: "una lectura posible…", "para los estoicos…".
- Autoridad externa nombrada + [S..] si se cita teoría / estudio / pensador / escuela / texto religioso (`phrasebook.md §11` / §11b).
- Idea filosófica o religiosa: **siempre con dueño** ("Frankl sostiene…", "Eclesiastés lo dice así…"); presentada como *una idea*, nunca como la verdad ni como llamada a creer.
- Para llevar: una sola idea, ≤ 90 s, pasa el test quirúrgico.
- **Menos moralina que Dieck**: enunciar el mecanismo o la tensión, no predicar el deber ni la fe (`brain/08 §1`).

### Si FORMA B — Lección distribuida (`phrasebook.md §15`)
[NOTA] La reflexión ya se entregó en 2-3 piezas dentro de la narrativa (Acto __, __, __).
[NARRACIÓN]
Bisagras de entrega usadas: "con lo que vimos, se entiende la primera lección…", "aquí entra la segunda…".
Cierre elegíaco / recapitulativo, NO un «para ti»: "aunque <…> fue breve, <…> permanece".

### Si FORMA C — Pregunta abierta (`phrasebook.md §16`)
[NARRACIÓN]
Recapitular qué SÍ está establecido → entregar el juicio al espectador con una pregunta real: "¿tú qué opinas? ¿quién crees que…?".
[NOTA] Sin veredicto implícito por música/montaje que el guion no defienda.

### (Opcional, cualquier forma) Coda emocional
[NARRACIÓN] Viñeta humana breve, verificada y veraz. No debe distorsionar ni pesar más que el caso documentado. [S..]

---

## 4. CTA CODA  (~10–20 s) — el closing ask, siempre presente (`brain/02` §4a)

> **Máximo dos CTA por episodio — nunca más.** Este de aquí (el closing ask) va siempre. El segundo, opcional, es el *mid-episode nudge* (§4b más abajo) — solo si el episodio tiene un punto que lo gane, cada capítulo es distinto. Revisa el tag `Tipo de CTA:` del closing ask del episodio anterior: no repitas tipo en ese slot dos veces seguidas, y no copies la frase — varía el fraseo.

[NOTA] Tipo de CTA: <like|suscribete|compartir|comentar|notificaciones|whatsapp>

[NARRACIÓN]
Después de que el cierre aterrice. CTA suave del canal, separado de la idea, ligado a lo que este episodio concreto acaba de entregar — no genérico. Tiende a `suscribete`/`notificaciones`/`whatsapp` (el ask de "sigue viendo este canal"), pero cualquier tipo vale si el caso lo justifica.
Ejemplo (tipo `comentar`, ligado al caso): «Si tú te dieras diez años más para algo — ¿para qué serían? Cuéntamelo en los comentarios, los leo todos.»

[EN PANTALLA] Rótulo opcional «Fuentes principales».

<!-- Mid-episode nudge (opcional, va DENTRO de un Acto de la narrativa, no aquí) — brain/02 §4b:
Justo tras un [PAY] o la salida señalizada de un [EXPLICADOR]. Tipo más ligero que el closing ask (like/comentar), nunca el mismo tipo que el closing ask de este episodio.
[NOTA] Tipo de CTA: <like|comentar>
[NARRACIÓN] Una frase, atada a lo que se acaba de decir — no genérica.
-->

<!-- Plug de producto/patrocinio — ocupa el slot del mid-episode nudge, no se suma — brain/02 §4c, brain/05 §0:
[NOTA] Tipo de CTA: producto-propio  (o: patrocinio (<marca>))
[NARRACIÓN] Disclosure hablado primero — "esto lo hace posible…" / "esto es publicidad" — nunca disfrazado de contenido editorial.
-->


---

## Índice de tags de fuente usados

| Tag | Afirmación | Fuente en source-log |
|-----|-----------|----------------------|
| S01 | | |
| S02 | | |

## Foreshadowing — registro

| # | Se promete en | Se paga en | Idea |
|---|---------------|-----------|------|
| 1 | | | |

## Interludios explicadores — registro

| # | Concepto | Acto | Palabras | Entrada/salida señalizadas |
|---|----------|------|----------|----------------------------|
| 1 | | | | ☐ |

## Autorrevisión del guionista (antes de pasar a fact-check)

- [ ] Recuento de palabras dentro del presupuesto de la duración objetivo
- [ ] Todo `[S..]` resuelve contra el source-log
- [ ] Orden: cold open (hook narrativo + `[HOOK VISUAL]` 2–5 planos) → bumper en negro → contexto → narrativa → cierre → CTA
- [ ] Cold open ≤ 45 s; hook + bumper ≤ 50 s; contexto corre para 0:50
- [ ] El hook se paga en el cuerpo
- [ ] 3-6 foreshadowings, todos pagados (tabla arriba)
- [ ] 2-4 interludios explicadores, señalizados entrada y salida (tabla arriba)
- [ ] Cierre en la forma fijada (A/B/C) y el/los registro(s) fijados (máx. 2); si B, las 2-3 piezas están identificadas
- [ ] Toda idea filosófica/religiosa lleva dueño + [S..]; presentada como idea, no como verdad; sin sermón ni llamada a creer
- [ ] Sin película dramatizada usada como registro histórico
- [ ] Sin moralina, sin desprecio al sujeto, sin clickbait
- [ ] Cumple `brain/08` y `brain/09`
- [ ] Español neutro-internacional; leído en voz alta sin tropiezos
