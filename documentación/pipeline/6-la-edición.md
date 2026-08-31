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
| 3 | **Revisión** de 1 y 2 en una página, aprobar clip a clip | `tools/edit_review.py` → `07c-edit.html` |
| 4 | **Montaje de b-roll**: cada beat sobre la voz, según el shotlist | Claude + ffmpeg |
| 5 | **Lecho de música** ominoso, ducking bajo la voz | — |
| 6 | **Subtítulos** `.srt` desde la voz ya trimmeada, corregidos a mano | — |

Luego: house grade → export → picture lock.

**Los pasos 1–3 pasan antes que el 4 a propósito:** se evalúa que el efecto Ken Burns y los cortes se ven bien *antes* de integrarlos al vídeo grande.

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

## 3 · Revisión — `edit_review.py` → `07c-edit.html`

Escanea `assets/kb/*.mp4` y `assets/*.trimmed.mp4` (+ `*.cuts.md`). Por clip:

- preview `<video>` · checkbox *aprobado* · caja de feedback.
- KB: «más lento» / «empieza a la izquierda» / «dir arriba» / «déjalo estático» / «dura 4 s».
- trim: «mantener la pausa en 00:12» / «cortar antes en 02:03» / «no cortes el "eh" de 03:04».

**«Finalizar Stage 9»** → `07c-review.txt`, cada línea `kb|trim  <id>  APROBADO | FIX: <texto>`. Claude lo lee, re-corre `kenburns.py` / `trim_talk.py` por cada FIX, regenera la página. Bucle hasta que **toda fila esté APROBADO**. Solo entonces empieza el paso 4.

## 4 · Montaje de b-roll

- `06-shotlist.md` marca qué beats son archivo / stock / IA; `07-selection.md` nombra el archivo (un clip KB para fijas, el clip stock/intro para vídeo). Cada uno sobre su beat, encima de la voz.
- **Clips de vídeo:** cortados a duración. Sin speed ramp, sin filtro, sin zoom. Loop solo si el clip es más corto que el beat *y* el punto de loop es invisible.
- **Cold open (§0):** 2–5 clips de `assets/intro/` en orden numerado, corte seco al beat de narración. El último plano aguanta ½ s → corte a negro.
- **Bumper (§0b):** 3–6 s negro + wordmark `Conquest` + la línea del presentador. Sin música.
- Beats reusados (`[PLANT]` / `[PAY]`): el **mismo** clip/fotograma las dos veces.

## 5 · Música — `find_music.py`

- **Brief: ambient ominoso.** Atmósfera, no pavor, no *stinger* de misterio. Instrumental, bajo, lento, melodía mínima o nula, sin voces, sin percusión con picos, loopea limpio.
- **Licencia:** un vídeo de YouTube monetizado es uso **comercial**. Solo sirve CC0 / dominio público, **CC-BY** (crédito en `09-description.md`) o **CC-BY-SA**. **Nunca** NC ni ND. `find_music.py` filtra a BY / BY-SA / CC0.
- El pool se acumula en `brand/assets/music/candidates.md` y se muestra en la **sección Música de `07-style-pass.html`** (audición inline). El canal se asienta en 3–5 lechos que se reutilizan siempre.
- **Por episodio:** un lecho bajo todo el vídeo, ~20–24 dB bajo el pico de voz; ducking −4 a −6 dB bajo el habla. Un segundo tema algo más cálido puede entrar en el cierre. **Sin música en el bumper.**

## 6 · Subtítulos

`.srt` desde la voz **ya trimmeada**, corregido **a mano contra `05-script.md`** — cada número, nombre y claim con `[S..]` debe leerse exactamente como está escrito. 1–2 líneas, ≤ 42 caracteres/línea, mínimo 1 s en pantalla. Español. No-negociable cada episodio.

## Herramientas — Claude primero, DaVinci después si hace falta

Pasos 1–3 son las herramientas de arriba. Pasos 4–5 (montaje + mezcla) se intentan con **Claude manejando ffmpeg**. Si cuadrar el b-roll a la voz se vuelve demasiado fino así, se integra el **MCP de DaVinci Resolve** y el montaje se muda ahí — las herramientas de revisión no cambian.

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

KB + trim firmados en `07c-edit.html` → b-roll + música montados → **picture lock** (no más cambios de timing) → un usuario (001 o 002) lo ve una vez, de principio a fin, contra `05-script.md` y `brain/04` (rótulos presentes, claims exactos, dignidad) → firma en `07c-edit.md` → sonido + `.srt` finales → Stage 10.

## El gate de Stage 9

- [ ] Cada clip KB y cada toma trimmeada **APROBADO** en `07c-review.txt`
- [ ] Solo los movimientos de `brain/16` — ningún otro efecto, transición o grade
- [ ] Cada beat del shotlist tiene su asset en pantalla; cold open 2–5 planos + bumper en negro
- [ ] El movimiento Ken Burns casa con la orientación de cada imagen; `[PLANT]`/`[PAY]` idénticos
- [ ] Un lecho de música, con ducking bajo la voz; sin música en el bumper; licencias registradas
- [ ] IA / recreación / coloreado rotulado en cada aparición
- [ ] `.srt` generado y corregido a mano contra `05-script.md`
- [ ] −14 LUFS integrado; 4K (o la mejor resolución común); picture lock firmado (un usuario) en `07c-edit.md`

---

Relacionado: [5-pase-de-estilo](5-pase-de-estilo.md) · [7-empaquetado-y-publicación](7-empaquetado-y-publicación.md) · [modelo-narrativo/1-anatomía-de-un-episodio](../modelo-narrativo/1-anatomía-de-un-episodio.md).
