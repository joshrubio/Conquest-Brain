# Fact-check — E002 «Toyota / Taiichi Ohno»

> `brain/14`. **Automatizado.** L1 (`factcheck.py`) + L2 (agent edit-pass). El guion pasa a registro con L1 `PASS` + changelog escrito.
>
> Corrido sobre el guion **v2** (expansión) el **2026-09-10**. L1 `PASS`. L2 aplicado. **Gate cerrado, sin paso humano** (`brain/14`).
>
> Nota de método: donde una afirmación no se podía confirmar con la descripción del source-log, L2 la **matizó / atribuyó / cortó ahí mismo** (nunca la aparcó para "verificar luego"). Lo único que espera a Stage 11 es la tabla 6 (legal/ético/dignidad). Los recortes que se pueden *reponer* si en el futuro alguien tiene el libro delante están en `05-script.md` § «Mejoras opcionales» — no bloquean nada.

## Layer 1 — deterministic

```
# Fact-check — Layer 1 (deterministic)

- Tags used: 72 (18 unique)
- Sources: 23 — A:8, B:11, C:4
- Orphan-claim candidates: 15 (todas confirmadas no-factuales por L2: notas de [HOOK VISUAL],
  frases retóricas de [PROMISE]/cierre/CTA, y líneas de las tablas meta del final del archivo)

ERRORS: ninguno.
Warnings: S08, S09, S10, S11, S21 definidas pero sin citar (tras las correcciones L2). OK.

## Verdict: PASS
```

Notas L1:
- Se normalizó la columna `tier` del source-log a una sola letra (A/B/C/D) — antes S04/S05/S06/S18/S19 iban como `A / C`, S17/S20/S22/S23 como `B / C`, S14 como `A (con sesgo)`; el matiz vive en `notes`. Convención de E001 y de `factcheck.py`. **E002 nunca había pasado L1** por esto.
- S08 (Wikipedia/Britannica, C), S10 (Strategos, C), S21 (prensa del motor, C) estaban como soporte único de alguna afirmación → L2 las re-etiquetó a S03 donde Cusumano lo cubre, o retiró la afirmación (Premio Deming, detalle del Toyopet Crown).

## Layer 2 — analysis (Partes A + C)

### 1. Afirmaciones factuales — desajustes y sin-tag (solo lo corregido; el resto `respalda`)

| # | Línea | Afirmación | [S..] | Veredicto | Acción |
|---|-------|------------|-------|-----------|--------|
| 1 | Cold open | «en una de las empresas automotrices más grandes del mundo» (Toyota, 1950) | S04 | **desajuste** — Toyota hacía 40 coches/día; se contradice con el propio episodio | reescrito |
| 2 | Cold open | «la compañía de Henry Ford fabrica 8.000 coches al día, aún luego de la muerte de su fundador» | S06 | subclaim sin tag (muerte de Ford 1947) | cortada la coletilla |
| 3 | Cold open | «lo acaba copiando, treinta años después, casi toda la industria» | S02 | impreciso (1950→estudio MIT 1990 = 40 años) | «una generación después» |
| 4 | Pivote | «Con parte de ese dinero [de Platt], Kiichirō monta el departamento de automóviles» | S18/S20 | **desajuste** — la propia Toyota lo presenta como paralelo; pago a plazos, renegociado (el [NOTA] ya lo decía) | «Por esos años…», sin el causal |
| 5 | Pivote | «durante casi diez años Toyota fabrica camiones» | S19/S03 | impreciso (~7–8 años) | «durante toda la guerra» |
| 6 | Pivote | «el 25 de junio de 1950, a dos semanas de que termine la huelga» | S03/S04 | **desajuste cronológico** — la huelga terminó el 10 jun, 15 días *antes* | «recién terminada la huelga» |
| 7 | Pivote | «pasó a la fábrica de coches en 1943, cuando Toyota absorbió los telares» | S03 | impreciso (fue la filial textil Toyoda Boshoku) | «absorbió su filial de telares» |
| 8 | §2 (1973) | recuperación del 73 | S01, S03 | S01 (Ohno, *TPS*) aún no obtenida | re-tag → S03 + S12 (ambas lo cubren, dossier C9) |
| 9 | §2 (NUMMI) | «Toyota la reabre con **los mismos obreros**» | S22 | overstatement (fuentes: ~85 %) | «casi toda la vieja plantilla» |
| 10 | §2 (NUMMI) | «Uno de los directivos que montó aquello era Teruyuki Minoura» | S12 | **no se puede saber** — Minoura dirigió TMMNA (Georgetown, 1988), no consta en NUMMI (Fremont, 1984) | **cortada** |
| 11 | §2 (Deming) | «Toyota gana el Premio Deming… mediados de los 60» | S08 (C) | soporte único Tier C | **cortada** la mención; queda «el sistema cubre casi toda la empresa» [S03] |
| 12 | §2 (US) | Toyopet Crown, «un coche tan flojo que no aguantaba una autopista sin recalentarse» | S21 (C) | soporte único Tier C | reescrito en genérico, tag S02 |
| 13 | §2 (Dodge) | «la línea Dodge… empiezan a caer empresas en cadena» | S10 (C) | soporte único Tier C | re-tag → S03 (Cusumano, intro pp. 19–21) |

