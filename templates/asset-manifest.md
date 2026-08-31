---
doc: asset-manifest
summary: "Resolves each archival beat to one concrete image with a direct link + the style-pass judgement."
stage: [7]
fills: "07-assets.md"
rule: [12, 03]
authority: template
---

# Manifiesto de recursos — E0XX «<título>»

> **Stage 7.** Resuelve cada beat archivístico del shotlist a **una imagen concreta**, con enlace directo, y registra el **pase de estilo** (¿encaja con la estética del vídeo?). Los beats de gráfico propio no van aquí — van al brief de diseño.
> Depende de: `06-shotlist.md` (los beats) · `brain/03` §Visual identity (grade, paleta, tipografía) · `material-search.md` (qué existe).

| Campo | Valor |
|-------|-------|
| ID episodio | E0XX |
| Responsable | Usuario 001 |
| Look de referencia | (grade / grano / letterbox / tratamiento de la serie — de `brain/03`) |
| Salida del canal | 4K (3840×2160) — `brain/03` |
| Fecha | AAAA-MM-DD |

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

**`07-style-pass.html` es el artefacto central del Stage 7.** Todo se decide ahí.

1. **Pull** — `07-pull.tsv` (beat · kind `stock|stock-img|video|intro|archive` · source · query · opts) + `build_ai_prompts.py` antes → `python tools/pull_assets.py E0XX-slug` → `07-style-pass.md` (registro) + `.html` (la superficie: intro arriba, candidatos por beat a la izquierda, prompts IA a la derecha).
2. **Pase** (Usuario 001) — intro (hasta 5 propios + sugeridos + checkbox «intro» en cards) · candidatos por beat con los criterios de abajo · rutas de imágenes IA en la columna derecha. **Finalizar Stage 7** (escribe `07-picks.txt`) → `python tools/pull_assets.py E0XX-slug --download` baja todo a `assets/{intro,stock,video,archive,ai}/`, verifica resolución, escribe `assets/CREDITS.md` + **`07-selection.md`**.
3. **Manifiesto** — plegar `07-selection.md` aquí; una fila por asset **aceptado** (intro / beat / IA), con Uso y Pase.

## Criterios del pase de estilo

Marca cada candidato:

- **Resolución** — ¿suficiente para el uso (plano completo vs. inserto) y para hacer push-in / parallax sin deshacerse?
- **Estado** — manchas (foxing), roturas, recorte del papel, decoloración: ¿aceptable o distrae?
- **Color** — ¿coherente con el grade del episodio? Las impresiones ukiyo-e varían mucho entre tiradas y entre escaneos de museo (unas cálidas, otras frías, otras con más contraste).
- **Encuadre / márgenes** — ¿el escaneo trae el margen del papel, sellos de coleccionista, montura? ¿lo queremos o lo recortamos a sangre?
- **Coherencia de secuencia** — las imágenes que van juntas en un tramo, ¿parecen de la misma familia (misma calidad de escaneo, mismo tratamiento)?
- **Veredicto** — ✅ aceptada · ⚠️ dudosa (anota qué falta) · ❌ rechazada (motivo)

## Intro / cold open (§0) — orden de pantalla

| # | Qué es | Fuente / enlace | Licencia | Res. real | Pase | Archivo local |
|---|--------|-----------------|----------|-----------|------|---------------|
| 1 | | | | | ✅/⚠️/❌ | `assets/intro/intro01_…` |
| 2 | | | | | | |

## Manifiesto (por beat + IA)

| # | Beat(s) | Qué es | Enlace de descarga | Museo / nº | Licencia | Res. real | Uso (estático / push-in / inserto) | Pase | Archivo local |
|---|---------|--------|--------------------|------------|----------|-----------|------------------------------------|------|---------------|
| 1 | | | | | CC0 / PD / licencia / IA (rótulo) / ⚠️ | px reales | | ✅/⚠️/❌ + nota | `assets/…` |
| 2 | | | | | | | | | |

## Gráficos propios (no van en el manifiesto — resumen para el brief de diseño)

| Gráfico | Beat(s) | Qué muestra | Datos / fuente [ID] |
|---------|---------|-------------|---------------------|
| G1 | | | |

## Huecos / a conseguir

- [ ] …

## Gate Stage 7

- [ ] Cold open (§0): 2–5 assets de intro aceptados, en orden
- [ ] Cada beat archivístico del shotlist tiene una imagen **aceptada** o un plan B (gráfico propio)
- [ ] Toda imagen con licencia clara (CC0 / PD / licencia obtenida) y **descarga directa sin captcha**
- [ ] Cada imagen **llega a la resolución** que pide su uso (tabla arriba); si no, se usa como inserto / recorte de detalle / se corta
- [ ] Coherencia de color/estado revisada por tramos, no solo por imagen
- [ ] Créditos de cortesía anotados para el bloque de descripción (`09-description.md`)
- [ ] Descargas hechas a `assets/` con nombres consistentes
- [ ] `brain/03` §Visual identity (grade, tipografía, dispositivo de expediente) — ya cerrado
