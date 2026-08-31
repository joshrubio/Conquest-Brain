# Manifiesto de recursos — E001 «Hokusai»

> **Stage 7.** Cada beat archivístico del shotlist (`06-shotlist.md`) → una imagen concreta con **descarga directa** + **pase de estilo** (Usuario 001). Los gráficos propios (G1–G5, contadores) van al brief de diseño, no aquí.
> Depende de `brain/03` §Visual direction — **sin cerrar**. El pase no es definitivo hasta tener el look de la serie.

| Campo | Valor |
|-------|-------|
| ID episodio | E001 · narrador Usuario 002 |
| Salida del canal | **PENDIENTE** (1080p o 4K — `brain/03`). Este manifiesto asume 4K y avisa lo que no llega. |
| Look de referencia | **PENDIENTE**. Provisional: prints a sangre (sin margen ni sellos), color cálido consistente, grano fino. |
| Fecha | 2026-08-30 |

## Estándar de resolución (px en el eje que llena la imagen)

| Uso | 1080p | 4K |
|-----|-------|-----|
| Estático | ≥1920 | ≥3840 |
| Push-in lento | ≥2500 | ≥4800 |
| Parallax fuerte | ≥3000 | ≥6000 |
| Inserto (≤40% cuadro) | ≥900 | ≥1800 |

Si no llega: usar como inserto, cortar un **detalle** (un detalle a 2000 px sirve donde la página entera no), o descartar.

## Fuentes: descarga directa, sin captcha

- **Sí:** The Met (*Download*, JPEG ~4000 px), Wikimedia Commons (ficheros *Google Art Project* = 7000–20000 px — **la mejor para 4K**), Library of Congress (TIFF), Smithsonian Open Access (CC0).
- **No para descargar:** ukiyo-e.org y Google Arts & Culture (solo para **localizar** en qué museo está); IMSLP y similares (captcha / temporizador); blogs, tiendas de prints, artículos.

## Manifiesto