### 2. Interpretación presentada como hecho

| # | Línea | Frase | Acción |
|---|-------|-------|--------|
| 1 | Cold open | «Para los japoneses era claro… estaban destinados a perder» | → «Para muchos, la conclusión parecía la misma que con la guerra: no había forma de ganar» (S14 = lectura de Ohno) |
| 2 | §2 friction | «un almacén lleno de piezas es una manta de seguridad» | metáfora, no afirmación factual — se deja; el punto (resistencia de los mandos) lo cubren S03/S12 |
| 3 | Cierre | «Copiar al que va primero te mantiene… en segundo lugar» | registro filosófico, enmarcado «una segunda lectura, más incómoda» + anclado a la escena de Eiji (`brain/09` A, observación anclada). OK; confirmar en Stage 11 |

### 3. Citas textuales

| # | Cita | ¿Traducción marcada? | ¿Atribución + fecha? | Riesgo de apócrifa |
|---|------|----------------------|----------------------|--------------------|
| 1 | «alcanzar a Estados Unidos en tres años…» (Kiichirō) | sí — «según lo cuenta Ohno… algo parecido a esto» + «la frase probablemente esté pulida» | sí (Ohno, ~1945) | bajo (ya enmarcada como posiblemente estilizada) |
| 2 | «un guijarro frente a una roca» (Eiji Toyoda) | implícito (traducción) | sí (S06, 1950) | bajo — **verificar redacción original (dossier)** |
| 3 | «igual que un año… de un luchador de sumo… diez días de combates» (Ohno) | conviene marcar «traducido» | sí (S14, 1982) | bajo — **verificar contra el original (dossier)** |
| 4 | «ponte ahí y mira el proceso» (Ohno, vía Minoura) | sí — L2 lo pasó a «algo así como…» | sí (S12, testimonio de Minoura) | bajo — **verificar la cita y las «8 horas» (dossier)** |

### 4. Afirmaciones que deberían ir matizadas — ya matizadas en v2

| # | Afirmación | Matiz (ya en el guion) |
|---|------------|------------------------|
| 1 | cifra 9:1 de productividad | [NOTA] + «se decía» / «había oído» + rótulo en pantalla |
| 2 | «cheque» de Platt que funda Toyota | [NOTA] + L2 quitó el causal de la narración |
| 3 | cambio de nombre Toyoda→Toyota | «se cuenta que fue por estética y superstición» |
| 4 | Premio Deming | retirado por L2 (Tier C) |

### 5. Psicología popular / conceptos

