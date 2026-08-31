# Fact-check — Layer 1 (deterministic)

- Script: `episodes/E001-hokusai/05-script.md`
- Source-log: `episodes/E001-hokusai/03-source-log.csv`
- Tags used: 44 (20 unique)
- Sources: 20 — A:3, B:17
- Orphan-claim candidates: 9

## Orphan-claim candidates (human: tag or confirm non-factual)

- L29: Para entender esa frase hay que ver la vida entera. Esta es la historia de Katsushika Hokusai.
- L87: Lo que no tuvo nunca fue estabilidad. Durante la mayor parte de su vida fue pobre —pobre de no saber si comería, no pobre de artista con …
- L122: Lo escribe a los setenta y cuatro años. Ya había hecho «La gran ola». Y su propio balance es: todavía no sé nada —pero voy en la direcció…
- L159: Hay dos maneras de hacerlo. Una es preguntarte: «¿ya llegué?». La otra: «¿me estoy acercando?».
- L172: No «¿esto me haría llegar?». Sino: «¿este es un trabajo del que querría tener diez años más?».
- L174: Porque el que se define por «ya está» y el que se define por «casi lo tengo» envejecen de forma muy distinta. Hokusai nunca llegó a donde…
- L254: - Cerrar S15 (DOI/ISBN), S19 (cada ejemplo por separado), S20 (fuente de población de Edo)
- L255: - Verificar: fecha de ruptura con Katsukawa (1793), año del incendio (~1839), parentesco exacto del nieto, datación de "La gran ola" con …
- L256: - Recuento de nombres (~30) y mudanzas (~93) contra la fuente

## Verdict: **PASS**

(PASS on consistency, but the orphan candidates above still need a human pass.)

> Script v1.2 (hallazgos de la búsqueda de recursos aplicados).

## Layer 2 — LLM

> Corrido 2026-08-29 sobre el guion v1 + `03-source-log.csv`. **El modelo no es fuente.** Cada bandera se re-verifica contra la fuente real (libro/ficha) por un humano antes de Layer 3. "¿Respalda?" = juicio del modelo sobre si la *descripción* del source-log encaja con la afirmación, no verificación.

### 1. Afirmaciones factuales

