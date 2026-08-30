# Exodo Channel

> **Exodo** (no accent, ever) · channel **Exodo Channel** · handle **`@exodochannel`** · own new YouTube channel, category *Education*. Brand spec: [docs/03-brand-identity.md](docs/03-brand-identity.md).

A Spanish-language journalistic-documentary YouTube channel — narrated real cases that close on a psychological/human reflection and a surgical, applicable takeaway. Led by **Carmen** (journalist, ex-university lecturer — editorial lead, T01 ideation, fact-check sign-off) and **Josh** (production/tech — writes every script, T02 ideation). Both are Venezuelan journalists; the *exodus* is their voice and motive, never an episode subject. Narration is assigned per episode.

Reference format: **Dieck Docs** (Farid Dieck). Standalone project — not a phase of, or funnel for, anything.

## What this repo is

Documentation, templates, per-episode folders, and the `tools/` that run the pipeline. Managed locally + GitHub ([docs/10-repo-and-git-workflow.md](docs/10-repo-and-git-workflow.md)).

## Language policy

- **`docs/`, `research/` analysis** — English.
- **`templates/`, `episodes/`, `ideas/`** — Spanish (the published content is Spanish).
- Commit messages, file/asset names, code comments — English.

## Folder map

| Path | Purpose |
|------|---------|
| `docs/` | Standing rules 00–16: charter, editorial/sourcing, format, brand, legal, independence, workflow (12 stages), publishing, tone, reflection, git, visual rhythm, available-material, hook naming, fact-check, AI illustration, edit & delivery. |
| `templates/` | Blank fill-in templates for every stage. |
| `episodes/` | One folder per episode. `_TEMPLATE-episode-folder/` to copy; `E000-EXAMPLE-*` worked reference; `_STATUS.md` master index. |
| `ideas/` | Two **tracks** (`tracks.md`): T01 Historias Inspiradoras (Carmen), T02 Exploración (Josh) → **idea pool** (`idea-pool.md`), scored with `idea-rubric.md`. |
| `research/` | Reverse-engineering the Dieck Docs format from transcripts (kept local — copyright). |
| `tools/` | `factcheck.py` · `build_ai_prompts.py` · `pull_assets.py` (Stage 7 hub) · `build_idea_pitch.py` · `kenburns.py` · `trim_talk.py` · `edit_review.py` · `find_music.py`. Keys in `tools/.env` (gitignored). |
| `brand/` | `naming-exploration.md`; `assets/` — avatar, banner, music. |

## Core non-negotiables (full text in [docs/00-project-charter.md](docs/00-project-charter.md))

1. **Subjects are public** — public figure, historical case, or company/practice with verifiable public documentation. Never private individuals, never unrecorded cases.
2. **No episode subject drawn from people Carmen or Josh personally know** — not even anonymized ([docs/05](docs/05-separation-policy.md)).
3. **No factual claim without a cited source.** No invented data or quotes.
4. The channel stays **independent in brand, folder, and workflow** — no co-branding or shared identity with any other channel or venture.

## Getting started on a new episode

1. Track owner proposes the idea (T01 Carmen / T02 Josh) with **3 hook-titles** ([docs/13](docs/13-hook-naming.md)).
2. **Available-material cross-check** ([docs/12](docs/12-available-material-protocol.md)) — public sources only.
3. Add to [ideas/idea-pool.md](ideas/idea-pool.md); score with [ideas/idea-rubric.md](ideas/idea-rubric.md).
4. If it passes: copy `episodes/_TEMPLATE-episode-folder/` → `episodes/E0XX-<slug>/`. Josh writes; assign narrator in the brief.
5. Work the 12 stages in order — [docs/06-production-workflow.md](docs/06-production-workflow.md). Fact-check (5) = `factcheck.py` + LLM prompt + Carmen's sign-off ([docs/14](docs/14-fact-check-protocol.md)); assets (7) run through **`07-photography-pass.html`** (`pull_assets.py`); edit (9) = `kenburns` → `trim_talk` → `edit_review` → b-roll → music ([docs/16](docs/16-edit-and-delivery.md)).
6. Update `episodes/_STATUS.md`.

## Status

- **Brand:** decided (name, channel type, spelling, category, palette, grade, typography, case-file device, 4K). To do: secure `@exodochannel` on IG/TikTok, produce logo SVG + thumbnail template, re-export banner at 2560×1440, trademark clearance (class 41, lawyer, before registering).
- **Format specs (`docs/02`, `08`, `09`) are v1** — validated against 6 Dieck Docs transcripts.
- **Idea pool:** 21 ideas + a pitch PDF (`ideas/idea-pool.pdf`, gitignored).
- **E001 Hokusai** in production — stuck at Stage 5 (Carmen's Layer 3 sign-off + closing S15/S19/S20).
- **Music:** Jamendo pool built; pick 3–5 beds from the Music section of the photography pass.
