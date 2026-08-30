# Carpeta de episodio — plantilla

Copiar toda esta carpeta a `episodes/E0XX-<slug>/` al aprobar una idea.

Trabajar los archivos **en orden**. Cada uno corresponde a un stage de `docs/06-production-workflow.md` y se rellena a partir de la plantilla maestra en `templates/`.

| Archivo | Stage | Plantilla maestra |
|---------|-------|-------------------|
| `01-brief.md` | 1 | `templates/episode-brief.md` |
| `02-research-dossier.md` | 2 | `templates/research-dossier.md` |
| `03-source-log.csv` | 2 | `templates/source-log.csv` |
| `05-script.md` | 4 | `templates/script-template.md` |
| `04-factcheck-auto.md` | 5 (L1+L2) | — (genera `tools/factcheck.py` + `templates/fact-check-auto-prompt.md`) |
| `04-fact-check.md` | 5 (L3) | `templates/fact-check-sheet.md` |
| `06-shotlist.md` | 6 | `templates/shotlist-broll.md` |
| `07-assets.md` | 7 | `templates/asset-manifest.md` |
| `07b-ai-prompts.md` | 7 (solo si hace falta) | `tools/build_ai_prompts.py` (genera; ver `docs/15`) |
| `07-photography-pass.md` | 7 | `tools/pull_assets.py` (genera; hub del stage) |
| `07c-edit.md` | 9 | `templates/edit-checklist.md` (ver `docs/16`) |
| `07c-edit.html` · `07c-review.txt` | 9 | `tools/edit_review.py` (genera; revisión de KB + trim) |
| `08-thumbnail-title.md` · `09-description.md` | 10 | `templates/…` — o `tools/package_review.py E0XX --init` |
| `10-package.html` · `10-package.txt` | 10 | `tools/package_review.py` (genera; revisión de título/miniatura/descripción con Carmen) |
| `10-publish-checklist.md` | 11 | `templates/publish-checklist.md` |
| `11-retro.md` | 12 | `templates/episode-retro.md` |
| `material-search.md` | 0/2 | — (Protocolo 1, `docs/12`) |
| `assets/` | 7–9 | archivo descargado, gráficos, exports |

Al crear la carpeta: añadir el episodio a `episodes/_STATUS.md`.
