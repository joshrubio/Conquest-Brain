---
doc: INDEX
summary: "One blank fill-in per pipeline stage. Copy the episode folder, don't copy these individually."
stage: all
authority: index
---

# templates/ — index

Blank fill-ins, one per stage. A new episode is `cp -r episodes/_TEMPLATE-episode-folder
episodes/E0XX-slug` — the numbered files there are copies of these. Spanish.
Each has frontmatter (`stage`, `fills`, `rule`).

| Stage | Template | Produces | Governed by |
|-------|----------|----------|-------------|
| 1 | `episode-brief.md` | `01-brief.md` | brain/06 |
| 2 | `research-dossier.md` | `02-research-dossier.md` | brain/01, 12 |
| 2 | `source-log.csv` | `03-source-log.csv` | brain/01 |
| 3 | `outline-template.md` | `03-outline.md` (beat sheet) | brain/02, 09 |
| 4 | `script-template.md` | `05-script.md` | brain/02, 08, 09 |
| 5 | `fact-check-auto-prompt.md` | `04-factcheck-auto.md` (L2) | brain/14 |
| 6 | `shotlist-broll.md` | `06-shotlist.md` | brain/11 |
| 7 | `asset-manifest.md` | `07-assets.md` | brain/12, 03 |
| 7 | `ai-prompts.md` | `07b-ai-prompts.md` | brain/15 |
| 9 | `edit-checklist.md` | `07c-edit.md` | brain/16 |
| 10 | `thumbnail-title-brief.md` | `08-thumbnail-title.md` | brain/13, 07 |
| 10 | `description-and-credits.md` | `09-description.md` | brain/07 |
| 11 | `publish-checklist.md` | `10-publish-checklist.md` | brain/04, 05 |
| 12 | `episode-retro.md` | `11-retro.md` | brain/07 |

Stage 0 (ideation) has no template — it lives in `ideas/idea-pool.md`.
