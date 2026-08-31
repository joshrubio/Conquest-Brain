---
doc: modelo-narrativo/8-rigor-y-fuentes
summary: "Ninguna afirmación sin fuente. Tiers A-D, etiquetas [S..], citas, elegibilidad, verdad vs. leyenda pulida, correcciones."
audience: "guionista, investigación"
mirrors: [brain/01]
authority: guide
---

# Rigor y fuentes

El valor entero del canal es este: **ninguna afirmación sin fuente**. Un espectador tiene que poder verificar cualquier dato y encontrarlo firme. Trata cada episodio como periodismo publicable, no como "contenido".

Regla completa: `brain/01-editorial-and-sourcing.md`.

## 1. La regla de la afirmación sin cita

Toda frase factual del guion —fechas, números, citas, causas, "él dijo", "la empresa hizo"— tiene que trazar a una fuente registrada en `03-source-log.csv` para ese episodio.

Si no se puede citar: se corta, o se enmarca **explícitamente** como desconocido/en disputa en pantalla ("no hay registro de…", "las fuentes discrepan…").

## 2. Los tiers de fuente

| Tier | Ejemplos | Uso |
|------|----------|-----|
| **A — Primaria** | Registros judiciales, expedientes oficiales, archivos, datos de gobierno, cartas/diarios originales, patentes, informes corporativos, grabaciones verificadas, testimonio de primera mano on the record. | Preferida. Toda claim fuerte necesita al menos una A o B. |
| **B — Secundaria de calidad** | Trabajo revisado por pares, libro de un historiador/periodista especialista **con citas**, cobertura de un periódico de referencia con firma. | Aceptable como soporte principal. |
| **C — Secundaria débil** | Artículos de interés general sin fuentes, resúmenes enciclopédicos, documentales. | **Solo para localizar leads.** Nunca el único soporte de una claim. |
| **D — Inservible** | Blogs anónimos, redes sociales, foros, granjas de contenido, output de IA, docs de "reconstrucción" no verificables. | **Nunca se cita.** |

**Mínimo por episodio:** toda claim de carga tiene ≥1 fuente Tier A/B. Los puntos en disputa necesitan ≥2 fuentes independientes, o se presentan como en disputa.

## 3. Las etiquetas `[S..]`

En el guion, cada frase factual termina con su etiqueta: `[S12]`. Esa etiqueta resuelve contra una fila del `03-source-log.csv`.

**Ejemplo — E001:**

> Y Edo, en ese momento, es probablemente la ciudad más grande del mundo: cerca de un millón de personas [S20], con una clase urbana que tiene dinero para gastar en teatro, en libros ilustrados y en estampas.

`[S20]` → una fila del source-log con el título de la fuente, el autor, el tier, la ubicación exacta (página / minuto), el estado de derechos.

Layer 1 del fact-check (`tools/factcheck.py`) comprueba automáticamente que **toda `[S..]` resuelve** y marca las frases que tienen número/fecha/nombre propio/comillas **sin** `[S..]` como candidatas a afirmación sin fuente.

## 4. Citas textuales

- Reproducidas **verbatim** de la fuente, con atribución y fecha, con la ubicación exacta anotada en el dossier.
- Traducciones al español: marcadas ("traducción propia" o cita de una traducción publicada). El original queda en el dossier.
- Sin paráfrasis presentada como cita. Sin citas "compuestas".

**Ejemplo — E001** (cita atribuida y con traducción marcada):

> Firmaba *Gakyō Rōjin Manji* — «el viejo loco por la pintura», en traducción propia [S13].

## 5. Elegibilidad de registro público

Antes de que empiece la investigación, el sujeto tiene que pasar `ideas/idea-rubric.md`:
- ¿Es figura pública, caso histórico, o empresa/práctica?
- ¿Hay un registro documental público (no solo chismorreo)?
- ¿Las fuentes están en dominio público / son legalmente accesibles?

Si alguna respuesta es no → **no elegible**. Sin excepciones por "gran historia".

## 6. Verdad vs. leyenda pulida

Muchos de nuestros sujetos traen un mito pegado: Colonel Sanders y sus "1009 rechazos", las "93 mudanzas" de Hokusai, la Tulipomanía como locura colectiva.

**El canal desmonta el mito de camino.** No lo ignora ni lo repite: lo nombra, dice qué está documentado y qué no, y sigue. Es literalmente on-brand — el canal va sobre "la versión real vs. la versión oficial".

**Ejemplo — E001** (cifra tradicional marcada como tal):

> Se cuenta que Hokusai se mudó unas noventa y tres veces. La cifra es tradicional y su origen es incierto — pero da la medida de un hombre que nunca se asentó.

Y en el shotlist ese beat lleva rótulo de salvedad obligatorio: «~93 mudanzas — cifra tradicional, origen incierto».

## 7. La IA como herramienta, nunca como fuente

La IA ayuda con navegación de investigación, estructura, transcripción y borrador. **El output de IA nunca es una fuente.** Todo dato que la IA saque se re-verifica contra una fuente real Tier A/B antes de entrar al guion. (Esto incluye a Claude en este mismo repo.)

## 8. El gate de fact-check

Ningún guion pasa a grabación hasta que el fact-check de Stage 5 despeje: **L1** (`factcheck.py`, determinista) = PASS y **L2**, una pasada del agente que analiza cada afirmación contra su fuente y **aplica las correcciones al guion** (ajustar a lo que la fuente respalda, matizar, atribuir, o cortar — nunca añadir un dato). 100% automático, sin firma. El pase legal/COI se marca una vez en Stage 11.

Detalle del proceso en [pipeline/4-fact-check](../pipeline/4-fact-check.md).

## 9. Correcciones tras publicar

Errores post-publicación: comentario fijado + nota en la descripción + tarjeta en pantalla si es material. Se registra en el `11-retro.md` del episodio. **Nunca se re-sube en silencio sin anotar el cambio.**
