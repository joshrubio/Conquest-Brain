---
doc: pipeline/6-la-edición
summary: "Stage 9 paso a paso: Ken Burns -> trim -> revisión -> b-roll -> música -> subtítulos. 4K, grade de casa, -14 LUFS."
audience: "editor"
mirrors: [brain/16]
authority: guide
---

# La edición (Stage 9)

Regla: `brain/16-edit-and-delivery.md`. Producto: `07c-edit.md` (checklist) + `07c-edit.html` (superficie de revisión, generada) + `07c-review.txt` (aprobaciones + feedback).

**Principio:** deliberadamente mínima. **Si un efecto no está en `brain/16`, no entra en el episodio.** Nada de rótulos inferiores, nada de source cards, ninguna transición que no sea corte seco o un fundido de sección. Un solo *grade* de casa (`brain/03`), aplicado entero. El rigor está en el guion y en las fuentes, no en los motion graphics.

## El orden

Los recursos del Stage 7 están elegidos; el metraje del Stage 8 está grabado. Entonces:

| # | Paso | Herramienta |
|---|------|-------------|
| 1 | **Ken Burns** sobre las imágenes fijas (+ imágenes IA) → clips con movimiento | `tools/kenburns.py --all` |
| 2 | **Trim**: quitar silencios y muletillas de cada toma | `tools/trim_talk.py` |
| 3 | **Revisión rápida** de clips crudos (opcional) | `tools/edit_review.py` → `07c-edit.html` |
| 4 | **Primer corte + timeline**: cada beat sobre la voz | `tools/assemble.py` → `tools/edit_timeline.py` → `09-edit.html` |
| 5 | **Lecho de música** ominoso, ducking bajo la voz | `assemble.py --final` |
| 6 | **Subtítulos** `.srt` desde la voz ya trimmeada, corregidos a mano | — |

Luego: house grade (lo aplica `assemble.py --final`) → export → picture lock.

**El montaje sigue el guion.** El formato es cortes secos en orden de guion, un solo grade. La timeline es para **colocar, sincronizar y ajustar**, no para componer libremente.

## 1 · Ken Burns — `kenburns.py`

Solo sobre fijas (el vídeo ya se mueve). El movimiento se elige de la **proporción real** de la imagen (registrada en `07-selection.md`) contra el marco 16:9:

| Imagen | Movimiento |
|--------|-----------|
| ~16:9 | push-in lento 1.00 → 1.10 (default seguro) |
| panorámica (ratio > 1.90) | paneo horizontal por todo el ancho, sin zoom |
| vertical (ratio < 0.90) | paneo vertical (default arriba→abajo; `--dir up` para terminar en una cara) |
| pequeña (lado largo < el marco 4K) | **estática**, centrada sobre fondo oscuro, sin movimiento |

```
python tools/kenburns.py E0XX-slug --all
```

→ `assets/kb/beatNN_<slug>.mp4` a 4K. Duración 5 s por defecto; overrides `--dur` / `--move` / `--dir` salen del feedback de la revisión. Un `[PLANT]` y su `[PAY]`: el **mismo** movimiento las dos veces.

## 2 · Trim — `trim_talk.py`

- `faster-whisper` transcribe cada toma → timestamps por palabra.
- Corta: **silencios** > `--gap` (0.6 s) → a ~0.15 s de aire; **muletillas** de una lista en español (`eh`, `este`, `o sea`, `pues` al empezar frase, arranques en falso) — conservador, solo aisladas.
- **Suave, no agresivo:** 120–180 ms de padding alrededor de cada tramo que se queda; una pausa < 0.4 s nunca se corta; fundido de 8 ms en cada empalme para matar clics.
- Salida: `<toma>.trimmed.mp4` + `<toma>.cuts.md` (transcripción con cada corte marcado). Las correcciones de la revisión lo re-corren con `--keep MM:SS`.

## 3 · Revisión rápida de clips crudos — `edit_review.py` (opcional)

Escanea `assets/kb/*.mp4` y `assets/*.trimmed.mp4`. Por clip: preview `<video>` · *aprobado* · feedback. Sirve para pillar un Ken Burns malo **antes** de la timeline. Se puede saltar — el inspector de la timeline (paso 4) tiene el mismo aprobar/corregir por clip, y en contexto.

## 4 · Primer corte + timeline

**`python tools/assemble.py E0XX-slug`** — automático, sin tokens:

1. parsea la tabla **«Timeline — la espina»** de `06-shotlist.md` (una fila por beat: `#`, `in`, `dur`, `sección`, `tipo`, `asset`, `rótulo`, `motion`, `marcador`, frag. de guion)
2. resuelve cada `asset` a un fichero real vía `07-selection.md` + las carpetas `assets/`
3. si hay una toma trimmeada, **alinea cada beat a la voz real** (cruza su frag. de guion con `*.words.json`); si no, usa los tiempos del shotlist
4. escribe `09-timeline.json` + `09-rough.mp4` (proxy 720p) + la waveform

**`edit_timeline.py`** genera **`09-edit.html`** — la sala de montaje:

- la waveform de la voz (fija) + bandas de sección + un bloque por beat, ancho ∝ duración, color por tipo; `PLANT`/`PAY` y `EXPLICADOR` marcados; los beats sin asset se ven en rojo hatch
- reproductor proxy con playhead arrastrable
- **inspector** por beat: cambiar asset · trim (arrastrar el borde o ±) · nudge ±frames · movimiento Ken Burns · nota para regenerar · aprobar
- **arrastra un bloque** para reubicarlo (imanta al límite de palabra); **rueda** = scroll, **Ctrl+rueda** = zoom, **Shift+rueda** = scroll rápido; minimapa para navegar
- **Previsualizar región** → re-renderiza ese tramo del proxy en segundos
- **Finalizar Stage 9** → guarda `09-timeline.json` + `09-decisions.txt`. Claude aplica las notas de regen (`kenburns.py` por beat) y corre `assemble.py --final` para el máster 4K. Los beats sin cubrir bloquean el render final.

