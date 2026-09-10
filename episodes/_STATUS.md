# Índice maestro de episodios

> Fuente única de verdad del estado de cada episodio. La escriben `tools/advance.py` y `tools/serve.py`; edítala a mano solo para las notas o el techo de auto-avance.

## Leyenda

**Stage** 0 idea · 1 brief · 2 investigación · 3 outline · 4 guion · 5 fact-check · 6 shotlist · 7 recursos+estilo · 8 grabación · 9 edición · 10 paquete · 11 publicación · 12 retro
**Gate** `abierto` (en curso) · `exportado` (decisiones tomadas, falta plegar) · `firmado` (gate pasado, listo para avanzar)
**Auto-avance** el stage máximo hasta el que el loop avanza sin pedirte permiso.

## Episodios

| ID | Slug | Título | Track | Narrador | Stage | Gate | Auto-avance | Notas |
|----|------|--------|-------|----------|-------|------|-------------|-------|
| E001 | E001-hokusai | «Hokusai» | Documental | Usuario 002 | 9 | exportado | 12 | timeline guardada · 0 correcciones + render 4K en cola |
| E002 | E002-toyota-taiichi-ohno | «Toyota / Taiichi Ohno» | Documental | Usuario 002 | 6 | abierto | 4 | Stage 5 cerrado 2026-09-10: L1 PASS, L2 aplicó 19 correcciones (`04-factcheck-auto.md`), sin cola de verificación. Único ítem para Stage 11: dignidad del retrato de la plantilla de Fremont (NUMMI). Siguiente: escribir 06-shotlist.md. |

## Reglas

- Un episodio no avanza de stage sin `Gate = firmado` (`brain/06`, `brain/17`).
- Máx. 2 episodios en stages 2–5 a la vez.
- Al publicar: `advance.py` mueve la fila al KPI log de `brain/07`.
