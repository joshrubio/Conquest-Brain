# 09 — Auditoría de ritmo · E001 «Hokusai»

> Stage 9. Encargo del director: (1) el vídeo se siente estático — planos que aguantan
> un solo gráfico/imagen demasiado tiempo (mencionó un caso de ~2,5 min); (2) los clips
> de intro elegidos en Stage 7 casi no se usan.
> Fuentes: `09-timeline.json` (corte actual, alineado a la voz), `06-shotlist.md` (la espina),
> `05-script.md` v2, `07-picks.txt`, `07-selection.md`, `assets/`, `brain/11`, `brain/02 §0`, `brain/16`.
> **No se ha tocado ni el código del pipeline ni la shotlist.** Esto es solo el informe.

---

## 1. Resumen

**14 planos señalados** por aguantar demasiado sobre un visual que no cambia, más
**2 pares** que reutilizan el mismo `asset` seguido por encima de ~18 s. Los dos peores,
con diferencia, son el **beat 9** (gráfico `G1_ukiyoe_pipeline` **estático 151 s** — 2 min 31 s,
el caso que vio el director) y el **beat 34** (`hokusai_signature_manji` con zoom, **137 s**).
Les siguen el beat 29 (72 s a cámara — su `frag` es una nota de producción, no narración,
y la alineación le volcó todo el hueco), el 12 (62 s), el 13 (57 s), el 43 (52 s) y el 33 (51 s).

Causa de fondo doble: **(a) la espina tiene solo 48 beats para 15:42 de metraje**
(~3 b/min; `brain/11 §2.2` pide 150–180 para 20 min, y la propia shotlist dice que la
lista final debía subir a ~130–160 — nunca se hizo). `assemble.py` estira los 48 beats
para cubrir la voz, así que casi todos duran 2–3× su `dur` planificado. **(b) la alineación
a la voz falla en toda la segunda mitad**: el `frag` de muchos beats no casa con la voz
entregada (parafraseada + whisper transcribe «pintor»→«tíntor»), así que caen en el
reparto proporcional y los pocos que casan por suerte anclan tramos enormes.

**Cold open:** el director eligió **5 clips de intro** en Stage 7 (`07-picks.txt`), pero
**ninguno se descargó** — `07-selection.md` no tiene sección INTRO y `assets/intro/` solo
contiene `intro01_pexelsv_8808479.mp4`, un huérfano cuyo id de Pexels **no coincide con
ninguno de los 5 elegidos**. La shotlist, además, solo tiene **un** beat `stock` en el cold
open (beat 2, `asset: intro01`) porque se escribió desde el guion (que en `[HOOK VISUAL]`
pide 4 planos, uno solo stock), no desde los picks. Resultado: el cold open corta por
AI-still → 1 clip → ola-still → retrato-still → cara; solo 2 de 5 planos se mueven, y el
retrato (beat 4) se congela 17 s en el momento más denso del episodio.

---

## 2. Tabla — planos largos sobre un visual

Duración real = `out − in` de `09-timeline.json`. `dur` = valor planificado en la espina
(pasa tal cual al timeline). «disparador» según los umbrales del encargo.