| # | Sección | Afirmación (resumida) | [S..] | ¿Respalda la descripción? | Veredicto |
|---|---------|-----------------------|-------|---------------------------|-----------|
| 1 | Cold open | Muere en 1849 a los ~88 | S12 | sí | respalda — *pero* la edad varía según el cómputo (88 occidental / 90 japonés). Añadir matiz o nota |
| 2 | Cold open | "Más de setenta años dibujando" | (deriva de S03) | parcial | sin tag propio; se deduce (aprendiz ~1778 → 1849). Aceptable si se tagea S03 |
| 3 | Cold open | "Una de las imágenes más reproducidas del planeta" | S14 | parcial | S14 dice "muy reproducida / japonismo", no cuantifica "del planeta". **Matizar** → "una de las imágenes japonesas más reconocibles" o atribuir |
| 4 | Cold open | Frase del lecho de muerte (5 o 10 años, "pintor de verdad") | S12 | sí (como relato) | respalda-como-matizado — el guion ya dice "según cuentan / dicen unas versiones" |
| 5 | Contexto | Nace ~1760 en Katsushika, Edo | S02 | sí | respalda |
| 6 | Contexto | Japón "más de un siglo prácticamente cerrado… shogun" | — | — | **sin tag** — contexto histórico establecido (sakoku). Tagear a una fuente general o aceptar como conocimiento común; "prácticamente" cubre Dejima |
| 7 | Contexto | Edo "ronda el millón de habitantes" | — | no | **sin tag y S02 no lo cubre.** Añadir fuente de población de Edo (~1780–1800) o suavizar a "una de las ciudades más grandes del mundo" |
| 8 | Explicador | Proceso ukiyo-e (dibujante/tallador/impresor/editor) | S02 | sí (plausible) | respalda — el catálogo del British Museum cubre esto; confirmar al abrir |
| 9 | Aprendizaje | Aprendiz de Shunshō ~1778; Shunshō hacía retratos de actores; nombre "Shunrō" | S03 | sí | respalda; **verificar el año exacto** (S03 lo pide) |
| 10 | Aprendizaje | Deja la escuela Katsukawa tras la muerte de Shunshō en 1793 | S04 | sí | respalda el hecho; **verificar 1793** (algunas fuentes dan 1792/1794 para la salida) |
| 11 | Aprendizaje | Motivo de la ruptura = estudiar escuelas rivales | S04 | sí (como tradición) | respalda-como-matizado — el guion dice "según se cuenta / no hay documento" |
| 12 | Acto 1 | "Alrededor de treinta" nombres artísticos | S05 | sí (con reserva) | respalda-como-matizado; **verificar el recuento de S05** |
| 13 | Acto 1 | Lista de nombres (Shunrō, Sōri, Hokusai, Taito, Iitsu, Manji) | S05 | sí | respalda — son gō reales de Hokusai |
| 14 | Acto 1 | Traspasó nombres a discípulos con clientela | S05 | sí | respalda (p. ej. "Taito" pasó a un discípulo) |
| 15 | Acto 1 | Cada cambio de nombre ↔ cambio de rumbo | S05 | sí (interpretación estándar) | respalda como lectura académica; ver tabla 2 |
| 16 | Acto 1 | *Hokusai Manga* desde 1814; miles de bocetos; material de estudio; éxito de ventas décadas | S10 | sí | respalda |
| 17 | Acto 1 | Daruma gigante ante público, Nagoya, 1817, "varios pisos" | S17 | sí (general) | respalda-como-general; **verificar fecha y dimensiones** (S17 lo pide) |
| 18 | Acto 1 | Miniaturas "sobre un grano de arroz" | S17 | sí (como tradición) | respalda-como-matizado — el guion dice "cuentan / se le atribuyen" |
| 19 | Acto 2 | "No fue un genio ignorado; tuvo nombre, público y encargos" | S10 | sí | respalda (myth-bust legítimo) |
| 20 | Acto 2 | Pobreza "de no saber si comería" | S06 | parcial | S06 dice "pobreza"; la severidad concreta ("no saber si comería") es dramatización. **Matizar** o sostener con cita |
| 21 | Acto 2 | "~93 mudanzas" | S06 | sí (con reserva) | respalda-como-matizado — guion + rótulo lo tratan como cifra tradicional. Opcional: nombrar el origen (biografía de Iijima, 1893) si se verifica |
| 22 | Acto 2 | Nieto endeudado en los 1830; Hokusai paga y se arruina | S08 | sí | respalda; **verificar parentesco y fechas** (S08 lo pide). El guion suaviza a "hijo de una de sus hijas" (bien) |
| 23 | Acto 3 | 36 vistas del Fuji "entre 1830 y 1833" | S09 | **desajuste interno** | S09 dice "1830-1832". **Alinear guion y source-log.** Recomendado: "principios de la década de 1830" y, para la Ola, "hacia 1831" |
| 24 | Acto 3 | Descripción de láminas concretas (campo de arroz, tonelero, Fuji rojo) | S09 | sí | respalda — son láminas reales de la serie |
| 25 | Acto 3 | "La gran ola": Fuji al fondo, ola en garras, tres barcas | S09 | sí | respalda; nota menor: las barcas son *oshiokuri-bune* (transporte rápido), no estrictamente "de pescadores" — común pero impreciso |
| 26 | Acto 3 | Hizo la Ola "a los unos setenta años" | S09 | sí | respalda (~70–71 si es de ~1831) |
| 27 | Acto 3 | Azul de Prusia importado, más intenso/estable que los azules vegetales, se abarata y se usa "a manta" | S18 | sí (general) | respalda-como-general; **confirmar fechas de disponibilidad del pigmento** (S18 lo pide) |
| 28 | Acto 3 | Buena parte de las 36 vistas construidas sobre ese azul | S18 | sí | respalda (primeras láminas en estilo aizuri-e) |
| 29 | Acto 4 | *Cien vistas del monte Fuji*, vol. con la nota firmada, 1834 | S01 | sí | respalda (vol. 1: 1834) |
| 30 | Acto 4 | La "escala de edades" del prefacio | S01 | **parcial — error** | el "cada punto y cada línea estarían vivos" es la afirmación de Hokusai **para los 110 años**, no los 100. El guion lo atribuye a los 100. **Corregir** (añadir "a los ciento diez" o reestructurar) |
| 31 | Acto 4 | Lo escribe a los 74 | S01 | sí | respalda (1834, nac. 1760) |
| 32 | Acto 4 | Firma tardía "Gakyō Rōjin Manji" | S13 | sí | respalda |
| 33 | Acto 4 | Incendio del taller ~1839 | S07 | sí | respalda-como-matizado; **verificar año** |
| 34 | Acto 4 | Últimos años con Katsushika Ōi, pintora, lo cuidaba | S11 | sí | respalda |
| 35 | Acto 4 | Atribuciones discutidas (Ōi ↔ obras tardías "de Hokusai") | S11 | sí | respalda; bien framedo como cuestión abierta |
| 36 | Acto 5 | Estampas a Europa "como papel de embalar de cerámica" | S19 | no | S19 no cubre esto. Es una anécdota semi-legendaria (Bracquemond, ~1856). **Matizar** ("se cuenta que…") o dar fuente propia |
| 37 | Acto 5 | Monet colgó estampas de Hokusai en Giverny | S14/S19 | parcial | verificable (colección de Giverny). **Confirmar Hokusai en concreto** (la colección tiene Hiroshige/Utamaro/Hokusai) |
| 38 | Acto 5 | Van Gogh "copió composiciones japonesas" | S19 | parcial | cierto en general (copió a Hiroshige, 1887); en un episodio de Hokusai el espectador infiere que copió a Hokusai. Aclarar o dejar genérico |
| 39 | Acto 5 | *La Mer* de Debussy (1905): la portada de la 1ª ed. llevaba una versión de "La gran ola" | S14/S19 | sí (alta confianza) | respalda — 1ª ed. Durand 1905. **Confirmar edición** |

