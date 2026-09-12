# Fact-check — E003 «Tulipomanía»

> `brain/14`. **Fully automated, no human step.**
>
> - **L1** — `python tools/factcheck.py 05-script.md 03-source-log.csv > 04-factcheck-auto.md`
> - **L2** — the agent runs `templates/fact-check-auto-prompt.md`, pastes Part A + C below, **applies Part B to `05-script.md`**, fills the Changelog.
>
> **Gate:** L1 `PASS` + Changelog written → Stage 6.
>
> Track: Documental (no citation-shelf / tabla 5b — es mecanismo exclusivo de Ensayo).

## Layer 1 — deterministic

```
# Fact-check — Layer 1 (deterministic)

- Script: `episodes/E003-tulipomania/05-script.md`
- Source-log: `episodes/E003-tulipomania/03-source-log.csv`
- Tags used: 53 (12 unique)
- Sources: 13 — A:7, B:5, C:1
- Orphan-claim candidates: 7

## Orphan-claim candidates (human: tag or confirm non-factual)

- L29: [HOOK VISUAL] 3 planos, corte seco al ritmo de la voz.
- L32: - v3 · «giro» (~4 s) — el Semper Augustus en una lámina de época, la variedad más cara de todas; aguanta ½ s → corte a negro.
- L86: Así que la joya más cara de toda la República era, sin que nadie lo supiera, una planta enferma muriéndose despacio y bonita mientras tan…
- L89: Ahí tienes la respuesta que prometí: trescientos años pagando fortunas por una flor «perfecta», sin saber que lo perfecto era, literalmen…
- L246: - Extraer del libro completo de Goldgar (no solo reseñas) 2–3 nombres o casos concretos de comerciantes documentados.
- L248: - Subir de Tier C a A/B el origen del comercio vía el jardín de Clusius, o dejarlo permanentemente marcado como tradición.
- L249: - Afinar (o decidir mantener abierto) el rango en dólares de S08 — actualmente deliberadamente amplio por la variación real entre metodol…

## Warnings

- source S07 defined but never cited in the script

## Verdict: **PASS**
```

*(Nota: el `FAIL` inicial — `[S07]` citado solo, sin compañía Tier A/B — se resolvió durante el propio pase L2: ver Changelog. S07 sigue en `03-source-log.csv` por trazabilidad de investigación, pero ya no se cita en el guion.)*

Resolución de los 7 candidatos a orphan-claim (ninguno requería nuevo tag):
- **L29, L32** — dirección de plano/producción (`[HOOK VISUAL]`), no son afirmaciones narradas. Confirmado no-factual.
- **L86, L89** — continuación/paráfrasis, en el mismo párrafo, de la afirmación del virus ya citada `[S06]` dos frases antes. Confirmado, cubierto por el tag existente.
- **L246, L248, L249** — notas de producción internas («Mejoras opcionales»), no forman parte del guion narrado. Confirmado no-factual.

## Layer 2 — analysis (Parts A + C of the prompt)

### 1. Afirmaciones factuales

