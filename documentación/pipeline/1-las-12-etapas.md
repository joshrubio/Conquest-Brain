# Las 12 etapas

Un episodio se produce en 12 etapas **con gates**: no empiezas una etapa hasta que el gate de la anterior está firmado. Los archivos viven en `episodes/E0XX-<slug>/`, numerados para casar con las etapas.

Regla completa: `brain/06-production-workflow.md`. Cada etapa tiene su plantilla en `templates/`.

## Vista rápida

| # | Etapa | Produce | Lead | Gate |
|---|-------|---------|------|------|
| 0 | Ideación | fila en `idea-pool.md` | dueño del track | hook-title + material + rúbrica ≥14 + Usuario 002 firma |
| 1 | Brief | `01-brief.md` | Usuario 001 | Usuario 001 + Usuario 002 de acuerdo; narrador asignado |
| 2 | Dossier de investigación | `02-research-dossier.md` + `03-source-log.csv` | Usuario 001 | toda claim de carga con ≥1 Tier A/B |
| 3 | Outline | (beat sheet) | Usuario 001 | la estructura se sostiene sin torcer hechos |
| 4 | Guion | `05-script.md` | Usuario 001 | autorrevisión hecha; toda `[S..]` resuelve |
| 5 | Fact-check | `04-factcheck-auto.md` + `04-fact-check.md` | L1+L2 auto · **L3 Usuario 002** | L1 PASS; L2 resuelto; Usuario 002 firma |
| 6 | Shotlist | `06-shotlist.md` | Usuario 001 | cada beat clasificado; cifras con rótulo de fuente |
| 7 | Recursos + pase de estilo | `07-assets.md` (+ `07b-ai-prompts.md`, `07-selection.md`) | Usuario 001 | cada beat cubierto; cold open 2–5; licencias claras |
| 8 | Grabación | tomas en `assets/` | narrador (Usuario 001 o Usuario 002) | toma completa contra guion bloqueado |
| 9 | Edición | `07c-edit.md` | Usuario 001 | KB + trim APROBADO; picture lock firmado por Usuario 002 |
| 10 | Paquete | `08-thumbnail-title.md`, `09-description.md` | Usuario 001 | título/miniatura honestos; 3 aprobaciones de Usuario 002 |
| 11 | Publicación | `10-publish-checklist.md` | Usuario 001 | tick legal/COI de ambos; subido y programado |
| 12 | Retro | `11-retro.md` | ambos | métricas a 48h + 30d; fixes de proceso |

## Las cuatro "review pages"

Cuatro etapas entregan el trabajo a una **página HTML generada** en vez de a una tabla markdown. Usuario 001 o Usuario 002 trabajan en el navegador, pulsan "Exportar", y Claude pliega el `.txt` de vuelta al doc fuente:

| Etapa | Página | Genera |
|-------|--------|--------|
| 0 | `ideas/idea-review.html` | `idea_review.py` |
| 7 | `07-style-pass.html` | `pull_assets.py` |
| 9 | `07c-edit.html` | `edit_review.py` |
| 10 | `10-package.html` | `package_review.py` |

El `.html` es regenerable (gitignored); el `.txt` exportado es el registro que sí se sube. Patrón detallado en `herramientas/9-páginas-de-revisión.md` (2ª pasada de guías).

## Roles

**`Usuario 001` y `Usuario 002` son *slots*, no personas.** Las responsabilidades son ítems asignables; el reparto de abajo es el de esta iteración. Quién es quién vive en [configuración-usuarios.md](../configuración-usuarios.md) (y `brain/USERS.md`) — los únicos archivos con nombres reales.

- **Usuario 001 escribe todos los guiones.** También: ideación T02, shotlist, edición, publicación, tech, `tools/`.
- **Usuario 002:** lead editorial, ideación T01, dirección de investigación, firma del fact-check (Layer 3), a cámara/narración (compartido).
- **Narrador** asignado por episodio — suele seguir al dueño del track; mantener un reparto equilibrado. En cámara dice su nombre real (`«Soy [nombre].»`).

| Etapa | Lead | Apoyo |
|-------|------|-------|
| 0 ideación | dueño del track | el otro |
| 1–3 investigación | Usuario 001 | Usuario 002 (dirección) |
| 4 guion | Usuario 001 | — |
| 5 fact-check | L1+L2 auto · L3 **Usuario 002** | Usuario 001 responde |
| 6 shotlist | Usuario 001 | Usuario 002 |
| 7 recursos + pase de estilo | Usuario 001 | — |
| 8 grabación | narrador | el otro |
| 9 edición | Usuario 001 | Usuario 002 revisa |
| 10 paquete | Usuario 001 | Usuario 002 aprueba título/miniatura |
| 11 publicación | Usuario 001 | Usuario 002 co-firma |
| 12 retro | ambos | — |

## Definition of Done

Publicado + subtítulos vivos + fuentes en la descripción + comentario fijado + `_STATUS.md` actualizado + retro programada.

## Dónde profundizar

- Etapa 0 → [2-de-idea-a-episodio](2-de-idea-a-episodio.md)
- Etapas 0/5 (protocolos) → [3-los-3-protocolos](3-los-3-protocolos.md)
- Etapa 5 → [4-fact-check](4-fact-check.md)
- Etapa 7 → [5-pase-de-estilo](5-pase-de-estilo.md)
- Etapa 9 → [6-la-edición](6-la-edición.md)
- Etapas 10–11 → [7-empaquetado-y-publicación](7-empaquetado-y-publicación.md)
- Etapa 12 → [8-retro-y-métricas](8-retro-y-métricas.md)
- Etapas 1–4 (escritura) → toda la carpeta `modelo-narrativo/`

## El estado de cada episodio

`episodes/_STATUS.md` es la fuente única de verdad del estado. Se actualiza en **cada cambio de etapa**. Reglas: un episodio no avanza sin pasar su gate; máx. 2 episodios en etapas 2–5 a la vez (cuello de botella = investigación + fact-check).
