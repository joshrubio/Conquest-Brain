# Shotlist / B-roll — E001 «Hokusai» (v2)

> Stage 6. Inferida del guion bloqueado (`brain/11-visual-rhythm.md`). **v2: regenerada sobre `05-script.md` v2.0** (narrativa continua + revisión del guionista + correcciones de fact-check 2026-09-08). v1 (2026-08-29) estaba sobre la estructura de 5 actos, ya obsoleta.
> Espina de ~46 beats clave. El shotlist final añade los intermedios (~130–160 para ~18 min con reutilización). Ningún visual pasa a edición sin estado de derechos en `03-source-log.csv`.

| Campo | Valor |
|-------|-------|
| ID episodio | E001 |
| Versión de guion | v2.0 (continuidad narrativa) + fact-check L2 2026-09-08 |
| Narrador del episodio | Usuario 002 |
| Responsable | Usuario 001 |
| Fecha | 2026-09-08 |

## Heurística aplicada (`brain/11 §1b + §2.1`)

**A-roll / B-roll:** el narrador está a cámara (`acamara`) en cold open · bumper · beat de opinión sobre «La gran ola» (30–31) · **todo el cierre** (43–48). El resto es B-roll (archivo / gráfico / stock / IA). ~13 de 48 beats a cámara ≈ **~35 % del metraje** — dentro de la horquilla 30–45 % de `brain/11 §1b`.

Resto: 1 beat cada ~2–3 frases o cambio de sujeto · todo `[EN PANTALLA]` literal · `[HOOK VISUAL]` = B-roll cortado sobre la narración a cámara · `[EXPLICADOR]` = secuencia motion sin talking-head · `[PROMISE n]`/`[PAY n]` = **mismo `asset` y `motion`** (B-roll) · el cierre corta a imágenes ya vistas · cifras dudosas → rótulo de salvedad · sin source cards (`brain/03`).

**Ritmo objetivo (`brain/11 §2.2`):** cold open 10–12 b/min · narrativa 7–9 (B-roll) · explicador 3–5 · cierre 3–5 a cámara (cara 4–8 s) · CTA 1. Casi todo el B-roll es **dominio público / CC0** (The Met, British Museum, Rijksmuseum, LOC, Wikimedia). 4 planos de IA con rótulo permanente (`brain/15`, `07b-ai-prompts.md`).

## A cámara (A-roll · narrador: Usuario 002)

Beats `acamara`: **1, 5, 6, 29, 30, 31, 43, 44, 46, 47, 48**. `assemble.py` recorta la toma (`assets/<toma>.trimmed.mp4`, Stage 8) a la ventana de cada beat; sin Ken Burns.

| Aspecto | Valor |
|---------|-------|
| Encuadre | Plano medio corto, mirada a cámara |
| Fondo / luz | Set fijo de serie (`brain/03`) |
| Toma | una sola toma continua (talking-head), ya grabada |

## Timeline — la espina (una fila por beat, en orden de emisión · `assemble.py` la parsea · re-alineada a la voz en Stage 9)

