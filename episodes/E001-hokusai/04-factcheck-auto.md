# Fact-check — Layer 1 (deterministic)

- Script: `episodes/E001-hokusai/05-script.md`
- Source-log: `episodes/E001-hokusai/03-source-log.csv`
- Última corrida L1: 2026-09-08 (sobre la revisión del guionista del guion v2.0)
- Verdict: **PASS** (consistencia — cada `[S..]` resuelve; todas las fuentes con tier + derechos)

Los "orphan-claim candidates" que reporta L1 son, tras revisión: líneas del cold open/cierre que son **interpretación o retórica**, no afirmaciones factuales (marco «yo creo» / «me parece», preguntas al espectador), más las líneas del apéndice/changelog del propio `.md`. Ninguna necesita `[S..]`.

---

## Layer 2 — pasada de edición · 2026-09-08

> Corrida sobre la **revisión del guionista** del guion v2.0 (el usuario reescribió el cierre, el CTA y varias frases de la narrativa). **El modelo no es fuente** (`brain/01` §9): cada corrección solo aprieta el guion a lo que la fuente citada respalda, añade una salvedad o una atribución, o recorta — nunca añade un hecho.
>
> La pasada anterior (2026-08-29, sobre v1) ya revisó las 39 afirmaciones factuales de la narrativa; esas siguen igual salvo lo indicado. Esta pasada se centra en **lo que cambió** + los ítems que seguían abiertos.

### 1. Afirmaciones factuales — cambios y pendientes

| # | Sección | Afirmación | [S..] | Veredicto | Acción |
|---|---------|-----------|-------|-----------|--------|
| 1 | Cold open | «una de las imágenes **más reproducidas del planeta**» | S14 | **sobrepasa la fuente** — S14 dice «muy reproducida / japonismo», no cuantifica | ✅ corregido → «una de las imágenes **japonesas** más reproducidas **del mundo**» |
| 2 | Narrativa | «pobre de **no saber si comería**» | S06 | **dramatización** — S06 dice «vivió en la pobreza», no la severidad concreta | ✅ corregido → «pobre de verdad, con estrecheces reales — no la pobreza de pose del genio incomprendido, porque incomprendido no fue» (alinea S06 + S10) |
| 3 | Narrativa (final) | muerte «con unos ochenta y ocho años» | S12 | falta la salvedad del doble cómputo (estaba en v1.2, se perdió en v2) | ✅ corregido → «…o noventa, según cómo se cuenten los años en Japón, donde uno nace con un año» |
| 4 | Narrativa (nuevo beat del guionista) | «ese momento de **Eureka**, donde **sin planearlo ni esperarlo** … algo hace click» (sobre cómo salió «La gran ola») | — (sin tag) | **interpretación como hecho + contradice la narrativa fuenteada**: el guion entero sostiene que la Ola es fruto de 50 años de trabajo + la ruina a los 70 ([S09][S10], y el PAY inmediatamente anterior: «no fue el premio a una vida ordenada, fue lo que le salió estando otra vez en el suelo») | ✅ reencuadrado → «no es que a Hokusai se le ocurriera "La gran ola" de la nada. Es que medio siglo de trabajo, y una mala racha que lo dejó otra vez sin nada, cuajaron ahí — y eso muchas veces ocurre cuando menos lo esperas». Mantiene el beat y el CTA; quita el «chispazo de la nada». **Revísalo — es prosa tuya, la toqué solo por el choque factual.** |
| 5 | Explicador (azul) | «un precio que permite usarlo **para la producción en masa**» | S18 | aceptable — el propio explicador establece que el ukiyo-e *es* producción en serie; S18 dice que el pigmento «se abarató» | sin cambio; verificar fechas de disponibilidad del pigmento (S18) en shotlist |
| 6 | Cierre | concepto metas de maestría vs. rendimiento | S15 | **S15 estaba sin cerrar** — era la cita abierta más importante | ✅ **S15 cerrada**: Nicholls 1984 (*Psychological Review* 91(3):328–346, DOI 10.1037/0033-295X.91.3.328) + Dweck, *Mindset* (Random House 2006, ISBN 978-1-4000-6275-1) |

Sin cambios respecto a la pasada de 2026-08-29 (siguen bien tratadas): la escala de edades a los 110 (ya corregido en v1.2), fechas de las *36 vistas* («principios de la década de 1830», alineado con S09), papel de embalar («se cuenta —y puede que la historia esté algo pulida—»), ~30 nombres y ~93 mudanzas (con rótulo de salvedad), Daruma de 1817 (atribuido), miniaturas «sobre granos de arroz» («cuentan»).

### 2. Interpretación presentada como hecho