| beat | in–out | dur real | dur plan. | sección | tipo | motion | asset | disparador | arreglo sugerido |
|---|---|---|---|---|---|---|---|---|---|
| **9** | 1:31–4:02 | **151 s** | 55 | pivote | gráfico | static | G1_ukiyoe_pipeline | gráfico >10 s · >20 s · static >12 s · **peor caso** | Rehacer G1 como **build animado** (una estación por vez: artista→tallador→impresor→editor) → 4 sub-beats ~10–12 s sincronizados a la VO. Intercalar archivo real: `hokusai_manga_pages` (beat16), un plano de talla en madera *(a conseguir)*, `shunsho_actor_print` (beat10). Cortar **a cámara** en «es… una industria del entretenimiento impreso» y en «Quédate con eso… es lo primero que sabemos de lo que quería» (línea de tesis, `brain/11 §1b`). 1 beat → ~8. Estiramiento de VO (2,7×) sobre un plan que ya era el bloque más largo. |
| **34** | 11:38–13:54 | **137 s** | 16 | acto 4 | zoom | zoom | hokusai_signature_manji | >20 s · ~2,5 min | Los 137 s son **artefacto de alineación** (ver §5): la VO real de los beats 35–42 está en 10:21–12:12 y el timeline los empujó a 13:54+. Contenido: `hokusai_signature_manji` zoom ~6 s → `hyakkei_colophon_1834` (reusar beat32) push al texto ~10 s → **a cámara** ~10 s en «su balance es: todavía no sé nada — pero voy en la dirección correcta». |
| **29** | 9:25–10:36 | **72 s** | 6 | acto 3 | cut | cut (acamara) | — | >20 s · cut >12 s | El `frag` es una **nota de producción** (`[NOTA] Tipo de CTA: comentar`), no narración → nunca casa con la VO y `align()` le da todo el hueco 28→30. Corregir el `frag` a la narración real («Y este detalle me llama la atención… así es como suele pasar»). Es un beat de opinión a cámara legítimo: 29 a cámara ~16 s + **29b** inserto `great_wave_full_met` (visto) ~8 s en «no es que se le ocurriera de la nada» + 30 a cámara ~14 s + 31 a cámara ~8 s («¿alguna vez te ha pasado…? Cuéntamelo»). |
| **12** | 4:13–5:15 | **62 s** | 26 | acto 1 | static | static | katsukawa_school_print | static >12 s · >20 s | 4+ cambios de sujeto en un plano. Partir: 12 `katsukawa_school_print` static→push ~10 s («1793 muere Shunshō») · 12b `shunsho_actor_print` (reusar beat10) push ~9 s («la ruptura… talleres rivales») · 12c **a cámara** ~7 s («No hay un documento que lo confirme; es la versión transmitida») · 12d `hokusai_manga_pages` o pintura china *(a conseguir)* ~10 s («mira en todas direcciones»). Estiramiento VO 2,4×. |
| **13** | 5:15–6:13 | **57 s** | 24 | acto 1 | pan-h | pan-h | G2_names_timeline | gráfico >10 s · >20 s | G2 debe **animarse nodo a nodo** (un nombre + su obra representativa, sincronizado a «Shunrō, Sōri, Hokusai, Taito, Iitsu, Manji»). Partir: 13 build G2 ~12 s · 13b **a cámara** ~9 s («"Hokusai"… solo cubre un tramo de su vida») · 13c `name_seal_transfer` (beat14, subir aquí) ~10 s («valor de mercado») · 13d G2 sigue ~12 s. |
| **43** | 14:02–14:54 | **52 s** | 22 | cierre | cut | cut (acamara) | — | >20 s · cut >12 s | Cierre = A-roll **cortando a imágenes ya vistas** (`brain/11 §2.2`). Ahora son 43+44 = ~97 s de cara continua. Intercalar: 43 a cámara ~14 s · 43b `G2_names_timeline` (reusar) ~8 s («los treinta nombres») · 43c a cámara ~12 s. |
| **33** | 10:47–11:38 | **51 s** | 30 | acto 4 | pan-v | pan-v | G4_age_ladder | gráfico >10 s · >20 s | G4 = escalera; animar los peldaños apareciendo (73→80→90→100→**110**) sincronizados a la VO. Partir: 33 build G4 ~16 s · 33b **a cámara** ~10 s (interpretación «todavía no sé nada, pero voy en la dirección correcta»). |
| **44** | 14:54–15:39 | **45 s** | 40 | cierre | cut | cut (acamara) | — | >20 s · cut >12 s | Continuación del cierre: 44 a cámara ~12 s («¿ya llegué? / ¿me estoy acercando?») · **44b** `G6_mastery_curve` ~14 s (es el beat 45, subirlo — hoy dura 2,5 s) · 44c a cámara ~12 s · 44d `great_wave_full_met` (visto) ~8 s («¿en qué punto… tu Gran Ola?»). |
| **28** | 8:40–9:25 | **44 s** | 20 | acto 3 | push | push | hokusai_portrait_60s | >20 s · **3ª reutilización** del mismo retrato (20·21·28) | PAY 3 debe mantener el mismo plano/motion que PROMISE 3 (beat 21) — **solo el momento del pago** (~8 s) sobre `hokusai_portrait_60s`/push. El resto: 28b `great_wave_full_met` (visto) ~10 s («lo que le salió estando otra vez en el suelo») · 28c **a cámara** ~12 s. |
| **27** | 8:02–8:40 | **38 s** | 45 | explicador | static | static | G3_prussian_blue | gráfico >10 s · >20 s · static >12 s | EXPLICADOR 2. Animar: la muestra de color se llena · se dibuja la ruta comercial Europa→Japón · una lámina se tiñe de azul. Partir: 27a build color ~12 s · 27b mapa de ruta ~12 s · 27c `gaifu_kaisei_met` (reusar beat24) ~8 s · 27d `great_wave_full_met` (reusar beat25) ~10 s («hecha, en parte, con tecnología europea»). |
| **20** | 6:36–7:01 | **25 s** | 30 | acto 2 | push | push | hokusai_portrait_60s | >20 s · 1ª de 3 reutilizaciones | El tramo que no es PROMISE: cortar a un archivo del episodio de las deudas del nieto *(a conseguir)* o reusar `edo_panorama_1809`, + **a cámara** en «solo que ahora sin la energía de los treinta». Tensar la Ken Burns. |
| **8** | 1:10–1:31 | **21 s** | 20 | pivote | pan-h | pan-h | edo_panorama_1809 | >20 s (justo) | Partir: 8 `edo_panorama_1809` pan-h ~12 s · 8b **tarjeta de cifra** «~1 millón — las fuentes varían» ~8 s (`brain/11 §2.1` regla 7: toda cifra → gráfico propio; hoy es solo un `label`). |
| **4** | 0:26–0:43 | **17 s** | 8 | cold open | static | static | hokusai_portrait_old | static >12 s · **en el cold open** | Es el plano «giro» del hook (`05-script §0`: «aguanta ½ s → corte a negro»). Recortar duro a ~5 s en el corte. Los 12 s de más son estiramiento porque el beat 5 (a cámara) dura solo 5,2 s; además el cold open necesita los clips de intro que faltan (§3) para llenar ese tiempo con **movimiento** en vez de un retrato congelado. |
| 25+26 | 8:14–8:40 | 12,2 s + 8,6 s = **21 s** | 22+14 | acto 3 | zoom→static | — | great_wave_full_met (×2 seguidos) | mismo `asset` seguido >18 s | **Aceptable pero al límite** — es el «detente y mírala» deliberado. Si molesta: en el beat 26 continuar el push del 25 (no `static`), o cortar a `great_wave_detail_met` (beat3) en «la cresta abierta en garras de espuma». |
| 20+21 | 6:36–7:11 | 25,3 s + 10,4 s = **36 s** | 30+16 | acto 2 | push | push | hokusai_portrait_60s (×2 seguidos) | mismo `asset` seguido >18 s | Ver beat 20. El retrato de los 60 es el único visual de todo el acto 2. Meter al menos un archivo/tarjeta distinto entre PROMISE 3 y su preparación. |