| # | in | dur | sección | tipo | asset | rótulo | motion | marcador | guion (frag.) |
|---|----|-----|---------|------|-------|--------|--------|----------|---------------|
| 1 | 0:00 | 9 | cold open | ia | E001_ai01_deathbed-room | Ilustración — Conquest | push | HOOK | «en 1849, en un cuarto de alquiler de Edo, un hombre se estaba muriendo» (VO sobre la ilustración) |
| 2 | 0:09 | 7 | cold open | stock | intro01 | — | cut | — | «llevaba más de setenta años dibujando» (clip de intro) |
| 3 | 0:16 | 8 | cold open | archivo | great_wave_detail_met | — | zoom | — | «una ola curvada como una garra, sobre tres barcas» |
| 4 | 0:24 | 8 | cold open | archivo | hokusai_portrait_old | — | static | — | «lo último que pidió no fue despedirse. Pidió tiempo» |
| 5 | 0:32 | 6 | cold open | acamara | — | — | cut | HOOK | «esa frase suena a fracaso. Voy a convencerte de lo contrario» (a cámara → negro) |
| 6 | 0:38 | 5 | bumper | acamara | — | Conquest | cut | — | wordmark + «Soy [nombre]» |
| 7 | 0:43 | 22 | pivote | archivo | katsushika_edo_map | — | pan-h | — | «nace hacia 1760 en Katsushika, a las afueras de Edo» |
| 8 | 1:05 | 20 | pivote | archivo | edo_panorama_1809 | población aproximada — las fuentes varían | pan-h | — | «Edo, probablemente la ciudad más grande del mundo» |
| 9 | 1:25 | 55 | pivote | gráfico | G1_ukiyoe_pipeline | — | static | EXPLICADOR 1 | «se llama ukiyo-e… artista / tallador / impresor / editor» |
| 10 | 2:20 | 22 | pivote | archivo | shunsho_actor_print | — | zoom | — | «1778, aprendiz de Katsukawa Shunshō, retratos de actores» |
| 11 | 2:42 | 20 | pivote | archivo | shunro_early_print | — | static | PROMISE 1 | «el nombre no es suyo, es de la casa» |
| 12 | 3:15 | 26 | acto 1 | archivo | katsukawa_school_print | según se cuenta | static | — | «1793 muere Shunshō; deja la escuela Katsukawa» |
| 13 | 3:41 | 24 | acto 1 | gráfico | G2_names_timeline | ~30 nombres — recuento aproximado | pan-h | — | «alrededor de treinta nombres artísticos» |
| 14 | 4:05 | 22 | acto 1 | archivo | name_seal_transfer | — | zoom | — | «un nombre acreditado tenía valor de mercado» |
| 15 | 4:27 | 24 | acto 1 | gráfico | G2_names_timeline | — | pan-h | — | «cada nombre nuevo = un cambio de rumbo» |
| 16 | 4:51 | 30 | acto 1 | archivo | hokusai_manga_pages | — | pan-v | — | «1814, los Hokusai Manga: miles de bocetos» |
| 17 | 5:21 | 24 | acto 1 | ia | E001_ai02_daruma-nagoya-1817 | Ilustración — Conquest | push | PROMISE 2 | «1817, Nagoya: un Daruma de varios pisos con escobas» |
| 18 | 5:45 | 14 | acto 1 | archivo | rice_grain_miniature | cuentan / relato tradicional | zoom | — | «figuras diminutas sobre granos de arroz» |
| 19 | 5:59 | 16 | acto 1 | ia | E001_ai02_daruma-nagoya-1817 | Ilustración — Conquest | push | — | «le gustaba lo grande, y que lo vieran hacerlo» (cierre PROMISE 2) |
| 20 | 6:20 | 30 | acto 2 | kb | hokusai_portrait_60s | — | push | — | «con sesenta y muchos, la peor racha: un nieto contrae deudas» |
| 21 | 6:50 | 16 | acto 2 | kb | hokusai_portrait_60s | — | push | PROMISE 3 | «setenta años, arruinado por las deudas de un nieto» |
| 22 | 7:10 | 24 | acto 3 | archivo | thirtysix_views_sheet | — | pan-h | — | «Treinta y seis vistas del monte Fuji — acabaron siendo 46» |
| 23 | 7:34 | 26 | acto 3 | archivo | fuji_ricefield_cooper | — | cut | — | «el Fuji desde un arrozal; entre los andamios de un tonelero» |
| 24 | 8:00 | 14 | acto 3 | archivo | gaifu_kaisei_met | — | static | — | «el Fuji rojo contra un cielo despejado» |
| 25 | 8:14 | 22 | acto 3 | archivo | great_wave_full_met | — | zoom | — | «una ola inmensa sobre tres barcas — La gran ola frente a Kanagawa» |
| 26 | 8:36 | 14 | acto 3 | archivo | great_wave_full_met | — | static | — | «detente y mírala. Tenía unos setenta años» |
| 27 | 8:50 | 45 | explicador | gráfico | G3_prussian_blue | — | static | EXPLICADOR 2 | «el azul de Prusia, pigmento sintético europeo recién llegado» |
| 28 | 9:35 | 20 | acto 3 | kb | hokusai_portrait_60s | — | push | PAY 3 | «hizo eso a los setenta. Fue lo que le salió estando otra vez en el suelo» |
| 29 | 9:55 | 6 | acto 3 | acamara | — | — | cut | — | `[NOTA] Tipo de CTA: comentar` (a cámara) |
| 30 | 10:01 | 26 | acto 3 | acamara | — | — | cut | — | «no se le ocurrió de la nada — medio siglo de trabajo cuajó ahí» (opinión, a cámara) |
| 31 | 10:27 | 10 | acto 3 | acamara | — | — | cut | — | «¿alguna vez te ha pasado algo así? Cuéntamelo» |
| 32 | 10:37 | 34 | acto 4 | archivo | hyakkei_colophon_1834 | — | zoom | — | «1834, Cien vistas del monte Fuji: una nota firmada de su puño» |
| 33 | 11:11 | 30 | acto 4 | gráfico | G4_age_ladder | — | pan-v | — | «a los 73… a los 80… a los 110 cada punto y cada línea, vivos» |
| 34 | 11:41 | 16 | acto 4 | archivo | hokusai_signature_manji | — | zoom | — | «lo escribe a los 74. Ya había hecho La gran ola» |
| 35 | 11:57 | 40 | explicador | gráfico | G3b_signature_manji | — | static | EXPLICADOR 3 | «firmaba Gakyō Rōjin Manji — "el viejo loco por la pintura"» |
| 36 | 12:37 | 24 | acto 4 | ia | E001_ai03_studio-fire-night | Ilustración — Conquest | push | — | «1839, un incendio destruyó su casa-taller. Volvió a empezar» |
| 37 | 13:01 | 26 | acto 4 | archivo | oi_night_scene | — | pan-h | — | «sus últimos años con su hija, Katsushika Ōi, también pintora» |
| 38 | 13:27 | 14 | acto 4 | ia | E001_ai04_closing-path | Ilustración — Conquest | static | PROMISE 4 | «un hombre de más de 80… dibujando junto a su hija» |
| 39 | 13:41 | 14 | acto 5 | gráfico | G7_death_card | 88 o 90 años, según el cómputo japonés | static | — | «muere en Edo en 1849, con unos ochenta y ocho años» |
| 40 | 13:55 | 20 | acto 5 | gráfico | G2_names_timeline | — | pan-h | PAY 1 | «se cambió el nombre unas treinta veces; murió sin encontrarlo» |
| 41 | 14:15 | 30 | acto 5 | archivo | japonismo_montage | — | cut | — | «Monet en Giverny; Van Gogh copiando; la portada de La Mer, 1905» |
| 42 | 14:45 | 16 | acto 5 | ia | E001_ai02_daruma-nagoya-1817 | Ilustración — Conquest | push | PAY 2 | «acabó siendo visto por más gente… cuando él ya no estaba» |
| 43 | 15:05 | 22 | cierre | acamara | — | — | cut | — | «"pintor de verdad" a los 88 suena a fracaso — yo creo que es lo contrario» |
| 44 | 15:27 | 40 | cierre | acamara | — | — | cut | — | «¿ya llegué? / ¿me estoy acercando? — la primera acaba mal siempre» |
| 45 | 16:07 | 30 | cierre | gráfico | G6_mastery_curve | — | static | — | «la psicología de la motivación distingue demostrar de aprender» [S15] (corte breve al gráfico) |
| 46 | 16:37 | 45 | cierre | acamara | — | — | cut | — | «la pregunta no es "esto es mi meta" sino "esto me lleva a mi meta"» (para llevar) |
| 47 | 17:22 | 18 | cierre | acamara | — | — | cut | — | «a los 88 todavía tenía a dónde ir. No es una vida frustrada» (cierre a cámara) |
| 48 | 17:40 | 14 | cta | acamara | — | Fuentes principales | cut | — | CTA `suscribete` + rótulo «Fuentes principales» |

