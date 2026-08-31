# 06 — Production Workflow

Pipeline for one episode. Stages are gated: do not start a stage until the previous gate is signed. Files live in `episodes/E0XX-<slug>/`, numbered to match the stages.

**Review pages.** Four stages hand off to a generated dark-theme HTML instead of a markdown table — Usuario 001 or Usuario 002 works in the browser, hits *Exportar*, and Claude folds the small `.txt` back into the source doc: Stage 0 `ideas/idea-review.html` · Stage 7 `07-style-pass.html` · Stage 9 `07c-edit.html` · Stage 10 `10-package.html`. The `.html` is regenerable (gitignored); the exported `.txt` is the tracked record.

## Stage 0 — Ideation
- Track owner proposes the idea: **T01 Historias Inspiradoras** (Usuario 002) or **T02 Exploración** (Usuario 001) — see [ideas/tracks.md](../ideas/tracks.md).
- **Protocol 2 — Hook Naming** ([brain/13](13-hook-naming.md)): 3 hook-title variants, Dieck register.
- **Protocol 1 — Available material** ([brain/12](12-available-material-protocol.md)): cross-check the case against public-domain archives; fill the worksheet. No material → no episode.
- Score with [ideas/idea-rubric.md](../ideas/idea-rubric.md): eliminatorios E1–E8 + /21.
- Record in [ideas/idea-pool.md](../ideas/idea-pool.md).
- **Usuario 002's review:** `python tools/idea_review.py` → `ideas/idea-review.html` — scores each idea, picks the strongest hook-title, comments; exports `idea-review.txt` → folded back into `idea-pool.md`.
- **Gate:** track assigned; hook-title chosen; material cross-check passes (E8); all eliminatorios YES; score ≥ 14; Usuario 002 signed off in `idea-pool.md`.

## Stage 1 — Brief  → `01-brief.md`
- Template: [templates/episode-brief.md](../templates/episode-brief.md).
- Working thesis, why now, structure in one sentence each, candidate close (form A/B/C), top 3 sources already found, risks.
- **Assign:** track, hook-title (from Stage 0), and **narrator (Usuario 001 or Usuario 002)**. Writer is always Usuario 001.
- **Gate:** Usuario 001 + Usuario 002 agree it's worth the research time; narrator assigned.

## Stage 2 — Research dossier  → `02-research-dossier.md` + `03-source-log.csv`
- Template: [templates/research-dossier.md](../templates/research-dossier.md), [templates/source-log.csv](../templates/source-log.csv).
- Full timeline, key figures, every claim with source + tier, open questions, contested points, rights status of any visual.
- **Gate:** every load-bearing claim has ≥1 Tier A/B source; contested points identified; no reliance on Tier C/D.

## Stage 3 — Outline
- Beat sheet against [brain/02-content-format.md](02-content-format.md): cold open → context pivot → narrative acts (mark explainer interludes + foreshadowing plants/pays) → close.
- Confirm the close form (A/B/C) chosen in the brief still fits the material.
- **Gate:** structure holds without stretching facts; close is honest to the case.

## Stage 4 — Script  → `05-script.md`
- Template: [templates/script-template.md](../templates/script-template.md).
- Full narration + on-screen cues + inline source tags `[S12]` linking to the source log.
- **Gate:** self-review complete; every `[S..]` resolves.

## Stage 5 — Fact-check  → `04-factcheck-auto.md` + `04-fact-check.md`
- Protocol: [brain/14-fact-check-protocol.md](14-fact-check-protocol.md). Three layers:
  - **L1 deterministic:** `python tools/factcheck.py 05-script.md 03-source-log.csv` → must PASS.
  - **L2 LLM-assisted:** run [templates/fact-check-auto-prompt.md](../templates/fact-check-auto-prompt.md); resolve every flag against the real source.
  - **L3 human:** **Usuario 002** (did not write it — Usuario 001 always does) completes [templates/fact-check-sheet.md](../templates/fact-check-sheet.md) + the legal/ethics ([brain/04](04-legal-and-ethics.md)) and independence/COI ([brain/05](05-separation-policy.md)) passes, and signs.
- **Gate (hard):** L1 PASS; all L2 flags resolved; `04-fact-check.md` signed by Usuario 002; legal + COI clear.

