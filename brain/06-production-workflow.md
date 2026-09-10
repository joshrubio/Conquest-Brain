---
doc: 06-production-workflow
summary: "The 12 gated stages, what each produces, the five review pages, per-stage roles, Definition of Done."
stage: all
read_when: "moving an episode between stages; unsure what a stage produces or what its gate is"
pairs_with: [00-project-charter, 14-fact-check-protocol, 12-available-material-protocol]
tools: [idea_review.py, research_review.py, pull_assets.py, edit_review.py, package_review.py]
authority: canonical
---

# 06 — Production Workflow

Pipeline for one episode. Stages are gated: do not start a stage until the previous gate is signed. Files live in `episodes/E0XX-<slug>/`, numbered to match the stages.

**The dashboard** ([brain/17](17-dashboard-and-advance.md)) — `dashboard.html` (from `tools/dash.py`) is one screen for every chapter; `tools/serve.py` + `tools/advance.py` close each gate with one click and regenerate it. **Review pages.** Six stages hand off to a generated dark-theme HTML instead of a markdown table — either user works in the browser and hits **Finalizar Stage N**: Stage 0 `ideas/idea-review.html` · Stage 2 `02-research.html` · Stage 4 `05-script.html` · Stage 7 `07-style-pass.html` · Stage 9 `07c-edit.html` · Stage 10 `10-package.html`. Most fold a small `.txt` of decisions back into the source doc (the server does the mechanical ones, Claude the rest). **Stage 4 is the exception** — its page is a direct editor, not a decisions form: the server writes what's in the editor straight into `05-script.md`, no folding step. The `.html` is regenerable (gitignored); the exported `.txt` is the tracked record. **Any gate can be signed by one person.**

## Stage 0 — Ideation
- Either founder proposes the idea and assigns a track — **Documental** or **Ensayo** ([ideas/tracks.md](../ideas/tracks.md)). Ideation is shared; the track (format + rights regime), not the proposer, sets the anatomy and montage rules. Both tracks are live; an Ensayo idea is scored and produced like any other.
- **Protocol 2 — Hook Naming** ([brain/13](13-hook-naming.md)): 3 hook-title variants, Dieck register. Tail = the track word.
- **Protocol 1 — Available material** ([brain/12](12-available-material-protocol.md)): Documental — cross-check the case against public-domain archives; fill the worksheet. Ensayo — the feasibility check of [brain/20](20-experimental-clip-protocol.md) §4.0 (lawful copy · ≥3 reading sources · clip budget). No material → no episode.
- Score with [ideas/idea-rubric.md](../ideas/idea-rubric.md): eliminatorios E1–E8 + /21.
- Record in [ideas/idea-pool.md](../ideas/idea-pool.md).
- **Review:** `python tools/idea_review.py` → `ideas/idea-review.html` — score each idea, pick the strongest hook-title, comment; exports `idea-review.txt` → folded back into `idea-pool.md`.
- **Gate:** track assigned; hook-title chosen; material cross-check passes (E8); all eliminatorios YES; score ≥ 14; signed off in `idea-pool.md`.

## Stage 1 — Brief  → `01-brief.md`
- Template: [templates/episode-brief.md](../templates/episode-brief.md).
- Working thesis, why now, structure in one sentence each, candidate close (form A/B/C), top 3 sources already found, risks.
- **Assign:** track, hook-title (from Stage 0), and **narrator**. Writer is always Usuario 001.
- **Gate:** worth the research time; narrator assigned.

## Stage 2 — Research dossier  → `02-research-dossier.md` + `03-source-log.csv`
- Template: [templates/research-dossier.md](../templates/research-dossier.md), [templates/source-log.csv](../templates/source-log.csv).
- Full timeline, key figures, every claim with source + tier, open questions, contested points, rights status of any visual. Claude drafts it from public sources (WebSearch/WebFetch); the reviewer checks it.
- **Review:** `python tools/research_review.py E0XX-slug` → **`02-research.html`** — dossier sections + the full source-log table (tier / rights / 2nd-source per row) + per-section OK box + notes. **Finalizar Stage 2** (writes `02-research.txt`) → folded back.
- **Gate:** every load-bearing claim has ≥1 Tier A/B source; contested points identified; no reliance on Tier C/D; `02-research.txt` signed (either user).