| # | Línea | Nota |
|---|-------|------|
| 1 | Cierre — «la restricción como fuerza de rediseño» | **no es psicología pop**: revisión revisada por pares (S16, Acar et al. 2019, *J. of Management*) + apoyo divulgativo (S15). Nombrado en general, no un estudio único del caso (`brain/09` A6). Enmarcado «yo creo». OK |

### 6. Legal / ético / independencia

| # | Línea | Riesgo | Tipo |
|---|-------|--------|------|
| 1 | §2 (NUMMI) | La plantilla de Fremont (principios de los 80) descrita en bloque como absentista / saboteadora / bebedora — colectivo, histórico, con fuente (This American Life + wiki). El propio beat la reencuadra con empatía (el problema era el sistema, no la gente). Riesgo bajo. | dignidad |

→ Detalle en «Para verificación humana» abajo.

## Parte C — Resumen

- Afirmaciones factuales revisadas: ~40 · `desajuste`: 5 · `sin tag`/`impreciso`: 4 · `no se puede saber`: 1 · Tier-C-solo: 3
- Correcciones aplicadas: **19** · Cortes: 2 (línea Minoura-NUMMI; mención Premio Deming) + 1 parcial (detalle Toyopet) · Ítems para Stage 11: **1** (tabla 6, dignidad)
- L1: **PASS**. Gate L2: changelog escrito → **Stage 6**. Sin firma, sin paso humano intermedio.

## Changelog — correcciones aplicadas a 05-script.md

