---
doc: pipeline/5-pase-de-estilo
summary: "Stage 7: la página 07-style-pass.html (intro / candidatos por beat / prompts IA / música), el flujo de pull -> pase -> descarga -> manifiesto."
audience: "producción"
mirrors: [brain/12, brain/15]
authority: guide
---

# El pase de estilo (Stage 7)

*(Antes lo llamábamos "pase de fotografía". Ahora "pase de estilo" / style pass, porque evalúa toda la estética —imagen, vídeo, IA, música—, no solo fotografía.)*

Stage 7 resuelve **cada beat del shotlist a un recurso concreto** y registra el juicio estético: ¿encaja con el look del canal? Todo se decide en una página: **`07-style-pass.html`**.

Regla: `brain/06` Stage 7, `brain/12`. Herramienta: `pull_assets.py` (detalle en `herramientas/2-pull_assets`).

## El artefacto central

`07-style-pass.html` es una página HTML autónoma con **cuatro superficies**:

| Superficie | Qué |
|------------|-----|
| **Intro (arriba)** | el cold open (`brain/02` §0): 5 inputs para rutas/links propios + los clips `INTRO*` sugeridos + un checkbox "intro" en cualquier card |
| **Candidatos por beat (izquierda)** | 1–3 imágenes/clips que el pull encontró para cada beat archivístico |
| **Prompts IA (derecha)** | los prompts de `07b-ai-prompts.md` + un input para pegar la ruta de la imagen que generaste |
| **Música (abajo)** | el pool de `find_music.py` (lechos ominosos ambientales, CC-BY/BY-SA/CC0) con preview de audio |

Además, **cada card de beat tiene un input "recurso propio"**: si pegas ahí una ruta, se usa **esa** y se ignora la selección de ese beat.

## El flujo

### 1 · Escribe `07-pull.tsv`

Una fila por beat que necesita imagen/clip (los beats de gráfico propio **no** van aquí):

```
beat  kind  source  query  opts
```

`kind`:
- `stock` — **vídeo primero** (Pexels/Pixabay), luego imágenes rellenan
- `stock-img` — solo imágenes
- `video` — solo vídeo
- `intro` — vídeo de impacto para el cold open; nombra el beat `INTRO1`, `INTRO2`…
- `archive` — la pieza real: Met, Wikimedia Commons

### 2 · Corre `build_ai_prompts.py` (si hace falta)

**Antes** del pull, para los beats sin imagen real ni gráfico propio. Así los prompts salen en la columna derecha del pase.

### 3 · Corre el pull

```
python tools/pull_assets.py E0XX-slug
```

Pega las APIs gratis (Met, Wikimedia Commons, Pexels, Pixabay, Unsplash, Openverse) → `07-style-pass.md` (registro que se sube) + `07-style-pass.html` (la superficie).

### 4 · El pase (Usuario 001, en el navegador)

Por cada candidato, juzga con estos criterios:

| Criterio | Pregunta |
|----------|----------|
| **Resolución** | ¿suficiente para el uso (plano completo vs. inserto) y para hacer push-in / parallax sin deshacerse? Estándar 4K: estático ≥3840 px, push-in ≥4800, parallax ≥6000, inserto ≥1800 |
| **Estado** | manchas (foxing), roturas, decoloración: ¿aceptable o distrae? |
| **Color** | ¿coherente con el grade del episodio? Los escaneos de museo varían mucho |
| **Encuadre / márgenes** | ¿el escaneo trae el margen del papel, sellos de coleccionista? ¿lo queremos o lo recortamos? |
| **Coherencia de secuencia** | las imágenes que van juntas en un tramo, ¿parecen de la misma familia? |

Marcas: ✅ aceptada · ⚠️ dudosa · ❌ rechazada.

Y en paralelo: la intro (hasta 5 propios + sugeridos + cards marcadas), las rutas de las imágenes IA que generaste, y las pistas de música que consideras.

### 5 · Exporta y descarga

**Exportar 07-picks.txt** (se guarda en la carpeta del episodio). Luego:

```
python tools/pull_assets.py E0XX-slug --download
```

Baja todo:
- intro → `assets/intro/intro01…` (en orden de pantalla)
- beats → `assets/{stock,video,archive}/`
- IA → `assets/ai/<nombre 07b>`
- música → `brand/assets/music/` + `LICENSES.md`

Verifica resolución real, escribe `assets/CREDITS.md` + **`07-selection.md`** (el registro de decisiones del pase), e imprime filas de manifiesto.

### 6 · El manifiesto

Se pliega `07-selection.md` en `07-assets.md` — una fila por asset **aceptado** (intro / beat / IA), con las columnas Uso y Pase rellenadas.

## El gate de Stage 7

- [ ] Cold open: 2–5 assets de intro aceptados, en orden
- [ ] Cada beat archivístico tiene una imagen aceptada o un plan B (gráfico propio)
- [ ] Toda imagen con licencia clara y descarga directa sin captcha
- [ ] Cada imagen llega a la resolución que pide su uso
- [ ] Coherencia de color/estado revisada por tramos
- [ ] Créditos de cortesía anotados para `09-description.md`
- [ ] Imágenes IA estilizadas, rotuladas, sin cara de persona real

## Reglas de fuente

- **Solo descarga directa, sin captcha.** Museos con Open Access (Met, Wikimedia Commons), stock libre.
- **NO como fuente de descarga:** agregadores (para localizar, no bajar), sitios con captcha/temporizador, blogs, tiendas de prints, **stock de pago** (fuera por regla actual).
- **Stock ≠ la pieza real.** El stock es b-roll genérico ilustrativo (una ola, un laboratorio moderno) — solo donde el espectador lo lee como *cutaway*, nunca como "esto es lo real".
- **IA:** solo donde no existe imagen real; estilo elegido por episodio (fotorrealista permitido); rótulo en pantalla **siempre**; nunca cara fotorrealista de persona real identificable; nunca documento/periódico falso (`brain/15`).

## Corre en paralelo con la grabación

Stage 7 y Stage 8 (grabación) van a la vez — grabar no depende de tener los recursos.
