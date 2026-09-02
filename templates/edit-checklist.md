---
doc: edit-checklist
summary: "The Stage-9 run: Ken Burns, trim, review, b-roll, music, subs, grade, export, picture lock."
stage: [9]
fills: "07c-edit.md"
rule: [16]
authority: template
---

# Edición — E0XX «<título>»

> Stage 9. Protocolo: `brain/16-edit-and-delivery.md`. **Solo lo que está en brain/16.**
> Depende de: `05-script.md` (bloqueado) · `06-shotlist.md` (tabla «Timeline — la espina») · `07-selection.md` · `brand/assets/music/`.
> Superficie de revisión: **`09-edit.html`** (la timeline — genera `tools/assemble.py` + `tools/edit_timeline.py`). Revisión rápida opcional de clips crudos: `07c-edit.html`.

| Campo | Valor |
|-------|-------|
| ID episodio | E0XX |
| Versión de guion | v__ |
| Responsable | Usuario 001 |
| Resolución de salida | **4K (3840×2160)**; si una fuente no llega, ese plano baja, el timeline sigue en 4K |
| fps | (24 / 30) |
| Fecha | AAAA-MM-DD |

---

## 0. Grabación (Stage 8) — tomas de entrada

| Toma | Archivo | Sección(es) del guion | Notas / pickups |
|------|---------|-----------------------|-----------------|
| T1 | `assets/…` | | |

## 1. Ken Burns  (`tools/kenburns.py`)

```
python tools/kenburns.py E0XX-slug --all        # 07-selection stills -> assets/kb/ (4K)
```

- [ ] Un clip por still de `assets/{archive,stock,ai}/` con nombre `beatNN_*`
- [ ] Movimiento por orientación (≈16:9 push-in · panorámica pan H · vertical pan V · pequeña estática en negro)

## 2. Trim  (`tools/trim_talk.py`)

```
python tools/trim_talk.py assets/T1.mp4          # -> T1.trimmed.mp4 + T1.cuts.md
```

- [ ] Una pasada por toma
- [ ] Cortes suaves (padding 120–180 ms; nada por debajo de 0.4 s)

| Toma | Cortes | Duración final |
|------|--------|----------------|
| T1 | | |

## 3. Revisión rápida de clips crudos  (`tools/edit_review.py` — opcional)

```
python tools/edit_review.py E0XX-slug            # -> 07c-edit.html
```

- [ ] Pasada rápida por los KB / trims crudos: `aprobado` o feedback. Sirve para pillar un KB malo antes de la timeline.
- [ ] (Se puede saltar — el inspector de la timeline tiene lo mismo, en contexto.)

## 4. Primer corte + timeline  (`assemble.py` → `edit_timeline.py` → `09-edit.html`)

```
python tools/assemble.py E0XX-slug               # -> 09-timeline.json + 09-rough.mp4 + waveform
python tools/edit_timeline.py E0XX-slug          # -> 09-edit.html
```

- [ ] `09-timeline.json` generado: los beats de la espina, alineados a la voz si ya está grabada
- [ ] En `09-edit.html`, por beat: asset correcto · duración · posición · movimiento Ken Burns · aprobado
- [ ] Beats **sin cubrir**: elegir asset en `07-selection.md` (bloquean el render final)
- [ ] Cold open: clips `intro` en orden, corte seco; último aguanta ½ s → negro
- [ ] Bumper: 3–6 s negro + marca `Conquest` + «Soy <narrador>». Sin música.
- [ ] `PLANT n`/`PAY n`: mismo `asset` y `motion` las dos veces
- [ ] **Finalizar Stage 9** → guarda `09-timeline.json` → Claude aplica las regen + `assemble.py --final` (máster 4K)

## 5. Música de fondo

- [ ] Un lecho de `brand/assets/music/` (ominosa ambiental) bajo todo el episodio
- [ ] ~20–24 dB bajo el pico de voz; ducking −4 a −6 dB bajo el habla
- [ ] (Opcional) segunda pista más cálida en el cierre (M3)
- [ ] **Sin música en el bumper**
- [ ] Licencia de cada pista en `brand/assets/music/LICENSES.md` + descripción

## 6. Subtítulos

- [ ] `.srt` del VO **ya trimmeado**, corregido a mano contra `05-script.md` (cifras, nombres, `[S..]` literales)
- [ ] 1–2 líneas, ≤ 42 car./línea, ≥ 1 s en pantalla · español

## Texto en pantalla

- [ ] **Sin source cards.** Toda cita → `09-description.md` «Fuentes principales» + comentario fijado
- [ ] En pantalla solo: dispositivo de expediente (`EXPEDIENTE: CASO 00XX`, Courier Prime — `brain/03`) · tarjetas de capítulo (Playfair) · rótulo IA/recreación
- [ ] IA / recreación / colorizado: rótulo en **cada** aparición (`Ilustración — Conquest` / `Recreación`)
- [ ] Grade de casa aplicado a todo el timeline (oscuro/cálido/desaturado + grano + viñeta — `brain/03`)

## Export

- [ ] 4K (3840×2160), o la mejor resolución común si 4K implica upscalear casi todo · fps fijo
- [ ] −14 LUFS integrado · true peak ≤ −1 dBTP · AAC estéreo 320k
- [ ] `E0XX-<slug>-vN.mp4`

## Revisión final

- [ ] Timeline finalizada + máster 4K renderizado (`assemble.py --final`) → **picture lock**
- [ ] Usuario 002: ve el corte entero contra `05-script.md` + `brain/04` (rótulos, claims, dignidad)
- [ ] Firma del picture lock (Usuario 002): __________  fecha: ______
- [ ] `.srt` finalizado → Stage 10

## Gate Stage 9

- [ ] Todo beat de `09-timeline.json` cubierto (0 «sin cubrir») y aprobado
- [ ] Solo los movimientos de `brain/16`; grade de casa aplicado; sin source cards; sin letterbox salvo que un clip lo fuerce
- [ ] Cold open = clips `intro` en orden + bumper en negro
- [ ] `motion` Ken Burns coherente con orientación; `PLANT n`/`PAY n` comparten `asset` y `motion`
- [ ] Un lecho de música, ducked; sin música en el bumper; licencias anotadas
- [ ] IA/recreación con `rótulo` en cada aparición
- [ ] `.srt` corregido contra el guion
- [ ] −14 LUFS; máster 4K; picture lock firmado por Usuario 002
