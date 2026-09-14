# Manifiesto de recursos — E003 «Tulipomanía»

> **Stage 7.** Resuelve cada beat archivístico del shotlist a **una imagen concreta**, con enlace directo, y registra el **pase de estilo** (¿encaja con la estética del vídeo?). Los beats de gráfico propio no van aquí — van al brief de diseño.
> Depende de: `06-shotlist.md` (los beats) · `brain/03` §Visual identity (grade, paleta, tipografía) · `material-search.md` (qué existe).

| Campo | Valor |
|-------|-------|
| ID episodio | E003 · narrador Usuario 002 |
| Responsable | Usuario 001 |
| Look de referencia | (grade / grano / letterbox / tratamiento de la serie — de `brain/03`) |
| Salida del canal | 4K (3840×2160) — `brain/03` |
| Fecha | 2026-09-13 |

## Estándar de resolución

Píxeles necesarios en el eje que **llena** la imagen:

| Uso | Salida 1080p | Salida 4K |
|-----|--------------|-----------|
| Estático (sin movimiento) | ≥ 1920 px | ≥ 3840 px |
| Push-in / paneo lento (~1,3×) | ≥ 2500 px | ≥ 4800 px |
| Parallax / zoom fuerte | ≥ 3000 px | ≥ 6000 px |
| Inserto (≤ 40% del cuadro) | ≥ 900 px | ≥ 1800 px |

Si una imagen no llega, la opción es: usarla más pequeña (inserto), cortar un **detalle** (un detalle a 2000 px sirve donde la página entera no), o descartarla.

## Fuentes: solo descarga directa, sin captcha

- **Archivo (la pieza real):** museos con Open Access de descarga directa — **The Met** (JPEG ~4000 px, botón *Download* / API), **Library of Congress** (TIFF), **Smithsonian Open Access** (CC0), **Rijksmuseum** (RM API), **Wikimedia Commons** (*Google Art Project* = 7000–20000 px).
- **Stock libre (b-roll genérico ilustrativo, no la pieza real):** Pexels, Pixabay, Unsplash, Openverse (imagen) · Pexels Videos, Coverr, Mixkit (vídeo). APIs gratis. Solo donde el espectador lo lee como *cutaway*, no como "esto es lo real".
- **No como fuente de descarga:** agregadores (ukiyo-e.org, Google Arts & Culture) — para **localizar**, no bajar. Sitios con captcha/temporizador (IMSLP y similares). Blogs, tiendas de prints, artículos. **Stock de pago** (Getty, Shutterstock, Storyblocks…) — fuera por regla actual.
- Si el único sitio que la tiene es de acceso restringido → **hueco**: misma pieza en otro museo, o plan B (gráfico propio / recorte / AI / se corta).

## Flujo

**`07-style-pass.html` es el artefacto central del Stage 7.** Todo se decide ahí — cada beat (cold open incluido) tiene su propia fila de candidatos, no hay una caja de «intro» aparte.

1. **Pull** — `07-pull.tsv` (beat · kind `stock|stock-img|video|archive` · source · query · opts) + `build_ai_prompts.py` antes → `python tools/pull_assets.py E0XX-slug` → `07-style-pass.md` (registro) + `.html` (la superficie: candidatos por beat, rutas de imágenes IA, música).
2. **Pase** (Usuario 001) — candidato por beat con los criterios de abajo, o ruta propia. **«Guardar»** guarda + descarga sin cerrar el stage; **«Finalizar Stage 7»** hace lo mismo y además pliega el gate: baja todo a `assets/{stock,video,archive,ai}/`, verifica resolución, escribe `assets/CREDITS.md` + `07-selection.md`.
3. **Manifiesto** — se rellena solo al plegar (`advance.py fold` → `_write_assets_manifest`), transcrito de `07-selection.md`. No hace falta tocarlo a mano.

## Criterios del pase de estilo

Marca cada candidato:

- **Resolución** — ¿suficiente para el uso (plano completo vs. inserto) y para hacer push-in / parallax sin deshacerse?
- **Estado** — manchas (foxing), roturas, recorte del papel, decoloración: ¿aceptable o distrae?
- **Color** — ¿coherente con el grade del episodio? Las impresiones ukiyo-e varían mucho entre tiradas y entre escaneos de museo (unas cálidas, otras frías, otras con más contraste).
- **Encuadre / márgenes** — ¿el escaneo trae el margen del papel, sellos de coleccionista, montura? ¿lo queremos o lo recortamos a sangre?
- **Coherencia de secuencia** — las imágenes que van juntas en un tramo, ¿parecen de la misma familia (misma calidad de escaneo, mismo tratamiento)?
- **Veredicto** — ✅ aceptada · ⚠️ dudosa (anota qué falta) · ❌ rechazada (motivo)