## Stage 6 — Shotlist / B-roll  → `06-shotlist.md`
- Template: [templates/shotlist-broll.md](../templates/shotlist-broll.md). Method: [brain/11-visual-rhythm.md](11-visual-rhythm.md).
- **Inferred from the locked script** — one beat per subject change / `[EN PANTALLA]` / `[EXPLICADOR]` / `[PLANT]`/`[PAY]`. Per beat: visual **need**, archival vs own-graphic, on-screen text, motion.
- **Gate:** every beat classified; every graphed number has a source label; beat count matches the target rhythm.

## Stage 7 — Asset selection + style pass  → `07-assets.md` (+ `07b-ai-prompts.md`)

**`07-style-pass.html` is the hub of this stage** — every asset decision (per beat, the AI images, and the cold-open intro) is made in that one page and exported as `07-picks.txt`; `--download` turns the picks into files + `07-selection.md`. Nothing enters the edit that didn't go through it.

- Template: [templates/asset-manifest.md](../templates/asset-manifest.md). Search feasibility already done in `material-search.md`; here it gets specific.
- **1. Candidate pull (`tools/pull_assets.py`):** write `07-pull.tsv` (one row per beat that needs an image/clip: beat, kind `stock|stock-img|video|archive|intro`, source, query, opts; `n=3` per beat). `stock` beats return **video first** (Pexels/Pixabay); `INTRO1…` rows with kind `intro` search high-impact cold-open footage. Run `build_ai_prompts.py` first so the AI prompts show in the pass. `python tools/pull_assets.py E0XX-slug` hits the free APIs (Met, Wikimedia Commons, AIC, Pexels, Pixabay, Unsplash, Openverse) → **`07-style-pass.md`** (git record) + **`07-style-pass.html`**.
- **2. Style pass (Usuario 001, manual) — in `07-style-pass.html`:**
  - **Intro row (top):** the cold open (brain/02 §0). Up to 5 inputs for your own paths/links + the suggested `intro` clips + an "intro" checkbox on any card below. Export order = own (1–5) → suggested → cards.
  - **Left column:** the pulled candidates per beat. Judge each thumbnail on resolution (vs. the template standard) / condition / colour / crop / sequence coherence against the series look ([brain/03](03-brand-identity.md) §Visual identity); tick the keepers.
  - **Right column:** the `07b-ai-prompts.md` prompts. For a beat the pull didn't cover: copy the prompt, generate, paste the image path/URL into that prompt's input.
  - **Music section (bottom):** the pool from `tools/find_music.py` (ominous-ambient beds, CC-BY/BY-SA/CC0). Audition inline, tick the ones to keep — early on, all of them; the channel settles on 3–5 (`brain/16` move 4).
  - **Exportar 07-picks.txt** (saves into the episode folder) writes all of it. Then `python tools/pull_assets.py E0XX-slug --download` pulls into `assets/{intro,stock,video,archive}/`, copies AI images into `assets/ai/`, downloads ticked music into `brand/assets/music/` + `LICENSES.md`, verifies resolution, appends `assets/CREDITS.md`, writes **`07-selection.md`**, prints manifest rows. (No browser? tick `- [x]` in `07-style-pass.md` for beats; intro/AI/music need the picker.)
