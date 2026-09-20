# Fact-check — E004 «Coca-Cola»

> `brain/14`. **Automatizado.** L1 (`factcheck.py`) + L2 (agent edit-pass). El guion pasa a registro con L1 `PASS` + changelog escrito.
>
> Corrido sobre el guion **v2** el **2026-09-18**. L1 `PASS`. L2 aplicado. **Gate cerrado, sin paso humano** (`brain/14`).
>
> Nota de método: donde una afirmación no se podía confirmar con la descripción del source-log, L2 la **matizó / atribuyó / cortó ahí mismo** (nunca la aparcó para "verificar luego"). Lo único que espera a Stage 11 es la tabla 6 (legal/ético/dignidad).

## Layer 1 — deterministic

```
# Fact-check — Layer 1 (deterministic)

- Tags used: 38 (6 unique)
- Sources: 10 — A:2, B:4, C:4
- Orphan-claim candidates: 15 (todas confirmadas no-factuales o intencionalmente sin tag por L2 —
  ver Parte A tabla 1 y el Changelog)

## Verdict: PASS
```

Notas L1:
- **Primer corrido (antes de L2): FAIL.** `[S03]`, `[S05]`, `[S08]` (y, tras arreglar un bug de CSV, también `[S07]`) estaban citadas en la narración siendo Tier C — regla del canal (`brain/01` §2, aplicada sin excepción por `factcheck.py`): una fuente Tier C nunca puede aparecer como cita `[S..]` en el guion, ni siquiera acompañando a una fuente A/B en la misma frase. Corregido por L2 (ver Changelog).
- **Bug de CSV encontrado y corregido:** la fila S07 de `03-source-log.csv` tenía comillas internas escapadas con `\"…\"` en vez del escape CSV correcto `""…""`, lo que desalineaba las columnas de esa fila (el campo `tier` real se leía como una fecha). Corregido — ver `03-source-log.csv`.
- Warnings: S03, S05, S07, S08 definidas en el source-log pero ya no citadas en el guion (correcto — son Tier C, se quedan como pistas de investigación documentadas, no como respaldo en pantalla).

## Layer 2 — analysis (Partes A + C)

### 1. Afirmaciones factuales (selección — no exhaustivo, ver Changelog para las que cambiaron)

