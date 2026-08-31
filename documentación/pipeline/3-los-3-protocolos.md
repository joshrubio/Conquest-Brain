---
doc: pipeline/3-los-3-protocolos
summary: "Protocolo 1 material disponible · Protocolo 2 hook naming · Protocolo 3 fact-check. Cuándo corre cada uno."
audience: "producción"
mirrors: [brain/12, brain/13, brain/14]
authority: guide
---

# Los tres protocolos

Tres protocolos corren en momentos concretos del pipeline. Dos en la ideación (Stage 0), uno en el fact-check (Stage 5).

| # | Protocolo | Cuándo | Doc |
|---|-----------|--------|-----|
| 1 | Material disponible | ideación, antes de aprobar | `brain/12` |
| 2 | Hook Naming | ideación, desde el minuto uno | `brain/13` |
| 3 | Fact-check | Stage 5, 3 capas | `brain/14` |

---

## Protocolo 1 — Material disponible

**Regla:** una idea no se aprueba hasta que alguien ha confirmado, **contra listados de archivo reales**, que hay suficiente material visual de dominio público —o un plan de gráficos propios que funcione— para sostener el episodio.

Nunca escribas un guion para una historia que no puedes ilustrar.

### Archivos que revisamos (dominio público / abiertos)

- **Imágenes, grabados, documentos:** Wikimedia Commons (PD/CC0), Library of Congress (Prints & Photographs, Chronicling America), National Archives (EE.UU. y RU), Europeana, NYPL Digital Collections, Rijksmuseum, The Met Open Access, Getty Open Content, Smithsonian Open Access, Gallica (BnF), Flickr Commons, NASA/NOAA, The Public Domain Review.
- **Imagen en movimiento:** Internet Archive (incl. Prelinger), NARA motion pictures, LOC film, Wikimedia Commons video.
- **Stock libre** (b-roll genérico ilustrativo, NO la pieza real): Pexels, Pixabay, Unsplash, Openverse (imagen); Pexels Videos, Coverr, Mixkit (vídeo).
- **Audio / música:** YouTube Audio Library, Pixabay Music, Jamendo (solo CC-BY/BY-SA/CC0), Musopen. Ver `referencia/música-y-licencias.md` (2ª pasada).
- **Lo nuestro:** gráficos, líneas de tiempo, mapas animados, tarjetas de texto — siempre disponibles; se cita la fuente del dato.

### La hoja de trabajo (por idea)

| Necesidad | ¿Encontrado? | Archivo + referencia | Derechos | Si no se encuentra |
|-----------|--------------|----------------------|----------|--------------------|
| Retrato(s) de la figura clave | | | PD / CC0 / CC-__ | ¿ilustración propia? ¿foto de estatua/placa pública? |
| Fotos de época del lugar / evento | | | | mapa/gráfico propio |
| Documentos (expedientes, cartas, titulares) | | | | normalmente PD si son antiguos / de gobierno |
| Imagen en movimiento de la época | | | | fijos + motion graphics |
| Datos para cualquier gráfico | | | | gráfico propio, citar fuente |

**Barra mínima:** cada beat de carga tiene ≥1 visual PD real O un gráfico propio que lo cubra del todo. Si más del ~30% del episodio sería "narrador sobre pantalla negra" o imágenes sin licencia, la idea falla E8.

### Sujeto sin fotografía

Común (Semmelweis, Hokusai, Tulipomanía). Enfoque en capas, de lo más honesto a lo más arriesgado:
1. Retratos/grabados de la época del propio sujeto.
2. Cómo lo mostraron otros / cómo se mostró él (autorretratos, caricaturas, una figura en su propia obra).
3. El acto en primer plano: manos, herramientas, el objeto hecho/usado. Muestra a la persona trabajando sin necesidad de cara.
4. Parallax 2.5D ligero sobre retratos fijos.
5. Una ilustración estilizada recurrente, claramente ilustración, rotulada una vez.

**No como recurso primario:** IA fotorrealista "dando vida" a un retrato. Como mucho un momento deliberado, rotulado (`brain/15`).

### Artefactos que produce

- `material-search.md` — la salida de este protocolo en la ideación / Stage 2. ¿Existe material suficiente, qué es débil, cómo se representa a un sujeto sin foto? **Es factibilidad, no selección.**

---

## Protocolo 2 — Hook Naming

Toda idea se nombra con un hook-title estilo Dieck **desde la ideación**. Sin gancho en el nombre, el vídeo no tiene audiencia.

- **3 variantes** de tipos distintos por idea, en `idea-pool.md`.
- La más fuerte → nombre de trabajo + favorito para el título publicado.
- Las otras dos → van a Stage 10 para A/B.

Detalle completo, tipos de gancho, plantillas y ejemplos en [modelo-narrativo/7-titular-con-gancho](../modelo-narrativo/7-titular-con-gancho.md).

---

## Protocolo 3 — Fact-check

Dos capas automáticas en Stage 5: L1 determinista (`tools/factcheck.py`) y L2 asistida por LLM (un prompt de 6 tablas de banderas). No hay firma humana. El guionista resuelve cada bandera en el guion. Ningún guion pasa a grabación hasta que L1 = PASS y cero banderas sin resolver.

Detalle completo en [4-fact-check](4-fact-check.md).
