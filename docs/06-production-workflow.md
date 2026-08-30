# 06 — Production Workflow (Phase 1)

Pipeline for one episode. Stages are gated: do not start a stage until the previous gate is signed. Files live in `episodes/E0XX-<slug>/`, numbered to match the stages.

## Stage 0 — Ideation
- Track owner proposes the idea: **T01 Historias Inspiradoras** (Carmen) or **T02 Exploración** (Josh) — see [ideas/tracks.md](../ideas/tracks.md).
- **Protocol 2 — Hook Naming** ([docs/13](13-hook-naming.md)): 3 hook-title variants, Dieck register.
- **Protocol 1 — Available material** ([docs/12](12-available-material-protocol.md)): cross-check the case against public-domain archives; fill the worksheet. No material → no episode.
- Score with [ideas/idea-rubric.md](../ideas/idea-rubric.md): eliminatorios E1–E8 + /21.
- Record in [ideas/idea-pool.md](../ideas/idea-pool.md).
- **Gate:** track assigned; hook-title done; material cross-check passes (E8); all eliminatorios YES; score ≥ 14.

## Stage 1 — Brief  → `01-brief.md`
- Template: [templates/episode-brief.md](../templates/episode-brief.md).
- Working thesis, why now, structure in one sentence each, candidate close (form A/B/C), top 3 sources already found, risks.
- **Assign:** track, hook-title (from Stage 0), and **narrator (Carmen or Josh)**. Writer is always Josh.
- **Gate:** Carmen + Josh agree it's worth the research time; narrator assigned.

## Stage 2 — Research dossier  → `02-research-dossier.md` + `03-source-log.csv`
- Template: [templates/research-dossier.md](../templates/research-dossier.md), [templates/source-log.csv](../templates/source-log.csv).
- Full timeline, key figures, every claim with source + tier, open questions, contested points, rights status of any visual.
- **Gate:** every load-bearing claim has ≥1 Tier A/B source; contested points identified; no reliance on Tier C/D.

## Stage 3 — Outline
- Beat sheet against [docs/02-content-format.md](02-content-format.md): cold open → context pivot → narrative acts (mark explainer interludes + foreshadowing plants/pays) → close.
- Confirm the close form (A/B/C) chosen in the brief still fits the material.
- **Gate:** structure holds without stretching facts; close is honest to the case.

## Stage 4 — Script  → `05-script.md`
- Template: [templates/script-template.md](../templates/script-template.md).
- Full narration + on-screen cues + inline source tags `[S12]` linking to the source log.
- **Gate:** self-review complete; every `[S..]` resolves.

## Stage 5 — Fact-check  → `04-factcheck-auto.md` + `04-fact-check.md`
- Protocol: [docs/14-fact-check-protocol.md](14-fact-check-protocol.md). Three layers:
  - **L1 deterministic:** `python tools/factcheck.py 05-script.md 03-source-log.csv` → must PASS.
  - **L2 LLM-assisted:** run [templates/fact-check-auto-prompt.md](../templates/fact-check-auto-prompt.md); resolve every flag against the real source.
  - **L3 human:** **Carmen** (did not write it — Josh always does) completes [templates/fact-check-sheet.md](../templates/fact-check-sheet.md) + the legal/ethics ([docs/04](04-legal-and-ethics.md)) and separation ([docs/05](05-separation-policy.md)) passes, and signs.
- **Gate (hard):** L1 PASS; all L2 flags resolved; `04-fact-check.md` signed by Carmen; legal + separation clear.

## Stage 6 — Shotlist / B-roll  → `06-shotlist.md`
- Template: [templates/shotlist-broll.md](../templates/shotlist-broll.md). Method: [docs/11-visual-rhythm.md](11-visual-rhythm.md).
- **Inferred from the locked script** — one beat per subject change / `[EN PANTALLA]` / `[EXPLICADOR]` / `[PLANT]`/`[PAY]`. Per beat: visual **need**, archival vs own-graphic, on-screen text, motion.
- **Gate:** every beat classified; every graphed number has a source label; beat count matches the target rhythm.

