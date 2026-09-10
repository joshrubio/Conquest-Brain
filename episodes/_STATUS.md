# Índice maestro de episodios

> Fuente única de verdad del estado de cada episodio. La escriben `tools/advance.py` y `tools/serve.py`; edítala a mano solo para las notas o el techo de auto-avance.

## Leyenda

**Stage** 0 idea · 1 brief · 2 investigación · 3 outline · 4 guion · 5 fact-check · 6 shotlist · 7 recursos+estilo · 8 grabación · 9 edición · 10 paquete · 11 publicación · 12 retro
**Gate** `abierto` (en curso) · `exportado` (decisiones tomadas, falta plegar) · `firmado` (gate pasado, listo para avanzar)
**Auto-avance** el stage máximo hasta el que el loop avanza sin pedirte permiso.

## Episodios

| ID | Slug | Título | Track | Narrador | Stage | Gate | Auto-avance | Notas |
|----|------|--------|-------|----------|-------|------|-------------|-------|
| E001 | E001-hokusai | «Hokusai» | Documental | Usuario 002 | 9 | exportado | 12 | BLOQUEADO en Stage 9: el fold necesita `assemble.py --final` (render 4K) y **no hay ffmpeg en esta máquina**. El loop no puede drenarlo. Correr el render en un box con ffmpeg. (Aviso: un beat sin `asset/file` en 09-timeline.json — revisar en 09-edit.html antes de renderizar.) |
| E002 | E002-toyota-taiichi-ohno | «Toyota / Taiichi Ohno» | Documental | Usuario 002 | 7 | abierto | 4 | 2026-09-11: Stage 6 estaba sin hacer (06/07 eran plantillas). Escrito `06-shotlist.md` (133 beats, registro de recreación) + `07b-ai-prompts.md` (19 prompts) + `07-pull.tsv`. `07-style-pass.html` YA existe (era el 404). Pase de estilo a medias: 24 candidatos / 11 beats — **`tools/.env` sin claves Pexels/Pixabay/Unsplash**, el stock no devuelve nada; archivo (Commons) sí. Falta: generar las 19 imágenes IA, pegar rutas, poner claves o enlaces propios, «Finalizar Stage 7». |

## Reglas

- Un episodio no avanza de stage sin `Gate = firmado` (`brain/06`, `brain/17`).
- Máx. 2 episodios en stages 2–5 a la vez.
- Al publicar: `advance.py` mueve la fila al KPI log de `brain/07`.