| # | Beat(s) | Qué es | Descarga directa | Museo / nº | Lic. | Res. esperada | Uso | Pase |
|---|---------|--------|------------------|------------|------|---------------|-----|------|
| 1 | 2, 27–28, 41, +G | **«La gran ola»** | Met https://www.metmuseum.org/art/collection/search/36491 → *Download* (~4000 px) · alt Wikimedia Commons *Google Art Project* (mayor res) | Met JP1847 / Commons | CC0 / PD | Met ~4000 px (4K justo para push-in) · Commons GAP mayor | full-frame + push-in → **preferir la de Commons si supera 4800 px** | |
| 2 | 26 | **«Fuji rojo» (*Gaifū kaisei*)** | TODO: localizar en Met o Wikimedia Commons (*Fine Wind, Clear Morning* / *South Wind, Clear Sky*) | Met / Commons | CC0 / PD | por confirmar | full-frame | |
| 3 | 26 | **Fuji en el barril del tonelero** | https://www.metmuseum.org/art/collection/search/36500 → *Download* | Met | CC0 | ~4000 px | full-frame (poco movimiento) | |
| 4 | 26 | **Fuji desde un camino** (*Tōkaidō Hodogaya*) | TODO: localizar en Met o Wikimedia Commons | Met / Commons | CC0 / PD | por confirmar | full-frame | |
| 5 | 25, 26 | 2–3 vistas más del Fuji | Met Open Access: https://www.metmuseum.org/art/collection/search?q=Thirty-six+Views+of+Mount+Fuji+Hokusai&showOnly=openAccess — elegir 2–3 de la serie, *Download* · alt Wikimedia Commons | Met / Commons | CC0 / PD | ~4000 px | cuadrícula (insertos) — **cualquier res sirve** | |
| 6b | 4, 24, 36 (una vez) | **Retrato de Hokusai por Keisai Eisen** — "la única cara real" | Commons: https://commons.wikimedia.org/wiki/File:Portrait_of_Hokusai_by_Keisai_Eisen.jpg | Commons | PD | por confirmar (verificar px del fichero) | inserto / uso puntual | |
| ai01 | 1 (cold open) | **Ilustración IA** — 1849, el cuarto, el hombre que se muere (de espaldas) | `07b-ai-prompts.md` §ai01 → generar | — | ilustración propia (IA) · **rótulo en pantalla** | ≥4800 px (upscale) | full-frame + push-in | ⧗ generar |
| ai02 | +B, +C (Acto 1) | **Ilustración IA** — el Daruma gigante de Nagoya (1817), figura de espaldas | `07b-ai-prompts.md` §ai02 | — | ilustración propia (IA) · rótulo | ≥4800 px | full-frame, zoom out | ⧗ generar |
| ai03 | 33 (Acto 4) | **Ilustración IA** — el incendio del taller, noche, ~1839, figura pequeña de espaldas | `07b-ai-prompts.md` §ai03 | — | ilustración propia (IA) · rótulo | ≥4800 px | full-frame | ⧗ generar |
| ai04 | 39 (cierre) | **Ilustración IA** — la metáfora del camino sin final (sustituye a G5) | `07b-ai-prompts.md` §ai04 | — | ilustración propia (IA) · rótulo | ≥4800 px | full-frame, ritmo lento | ⧗ generar |
| 9 | 34–35 · self-depiction | **«Autorretrato como pescador»** (1835) | TODO: localizar en Met o Wikimedia Commons (dibujo de Hokusai + inscripción de Ōi) | Met / Commons | CC0 / PD | por confirmar | full-frame | |
| 10 | 11–12 · [PLANT 1] | **Obra temprana firmada "Shunrō"** (actor kabuki, *hosoban*, 1780s) | Met Open Access: https://www.metmuseum.org/art/collection/search?q=Shunro&showOnly=openAccess — elegir una con **firma legible**, *Download* | Met | CC0 | ~4000 px | inserto + zoom a la firma → basta | |
| 11 | 10 | Actor de la **escuela Katsukawa (Shunshō)** | https://www.metmuseum.org/art/collection/search?q=Katsukawa+Shunsho&showOnly=openAccess → *Download* | Met | CC0 | ~4000 px | full-frame | |
| 12 | 21–22 · +A | **Páginas de los *Hokusai Manga*** | Met tiene **hojas sueltas** como objeto (CC0, ~4000 px): https://www.metmuseum.org/art/collection/search?q=Hokusai+Manga&showOnly=openAccess · alt Smithsonian Libraries (JPEG-2000) | Met / Smithsonian | PD/CC0 | Met ~4000 px OK · scans de libro ~2000 px → **usar recorte de detalle** (una figura, no la página) | insertos rápidos → cualquier res | |
| 13 | +B, +C | Daruma gigante de Nagoya (1817) | no hay imagen de época → **ilustración/reconstrucción propia** | — | propio | — | — | n/a |
| 14 | 30–31 · G4 | **Colofón de *Cien vistas del monte Fuji*** (1834) | Met tiene el libro y hojas: https://www.metmuseum.org/art/collection/search?q=One+Hundred+Views+of+Mount+Fuji+Hokusai&showOnly=openAccess — buscar la página del colofón · el texto se rehace como **tarjeta propia** con traducción propia (más legible que la foto del original) | Met | CC0 | variable | **plan real: tarjeta de texto propia** + la página original de fondo como inserto | |
| 15 | 25b–26 | Lámina de *Cien vistas* para ilustrar la serie | Met (misma búsqueda que #14) → *Download* | Met | CC0 | ~4000 px | full-frame | |
| 16 | 33 | **Incendio urbano en Edo** | LOC *Fine Prints Japanese pre-1915*, TIFF: https://www.loc.gov/collections/japanese-fine-prints-pre-1915/?q=fire — o Met «hikeshi / firemen» | LOC / Met | PD/CC0 | LOC TIFF alta · Met ~4000 px | atmósfera, full-frame | |
| 17 | 34–35 | **Obra de Katsushika Ōi** | **HUECO** — MFA Boston (open access, TIFF) y Freer/Smithsonian: buscar «Katsushika Oi» en https://collections.mfa.org y https://asia.si.edu . «Night Scene in the Yoshiwara» (Ōta Memorial, Tokio) **NO es open access**. Plan B: solo #9 + tarjeta de texto | MFA / Freer / ⚠️ Ōta | CC0 (MFA/Freer) | por confirmar | full-frame o inserto | ⚠️ |
| 18 | 6–7 | Mapa / vista de Edo s. XVIII–XIX | LOC https://www.loc.gov/collections/japanese-fine-prints-pre-1915/ (TIFF) · Commons *Old maps of Edo* (varios GAP, alta res) | LOC / Commons | PD | alta | full-frame | |
| 19 | 8 · G1 | Referencia del proceso ukiyo-e | Commons *Woodblock printing in Japan* | Commons | PD | — | solo referencia; el beat es motion-graphic propio | |
| 20 | +D | Tirada azul (*aizuri-e*) de una vista del Fuji | localizar en ukiyo-e.org («Kajikazawa aizuri» / estados de «Kanagawa») → ir al **museo que la tenga** y descargar IIIF/Download; muchos están en Met / Wikimedia Commons | Met / Commons | CC0 / PD | ~5000 px | comparativa, insertos | |
| 21 | +F | **Portada de *La Mer*** (1905, Durand) | **IMSLP tiene captcha → no.** Opción real: BnF **Gallica** (IIIF, sin captcha) buscar «Debussy La Mer Durand 1905» · si no hay res buena → **plan B: mostrar la Ola real (#1) y decir en la narración que fue a la portada**, o la portada como inserto de baja res durante 2 s | Gallica / — | PD (1905) | Gallica variable | inserto breve → baja res tolerable | ⚠️ |
| 22 | +F | **Van Gogh copiando a Hiroshige** (1887) | Commons *Google Art Project* (alta res): https://commons.wikimedia.org/wiki/File:Vincent_van_Gogh_-_Brug_in_de_regen-_naar_Hiroshige_-_Google_Art_Project.jpg | Commons / VG Museum | PD (†1890) | ~10000 px | full-frame | ✅ res |
| 23 | +E, +F | Interior de Giverny (Monet) | **sin fuente PD** — foto con licencia. **Recomendación: cortar el plano.** La línea "Monet las coleccionaba" se cubre con #22. | — | ❌ | — | — | ❌ manifiesto PD |

## Decisión: la cara de Hokusai — RESUELTO

Método elegido: **ilustración estilizada por IA** (opción C, vía IA en vez de ilustrador), en registro **sumi-e / xilografía**, para que se siente al lado de los prints reales y se lea como ilustración. **Sin cara reconocible** (figura de espaldas / silueta / distancia). Rótulo en pantalla siempre. Protocolo: `brain/15`.

- Prompts: **[`07b-ai-prompts.md`](07b-ai-prompts.md)** — 4 imágenes (`ai01` cold open, `ai02` Daruma, `ai03` incendio, `ai04` camino del cierre).
- Se mantiene además el grabado de **Keisai Eisen** 1–2 veces como "la única cara real que existe" (fila 6b abajo).
- El material archivístico real (los ~20 prints CC0) sigue siendo la base. Las 4 IA son beats puntuales.

## Gráficos propios (brief de diseño)

| Gráfico | Beat(s) | Qué muestra | Fuente |
|---------|---------|-------------|--------|
| G1 | 8 | Proceso ukiyo-e (dibujo → planchas → impresión) | conceptual [S02] |
| G2 | 15, 38, 41 | Línea de tiempo de nombres, obra bajo cada uno | [S05] |
| G3 | 19 | Mapa de Edo con las ~93 mudanzas | [S06] — salvedad |
| G4 | 30–31 | Escala de edades del prefacio de 1834 (traducción propia, hasta los 110) | [S01] |
| G5 | 39 | "¿ya llegué?" vs "¿me estoy acercando?" | [S15] |
| — | 25b | Contador «36 → 46» | [S09] |

## Huecos reales

- [x] ~~Decisión sobre la cara de Hokusai~~ → **ilustración IA** (`07b-ai-prompts.md`)
- [ ] **Generar las 4 IA** (ai01–ai04) y guardarlas en `assets/ai/`
- [ ] **Salida del canal** 1080p vs 4K (`brain/03`) — determina qué imágenes archivísticas valen
- [ ] #17 Ōi — confirmar qué hay en MFA/Freer con TIFF libre; si nada → plan B
- [ ] #21 *La Mer* — probar Gallica; si no, plan B
- [ ] #10 — abrir el objeto Met y confirmar firma "Shunrō" legible
- [ ] Elegir **una** impresión de "La gran ola" y de cada lámina; cerrar nº de objeto en el pase

## Gate Stage 7

- [ ] Cada beat archivístico → imagen aceptada, inserto/recorte viable, o plan B (gráfico propio)
- [ ] Toda imagen con descarga directa sin captcha y licencia clara
- [ ] Cada imagen llega a la resolución de su uso (o se reasigna a inserto/detalle)
- [ ] Color/estado revisados por tramo (las 36 vistas juntas; los retratos juntos)
- [ ] Créditos de cortesía para `09-description.md` (Met, LOC, Commons…)
- [ ] Descargas a `assets/` — `E001_beat27_greatwave_met.tif`
- [ ] `brain/03` §Visual direction + salida del canal cerrados