Notas transversales:
- **`assets/kb/` está vacío** — `kenburns.py` no se ha ejecutado; los beats `kb` (20/21/28) y todos los
  stills aún no tienen clip de movimiento renderizado. El movimiento «push/zoom/pan» de la tabla es
  intención, no está en el corte.
- **Todos los `gráfico` son PNG estáticos** (`assets/graphic/*.png`) con una sola Ken Burns. `brain/11 §2.3`
  define `[EXPLICADOR]` como *secuencia* de motion graphics. G1/G2/G3/G3b/G4 deberían ser builds animados
  (`make_graphics.py`) partidos en sub-beats sincronizados a la VO.

---

## 3. Cold open — qué se eligió, qué hay, qué referencia la shotlist, dónde se rompió

### 3.1 Elegido en Stage 7 (`07-picks.txt`, bloque `# --- INTRO ---`)

5 clips, ranuras `custom:1`…`custom:5`, todos URL de vídeo de Pexels, en orden de exportación:

| ranura | tema | Pexels ID |
|--------|------|-----------|
| custom:1 | madera / embarcadero / mar | 20293162 |
| custom:2 | santuario Meiji nevado, invierno | 36365140 |
| custom:3 | flores de cerezo, Japón histórico | 31387395 |
| custom:4 | Japón time-lapse | 31453316 |
| custom:5 | escaleras de montaña, Japón | 19757067 |

Además, la línea `2  pixabayv:10378` (un vídeo de Pixabay para el beat 2) **sí** se descargó →
`assets/video/beat2_pixabayv_10378.mp4`.

### 3.2 Qué hay realmente en `assets/intro/`