| # | Línea/sección | Afirmación (resumida) | `[S..]` | ¿Respalda? | Veredicto |
|---|---|---|---|---|---|
| 1 | L25 Hook | Existe una fórmula guardada con mucho recelo | [S01] | sí | respalda |
| 2 | L57 Pivote | Pemberton, 30 años de farmacéutico, junta de licencias de Georgia | [S01] | sí | respalda |
| 3 | L75 Acto 1 | Herida en Columbus, abril 1865, teniente coronel 3er Batallón | [S01][S02] | sí | respalda |
| 4 | L94 Acto 2 | Robinson sugirió el nombre y el logo | *(sin tag, ver Changelog #1)* | Tier C único, sin A/B | matizado + tag retirado |
| 5 | L109 Acto 3 | Reparto caótico de derechos a 4 partes | *(sin tag, ver Changelog #2)* | Tier C único, sin A/B | matizado + tag retirado |
| 6 | L116 Acto 3 | Causa de muerte: cáncer de estómago | [S01][S02] + matiz en texto | el cáncer específicamente solo en Tier C | matizado + tag retirado del cáncer (Changelog #3) |
| 7 | L122 Acto 4 | Candler consolida la propiedad hacia 1891, $2.300 | [S02][S04] | sí (S04 citado como lo que la empresa dice, no como respaldo del relato completo — ya así desde Stage 2) | respalda |
| 8 | **L124 Acto 4** | **1892: se incorpora The Coca-Cola Company (Candler, hermano, Robinson, 2 socios)** | **sin tag** | — | **sin tag → corregido, Changelog #6** |
| 9 | L129 Acto 4 | Retirada de la cocaína hacia 1901 | [S02] | sí, pero el año exacto varía en las fuentes | matizado (Changelog #4) |
| 10 | L139-145 Acto 5 | Historia completa del hijo, Charles Ney Pemberton | *(sin tag, ver Changelog #5)* | Tier C único (x3), sin A/B | matizado + tags retirados |
| 11 | L155 Cierre | Khantzian, 1985, hipótesis de la automedicación | [S09] | sí — verificado contra el resumen consultado (Psychiatric Times/PubMed); representa la teoría con precisión | respalda |
| 12 | L163 Cierre | Parábola del buen samaritano, Lucas 10:25-37 | [S10] | sí | respalda |

### 2. Interpretación presentada como hecho

| # | Línea | Frase | Reescritura con marco |
|---|---|---|---|
| 1 | L157 Cierre | "Está tratando de sobrevivirse a sí mismo." | Ya enmarcada: la frase anterior dice explícitamente "Es una lectura, no un diagnóstico". Sin cambios. |
| 2 | L159 Cierre | "esta lectura no explica solo a Pemberton. Explica media era." | Ya enmarcada como lectura ("si te fijas, esta lectura…"). Sin cambios. |

No se encontraron afirmaciones interpretativas sin marco explícito — el guion ya usa consistentemente "es una lectura", "si esa lectura es correcta", "probablemente".

### 3. Citas textuales

| # | Cita | ¿Traducción marcada? | ¿Atribución + fecha? | Riesgo de apócrifa |
|---|---|---|---|---|
| 1 | «la bebida de los sobrios» (L96) | No estaba marcada → **corregida, Changelog #7** | Sí (S02, época ~1886) | Bajo — eslogan de marca de época, ampliamente documentado, no cita personal |
| 2 | «Pemberton's French Wine Coca» (L81) | N/A — nombre propio de producto, no una cita | — | Ninguno |

### 4. Afirmaciones que deberían ir matizadas

Todas resueltas en el Changelog (#1–#5) — ver abajo. Ninguna queda pendiente.

### 5. Psicología popular / conceptos

| # | Línea | Afirmación | Nota |
|---|---|---|---|
| 1 | L155 Cierre | Hipótesis de la automedicación (Khantzian) | No es pop-psych — es una hipótesis real, publicada en *American Journal of Psychiatry* (1985), ampliamente citada en el campo de las adicciones. Nombrada, atribuida, sourceada `[S09]`. Cumple `brain/09` A6. |
| 2 | L163 Cierre | Parábola del buen samaritano | Registro religioso, no psicológico — nombrada, atribuida a la tradición cristiana, presentada como "una tradición… se ha hecho la misma pregunta", nunca como la verdad. Cumple `brain/09` reglas 1-3. |

Sin banderas — ambos registros del cierre cumplen el estándar de `brain/09` A6, incluida la nueva regla del 2026-09-18 (nombrar la autoridad en voz alta en la narración, no solo en el `[NOTA]`) — E004 es, de hecho, el episodio que motivó esa regla.

### 6. Legal / ético / independencia — PARA REVISIÓN HUMANA (Stage 11)

| # | Línea | Riesgo | Tipo |
|---|---|---|---|
| 1 | Todo el episodio, especialmente Cierre y Acto 5 | La adicción es ahora un tema mucho más central que en v1 (dos generaciones). `brain/04` §7 pide "incluir nota de recurso de ayuda en la descripción donde sea relevante" para temas de adicción. **No añadido todavía** — decisión de Usuario 001/002 en Stage 11, no de L2 | tema-sensible |
| 2 | Acto 5 / Cierre | Charles Ney Pemberton es una figura histórica menor (m. ~1894) sin herederos conocidos por el equipo — mismo estándar de dignidad que Pemberton padre (sin monólogo interior fabricado, tratado con sobriedad). Sin riesgo de difamación (fallecido hace >130 años) | sujeto-privado (mitigado — figura histórica, no persona privada viva) |
| 3 | Fuente S07 (Hektoen International) | Esta fuente, ya retirada como tag del guion, tiene un error factual verificado (fecha de muerte de Pemberton) en el mismo artículo que corrobora la historia del hijo — queda documentado en `03-source-log.csv` con nota de fiabilidad explícita. No es un riesgo del guion en sí, pero el equipo debe saber que esa fuente no es confiable para nada más que ya no se use | — (nota de calidad de fuente, no legal) |

## PARTE B — Changelog (correcciones aplicadas a `05-script.md`)

| # | Texto actual (antes) | Texto nuevo | Motivo |
|---|---|---|---|
| 1 | "Se lo sugiere Frank Robinson… [S05]" | "La versión más repetida es que se lo sugiere Frank Robinson… dice la tradición… A Robinson también se le atribuye…" (sin tag) | S05 es Tier C, único respaldo — `brain/01` §2 / `factcheck.py` no admite Tier C citado. Matizado en el propio texto, tag retirado |
| 2 | "Pemberton empieza a vender participaciones… [S05]" | "…según los registros que han llegado hasta hoy… Esos mismos registros describen…" (sin tag) | Mismo motivo — S05 único respaldo |
| 3 | "…y con un cáncer de estómago que llevaba tiempo consumiéndolo [S01][S02][S03]" | "…y, según las fuentes disponibles, con un cáncer de estómago… [S01][S02]" | El cáncer específicamente solo lo respalda S03 (Tier C); S01/S02 cubren el resto de la frase. Se matiza y se retira solo la parte del tag que dependía de S03 |
| 4 | "hacia 1901, en plena ola…" | "hacia 1901 — las fuentes varían entre 1901 y 1903 —, en plena ola…" | El dossier (§5) ya documentaba el rango; el guion solo decía "hacia 1901" sin la salvedad explícita en pantalla |
| 5 | Todo Acto 5 (hijo de Pemberton) con `[S03]`/`[S07]`/`[S08]` | Mismo contenido, con matices en el texto ("según los registros disponibles", "según cuenta esa misma genealogía familiar", "según coinciden dos fuentes independientes aunque ninguna de ellas concluyente") y sin tags | S03/S07/S08 son las tres Tier C, sin ninguna A/B de respaldo — el hallazgo se queda en el guion (es central para el cierre) pero atribuido en prosa, no anclado a un tag que implique un estándar de fuente que no tiene |
| 6 | "Y en 1892 se incorpora formalmente The Coca-Cola Company — Candler, su hermano, el propio Frank Robinson, y dos socios más." (sin tag) | Igual + `[S02]` | Afirmación factual sin ninguna cita — S02 (Pendergrast) ya cubre esta fecha y estos nombres, tag simplemente faltaba |
| 7 | "«la bebida de los sobrios» [S02]" | "el eslogan de la época, traducido, viene a decir algo como «la bebida de los sobrios» [S02]" | Cita/eslogan de época sin marca de traducción (`brain/01` §4) |
| 8 | `03-source-log.csv`, fila S07 | Comillas `\"…\"` → `""…""` | Bug de escapado CSV que desalineaba las columnas de esa fila (ver Layer 1) |

**Tabla 5b:** no aplica — Track Documental, no Ensayo.

## PARTE C — Resumen

- Afirmaciones factuales revisadas: 12 (muestra) · `desajuste`: 0 · `sin tag` (corregido): 1 · matizadas/tag retirado: 6
- Correcciones aplicadas: 8 · Cortes: 0 · Ítems para revisión humana: 3 (tabla 6, todos Stage 11)
- (Ensayo) No aplica

No se inventó ninguna fuente. Todo lo que no se pudo confirmar con el source-log se matizó o se destagueó, nunca se dejó como "verificar después".

## PARA REVISIÓN HUMANA (Stage 11)

Copiado también a `10-publish-checklist.md` cuando se llegue a Stage 10:

1. **Nota de recurso de ayuda sobre adicción** en la descripción — `brain/04` §7, ahora más relevante que en v1 porque el cierre trata dos generaciones de la misma familia.
2. Confirmar que el tratamiento de Charles Ney Pemberton (figura histórica menor, fallecido ~1894) se mantiene con el mismo estándar de dignidad que su padre — ya cumplido en el guion, doble chequeo en Stage 11.
3. S07 (Hektoen International) tiene un error factual verificado — ya no se cita en el guion, pero si algún día se usa esa fuente para otra cosa, no tratarla como fiable sin cruzar.