## Detalle por beat — derechos (para el humano — no se parsea)

| asset | Visual | Origen probable | Fuente [ID] | Derechos |
|-------|--------|-----------------|-------------|----------|
| E001_ai01_deathbed-room · E001_ai02_daruma-nagoya-1817 · E001_ai03_studio-fire-night · E001_ai04_closing-path | ilustración IA | `07b-ai-prompts.md` | — | **IA — rótulo permanente «Ilustración — Conquest»** (`brain/15`). Sin cara fotorrealista identificable |
| great_wave_detail_met · great_wave_full_met | «La gran ola frente a Kanagawa» | The Met Open Access (acc. nº en `07-assets.md`: `E001_beat27_greatwave_met`) | S09 | **CC0 / dominio público** |
| gaifu_kaisei_met | «Fuji rojo» (*Gaifū kaisei*) | The Met / British Museum | S09 | CC0 / dominio público |
| thirtysix_views_sheet · fuji_ricefield_cooper | láminas de las *36 vistas* | The Met / Rijksmuseum | S09 | CC0 / dominio público |
| hokusai_manga_pages | páginas de los *Hokusai Manga* | Wikimedia / bibliotecas digitales | S10 | dominio público (pre-1900) |
| hyakkei_colophon_1834 | colofón de *Fugaku Hyakkei* vol. 1 | escaneo de edición de 1834 | S01 | texto primario, dominio público (1834) |
| hokusai_portrait_old · hokusai_portrait_60s · hokusai_signature_manji | retrato de Hokusai anciano / firma | reproducción PD (cat. British Museum / Wikimedia) | S16, S13 | dominio público — **confirmar ficha del objeto** |
| shunsho_actor_print · katsukawa_school_print · shunro_early_print | grabados de la escuela Katsukawa | The Met / museos | S03 | CC0 / dominio público |
| katsushika_edo_map · edo_panorama_1809 | mapa de Edo / panorama de época | LOC · biombos digitalizados (Wikimedia) | S02, S20 | dominio público |
| oi_night_scene | obra nocturna de Katsushika Ōi | reproducción PD (museo) | S11 | dominio público — confirmar |
| japonismo_montage | Giverny (Monet) · japonaiserie (Van Gogh) · portada *La Mer* Durand 1905 | Van Gogh Museum (PD) · Sibley Music Library (partitura 1905, PD) · foto de Giverny (**con derechos → plan B: gráfico propio**) | S19, S14 | mixto — **La Mer PD; Giverny con derechos** |
| rice_grain_miniature | miniatura sobre grano de arroz | stock / gráfico propio (relato tradicional) | S17 | ilustrativo — rótulo «cuentan» |
| INTRO_hands_brush · INTRO_edo_dawn | b-roll del cold open | stock (Pexels/Pixabay vídeo) | — | licencia stock — crédito en `09-description.md` |
| bumper_conquest · cta_card_* · death_1849_card | gráfico propio (texto) | Conquest | — | propio |