- **3. Own-graphics** beats → design brief, not the manifest.
- **4. AI-illustration** ([brain/15](15-ai-illustration-protocol.md)): for the beats left ❌ (no real image, no own-graphic), `tools/build_ai_prompts.py` → `07b-ai-prompts.md` *before* the pull. Pick the episode style (photoreal allowed); Claude writes the scenes; Usuario 001 generates and pastes paths in the picker. On-screen label always; never a photoreal face of a real person; never a fake document.
- **5. Manifest:** fold `07-selection.md` into `07-assets.md` — one row per **accepted** asset (intro / beat / AI), with the Uso + Pase columns filled by Usuario 001.
- **Gate:** every beat covered (accepted image / graphic / AI); cold open has 2–5 intro assets; every asset a clear licence + resolution for its use; colour/condition checked by sequence; AI images stylised, labelled, no real-person face; courtesy credits logged for `09-description.md`.
- Runs in parallel with Stage 8 (recording doesn't depend on it).

## Stage 8 — Record
- The episode's assigned narrator (Usuario 001 or Usuario 002) does VO + on-camera per shotlist. Clean audio pass.
- **Gate:** full take against locked script; pickups noted.

## Stage 9 — Edit  → `07c-edit.md`
- Protocol: [brain/16-edit-and-delivery.md](16-edit-and-delivery.md). Template: [templates/edit-checklist.md](../templates/edit-checklist.md). **Deliberately minimal**, in order:
  1. **Ken Burns clips** — `tools/kenburns.py --all` (Stage 7 stills + AI images → moving clips, move by orientation, 4K).
  2. **Trim** — `tools/trim_talk.py` (faster-whisper → cut silences + fillers, smooth) per Stage 8 take.
  3. **Review** — `tools/edit_review.py` → `07c-edit.html`: watch every KB clip + trimmed take, approve or leave feedback; **Exportar 07c-review.txt** → Claude re-runs the tools per the feedback → repeat until all **APROBADO**.
  4. **B-roll assembly** — only after step 3 is all-green. Lay each beat's asset on the VO per `06-shotlist.md` + `07-selection.md`. Cold open = 2–5 `assets/intro/` clips + bumper on black.
  5. **Background music** — one ominous-ambient bed from `brand/assets/music/`, ducked under the VO. No music in the bumper.
  6. **Subtitles** — `.srt` from the trimmed VO, hand-corrected against `05-script.md`.
- Assembly (4–5) with Claude + ffmpeg for now; **DaVinci Resolve MCP** an option later if that's too fiddly.
- **4K** output; a shot that can't fill it drops to its best, timeline stays 4K. House grade from `brain/03` applied whole (dark/warm/desaturated + grain + vignette). **No source cards** — citations in the description. AI + reenactment labelled every appearance.
- Export −14 LUFS, `E0XX-<slug>-vN.mp4`.
- **Gate:** every KB clip + trimmed take APROBADO; only the listed moves; every beat covered; music ducked + licences logged; AI/reenactment labelled; `.srt` corrected; 4K (or best common); picture lock signed by **Usuario 002** in `07c-edit.md`.

## Stage 10 — Package  → `08-thumbnail-title.md`, `09-description.md`
- Templates: [templates/thumbnail-title-brief.md](../templates/thumbnail-title-brief.md), [templates/description-and-credits.md](../templates/description-and-credits.md).
- `python tools/package_review.py E0XX-slug --init` scaffolds `08` + `09` (pulls the 3 hook-titles from `idea-pool.md`). Fill them, then `python tools/package_review.py E0XX-slug` → **`10-package.html`**: Usuario 002 picks the title, picks the thumbnail variant, edits the description (Fuentes principales auto-built from `03-source-log.csv` Tier A/B), ticks the 3 approvals. Exports `10-package.txt` → folded into `08` + `09`.
- Description = 2–3 sentence summary + chapters + **Fuentes principales** + courtesy credits + soft CTA. No source cards on screen — this is where citations live.
- **Gate:** title/thumbnail honest to the content (no clickbait the body doesn't pay off); Usuario 002's 3 approvals in `10-package.txt`.

## Stage 11 — Publish  → `10-publish-checklist.md`
- Template: [templates/publish-checklist.md](../templates/publish-checklist.md).
- Final legal/separation tick by Usuario 001 + Usuario 002. Upload, subtitles, chapters, end screen, pinned comment (sources / any caveat). Schedule.

## Stage 12 — Retro  → `11-retro.md`
- Template: [templates/episode-retro.md](../templates/episode-retro.md).
- 48h + 30d: metrics, what worked, corrections issued, process fixes.
- Update [episodes/_STATUS.md](../episodes/_STATUS.md) and [brain/07-publishing-seo-metrics.md](07-publishing-seo-metrics.md) KPI log.

## Roles

- **Usuario 001 writes every script.** Also: T02 ideation, shotlist, edit, publishing, tech, `tools/`.
- **Usuario 002:** editorial lead, T01 ideation, research direction, fact-check sign-off (Layer 3), on-camera/narration (share).
- **Narrator** assigned per episode (Usuario 001 or Usuario 002) — usually follows the track owner; keep a rough balance.

| Stage | Lead | Support |
|-------|------|---------|
| 0 ideation | Track owner (Usuario 002 T01 / Usuario 001 T02) | the other |
| 1–3 research | Usuario 001 | Usuario 002 (direction) |
| 4 script | Usuario 001 | — |
| 5 fact-check | L1+L2 automated · L3 **Usuario 002** | Usuario 001 answers |
| 6 shotlist | Usuario 001 | Usuario 002 |
| 7 asset selection + style pass | Usuario 001 | — |
| 8 record | Narrator (Usuario 001 or Usuario 002) | the other |
| 9 edit | Usuario 001 | Usuario 002 reviews |
| 10 package | Usuario 001 | Usuario 002 approves title/thumb |
| 11 publish | Usuario 001 | Usuario 002 co-signs |
| 12 retro | Both | — |

## Definition of Done

Published + subtitles live + sources in description + pinned comment + `_STATUS.md` updated + retro scheduled.
