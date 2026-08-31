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
> Depende de: `05-script.md` (bloqueado) · `06-shotlist.md` · `07-selection.md` · `brand/assets/music/`.
> Superficie de revisión: `07c-edit.html` (genera `tools/edit_review.py`).

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

## 3. Revisión  (`tools/edit_review.py` → `07c-edit.html`)

```
python tools/edit_review.py E0XX-slug            # -> 07c-edit.html
```

- [ ] Cada clip KB: `aprobado` o feedback («más lento» / «empieza a la izquierda» / «dir arriba» / «estática» / «dura 4 s»)
- [ ] Cada toma trimmeada: `aprobado` o correcciones («mantener pausa 00:12» / «cortar antes 02:03» / «no cortes el "eh" 03:04»)
- [ ] **Exportar `07c-review.txt`** → Claude re-genera los clips con FIX → re-revisar
- [ ] **Todo APROBADO** antes de pasar al b-roll

## 4. B-roll  (ensamblaje — Claude + ffmpeg; DaVinci MCP más adelante si hace falta)

- [ ] Cada beat de `06-shotlist.md` (archivo/stock/IA) con su asset de `07-selection.md` sobre el VO
- [ ] Cold open: 2–5 clips de `assets/intro/` en orden, corte seco; último aguanta ½ s → negro
- [ ] Bumper: 3–6 s negro + marca `Exodo` + «Soy <narrador>». Sin música.
- [ ] Clips de vídeo a duración, sin rampa ni filtro; loop solo si el punto es invisible
- [ ] `[PLANT]`/`[PAY]`: mismo plano las dos veces

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
- [ ] IA / recreación / colorizado: rótulo en **cada** aparición (`Ilustración — Exodo` / `Recreación`)
- [ ] Grade de casa aplicado a todo el timeline (oscuro/cálido/desaturado + grano + viñeta — `brain/03`)

## Export

- [ ] 4K (3840×2160), o la mejor resolución común si 4K implica upscalear casi todo · fps fijo
- [ ] −14 LUFS integrado · true peak ≤ −1 dBTP · AAC estéreo 320k
- [ ] `E0XX-<slug>-vN.mp4`

## Revisión final

- [ ] Usuario 001: b-roll + música ensamblados → **picture lock**
- [ ] Usuario 002: ve el corte entero contra `05-script.md` + `brain/04` (rótulos, claims, dignidad)
- [ ] Firma del picture lock (Usuario 001 o Usuario 002): __________  fecha: ______
- [ ] Sonido + `.srt` finalizados → Stage 10

## Gate Stage 9

- [ ] Cada clip KB y cada toma trimmeada **APROBADO** en `07c-review.txt`
- [ ] Solo los movimientos de `brain/16`; grade de casa aplicado; sin source cards; sin letterbox salvo que un clip lo fuerce
- [ ] Todo beat con su asset; cold open 2–5 planos + bumper en negro
- [ ] Ken Burns coherente con orientación; `[PLANT]`/`[PAY]` idénticos
- [ ] Un lecho de música, ducked; sin música en el bumper; licencias anotadas
- [ ] IA/recreación rotulado en cada aparición
- [ ] `.srt` corregido contra el guion
- [ ] −14 LUFS; 4K (o mejor común); picture lock firmado (un usuario)
