# Edición — E0XX «<título>»

> Stage 9. Protocolo: `docs/16-edit-and-delivery.md`. **Cinco movimientos, nada más.**
> Depende de: `05-script.md` (bloqueado) · `06-shotlist.md` · `07-selection.md` · `brand/assets/music/`.

| Campo | Valor |
|-------|-------|
| ID episodio | E0XX |
| Versión de guion | v__ |
| Responsable | Josh |
| Resolución de salida | (1080p / 4K — de `docs/03`) |
| fps | (24 / 30) |
| Fecha | AAAA-MM-DD |

---

## 0. Grabación (Stage 8) — tomas de entrada

| Toma | Archivo | Sección(es) del guion | Notas / pickups |
|------|---------|-----------------------|-----------------|
| T1 | `assets/…` | | |

## 1. Trim  (`tools/trim_talk.py`)

```
python tools/trim_talk.py assets/T1.mp4        # -> T1.trimmed.mp4 + T1.cuts.md
```

- [ ] Transcripción revisada; cortes vetados anotados (`--keep MM:SS`)
- [ ] Cortes suaves (padding 120–180 ms; nada por debajo de 0.4 s)
- [ ] Tomas ensambladas en orden de secciones del guion

| Toma | Cortes | Duración final | Vetos aplicados |
|------|--------|----------------|-----------------|
| T1 | | | |

## 2. B-roll

- [ ] Cada beat de `06-shotlist.md` marcado archivo/stock/IA tiene su asset de `07-selection.md` en pantalla
- [ ] Cold open: 2–5 clips de `assets/intro/` en orden, corte seco; último aguanta ½ s → negro
- [ ] Bumper: 3–6 s negro + marca `Éxodo` + «Soy <narrador>». Sin música.
- [ ] Clips de vídeo a duración, sin rampa ni filtro; loop solo si el punto es invisible
- [ ] `[PLANT]`/`[PAY]`: mismo plano las dos veces

## 3. Ken Burns  (`tools/kenburns.py`)

```
python tools/kenburns.py E0XX-slug --all       # lee 07-selection.md -> assets/kb/
```

- [ ] Movimiento por orientación (≈16:9 push-in · panorámica pan H · vertical pan V · pequeña estática)
- [ ] Duración = duración del beat
- [ ] Overrides por beat anotados abajo

| Beat | Imagen (W×H) | Movimiento | Override |
|------|-------------|------------|----------|
| | | | |

## 4. Música de fondo

- [ ] Un lecho de `brand/assets/music/` (ominosa ambiental) bajo todo el episodio
- [ ] ~20–24 dB bajo el pico de voz; ducking −4 a −6 dB bajo el habla
- [ ] (Opcional) segunda pista más cálida entra en el cierre (M3)
- [ ] **Sin música en el bumper**
- [ ] Licencia de cada pista en `brand/assets/music/LICENSES.md`

| Cue | Sección | Pista | Nivel | Ducking |
|-----|---------|-------|-------|---------|
| M1 | todo | | | |
| M3 | cierre | | | |

## 5. Subtítulos

- [ ] `.srt` generado del VO **ya trimmeado**
- [ ] Corregido a mano contra `05-script.md` (cifras, nombres, claims `[S..]` literales)
- [ ] 1–2 líneas, ≤ 42 car./línea, ≥ 1 s en pantalla · español

## Source cards (mínimo)

Cita en pantalla **solo si**: cita textual · cifra en disputa/aproximada · documento nombrado. El resto → `09-description.md` «Fuentes principales».

| Beat | Qué | Texto en pantalla (`Autor — Obra / Año`) |
|------|-----|------------------------------------------|
| | | |

- [ ] IA / recreación / colorizado: rótulo en **cada** aparición (`Ilustración — Éxodo` / `Recreación`)

## Export

- [ ] Resolución del canal (`docs/03`) · fps fijo
- [ ] −14 LUFS integrado · true peak ≤ −1 dBTP · AAC estéreo 320k
- [ ] `E0XX-<slug>-vN.mp4`

## Revisión

- [ ] Josh: montaje → **picture lock** (sin más cambios de timing)
- [ ] Carmen: ve el corte entero contra `05-script.md` + `docs/04` (rótulos, claims, dignidad)
- [ ] Carmen firma el picture lock: __________  fecha: ______
- [ ] Sonido + `.srt` finalizados → Stage 10

## Gate Stage 9

- [ ] Solo los cinco movimientos; sin grade/letterbox/grano
- [ ] Todo beat con su asset; cold open 2–5 planos + bumper en negro
- [ ] Ken Burns coherente con orientación; `[PLANT]`/`[PAY]` idénticos
- [ ] Un lecho de música, ducked; sin música en el bumper; licencias anotadas
- [ ] IA/recreación rotulado en cada aparición
- [ ] `.srt` corregido contra el guion
- [ ] −14 LUFS; resolución del canal; picture lock firmado por Carmen