**Reglas que no se mueven:**
- **Clips de vídeo:** cortados a duración, sin speed ramp, sin filtro. Loop solo si el clip es más corto que el beat *y* el punto de loop es invisible.
- **Cold open:** los clips `intro` en orden numerado, corte seco. El último aguanta ½ s → negro.
- **Bumper:** 3–6 s negro + wordmark `Conquest` + presentador. Sin música.
- `PLANT n` / `PAY n`: el **mismo** `asset` y `motion` (lo fija la espina del shotlist).

## 5 · Música — `find_music.py`

- **Brief: ambient ominoso.** Atmósfera, no pavor, no *stinger* de misterio. Instrumental, bajo, lento, melodía mínima o nula, sin voces, sin percusión con picos, loopea limpio.
- **Licencia:** un vídeo de YouTube monetizado es uso **comercial**. Solo sirve CC0 / dominio público, **CC-BY** (crédito en `09-description.md`) o **CC-BY-SA**. **Nunca** NC ni ND. `find_music.py` filtra a BY / BY-SA / CC0.
- El pool se acumula en `brand/assets/music/candidates.md` y se muestra en la **sección Música de `07-style-pass.html`** (audición inline). El canal se asienta en 3–5 lechos que se reutilizan siempre.
- **Por episodio:** un lecho bajo todo el vídeo, ~20–24 dB bajo el pico de voz; ducking −4 a −6 dB bajo el habla. Un segundo tema algo más cálido puede entrar en el cierre. **Sin música en el bumper.**

## 6 · Subtítulos

`.srt` desde la voz **ya trimmeada**, corregido **a mano contra `05-script.md`** — cada número, nombre y claim con `[S..]` debe leerse exactamente como está escrito. 1–2 líneas, ≤ 42 caracteres/línea, mínimo 1 s en pantalla. Español. No-negociable cada episodio.

## Herramientas — la timeline es nuestra; DaVinci es la salida de emergencia

El montaje, el ducking, el grade y el −14 LUFS viven todos en el grafo `filter_complex` de `assemble.py`. Si un episodio concreto necesita artesanía a nivel de frame que la timeline no da (un J-cut, un montaje, motion graphics), te llevas `09-timeline.json` a **DaVinci Resolve** (vía su MCP) como punto de partida — la colocación ya está hecha, Claude no re-coloca 45 clips a mano. La mayoría de episodios no lo necesitan.

## Resolución — objetivo 4K, caída elegante

**Objetivo 4K (3840×2160).** La timeline se queda en 4K. Un plano que no la llene —una fija menor que 4K, un clip stock solo en 1080— baja un escalón **solo para ese plano** (inset / estático / upscale mínimo), no el proyecto entero.

## Texto en pantalla — mínimo

- **Sin source cards.** Toda cita vive en `09-description.md` «Fuentes principales» + el comentario fijado.
- En pantalla solo: el **dispositivo de expediente** (`EXPEDIENTE: CASO 00XX`, Courier Prime — `brain/03`), las **tarjetas de capítulo/sección** (Playfair), y el **rótulo de IA / recreación** — `Ilustración — Conquest` o `Recreación`, permanente, cada aparición.

## Grade de casa

Aplicado a toda la timeline: **oscuro, cálido, desaturado ~15–20%**, negros levantados en cálido; grano de película fino constante a baja opacidad; viñeta sutil de foco. Documentos sobre fondo de papel envejecido. Sin letterbox salvo que un clip fuente lo fuerce (pad sobre `#100D09`, nunca estirar).

## Export

- **4K** objetivo; baja a la mayor resolución que soporten todas las fuentes si 4K implicaría upscalear casi todo.
- H.264 / H.265, bitrate alto; AAC estéreo 320 kbps.
- Loudness **−14 LUFS** integrado (objetivo YouTube), true peak ≤ −1 dBTP.
- Nombre `E0XX-<slug>-vN.mp4`.

## El picture lock

Timeline finalizada en `09-edit.html` (todo beat cubierto + aprobado) → Claude aplica las regen + `assemble.py --final` → **picture lock** (no más cambios de timing) → Usuario 002 lo ve una vez, de principio a fin, contra `05-script.md` y `brain/04` (rótulos presentes, claims exactos, dignidad) → firma en `07c-edit.md` → `.srt` final → Stage 10.

## El gate de Stage 9

- [ ] Todo beat de `09-timeline.json` tiene asset (0 «sin cubrir») y está aprobado
- [ ] Solo los movimientos de `brain/16` — ningún otro efecto, transición o grade
- [ ] Cold open = clips `intro` en orden + bumper en negro
- [ ] El `motion` Ken Burns casa con la orientación de cada imagen; `PLANT n`/`PAY n` comparten `asset` y `motion`
- [ ] Un lecho de música, con ducking bajo la voz; sin música en el bumper; licencias registradas
- [ ] IA / recreación / coloreado con `rótulo` en cada aparición
- [ ] Máster 4K renderizado; `.srt` generado y corregido a mano contra `05-script.md`
- [ ] −14 LUFS integrado; picture lock firmado por Usuario 002 en `07c-edit.md`

---

Relacionado: [5-pase-de-estilo](5-pase-de-estilo.md) · [7-empaquetado-y-publicación](7-empaquetado-y-publicación.md) · [modelo-narrativo/1-anatomía-de-un-episodio](../modelo-narrativo/1-anatomía-de-un-episodio.md).