## Gráficos / motion — guion de cada uno

| id | Beat # | Qué muestra | Datos (fuente [ID]) | Rótulo de fuente/salvedad | Notas de estilo |
|----|--------|-------------|---------------------|---------------------------|-----------------|
| G1_ukiyoe_pipeline | 9 | cadena del grabado: dibujante → tallador → impresor → editor; el nombre firmado ≠ quien toca la madera | S02 | — (proceso, no cifra) | isométrico simple, 4 estaciones, la firma «viaja» al final |
| G2_names_timeline | 13·15·30·40 | línea de tiempo de los ~30 nombres, con una obra bajo cada uno; se reusa 4× (rima visual con PAY 1) | S05 | «~30 nombres — recuento aproximado» | horizontal, scroll lento; misma animación cada vez |
| G3_prussian_blue | 27 | el azul de Prusia: llega de Europa, se abarata hacia finales de 1820, se usa en las primeras láminas *aizuri-e* | S18 | — | muestra de color + mapa de ruta comercial; sin fechas duras en pantalla si S18 no las cierra |
| G3b_signature_manji | 35 | la firma «Gakyō Rōjin Manji» + traducción propia «el viejo loco por la pintura» | S13 | «traducción propia» | caligrafía → gloss |
| G4_age_ladder | 33 | la escala del prefacio: 73 → 80 → 90 → 100 → **110** («cada punto y cada línea, vivos») | S01 | «traducción propia» | escalera ascendente; el 110 destacado (corrección L2 #30 del fact-check) |
| G6_mastery_curve | 45 | metas de demostrar (ego) vs. aprender (maestría); se nombra en general, **sin source card** | S15 (Nicholls 1984 / Dweck 2006) | — (cita en la descripción, `brain/03`) | dos curvas: una con techo, otra abierta |
| G7_death_card | 39 | rótulo: «Edo, 1849 · ~88 años» | S12 | «88 o 90, según el cómputo japonés» | tarjeta de texto sobre negro, Playfair |

## Música / sonido

| Cue | Sección | Pista (librería + licencia) | Notas |
|-----|---------|-----------------------------|-------|
| M1 | Cold open (1–5) | (por elegir — YouTube Audio Library / Pixabay Music) | sin letras; tensión contenida, corta en el negro del bumper |
| M2 | Narrativa (7–42) | (por elegir) | lecho bajo la voz, muy bajo; sube levemente en «La gran ola» (25–26) |
| M3 | Cierre (43–47) | (por elegir) | entra en el «para llevar» (46); nada en la coda CTA |

## Faltantes / a conseguir

- [ ] Confirmar ficha del objeto: retrato de Hokusai anciano (S16), obra nocturna de Ōi (S11), la lámina exacta de la Ola elegida (2ª ficha de museo, `03-source-log.csv` S09).
- [ ] S19: foto de Giverny con Hokusai identificable (con derechos → **plan B gráfico propio**); copia de Van Gogh (Van Gogh Museum, PD).
- [ ] S20: cerrar fuente de población de Edo — el rótulo del beat 8 dice «población aproximada».
- [ ] 4 prompts de IA (`07b-ai-prompts.md`) — ya redactados; generar en Stage 7.
- [ ] `07-pull.tsv` para los beats `stock` (INTRO_hands_brush, INTRO_edo_dawn) y cualquier archivo sin id cerrado.

## Gate Stage 6

- [x] La tabla **Timeline — la espina** está completa: toda fila con `#`, `in`, `dur`, `sección`, `tipo`, `motion`, `marcador`
- [x] Reparto A-roll / B-roll marcado (`brain/11 §1b`): `acamara` en 1·5·6·29·30·31·43·44·46·47·48 ≈ 35 %
- [~] Todo visual con estado de derechos — la mayoría PD/CC0; pendientes marcados en Faltantes (S16, S11, S19-Giverny, S20)
- [x] Todo dato en gráfico con fuente [ID]; G4 lleva «traducción propia», G6 se nombra en general sin source card
- [x] `PROMISE n` y `PAY n` usan el mismo `asset` y el mismo `motion` (1: G2_names_timeline · 2: E001_ai02_daruma-nagoya-1817 / push · 3: hokusai_portrait_60s / push · 4: E001_ai04_closing)
- [x] Sin clip de película dramatizada como registro histórico
- [x] Reenactments / IA con `rótulo` en pantalla («Ilustración — Conquest», 4 planos)
- [x] Cold open: narración a cámara + B-roll de hook + bumper; hook+bumper ≤ 50 s (0:00–0:43)
- [~] Nº de beats (48 en la espina) coherente con el ritmo para ~18 min — es la **espina**; el shotlist final añade intermedios hasta ~130–160