| # | Frase | Estado |
|---|-------|--------|
| A | Cierre: «me parece que él se medía más bien con la segunda» | ✅ bien — el guionista añadió «me parece», marco interpretativo explícito |
| B | Explicador: «tecnología europea recién llegada» (un pigmento) | licencia retórica; el guionista la mantuvo. Aceptable |
| C | «Ōi tenía un don propio, sobre todo para la luz y la noche» | juicio crítico como hecho — leve. Opción: «en su obra conservada destacan las escenas nocturnas». No aplicado (menor, el guionista lo dejó) |
| D | Beat del «Eureka» | ✅ ver tabla 1 #4 |

### 3. Citas textuales

| Cita | ¿Traducción marcada? | ¿Atribución? | Riesgo |
|------|----------------------|--------------|--------|
| Prefacio de 1834 (parafraseado) | sí («esto es traducción nuestra») | sí (1834); escala a los 110 correcta | bajo |
| «podría llegar a ser un pintor de verdad» (lecho de muerte) | sí | como relato tradicional («según cuentan», «dicen unas versiones») | medio — bien marcado |
| «el viejo loco por la pintura» | sí | sí | bajo |

### 4. Afirmaciones que van matizadas — estado

| Afirmación | Estado |
|-----------|--------|
| «del planeta» → | ✅ corregido (tabla 1 #1) |
| «pobre de no saber si comería» → | ✅ corregido (tabla 1 #2) |
| edad 88/90 → | ✅ nota añadida (tabla 1 #3) |
| «papel de embalar» → | ✅ ya llevaba «se cuenta» |

### 5. Psicología popular / conceptos

| Afirmación | Nota |
|-----------|------|
| Cierre: metas de maestría vs. rendimiento [S15] | **No es psicología pop** — distinción académica real (task/ego, Nicholls; mindset, Dweck). **S15 ya cerrada.** En pantalla se nombra en general, sin atribuir un estudio único (`brain/09` A6). Limpio. |
| — | Sin «10% del cerebro», «10.000 horas», etc. Limpio. |

### 6. Resumen

- **Correcciones aplicadas al guion: 4** (tabla 1 #1–#4).
- **Citas cerradas: 1** — S15 (la crítica).
- **Sin banderas legales / éticas / COI** en esta pasada.
- **Pendiente (Stage 5 / shotlist, no bloqueante):**
  - **S19** — Monet coleccionaba Hokusai *en concreto* en Giverny (confirmar, no solo Hiroshige/Utamaro); Van Gogh: el guion dice «composiciones japonesas» (genérico, OK). *La Mer* 1905: cerrado.
  - **S20** — cerrar con una fuente concreta de población de Edo (~1780–1800). El guion mantiene «probablemente».
  - Verificaciones de detalle: ruptura con Katsukawa 1793, incendio ~1839, parentesco del nieto, 2ª ficha de museo para «La gran ola», dimensiones del Daruma, recuento de nombres/mudanzas.

---

## Changelog — correcciones aplicadas a 05-script.md (2026-09-08)

| # | Antes (verbatim) | Después | Motivo |
|---|------------------|---------|--------|
| 1 | «…en una de las imágenes más reproducidas del planeta [S14].» | «…en una de las imágenes japonesas más reproducidas del mundo [S14].» | S14 no cuantifica «del planeta»; se aprieta a lo que la fuente respalda |
| 2 | «…fue pobre —pobre de no saber si comería, no pobre de artista sin mucho reconocimiento.» | «…fue pobre de verdad, con estrecheces reales — no la pobreza de pose del genio incomprendido, porque incomprendido no fue.» | S06 = «pobreza», sin la severidad concreta; y se alinea el myth-bust con S10 (tuvo éxito) |
| 3 | «Hokusai muere en Edo en 1849, con unos ochenta y ocho años [S12].» | «…con unos ochenta y ocho años — o noventa, según cómo se cuenten los años en Japón, donde uno nace con un año [S12].» | Salvedad del doble cómputo (estaba en v1.2, se perdió en la reescritura); S12 la pide |
| 4 | «…ese maravilloso momento de genialidad, ese momento de Eureka, donde sin planearlo ni esperarlo, ni estar en las mejores condiciones, algo hace click. / Alguna vez te ha sucedido? si es así, dejamelo saber en los comentarios.» | «…No es que a Hokusai se le ocurriera «La gran ola» de la nada. Es que medio siglo de trabajo, y una mala racha que lo dejó otra vez sin nada, cuajaron ahí — y eso muchas veces ocurre cuando menos lo esperas, y casi nunca en las mejores condiciones. / ¿Alguna vez te ha pasado algo así? Si es así, déjamelo saber en los comentarios.» | Interpretación como hecho + **contradice la narrativa fuenteada** ([S09][S10] y el PAY anterior): la Ola no fue un chispazo, fue el fruto de décadas de trabajo + la ruina. Se conserva el beat y el CTA, se quita el «Eureka de la nada» |

## Para revisión humana (Stage 11)

(sin banderas legales / éticas / COI abiertas en esta pasada)