| # | Sección | Afirmación (resumida) | [S..] | ¿La fuente respalda? | Veredicto |
|---|---------|------------------------|-------|------------------------|-----------|
| 1 | Cold open | Un Semper Augustus llegó a costar como una mansión de canal | S01, S08 | Sí | respalda |
| 2 | Cold open | Anécdota del marinero que comió un bulbo y fue a la cárcel | S02 | Sí — como relato de Mackay, no como hecho de 1637 | respalda |
| 3 | Pivote | Fundación de la VOC (1602), primera corporación con acciones negociables, primera bolsa | S11 | Sí (Petram) | respalda |
| 4 | Pivote | Riqueza de Ámsterdam, mecenazgo de pintores, banco central, canales | S12 | Sí (Schama) | respalda |
| 5 | Pivote | Clusius planta bulbos en el jardín de Leiden, 1593 | S01 | Sí | respalda |
| 6 | Pivote | Jardín de Clusius asaltado; bulbos robados siembran el comercio | *(sin tag)* | No verificable — tradición sin acta | ya framed on-screen como tradición no confirmada |
| 7 | Pivote | Bulbos con pétalos en llamas ya caros en 1620s | S01 | Sí | respalda |
| 8 | Explicador 1 | Venta por catálogo (tulpenboek) + contrato a futuro | S05 | Sí (Rijksmuseum) | respalda |
| 9 | Acto 1 | Semper Augustus: pétalos únicos, el más codiciado | S01 | Sí | respalda |
| 10 | Acto 1 | Nadie sabía por qué "rompían" de color | S06 | Sí | respalda |
| 11 | Explicador 2 | Virus (pulgones) descubierto por injerto en 1928 | S06 | Sí (Cayley/John Innes) | respalda |
| 12 | Acto 2 | Witte Croonen: 64 → >1.600 florines, 5-feb-1637, ~26× | S01, S10 | Sí — confirmado también por Garber, independiente de Goldgar | respalda |
| 13 | Acto 2 | Artesano cualificado ganaba ~300 florines/año | S08 | Aproximado, Tier C, ya explícitamente cualitativo en pantalla | respalda (matizado) |
| 14 | Acto 2 | Tabernas-bolsa, contratos de mano en mano, «windhandel» | S01 | Sí | respalda |
| 15 | Acto 3 | 3-feb-1637, Haarlem: compradores se niegan a pagar | S01 | Sí | respalda |
| 16 | Acto 3 | 5-feb-1637, Alkmaar: subasta de huérfanos, 99 lotes, tabernero fallecido, 7 hijos | S09 | Sí | respalda |
| 17 | Acto 3 | Cifras: Admirael van Enkhuizen 5.200; dos Virrey 4.203 y 3.000; total ~90.000 florines | S09 | Sí | respalda |
| 18 | Acto 3 | Precios caen hasta 95% en los casos más citados | S01 | Sí | respalda |
| 19 | Acto 3 | Gremio de Haarlem: contratos post-30-nov anulables pagando fracción | S01, S03 | Sí | respalda |
| 20 | Acto 4 | La versión popular viene del libro de Mackay, 1841 | S02 | Sí | respalda |
| 21 | Acto 4 | Mackay se apoya en panfletos satíricos de 1637, no en archivo | S02, S04 | Sí | respalda |
| 22 | Acto 5 | Goldgar revisa archivo notarial, no encuentra bancarrotas | S01, S04 | Sí — cita verificada: "I couldn't find anybody that went bankrupt" | respalda |
| 23 | Acto 5 | Mercado acotado a comerciantes con dinero, no "todo el país" | S01, S04 | Sí | respalda |
| 24 | Acto 5 | Disputas de confianza rota resueltas en tribunales locales | S01, S04 | Sí | respalda |
| 25 | Acto 6 | Thompson (2007): contratos reinterpretados de facto como opciones | S03 | Sí | respalda |
| 26 | Pay HOOK | El marinero no aparece en registro de 1637, solo en Mackay 1841 | S02 | Sí — el anecdotario más antiguo localizado es un diario de viaje de 1705, no un registro de 1637; Mackay lo toma de Beckmann | respalda |
| 27 | Cierre | La «falacia narrativa»: relatos simples/morales se sienten más verdaderos y se repiten más | S13 | Sí (Kahneman, atribuido a Taleb) | respalda — corrección aplicada (ver Changelog) |

### 2. Interpretación presentada como hecho

| # | Línea | Frase | Reescritura con marco |
|---|-------|-------|------------------------|
| 1 | Acto 4 | "Mackay tenía un motivo para encontrar... un espejo conveniente" — se afirmaba como hecho psicológico conocido, sin marco | Reescrito a "Una lectura posible es que encontrara... un espejo conveniente" — ver Changelog |

Resto del guion: la reflexión de cierre ya usa correctamente "una lectura posible es esta" (`brain/01` §5) — sin cambios.

### 3. Citas textuales

No hay citas textuales entre comillas atribuidas a una persona con "dijo"/"escribió" + verbatim en el guion (las citas de Goldgar usadas como respaldo en el source-log no se reproducen palabra por palabra en pantalla). Tabla no aplica.

### 4. Afirmaciones que deberían ir matizadas

| # | Línea | Afirmación | Matiz sugerido |
|---|-------|-----------|-----------------|
| 1 | Cold open / Acto 1 | Equivalencia en dólares de hoy del Semper Augustus | Ya matizado en pantalla ("las conversiones varían muchísimo…"); decisión de fact-check: mantener el rango abierto, no afinar a una cifra (pendiente resuelto) |
| 2 | Acto 2 | Salario anual de un artesano (~300 florines) | Ya matizado ("alrededor de"); Tier C aceptado como comparación cualitativa, no carga central |

### 5. Psicología popular / conceptos

| # | Línea | Afirmación | Nota |
|---|-------|-----------|------|
| 1 | Cierre | Se nombra explícitamente la «falacia narrativa» (Kahneman/Taleb) como mecanismo del cierre | Concepto ahora nombrado con precisión y con `[S13]` propio — resuelve el pendiente `brain/09` A6 que dejó abierto el guionista |

### 6. Legal / ético / independencia

| # | Línea | Riesgo | Tipo |
|---|-------|--------|------|
| — | — | Ninguno detectado | — |

Sujeto: episodio histórico (1637) + un autor fallecido (Mackay, m. 1889) citado únicamente como origen documentado del mito, nunca como respaldo de hechos. Sin personas vivas nombradas, sin menores, sin tema sensible (violencia/suicidio/abuso), sin sponsor. `brain/04` checklist limpio para Stage 5; el tick formal de independencia/COI + derecho de réplica sigue pendiente de Stage 11 como en todo episodio (no es un flag nuevo de este pase).