## Stage 3 — Outline  → `03-outline.md`
- Template: [templates/outline-template.md](../templates/outline-template.md). Beat sheet against [brain/02-content-format.md](02-content-format.md): cold open → context pivot → narrative acts (mark explainer interludes + foreshadowing promises/pays) → close.
- One row per beat: section, beat, ~duration, planned `[S..]` tag, craft note (HOOK / PROMISE n/N / PAY n/N / EXPLICADOR n). Foreshadowing + explainer registers as their own tables.
- Confirm the close form (A/B/C) and register(s) chosen in the brief still fit the material (`brain/09`).
- Claude drafts it from `02-research-dossier.md` + `01-brief.md`; queued automatically on entering the stage.
- **Gate:** every beat in order; HOOK paid in the close; all promises made **and** paid; structure holds without stretching facts; close honest to the case.

## Stage 4 — Script  → `05-script.md`
- Template: [templates/script-template.md](../templates/script-template.md). Craft: all of `documentación/modelo-narrativo/`; rules `brain/02`, `08`, `09`, `13`.
- Full narration + on-screen cues + inline source tags `[S12]` linking to the source log. Close: form (A/B/C) + register(s) per the brief (`brain/09`).
- **The script pass:** `python tools/script_review.py E0XX-slug` → **`05-script.html`** — the guion rendered as one continuous editable document: each beat is a text box you type into directly, with its cue/PROMISE/PAY/source stamps as pills right above it (click a cue pill for its explainer) and a "revisado" toggle. **Finalizar Stage 4** saves the edited script straight into `05-script.md` every time it's pressed; the gate to Stage 5 only firms once "aprobado" is ticked with a reviewer name.
- **Gate:** self-review complete; script pass done (aprobado + firmado); every `[S..]` resolves.

## Stage 5 — Fact-check  → `04-factcheck-auto.md`  *(fully automated, no human step)*
- Protocol: [brain/14-fact-check-protocol.md](14-fact-check-protocol.md).
  - **L1 deterministic:** `python tools/factcheck.py 05-script.md 03-source-log.csv` → must PASS.
  - **L2 agent edit-pass:** run [templates/fact-check-auto-prompt.md](../templates/fact-check-auto-prompt.md) → six analysis tables + exact corrections; the agent **applies the corrections to `05-script.md`** and writes the Changelog in `04-factcheck-auto.md`. Legal/ethics/COI items it can't resolve go to the "Para revisión humana" list → `10-publish-checklist.md`.
- **Gate:** L1 PASS + L2 Changelog written. No sign-off. (The legal/COI checklist is the one human tick, at Stage 11.)

## Stage 6 — Shotlist / B-roll  → `06-shotlist.md`
- Template: [templates/shotlist-broll.md](../templates/shotlist-broll.md). Method: [brain/11-visual-rhythm.md](11-visual-rhythm.md).
- **Inferred from the locked script** — one beat per subject change / `[EN PANTALLA]` / `[EXPLICADOR]` / `[PROMISE]`/`[PAY]`. Per beat: visual **need**, archival vs own-graphic, on-screen text, motion.
- **Gate:** every beat classified; every graphed number has a source label; beat count matches the target rhythm.

## Stage 7 — Asset selection + style pass  → `07-assets.md` (+ `07b-ai-prompts.md`)

**`07-style-pass.html` is the hub** — every asset decision (per beat, AI images, cold-open intro, music) is made in that one page and exported as `07-picks.txt`; `--download` turns picks into files + `07-selection.md`. Nothing enters the edit that didn't go through it. Detail: [brain/12](12-available-material-protocol.md), [brain/15](15-ai-illustration-protocol.md), `documentación/pipeline/5`.

1. **AI prompts first** (if needed) — `build_ai_prompts.py E0XX-slug <slug>…` for beats with no real image and no own-graphic, so they render in the pass ([brain/15](15-ai-illustration-protocol.md)).
2. **Pull** — write `07-pull.tsv` (one row per beat: kind `stock|stock-img|video|archive|intro`, query, `n=3`; `stock` = video-first; `INTRO1…` = cold-open footage). `python tools/pull_assets.py E0XX-slug` → `07-style-pass.md` (git record) + `.html`.
3. **Style pass** (Usuario 001, in the page) — intro row (5 own slots + suggested + card checkboxes), per-beat candidates judged on resolution / condition / colour / sequence fit vs. [brain/03](03-brand-identity.md), AI prompt paste-ins, music pool. **Finalizar Stage 7** (writes `07-picks.txt`).
4. **Download** — `pull_assets.py E0XX-slug --download` → `assets/{intro,stock,video,archive,ai}/` + music + `LICENSES.md`, verifies resolution, appends `CREDITS.md`, writes `07-selection.md`.
5. **Manifest** — fold `07-selection.md` into `07-assets.md` (one row per accepted asset).
- **Gate:** every beat covered; cold open 2–5 intro assets; every asset a clear licence + resolution for its use; AI stylised + labelled + no real-person face; credits logged for `09-description.md`.
- Runs in parallel with Stage 8.

