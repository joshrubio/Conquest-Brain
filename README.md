# Cross Check — YouTube Blueprint (Phase 1)

> **Name:** *Cross Check* (chosen 2026-08-28; handle differentiator "Official" if needed). See [docs/03-brand-identity.md](docs/03-brand-identity.md). Trademark search (class 41) and handle acquisition still pending.

Free-content YouTube channel/segment ("Phase 1") that feeds a hyperlocal membership business for the Spanish-speaking community of Rotterdam, led by **Carmen** (journalist, ex-university lecturer) and **Josh** (production/technology). Both write and both narrate — narration is assigned per episode.

Reference format: **Dieck Docs** (Farid Dieck) — journalistic documentaries/biographies that close on a psychological or human reflection with an applicable lesson.

## What this repo is

The **blueprint**: documentation, templates and folder structure. **No video production yet.** Managed locally + GitHub (see [docs/10-repo-and-git-workflow.md](docs/10-repo-and-git-workflow.md)).

## Language policy

- **`docs/`, `research/` analysis** — English (project/process documentation; global rule).
- **`templates/`, `episodes/`, `ideas/`** — Spanish (production artifacts: the published content is in Spanish).
- Commit messages, file/asset names, code comments — English.

## Folder map

| Path | Purpose |
|------|---------|
| `docs/` | Standing rules: charter, editorial standard, format spec, tone, reflection rules, legal/ethics, separation policy, workflow, publishing, git workflow, visual rhythm. |
| `templates/` | Blank fill-in templates for every stage of an episode. |
| `episodes/` | One folder per episode. `_TEMPLATE-episode-folder/` to copy; `E000-EXAMPLE-*` as a worked reference; `_STATUS.md` master index. |
| `ideas/` | Two tiers: **themes** (recurring topic areas, filtered) → **idea pool** (individual video ideas, scored). See `ideas/README.md`. |
| `research/` | Reverse-engineering the Dieck Docs format from transcripts to ground the `docs/` specs. Transcripts stay local (copyright). |
| `brand/` | Logo, fonts, graphic templates (empty until brand is set). |

## Core non-negotiables (full text in [docs/00-project-charter.md](docs/00-project-charter.md))

1. **Never** use real cases, stories or people from Carmen's Rotterdam Spanish-speaking community — not even anonymized. That material belongs only to the membership business.
2. Every episode is about a **public figure, historical case, or company/practice with verifiable public documentation** — no private individuals, no unrecorded cases.
3. **No factual claim without a cited source.** No invented data or quotes.
4. Kept **separate in brand, folder and workflow** from the membership business and any other team video channel.

## Getting started on a new episode

1. Confirm an approved **theme** covers it ([ideas/themes.md](ideas/themes.md)); if not, filter the theme first ([ideas/theme-rubric.md](ideas/theme-rubric.md)).
2. Add the idea to [ideas/idea-pool.md](ideas/idea-pool.md); score it with [ideas/evaluation-rubric.md](ideas/evaluation-rubric.md).
3. If it passes: copy `episodes/_TEMPLATE-episode-folder/` → `episodes/E0XX-<slug>/`. Assign writer + narrator (Carmen or Josh) in the brief.
4. Work the stages in order (brief → research → fact-check → script → …). See [docs/06-production-workflow.md](docs/06-production-workflow.md).
5. Update `episodes/_STATUS.md`.

## Open decisions

- **Channel type:** own new channel vs. recurring segment inside an existing team channel — **undecided**. Blueprint is written channel-agnostic.
- **Name:** *Cross Check* — decided. Trademark search (class 41) + handle acquisition + visual identity still to do ([docs/03](docs/03-brand-identity.md)).
- **Publishing cadence** — proposed default in [docs/07-publishing-seo-metrics.md](docs/07-publishing-seo-metrics.md), not locked.
- **Format specs (`docs/02`, `08`, `09`) are v1** — validated against 6 Dieck Docs transcripts (`research/dieck-docs/structure-analysis.md`). Re-validate as more are added.
- **Themes:** at least one theme must be approved in [ideas/themes.md](ideas/themes.md) before any episode can start.