### Resumen (Parte C)

- Afirmaciones factuales: 27 · `desajuste`: 0 · `sin tag` (ya framed on-screen): 1 · `no se puede saber por la descripción`: 0
- Correcciones aplicadas: 9 · Cortes: 0 · Ítems para revisión humana: 0

## Changelog — corrections applied to 05-script.md

| # | Antes (verbatim) | Después | Motivo |
|---|------------------|---------|--------|
| 1 | `...el lugar más rico e innovador del planeta [S07].` | `...el lugar más rico e innovador del planeta [S12].` | S07 es Tier C y era el único respaldo — retag a Schama, *The Embarrassment of Riches* (Tier B) |
| 2 | `...la primera bolsa de valores de la historia [S07].` | `...la primera bolsa de valores de la historia [S11].` | Ídem — retag a Petram, *The World's First Stock Exchange* (Tier B), confirmado por búsqueda: VOC 1602, primera empresa en emitir acciones al público |
| 3 | `...encuentra clientes con dinero de sobra para pagar un retrato [S07].` | `...encuentra clientes con dinero de sobra para pagar un retrato [S12].` | Ídem — retag a Schama |
| 4 | `...ese algo fue, contra todo pronóstico, una flor [S07].` | `...ese algo fue, contra todo pronóstico, una flor [S12].` | Ídem — retag a Schama |
| 5 | `...traída de más al este [S07]. Se cuenta que su jardín fue asaltado varias veces...` | `...traída de más al este [S01]. Se cuenta que su jardín fue asaltado varias veces... como tradición, sin cita de respaldo.` | Introducción de Clusius retagueada a S01 (Goldgar, ya cubre el contexto); el robo del jardín queda explícitamente sin cita — es tradición no confirmada, ya se framea así en pantalla, no puede sostenerse ni siquiera en Tier C sin acta |
| 6 | `...cuánto habían prosperado [S07].` | `...cuánto habían prosperado [S12].` | Ídem — retag a Schama |
| 7 | `...veintiséis veces más en poco más de un mes [S01].` | `...veintiséis veces más en poco más de un mes [S01][S10].` | Confirmación independiente de la cifra del Witte Croonen contra Garber (no solo Goldgar) — resuelve el pendiente del guionista |
| 8 | `...Mackay tenía un motivo para encontrar, en un episodio holandés de dos siglos atrás, un espejo conveniente de sus propias advertencias. Una forma de ilustrar, de manera tal vez exagerada y satirica, los peligros de la avaricia y la malversación del dinero. Miralo como una critica social, despues de todo, Mackay era un periodista.` | `Una lectura posible es que encontrara, en un episodio holandés de dos siglos atrás, un espejo conveniente para sus propias advertencias — una forma de ilustrar, quizás de manera exagerada y satírica, los peligros de la avaricia y la malversación del dinero. Después de todo, Mackay era periodista, no historiador de archivo, y esto se lee mejor como una crítica social de su época que como un reportaje de la de 1637.` | El motivo de Mackay se afirmaba como hecho psicológico conocido — reescrito como interpretación explícita (`brain/01` §5); corregidos de paso los tipos "epoca/satirica/despues/critica" y el uso irregular de "Mito" con mayúscula |
| 9 | `Una lectura posible es esta: un relato simple y con una lección moral clara como el de Mackay es más fácil de repetir y más útil para quien lo cuenta... Y eso no es exclusivo de Charles Mackay ni de 1841: es, en general, cómo han sobrevivido muchas historias a lo largo del tiempo — no porque sean ciertas de cabo a rabo, sino porque son más cómodos entender que la realidad [S04].` | `Una lectura posible es esta, y tiene nombre propio en psicología: la «falacia narrativa»... [S13]. ... Y eso no es exclusivo de Charles Mackay ni de 1841: así sobreviven muchas historias a lo largo del tiempo — no porque sean ciertas de cabo a rabo, sino porque son más fáciles de entender que la realidad [S04][S13].` | Ancla el mecanismo del cierre a una fuente teórica propia (Kahneman/Taleb, `brain/09` A6) — resuelve el pendiente del guionista; también corrige "más cómodos" → "más fáciles" (concordancia) |

`03-source-log.csv`: añadidas 4 filas — `S10` (Garber, Witte Croonen), `S11` (Petram, VOC/bolsa), `S12` (Schama, Siglo de Oro/estatus), `S13` (Kahneman, falacia narrativa). `S07` marcada como superseded (ya no citada, se conserva por trazabilidad).

## Para revisión humana (Stage 11)

Ninguna. No se detectaron riesgos legales/éticos/COI que requieran juicio humano en este pase — tabla 6 vacía. (El tick formal de `brain/04` sigue siendo obligatorio en Stage 11, como en todo episodio; esto no es una excepción, es que este pase no encontró nada nuevo que marcar ahí.)