## Stage 8 — Record
- The episode's assigned narrator (Usuario 001 or Usuario 002) does VO + on-camera per shotlist. Clean audio pass.
- **Gate:** full take against locked script; pickups noted.

## Stage 9 — Edit  → `07c-edit.md`
- Protocol: [brain/16-edit-and-delivery.md](16-edit-and-delivery.md). Template: [templates/edit-checklist.md](../templates/edit-checklist.md). **Deliberately minimal**, in order:
  1. **Ken Burns clips** — `tools/kenburns.py --all` (Stage 7 stills + AI images → moving clips, move by orientation, 4K).
  2. **Trim** — `tools/trim_talk.py` (faster-whisper → cut silences + fillers, smooth) per Stage 8 take.
  3. **Review** — `tools/edit_review.py` → `07c-edit.html`: watch every KB clip + trimmed take, approve or leave feedback; **Finalizar Stage 9** (writes `07c-review.txt`) → Claude re-runs the tools per the feedback → repeat until all **APROBADO**.
  4. **B-roll assembly** — only after step 3 is all-green. Lay each beat's asset on the VO per `06-shotlist.md` + `07-selection.md`. Cold open = 2–5 `assets/intro/` clips + bumper on black.
  5. **Background music** — one ominous-ambient bed from `brand/assets/music/`, ducked under the VO. No music in the bumper.
  6. **Subtitles** — `.srt` from the trimmed VO, hand-corrected against `05-script.md`.
- Assembly (4–5) with Claude + ffmpeg for now; **DaVinci Resolve MCP** an option later. Output 4K, house grade, −14 LUFS, `E0XX-<slug>-vN.mp4` — all per [brain/16](16-edit-and-delivery.md).
- **Gate:** every KB clip + trimmed take APROBADO; only the listed moves; every beat covered; music ducked + licences logged; AI/reenactment labelled; `.srt` corrected; 4K (or best common); picture lock signed in `07c-edit.md` (either user).

## Stage 10 — Package  → `08-thumbnail-title.md`, `09-description.md`
- Templates: [templates/thumbnail-title-brief.md](../templates/thumbnail-title-brief.md), [templates/description-and-credits.md](../templates/description-and-credits.md).
- `python tools/package_review.py E0XX-slug --init` scaffolds `08` + `09` (pulls the 3 hook-titles from `idea-pool.md`). Fill them, then `python tools/package_review.py E0XX-slug` → **`10-package.html`**: pick the title, pick the thumbnail variant, edit the description (Fuentes principales auto-built from `03-source-log.csv` Tier A/B), tick the 3 approvals. Exports `10-package.txt` → folded into `08` + `09`.
- Description = 2–3 sentence summary + chapters + **Fuentes principales** + courtesy credits + soft CTA. No source cards on screen — this is where citations live.
- **Gate:** title/thumbnail honest to the content (no clickbait the body doesn't pay off); the 3 approvals ticked in `10-package.txt`.

## Stage 11 — Publish  → `10-publish-checklist.md`
- Template: [templates/publish-checklist.md](../templates/publish-checklist.md).
- Final legal + independence/COI tick (either user). Upload, subtitles, chapters, end screen, pinned comment (sources / any caveat). Schedule.

## Stage 12 — Retro  → `11-retro.md`
- Template: [templates/episode-retro.md](../templates/episode-retro.md).
- 48h + 30d: metrics, what worked, corrections issued, process fixes.
- Update [episodes/_STATUS.md](../episodes/_STATUS.md) and [brain/07-publishing-seo-metrics.md](07-publishing-seo-metrics.md) KPI log.

## Roles

Slots and the responsibility split: [brain/00](00-project-charter.md) + [brain/USERS.md](USERS.md).

- **Stage 0 ideation** — shared; whoever proposes the idea leads, the other supports.
- **Stages 1–7, 9–10** — Usuario 001 leads; the picture-lock and package gates are review pages **either user can sign**.
- **Stage 8 record** — the assigned narrator.
- **Stage 11 publish, Stage 12 retro** — Usuario 001; the legal/COI tick can be either user.

## Definition of Done

Published + subtitles live + sources in description + pinned comment + `_STATUS.md` updated + retro scheduled.