**Un solo archivo:** `intro01_pexelsv_8808479.mp4` (Pexels ID **8808479**).
Ese ID **no coincide con ninguno de los 5 elegidos**. Es un huérfano — casi seguro una
tarjeta autosugerida (`intro_sug` en `pull_assets.py`, hasta 5 desde filas `intro` de
`07-pull.tsv`) descargada en un pase anterior, o un resto.
`07-selection.md` (el registro de `pull_assets.py --download`) **no tiene sección INTRO**:
solo «Por beat» + «Ilustración IA». Los 5 clips del director nunca se descargaron.
La propia shotlist lo tiene pendiente en «Faltantes / a conseguir»:
`[ ] 07-pull.tsv para los beats stock (INTRO_hands_brush, INTRO_edo_dawn)…`.

### 3.3 Qué referencia la shotlist en `section: "cold open"`

5 beats (espina): 1 `ia E001_ai01_deathbed-room` · **2 `stock intro01`** · 3 `archivo great_wave_detail_met`
· 4 `archivo hokusai_portrait_old` · 5 `acamara`.
Referencia `intro01` **exactamente una vez** (beat 2, `frag`: «llevaba más de setenta años dibujando
(clip de intro)»). **No hay `intro02`/`03`/`04`/`05`.**
La tabla en prosa «Detalle por beat — derechos» menciona `INTRO_hands_brush · INTRO_edo_dawn`
(2 nombres) pero la espina solo tiene ese beat 2.
La shotlist implementa **el guion**, no los picks: `05-script §0 [HOOK VISUAL]` lista 4 planos
—v1 AI/tatami, **v2 stock manos/pincel**, v3 ola detalle, v4 retrato→negro— y la espina los
copia 1:1 (beat1=v1, beat2=v2, beat3=v3, beat4=v4). El guion solo pide **un** clip stock en el hook.

### 3.4 Dónde se rompió — tres fallos que se suman

1. **La shotlist se escribió desde el guion, no desde los picks.** `brain/11 §1`: «los planos se
   planifican desde el guion bloqueado». El `[HOOK VISUAL]` del guion tiene 4 planos, uno solo stock.
   La shotlist v2 (regenerada 2026-09-08 sobre el guion v2) codifica eso exacto. Los 5 clips del
   director (embarcadero, santuario, cerezos, time-lapse, escaleras) son metraje de ambiente/montaje
   para el cold open y **nunca recibieron beats**.
2. **Los 5 clips nunca se descargaron.** Sin sección INTRO en `07-selection.md`; `assets/intro/` solo
   tiene el huérfano `intro01` (8808479, que no es ninguno de los 5). El `07-pull.tsv` de los beats
   intro/stock sigue como TODO abierto en la propia shotlist.
3. **`assemble.py` solo construye beats que existen en la espina** y resuelve `intro01` por prefijo
   al único archivo presente. No tiene lógica para abrir varios `assets/intro/introNN` en beats
   extra — la espina es la fuente de verdad. Así que hasta el clip que sí está llena exactamente un beat.

Neto: cold open = AI-still + 1 clip + ola-still + retrato-still + cara. Solo 2 de 5 planos se mueven.
Contra `brain/02 §0` (2–5 planos, stock preferido, 10–12 b/min, «un plano en movimiento vale más que
un push sobre un still») está poco cortado y demasiado quieto — agravado por el beat 4 congelado 17 s.

### 3.5 Arreglo — beats de cold open a añadir a la espina

La narración del hook (~55–100 palabras, ~25–30 s) admite 5–6 planos cortos. Propuesta (sustituye
las filas 1–5 por ~8), mapeando cada plano a **una imagen concreta que nombra la voz** (`brain/02 §0`):

