# Éxodo — YouTube Blueprint (Phase 1)

> **Name:** *Éxodo* (wordmark / handles: "Exodo Official", `@exodoofficial`). Chosen 2026-08-28. See [docs/03-brand-identity.md](docs/03-brand-identity.md). Trademark search (class 41) and handle acquisition still pending.

Free-content YouTube channel/segment ("Phase 1") that feeds a hyperlocal membership business for the Spanish-speaking community of Rotterdam, led by **Carmen** (journalist, ex-university lecturer — editorial lead, T01 ideation, fact-check sign-off) and **Josh** (production/tech — writes every script, T02 ideation). Both are Venezuelan journalists. Narration is assigned per episode.

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
| `docs/` | Standing rules, 00–15: charter, editorial/sourcing, format, brand, legal, separation, workflow (12 stages), publishing, tone, reflection, git, visual rhythm, available-material, hook naming, fact-check, AI illustration. |
| `templates/` | Blank fill-in templates for every stage of an episode. |
| `episodes/` | One folder per episode. `_TEMPLATE-episode-folder/` to copy; `E000-EXAMPLE-*` as a worked reference; `_STATUS.md` master index. |
| `ideas/` | Two **tracks** (`tracks.md`): T01 Historias Inspiradoras (Carmen), T02 Exploración (Josh) → **idea pool** (`idea-pool.md`), scored with `idea-rubric.md`. |
| `research/` | Reverse-engineering the Dieck Docs format from transcripts to ground the `docs/` specs. Transcripts stay local (copyright). |
| `tools/` | `factcheck.py` (fact-check L1) · `build_ai_prompts.py` (Stage 7 AI prompts) · `build_idea_pitch.py` (idea-pool PDF). |
| `brand/` | `naming-exploration.md`; `assets/` empty until visual identity is set. |

## Core non-negotiables (full text in [docs/00-project-charter.md](docs/00-project-charter.md))

1. **Never** use real cases, stories or people from Carmen's Rotterdam Spanish-speaking community — not even anonymized. That material belongs only to the membership business.
2. Every episode is about a **public figure, historical case, or company/practice with verifiable public documentation** — no private individuals, no unrecorded cases.
3. **No factual claim without a cited source.** No invented data or quotes.
4. Kept **separate in brand, folder and workflow** from the membership business and any other team video channel.

## Getting started on a new episode

1. Track owner proposes the idea (T01 Carmen / T02 Josh) with **3 hook-titles** ([docs/13](docs/13-hook-naming.md)).
2. **Available-material cross-check** ([docs/12](docs/12-available-material-protocol.md)) — public-domain archives only.
3. Add to [ideas/idea-pool.md](ideas/idea-pool.md); score with [ideas/idea-rubric.md](ideas/idea-rubric.md) (eliminatorios + /21).
4. If it passes: copy `episodes/_TEMPLATE-episode-folder/` → `episodes/E0XX-<slug>/`. Josh writes; assign narrator in the brief.
5. Work the 12 stages in order. See [docs/06-production-workflow.md](docs/06-production-workflow.md). Fact-check (5) = `factcheck.py` + LLM prompt + Carmen's sign-off ([docs/14](docs/14-fact-check-protocol.md)); shotlist (6) → asset selection + photography pass (7, `07-assets.md`), AI-illustration prompts (`07b-ai-prompts.md`) only for beats with no real image ([docs/15](docs/15-ai-illustration-protocol.md)).
6. Update `episodes/_STATUS.md`.

## Open decisions

- **Channel type:** own new channel vs. recurring segment inside an existing team channel — **undecided**. Blueprint is written channel-agnostic.
- **Name:** *Éxodo* / "Exodo Official" — decided. Trademark search (class 41) + handle acquisition + visual identity still to do ([docs/03](docs/03-brand-identity.md)).
- **Publishing cadence** — proposed default in [docs/07-publishing-seo-metrics.md](docs/07-publishing-seo-metrics.md), not locked.
- **Format specs (`docs/02`, `08`, `09`) are v1** — validated against 6 Dieck Docs transcripts. Re-validate as more are added.
- **Idea pool:** 21 ideas (Round 1) — `ideas/idea-pool.md` + a pitch PDF (`ideas/idea-pool.pdf`, gitignored). E001 Hokusai in production.