| # | Antes (verbatim) | Después | Motivo |
|---|------------------|---------|--------|
| 1 | «Y en una de las empresas automotrices más grandes del mundo, los trabajadores llevan dos meses de huelga… La fabrica de Toyota está a punto de cerrar. [S04].» | «En la fábrica de coches de una empresa llamada Toyota, los trabajadores llevan dos meses de huelga… La fábrica está al borde del cierre [S04].» | Toyota no era «de las más grandes del mundo» en 1950 (40 coches/día) — contradecía el episodio |
| 2 | «la compañia de Henry Ford fabrica ocho mil coches al día, aún luego de la muerte de su fundador. Toyota en cambio apenas fabrica cuarenta coches al día [S06].» | «la compañía de Henry Ford fabrica ocho mil coches al día. Toyota, en cambio, apenas fabrica cuarenta [S06].» | subclaim sin fuente (muerte de Ford) — se corta, no aporta |
| 3 | «lo acaba copiando, treinta años después, casi toda la industria» | «…una generación después…» | 1950→estudio MIT 1990 = 40 años; vaguedad más segura |
| 4 | «Para los japoneses era claro, al igual que con la guerra, estaban destinados a perder [S14].» | «Para muchos, la conclusión parecía la misma que con la guerra: no había forma de ganar [S14].» | no atribuir un estado mental a «los japoneses» en bloque; S14 = lectura de Ohno |
| 5 | «Con parte de ese dinero, el hijo de Sakichi… monta… automóviles [S18][S20].» | «Por esos años, el hijo de Sakichi… monta… automóviles [S20].» | el vínculo directo venta-de-patente → financiación es el mito que el propio [NOTA] desmiente |
| 6 | «durante casi diez años Toyota fabrica camiones para el ejército» | «durante toda la guerra Toyota fabrica camiones para el ejército» | ~7–8 años, no «casi diez» |
| 7 | «a dos semanas de que termine la huelga, estalla la guerra de Corea» | «recién terminada la huelga, estalla la guerra de Corea» | la huelga terminó el 10 jun 1950; la guerra el 25 jun — *después*, no antes |
| 8 | «pasó a la fábrica de coches en 1943, cuando Toyota absorbió los telares [S03]» | «…cuando Toyota absorbió su filial de telares [S03]» | precisión: fue la filial textil (Toyoda Boshoku) |
| 9 | «En 1949 el gobierno aplica un plan de choque… empiezan a caer empresas en cadena [S10].» | «…[S03].» | S10 es Tier C; Cusumano (S03, intro pp. 19–21) cubre la crisis del 49–50 |
| 10 | «de golpe tiene los libros llenos [S03][S10].» | «…[S03].» | quita la dependencia de S10 (C) |
| 11 | «cuando Toyota absorbió los telares [S03][S08]» (Ohno a coches 1943) | «…[S03]» | S08 es Tier C; S03 (Tabla 72, «Career of Ono Taiichi») lo cubre |
| 12 | «Ohno dibujó un círculo en el suelo, le dijo «quédate ahí y mira el proceso» y se marchó» | «…le dijo algo así como «ponte ahí y mira el proceso» y se marchó» | cita traducida y parafraseada — se marca como no literal (`brain/08` §3) |
| 13 | «Para los años sesenta el sistema cubre ya casi toda la empresa, y Toyota gana el Premio Deming… [S08]. [NOTA] …a confirmar en Stage 5 [S08].» | «Para los años sesenta el sistema cubre ya casi toda la empresa [S03]. [NOTA] En v1 este beat citaba el Premio Deming… L2 lo retiró por falta de fuente A/B…» | Premio Deming solo con Tier C (S08); se retira hasta tener fuente A/B |
| 14 | «Toyota también cae… mientras el mundo se paraba [S01][S03].» | «…[S03][S12].» | S01 (Ohno *TPS*) aún no obtenida; S03 + S12 cubren el 73 (dossier C9) |
| 15 | «Y el método sale de Japón. Toyota ya lo había intentado en Estados Unidos… con un coche tan flojo que no aguantaba una autopista sin recalentarse; se retiraron y volvieron a empezar [S21]. Para los setenta… amenaza para Detroit [S21][S02].» | «Y el método sale de Japón. Los coches pequeños japoneses… llevaban años intentando entrar en el mercado americano sin conseguirlo. Con la crisis del petróleo de los setenta… amenaza para Detroit [S02].» | el detalle del Toyopet Crown solo lo respaldaba S21 (C); se generaliza a lo que cubre S02 (B) |
| 16 | «Toyota la reabre con **los mismos obreros** que GM había despedido» | «Toyota la reabre con casi toda la vieja plantilla —los obreros que GM había despedido—» | fuentes: ~85 %, no el 100 % |
| 17 | «Uno de los directivos de Toyota que montó aquello era Teruyuki Minoura — el mismo del círculo de tiza [S12].» | *(cortada)* | Minoura dirigió TMMNA/Georgetown (1988), no consta que trabajara en NUMMI (1984) |
| 18 | «Toyota, cuarenta. «Un guijarro frente a una roca», dice. [S06].» | «…Toyota al lado de Ford, dice —en sus palabras, traducidas—, es «un guijarro frente a una roca» [S06].» | cita traducida sin marcar (`brain/08` §3) |
| 19 | «Ohno lo describía con una imagen: «igual que un año en la vida de un luchador de sumo…»» | «Ohno lo describía, en sus palabras traducidas, con una imagen: «…»» | cita traducida sin marcar |

*(También: `tier` del source-log normalizado a una letra; § del guion reescrita — «Pendiente/bloqueante» → «Mejoras opcionales, no bloquean nada».)*

## Para revisión humana (Stage 11) — tabla 6, único ítem

`brain/14`: L2 no edita esto, lo deja para el tick humano de Stage 11. Todo lo demás quedó resuelto en el guion.

| Línea | Riesgo | Tipo |
|-------|--------|------|
| §2 (NUMMI) | La plantilla de Fremont (principios de los 80) descrita en bloque como absentista / saboteadora / bebedora — colectivo, histórico, con fuente (This American Life 403/561 + wiki). El propio beat la reencuadra con empatía: el problema era el sistema, no la gente (esa es la tesis del beat). Riesgo bajo; confirmar que el montaje final no lo deja en clave de desprecio. | dignidad |