## Manifiesto (auto — transcrito de `07-selection.md` al plegar Stage 7)

> Cada fila ya pasó el pase de estilo al elegirse entre candidatos en `07-style-pass.html` — no hace falta un veredicto aparte aquí. Licencia y detalle exacto de cada pieza: `assets/CREDITS.md`.

| Beat | Fuente | Res. | Archivo |
|------|--------|------|---------|
| 35 | pexelsv:35 | — | `assets/video/beat35_pexelsv_35.mp4` |
| 4 | commons:96820986 | 1931x2422 | `assets/archive/beat4_commons_96820986.png` |
| 5 | commons:135440978 | 3296x2404 | `assets/archive/beat5_commons_135440978.jpg` |
| 6 | commons:199488 | 1182x1829 | `assets/archive/beat6_commons_199488.jpg` |
| 12 | commons:79710878 | 14168x11528 | `assets/archive/beat12_commons_79710878.jpg` |
| 13 | commons:91985874 | 1200x900 | `assets/archive/beat13_commons_91985874.jpg` |
| 14 | commons:3686665 | 2360x2948 | `assets/archive/beat14_commons_3686665.jpg` |
| 16 | commons:22605738 | ? | `assets/archive/beat16_commons_22605738.jpg` |
| 17 | commons:199488 | 1182x1829 | `assets/archive/beat17_commons_199488.jpg` |
| 41 | commons:135414414 | 1348x1747 | `assets/archive/beat41_commons_135414414.png` |
| 43 | pixabayv:111281 | — | `assets/video/beat43_pixabayv_111281.mp4` |
| 45 | commons:136637512 | 793x525 | `assets/archive/beat45_commons_136637512.jpg` |
| 56 | commons:107432089 | 1211x1591 | `assets/archive/beat56_commons_107432089.png` |
| 57 | commons:19048320 | 1649x1032 | `assets/archive/beat57_commons_19048320.jpg` |
| 1 | ai:ai01 | 1672x941 | `assets/ai/E003_ai01_hero-amsterdam.png` |
| 2 | ai:ai02 | 1672x941 | `assets/ai/E003_ai02_marinero-bulbo.png` |
| 15 | ai:ai03 | 1672x941 | `assets/ai/E003_ai03_jardin-asalto.png` |
| 25 | ai:ai04 | 1672x941 | `assets/ai/E003_ai04_flor-fantasma.png` |
| 29 | ai:ai05 | 1672x941 | `assets/ai/E003_ai05_cultivadores-experimentos.png` |
| 34 | ai:ai06 | 1672x941 | `assets/ai/E003_ai06_laboratorio-1928.png` |
| 40 | ai:ai07 | 1672x941 | `assets/ai/E003_ai07_taberna-bolsa.png` |
| 49 | ai:ai08 | 1672x941 | `assets/ai/E003_ai08_impreso-resultados.png` |
| 52 | ai:ai09 | 1672x941 | `assets/ai/E003_ai09_gremio-haarlem.png` |
| 53 | ai:ai10 | 1672x941 | `assets/ai/E003_ai10_fortunas-perdidas.png` |
| 59 | ai:ai11 | 1672x941 | `assets/ai/E003_ai11_crisis-britanicas.png` |
| 63 | ai:ai12 | 1672x941 | `assets/ai/E003_ai12_archivo-notarial.png` |
| 69 | ai:ai13 | 1672x941 | `assets/ai/E003_ai13_thompson-articulo.png` |


## Gráficos propios (no van en el manifiesto — resumen para el brief de diseño)

| Gráfico | Beat(s) | Qué muestra | Datos / fuente [ID] |
|---------|---------|-------------|---------------------|
| G1 | | | |

## Huecos / a conseguir

- [ ] …

## Gate Stage 7

- [ ] Cada beat del shotlist (cold open incluido) tiene un recurso **aceptado** o un plan B (gráfico propio) — nunca «sin fila» en `07-pull.tsv` (`brain/12`: si el pull no encuentra nada, se afina la búsqueda y se corre de nuevo solo para ese beat antes de recurrir a recreación/ilustración)
- [ ] Toda imagen con licencia clara (CC0 / PD / licencia obtenida) y **descarga directa sin captcha**
- [ ] Cada imagen **llega a la resolución** que pide su uso (tabla arriba); si no, se usa como inserto / recorte de detalle / se corta
- [ ] Coherencia de color/estado revisada por tramos, no solo por imagen
- [ ] Créditos de cortesía anotados para el bloque de descripción (`09-description.md`)
- [ ] Descargas hechas a `assets/` con nombres consistentes
- [ ] `brain/03` §Visual identity (grade, tipografía, dispositivo de expediente) — ya cerrado
