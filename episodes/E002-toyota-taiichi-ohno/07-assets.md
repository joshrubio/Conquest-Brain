# Manifiesto de recursos — E002 «Toyota / Taiichi Ohno»

> **Stage 7.** Resuelve cada beat archivístico del shotlist a **una imagen concreta**, con enlace directo, y registra el **pase de estilo** (¿encaja con la estética del vídeo?). Los beats de gráfico propio no van aquí — van al brief de diseño.
> Depende de: `06-shotlist.md` (los beats) · `brain/03` §Visual identity (grade, paleta, tipografía) · `material-search.md` (qué existe).

| Campo | Valor |
|-------|-------|
| ID episodio | E002 · narrador Usuario 002 |
| Responsable | Usuario 001 |
| Look de referencia | (grade / grano / letterbox / tratamiento de la serie — de `brain/03`) |
| Salida del canal | 4K (3840×2160) — `brain/03` |
| Fecha | 2026-09-11 |

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
| 2 | pexelsv:2 | — | `assets/video/beat2_pexelsv_2.mp4` |
| 3 | pexelsv:3 | — | `assets/video/beat3_pexelsv_3.mp4` |
| 5 | commons:133224482 | 3720x2520 | `assets/archive/beat5_commons_133224482.jpg` |
| 25 | commons:6044645 | 2463x1733 | `assets/archive/beat25_commons_6044645.jpg` |
| 29 | pixabay:350376 | 1280x853 | `assets/stock/beat29_pixabay_350376.jpg` |
| 35 | commons:152655585 | 635x654 | `assets/archive/beat35_commons_152655585.jpg` |
| 43 | commons:17099316 | 3000x2028 | `assets/archive/beat43_commons_17099316.jpg` |
| 45 | pexels:7018662 | 5790x3860 | `assets/stock/beat45_pexels_7018662.jpeg` |
| 47 | commons:139506 | 4446x3149 | `assets/archive/beat47_commons_139506.jpg` |
| 50 | commons:139506 | 4446x3149 | `assets/archive/beat50_commons_139506.jpg` |
| 52 | commons:139506 | 4446x3149 | `assets/archive/beat52_commons_139506.jpg` |
| 74 | commons:28067171 | 2000x1528 | `assets/archive/beat74_commons_28067171.jpg` |
| 76 | commons:28067171 | 2000x1528 | `assets/archive/beat76_commons_28067171.jpg` |
| 77 | unsplash:AXBtbNQOAZw | 4000x6000 | `assets/stock/beat77_unsplash_AXBtbNQOAZw.jpg` |
| 81 | unsplash:AXBtbNQOAZw | 4000x6000 | `assets/stock/beat81_unsplash_AXBtbNQOAZw.jpg` |
| 97 | commons:17082264 | 3000x2018 | `assets/archive/beat97_commons_17082264.jpg` |
| 98 | commons:17082264 | 3000x2018 | `assets/archive/beat98_commons_17082264.jpg` |
| 106 | commons:5963985 | 2816x1728 | `assets/archive/beat106_commons_5963985.jpg` |
| 108 | pexelsv:34126231 | — | `assets/video/beat108_pexelsv_34126231.mp4` |
| 126 | pexelsv:34126231 | — | `assets/video/beat126_pexelsv_34126231.mp4` |
| 1 | ai:ai01 | 1672x941 | `assets/ai/E002_ai01_koromo-crisis.png` |
| 4 | ai:ai09 | 1672x941 | `assets/ai/E002_ai09_kiichiro-leaves.png` |
| 8 | ai:ai02 | 1672x941 | `assets/ai/E002_ai02_ohno-portrait.png` |
| 12 | ai:ai03 | 1672x941 | `assets/ai/E002_ai03_sakichi-loom.png` |
| 15 | ai:ai04 | 1672x941 | `assets/ai/E002_ai04_loom-autostop.png` |
| 18 | ai:ai05 | 1672x941 | `assets/ai/E002_ai05_kiichiro-chevy.png` |
| 21 | ai:ai06 | 1672x941 | `assets/ai/E002_ai06_model-aa.png` |
| 23 | ai:ai07 | 1672x941 | `assets/ai/E002_ai07_war-trucks.png` |
| 24 | ai:ai08 | 1672x941 | `assets/ai/E002_ai08_koromo-bombed.png` |
| 56 | ai:ai10 | 1672x941 | `assets/ai/E002_ai10_shopfloor-chaos.png` |
| 64 | ai:ai11 | 1672x941 | `assets/ai/E002_ai11_kanban-card.png` |
| 70 | ai:ai12 | 1672x941 | `assets/ai/E002_ai12_andon-cord.png` |
| 75 | ai:ai13 | 1672x941 | `assets/ai/E002_ai13_supermarket-slides.png` |
| 82 | ai:ai14 | 1672x941 | `assets/ai/E002_ai14_ohno-supermarket.png` |
| 87 | ai:ai16 | 1672x941 | `assets/ai/E002_ai16_supplier-daily.png` |
| 91 | ai:ai15 | 1672x941 | `assets/ai/E002_ai15_chalk-circle.png` |
| 102 | ai:ai17 | 1672x941 | `assets/ai/E002_ai17_toyota-seminars.png` |
| 104 | ai:ai18 | 1672x941 | `assets/ai/E002_ai18_ohno-book.png` |
| 110 | ai:ai19 | 1672x941 | `assets/ai/E002_ai19_nummi-line.png` |


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
