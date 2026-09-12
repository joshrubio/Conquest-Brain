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
| E002 | E002-toyota-taiichi-ohno | «Toyota / Taiichi Ohno» | Documental | Usuario 002 | 8 | abierto | 4 | créditos    → episodes/E002-toyota-taiichi-ohno/assets/CREDITS.md |
| E003 | E003-tulipomania | «Tulipomanía» | Documental | Usuario 002 | 7 | abierto | 12 | guion actualizado directamente en 05-script.md |
| E004 | E004-coca-cola | «Coca-Cola» | Documental | — | 2 | abierto | 12 | dossier + source-log escritos, esperando revisión Usuario 001/002 (Stage 2, gate de alto riesgo) |

## Reglas

- Un episodio no avanza de stage sin `Gate = firmado` (`brain/06`, `brain/17`).
- Al publicar: `advance.py` mueve la fila al KPI log de `brain/07`.
