# Fact-check (Stage 5)

**Dos capas, las dos automáticas. No hay firma humana.** La pasada L2 es el último control antes de grabar; el guionista resuelve cada bandera en el guion.

Regla: `brain/14-fact-check-protocol.md`. Producto: `04-factcheck-auto.md` (L1 + L2 + tabla de Resolución).

---

## Layer 1 — Pasada determinista

`python tools/factcheck.py 05-script.md 03-source-log.csv`

Sin juicio — pura consistencia:

1. **Toda `[S..]` del guion resuelve** a una fila de `03-source-log.csv`.
2. Toda fila del source-log tiene `tier` (A/B/C/D) y `rights_status`.
3. **Heurística de huérfana:** marca frases con número / fecha / nombre propio / comillas **sin `[S..]`** → candidatas a claim sin fuente.
4. **Chequeo de tier:** toda claim cuya única `[S..]` es Tier C/D → subir de tier o reformular como disputada.
5. Reporta conteos.

**Gate:** `PASS` — cero errores de etiqueta/tier; cada huérfana etiquetada en el guion o confirmada como no-factual.

---

## Layer 2 — Pasada asistida por LLM

`templates/fact-check-auto-prompt.md`: pega guion + source-log, devuelve **seis tablas de banderas**:

1. **Afirmaciones factuales** — cada una con su `[S..]`; `respalda` / `desajuste` / `no se puede saber` / `sin tag`.
2. **Interpretación como hecho** — + reescritura sugerida con marco ("una lectura posible…").
3. **Citas textuales** — ¿traducción marcada? ¿atribución + fecha? ¿riesgo apócrifa?
4. **Afirmaciones que deberían ir matizadas.**
5. **Psicología popular / datos-mito.**
6. **Riesgos legales / éticos / de independencia** — difamación, alegación sin desenlace, menor identificable, tema sensible, sujeto privado, pitch externo, dignidad (`brain/04`, `brain/05`).

**El LLM no es una fuente** (`brain/01` §9). Una bandera es una tarea de comprobar contra la fuente real, no un veredicto.

---

## Resolver las banderas

Usuario 001 (quien escribió) recorre cada bandera y:
- **aplica la corrección** en `05-script.md` (arregla una fecha, añade un matiz, reencuadra una interpretación, corta una línea sin fuente, añade una atribución en pantalla), o
- **la descarta** con una línea de motivo ("el guion ya lo marca como tradición").

Se anota en la **tabla de Resolución** de `04-factcheck-auto.md`.

**Gate:** L1 `PASS` + cero banderas sin resolver → el guion pasa a grabación. El pase legal/COI se vuelve a marcar en Stage 11 (`templates/publish-checklist.md`).

### Lo que L2 encontró en E001 (ejemplo real)

L2 marcó 39 afirmaciones y encontró:
- **2 errores reales:** la escala de edades del prefacio decía "a los 100" cuando el original dice "a los 110"; y una inconsistencia interna de fechas de la serie del Fuji.
- **3 claims poco sostenidas:** "Japón cerrado", la población de Edo, la anécdota del papel de embalar.

Los errores se corrigen en el guion; la anécdota se enmarca como lo que es ("se cuenta —y puede que la historia esté algo pulida—").

---

## Qué significa "automatizado" aquí

L1 y L2 convierten una revisión de página en blanco en un triaje de banderas ya encontradas, en minutos. No hay tercera capa: el criterio del canal es que un guion que pasa L1 limpio y con cada bandera de L2 resuelta está listo. El riesgo legal/ético fuerte se vuelve a mirar en el checklist de publicación.

## Si aparece un error después de publicar

Ver [modelo-narrativo/8-rigor-y-fuentes](../modelo-narrativo/8-rigor-y-fuentes.md) §9: comentario fijado + nota en descripción + tarjeta si es material, registrado en el retro. Nunca re-subir en silencio.