## Stage 7 — Asset selection + photography pass  → `07-assets.md` (+ `07b-ai-prompts.md`)
- Template: [templates/asset-manifest.md](../templates/asset-manifest.md). Search feasibility already done in `material-search.md`; here it gets specific.
- **1. Candidate pull (`tools/pull_assets.py`):** write `07-pull.tsv` (one row per beat that needs an image/clip: beat, kind `stock|stock-img|video|archive`, source, query, opts; `n=3` per beat). `stock` beats return **video first** (Pexels/Pixabay), images only fill the rest — a found clip saves hand-building b-roll in the edit. `python tools/pull_assets.py E0XX-slug` hits the free APIs (Met, Wikimedia Commons, AIC, Pexels, Pixabay, Unsplash, Openverse) and writes **`07-candidates.md`** (git record) + **`07-candidates.html`** (thumbnail picker; video cards flagged ▶). Keys in `tools/.env` (gitignored); keyless sources still run without it.
- **2. Photography pass (Josh, manual) — one surface, `07-candidates.html`:**
  - **Left:** the pulled candidates per beat. Judge each thumbnail on resolution (vs. the template standard) / condition / colour / crop / sequence coherence against the series look ([docs/03](03-brand-identity.md) §Visual direction); tick the keepers.
  - **Right:** the `07b-ai-prompts.md` prompts (if the file exists). For a beat the pull didn't cover: copy the prompt, generate, paste the image path/URL into that prompt's input.
  - **Exportar 07-picks.txt** (saves into the episode folder) writes both the ticked candidates and the filled AI paths. Then `python tools/pull_assets.py E0XX-slug --download` pulls candidates into `assets/stock|video|archive/`, copies the AI images into `assets/ai/` under their `07b` filenames, verifies resolution, appends `assets/CREDITS.md`, prints manifest rows. (No browser? tick `- [x]` in `07-candidates.md`; AI still needs the picks file.)
- **3. Own-graphics** beats → design brief, not the manifest.
- **4. AI-illustration** ([docs/15](15-ai-illustration-protocol.md)): for the beats left ❌ (no real image, no own-graphic), run `tools/build_ai_prompts.py` → `07b-ai-prompts.md` *before* the pull so the prompts show in the picker's right column. Pick the episode style (photoreal allowed); Claude writes the scenes; Josh generates and pastes paths in the picker. On-screen label always; never a photoreal face of a real person; never a fake document.
- **5. Manifest:** one row per **accepted** image (archival or AI), downloaded to `assets/` with a consistent name.
- **Gate:** every beat covered (accepted image / graphic / AI); every image a clear licence + resolution for its use; colour/condition checked by sequence; AI images stylised, labelled, no real-person face; courtesy credits logged for `09-description.md`.
- Runs in parallel with Stage 8 (recording doesn't depend on it).

## Stage 8 — Record
- The episode's assigned narrator (Carmen or Josh) does VO + on-camera per shotlist. Clean audio pass.
- **Gate:** full take against locked script; pickups noted.

## Stage 9 — Edit
- Assembly → picture lock → sound → captions/lower-thirds → source cards.
- Spanish subtitles (.srt) generated and corrected.
- **Gate:** picture lock reviewed by both; captions accurate.

## Stage 10 — Package  → `08-thumbnail-title.md`, `09-description.md`
- Templates: [templates/thumbnail-title-brief.md](../templates/thumbnail-title-brief.md), [templates/description-and-credits.md](../templates/description-and-credits.md).
- 3 title options (from the hook-titles), thumbnail, description with **Fuentes principales** block + asset courtesy credits, chapters, tags.
- **Gate:** title/thumbnail honest to the content (no clickbait the body doesn't pay off).

## Stage 11 — Publish  → `10-publish-checklist.md`
- Template: [templates/publish-checklist.md](../templates/publish-checklist.md).
- Final legal/separation tick by Carmen + Josh. Upload, subtitles, chapters, end screen, pinned comment (sources / any caveat). Schedule.

## Stage 12 — Retro  → `11-retro.md`
- Template: [templates/episode-retro.md](../templates/episode-retro.md).
- 48h + 30d: metrics, what worked, corrections issued, process fixes.
- Update [episodes/_STATUS.md](../episodes/_STATUS.md) and [docs/07-publishing-seo-metrics.md](07-publishing-seo-metrics.md) KPI log.

## Roles

- **Josh writes every script.** Also: T02 ideation, shotlist, edit, publishing, tech, `tools/`.
- **Carmen:** editorial lead, T01 ideation, research direction, fact-check sign-off (Layer 3), on-camera/narration (share).
- **Narrator** assigned per episode (Carmen or Josh) — usually follows the track owner; keep a rough balance.

| Stage | Lead | Support |
|-------|------|---------|
| 0 ideation | Track owner (Carmen T01 / Josh T02) | the other |
| 1–3 research | Josh | Carmen (direction) |
| 4 script | Josh | — |
| 5 fact-check | L1+L2 automated · L3 **Carmen** | Josh answers |
| 6 shotlist | Josh | Carmen |
| 7 asset selection + photography pass | Josh | — |
| 8 record | Narrator (Carmen or Josh) | the other |
| 9 edit | Josh | Carmen reviews |
| 10 package | Josh | Carmen approves title/thumb |
| 11 publish | Josh | Carmen co-signs |
| 12 retro | Both | — |

## Definition of Done

Published + subtitles live + sources in description + pinned comment + `_STATUS.md` updated + retro scheduled.
