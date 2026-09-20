# Índice maestro de episodios

> Fuente única de verdad del estado de cada episodio. La escriben `tools/advance.py` y `tools/serve.py`; edítala a mano solo para las notas o el techo de auto-avance.

## Leyenda

**Stage** 0 idea · 1 brief · 2 investigación · 3 outline · 4 guion · 5 fact-check · 6 shotlist · 7 recursos+estilo · 8 grabación · 9 edición · 10 paquete · 11 publicación · 12 retro
**Gate** `abierto` (en curso) · `exportado` (decisiones tomadas, falta plegar) · `firmado` (gate pasado, listo para avanzar)
**Auto-avance** el stage máximo hasta el que el loop avanza sin pedirte permiso.

## Episodios

| ID | Slug | Título | Track | Narrador | Stage | Gate | Auto-avance | Notas |
|----|------|--------|-------|----------|-------|------|-------------|-------|
| E001 | E001-hokusai | «Hokusai» | Documental | Usuario 002 | 11 | abierto | 12 | Stage 10 aprobado (titulo C, miniatura+descripcion OK) — listo para avanzar a Stage 11 (Publicacion) |
| E002 | E002-toyota-taiichi-ohno | «Toyota / Taiichi Ohno» | Documental | Usuario 002 | 9 | exportado | 4 | timeline guardada · 0 correcciones + render 4K en cola |
| E003 | E003-tulipomania | «Tulipomanía» | Documental | Usuario 002 | 9 | abierto | 12 | toma nueva subida y procesada — trim + timeline listos, 18 líneas del guion sin cobertura clara (revisar assets/E003-vo.review.html) |
| E004 | E004-coca-cola | «Coca-Cola» | Documental | — | 6 | abierto | 12 | guion actualizado directamente en 05-script.md |

## Reglas

- Un episodio no avanza de stage sin `Gate = firmado` (`brain/06`, `brain/17`).
- Al publicar: `advance.py` mueve la fila al KPI log de `brain/07`.