### 2. Interpretación presentada como hecho

| # | Sección | Frase | Reescritura sugerida |
|---|---------|-------|---------------------|
| A | Acto 1 | "Cada cambio de nombre coincidía… con un cambio de rumbo en el trabajo" | ya lleva "más o menos"; opcional añadir "según los estudios de su obra" |
| B | Acto 3 | "La imagen más japonesa que conoces está hecha, en parte, con tecnología europea recién llegada" | retórico; un pigmento no es "tecnología" en sentido fuerte — o se asume como licencia, o "con un pigmento europeo recién llegado" |
| C | Acto 4 | Ōi "tenía un don propio, sobre todo para la luz y la noche" | juicio crítico como hecho → "en su obra conservada destacan las escenas nocturnas y los efectos de luz" |
| D | Cierre | Hokusai "eligió, a conciencia, la segunda [forma de medirse]" | reclama intención → "si nos guiamos por lo que escribió, se medía con la segunda" |

### 3. Citas textuales

| # | Cita en el guion | ¿Traducción marcada? | ¿Atribución + fecha? | Riesgo apócrifa |
|---|------------------|----------------------|----------------------|-----------------|
| 1 | Prefacio de 1834 (parafraseado) | sí ("esto es traducción nuestra") | sí (1834) | bajo — texto primario PD; **pero** revisar la asignación 100 vs 110 (tabla 1 #30) |
| 2 | "podría llegar a ser un pintor de verdad" (lecho de muerte) | sí (traducción propia) | como relato tradicional, sin fecha exacta | medio — relato tradicional; el guion ya lo marca ("según cuentan", "dicen unas versiones") |
| 3 | "el viejo loco por la pintura" (Gakyō Rōjin Manji) | sí (traducción propia) | sí | bajo |

### 4. Afirmaciones que deberían ir matizadas

| # | Sección | Afirmación | Matiz sugerido |
|---|---------|-----------|----------------|
| 1 | Cold open | "una de las imágenes más reproducidas del planeta" | "una de las imágenes japonesas más reconocibles del mundo" o atribuir la afirmación |
| 2 | Acto 2 | "pobre de no saber si comería" | "pobre de verdad, con estrecheces reales" (o sostener la severidad con cita) |
| 3 | Acto 5 | "sus estampas llegaron a Europa… como papel de embalar" | "se cuenta que algunas llegaron como papel de embalar" |
| 4 | Cold open / Acto 5 | edad "~88" | añadir una vez la nota del doble cómputo (88/90) |

### 5. Psicología popular / conceptos

| # | Sección | Afirmación | Nota |
|---|---------|-----------|------|
| 1 | Cierre | "La psicología de la motivación lo describe… demostrar lo que vale vs. mejorar sin punto final" [S15] | **NO es psicología pop** — es una distinción real (metas de rendimiento vs. de maestría; Nicholls, Dweck, Elliot). **Pero S15 sigue sin cerrar.** Es la cita abierta más importante del guion. Cerrar con una referencia concreta (p. ej. Dweck *Mindset*; o Elliot & McGregor 2001) |
| 2 | — | (sin "usamos el 10% del cerebro", "10.000 horas", etc.) | limpio |

### 6. Resumen

- **Afirmaciones factuales revisadas:** 39
- `desajuste` / error: **2** — #23 (fechas 36 vistas, guion ≠ source-log) · #30 (escala de edades: "punto y línea vivos" es a los 110, no 100)
- `sin tag` / fuente insuficiente: **3** — #6 (Japón cerrado), #7 (población de Edo), #36 (papel de embalar)
- `respalda-como-matizado`: 8 (ya bien tratadas en el guion)
- Banderas de matiz (tabla 4): 4 · Interpretación como hecho (tabla 2): 4
- **Cita abierta crítica:** S15 (concepto de la reflexión) y S19 (japonismo, cada ejemplo por separado)

**Lo más urgente (Usuario 001 aplica en el guion):**
1. Corregir #30 — la escala del prefacio: "cada punto y línea vivos" = 110 años.
2. Alinear #23 — fechas de las *Treinta y seis vistas* entre guion y source-log.
3. Cerrar S15 con una referencia real (metas de maestría vs. rendimiento).
4. Matizar #3/#20/#36 y añadir la nota de edad 88/90.
5. Verificar S19 ejemplo por ejemplo (Giverny, Van Gogh, *La Mer* 1905).

---

## Resolución de banderas

Pendiente. Resolver **cada bandera de arriba** contra la fuente real (no contra este informe): aplicar la corrección en `05-script.md` o descartarla con un motivo. Anotar aquí.

| Bandera | Qué se hizo | Guion actualizado |
|---------|-------------|-------------------|
| #30 | | |
| #23 | | |