| # | in | dur | sección | tipo | asset | rótulo | motion | marcador | guion (frag.) |
|---|----|-----|---------|------|-------|--------|--------|----------|---------------|
| 1 | 0:00 | 3 | cold open | ia | E001_ai01_deathbed-room | Ilustración — Conquest | static | HOOK | «en 1849, en un cuarto de alquiler de Edo… se estaba muriendo» |
| 2 | 0:03 | 3 | cold open | stock | intro02_meiji_snow | — | cut | — | «—el Tokio de entonces—» (clip de intro · Japón, invierno) |
| 3 | 0:06 | 4 | cold open | stock | intro04_japan_timelapse | — | cut | — | «llevaba más de setenta años dibujando» (time-lapse) |
| 4 | 0:10 | 3 | cold open | stock | intro01_hands_brush | — | cut | — | «había publicado miles de imágenes» (manos / pincel — clip actual, o pixabay 10378) |
| 5 | 0:13 | 4 | cold open | archivo | great_wave_detail_met | — | zoom | — | «una ola curvada como una garra, sobre tres barcas» |
| 6 | 0:17 | 3 | cold open | stock | intro03_cherry_blossom | — | cut | — | «una de las imágenes japonesas más reproducidas del mundo» |
| 7 | 0:20 | 5 | cold open | archivo | hokusai_portrait_old | — | static | — | «lo último que pidió no fue despedirse. Pidió tiempo» (giro · aguanta ½ s → negro) |
| 8 | 0:25 | 6 | cold open | acamara | — | — | cut | HOOK | «esa frase suena a fracaso. Voy a convencerte de lo contrario» → negro |

≈ 6 planos en movimiento en ~25 s → ~13 b/min, dentro del objetivo de `brain/11 §2.2`.
Requiere:
- **Descargar 3 de los 5 picks**: Pexels **36365140** (santuario nevado), **31453316** (time-lapse),
  **31387395** (cerezos). Escribir filas `intro` en `07-pull.tsv` y re-correr `pull_assets.py --download`
  para que caigan como `assets/intro/intro02_…`, `intro03_…`, `intro04_…` (`assemble.py` casa por prefijo).
- **Descartar** Pexels 19757067 (escaleras) y opcionalmente 20293162 (embarcadero) — encajan flojo
  con las imágenes que nombra la voz.
- Confirmar el clip de manos/pincel (el huérfano `intro01_pexelsv_8808479.mp4` sirve si es eso; si no,
  usar `beat2_pixabayv_10378.mp4` renombrado a `assets/intro/`).
- Corregir en la shotlist la tabla «Detalle por beat — derechos» y «Faltantes» con la lista real.

---

## 4. Cambios de shotlist propuestos (no aplicados)

Lista para que el director apruebe. Filas de la tabla «Timeline — la espina» de `06-shotlist.md`.

### Cold open
- **Fila 2** — *reemplazar*. Era `stock · intro01 · cut · 7 s`. Pasa a **4 beats stock** (nuevas
  filas 2,3,4,6 de §3.5), 3–4 s cada uno, cada uno con una imagen distinta del hook.
- **Fila 3** (`great_wave_detail_met`) — *acortar* `dur` 8→4, mantener `zoom`.
- **Fila 4** (`hokusai_portrait_old`) — *acortar* `dur` 8→5, mantener `static`; es el «giro», recorte duro.
- **Añadir** filas para `intro02_meiji_snow`, `intro03_cherry_blossom`, `intro04_japan_timelapse`.
- **Faltantes / Detalle-derechos** — *actualizar* `INTRO_hands_brush · INTRO_edo_dawn` → lista real
  de 3–4 clips con sus IDs de Pexels.

### Task 1 — planos largos
- **Fila 8** (`edo_panorama_1809`, 20 s) — *partir* → 8 pan-h 12 s + **8b** tarjeta de cifra
  «~1 millón — las fuentes varían» 8 s.
- **Fila 9** (`G1_ukiyoe_pipeline`, static 55 s) — *reemplazar 1 beat por ~8*: build animado
  4 estaciones (~10–12 s c/u) + insertos de archivo (`hokusai_manga_pages` beat16 · plano de talla
  *a conseguir* · `shunsho_actor_print` beat10) + **a cámara** en la línea de tesis final.
- **Fila 12** (`katsukawa_school_print`, static 26 s) — *partir en 4*: 12 (10 s) · 12b `shunsho_actor_print`
  reusa beat10 (9 s) · 12c **a cámara** (7 s) · 12d `hokusai_manga_pages` o pintura china (10 s).
- **Filas 13–15** (`G2_names_timeline` ×2 + `name_seal_transfer`) — *rehacer G2 como build animado*;
  intercalar 13b **a cámara** y subir `name_seal_transfer` a la posición «valor de mercado».
- **Filas 20–21** (`hokusai_portrait_60s` ×2 push) — *insertar* un archivo/tarjeta distinto entre
  medias; el retrato de los 60 no puede ser el único visual del acto 2.
- **Fila 27** (`G3_prussian_blue`, static 45 s) — *partir en 4*: build color 12 s · mapa de ruta 12 s ·
  `gaifu_kaisei_met` reusa beat24 8 s · `great_wave_full_met` reusa beat25 10 s.
- **Fila 28** (`hokusai_portrait_60s`, push, PAY 3) — *acortar el plano-PAY a ~8 s*; añadir 28b
  `great_wave_full_met` (visto) 10 s + 28c **a cámara** 12 s.
- **Fila 29** — *corregir el `frag`*: hoy es `[NOTA] Tipo de CTA: comentar` (nota de producción).
  Poner la narración real («Y este detalle me llama la atención… así es como suele pasar»). Añadir
  **29b** inserto `great_wave_full_met` 8 s. Re-cronometrar 30 (~14 s) y 31 (~8 s).
- **Fila 33** (`G4_age_ladder`, pan-v 30 s) — *partir*: build peldaños 16 s + 33b **a cámara** 10 s.
- **Fila 34** (`hokusai_signature_manji`, zoom) — *partir*: firma 6 s + `hyakkei_colophon_1834`
  reusa beat32 push-al-texto 10 s + **a cámara** 10 s. (Los 137 s del corte son de alineación, §5.)
- **Fila 35** (`G3b_signature_manji`, static 40 s plan. / 7 s corte) — *darle ~15 s reales* de build
  animado (caligrafía → glosa); hoy está famélica.
- **Filas 43–47** (cierre) — *intercalar imágenes ya vistas* entre los tramos a cámara:
  43 (14 s) · 43b `G2_names_timeline` reusa (8 s) · 43c (12 s) · 44 (12 s) · **44b `G6_mastery_curve`**
  (14 s — es la fila 45, subirla) · 44c (12 s) · 44d `great_wave_full_met` (8 s) · 47 (12 s).
- **Fila 45** (`G6_mastery_curve`, static 30 s plan. / 2,5 s corte) — *fundir* en la secuencia de
  cierre como beat de ~14 s (44b), no un destello final de 2,5 s.

### Task raíz (sin lo cual los arreglos de arriba se vuelven a estirar)
- **Expandir la espina de 48 → ~130–160 beats** (lo que la propia shotlist dice que falta): añadir
  los intermedios, 1 beat cada ~2–3 frases o cambio de sujeto (`brain/11 §2.1`).
- **Reescribir la columna `guion (frag.)` citando la VO entregada literal** (desde
  `assets/E001-vo.cuts.md` / `assets/E001-vo.words.json`), no el borrador del guion, para que
  `align()` de `assemble.py` case (necesita ≥2 tokens exactos seguidos). Luego re-correr `assemble.py`.
- Ejecutar `kenburns.py --all` y `make_graphics.py` para que los movimientos y los builds de
  gráfico existan en el corte (hoy `assets/kb/` está vacío y los gráficos son PNG fijos).

---

## 5. Anexo — por qué el corte actual dura 15:42 y la 2ª mitad está desalineada

- La VO entregada (`assets/E001-vo.trimmed.mp4`, 2530 palabras, última en t=942,1 s) dura **~15:42**,
  no los 18–19 min del guion. `E001-vo.cuts.md`: 114 cortes, −231,5 s, de 1138 s a 906,7 s.
- `align()` desliza cada `frag` contra los timestamps de palabra y exige **≥2 tokens exactos seguidos**.
  Muchos `frag` de la 2ª mitad **no casan** (comprobado: «Treinta y seis vistas», «gran ola frente»,
  «azul de Prusia», «Cien vistas», «a los 73», «Katsushika Ōi» no aparecen como tokens consecutivos
  en la transcripción). Esos beats caen al reparto proporcional del hueco.
- Posiciones reales en la VO vs. lo que puso el timeline:
  «el viejo loco» (beat 35) → real **10:21**, timeline **13:54**.
  «incendio» (beat 36) → real **10:33**, timeline **14:02**.
  «Monet» (beat 41) → real **12:12**, timeline **14:06**.
- Consecuencia: los beats 9 y 34 (que casaron por suerte) absorben minutos enteros, y los beats
  39–48 (tarjeta de muerte, PAY 1, japonismo, PAY 2, parte del cierre, curva de maestría, CTA) se
  colapsan a ~0,6 s cada uno al final. Arreglarlo es requisito para que la auditoría de ritmo tenga
  un corte fiable sobre el que medir.
