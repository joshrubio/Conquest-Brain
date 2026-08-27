# 06 — Production Workflow (Phase 1)

Pipeline for one episode. Stages are gated: do not start a stage until the previous gate is signed. Files live in `episodes/E0XX-<slug>/`, numbered to match the stages.

## Stage 0 — Idea intake
- Add to [ideas/backlog.md](../ideas/backlog.md).
- Score with [ideas/evaluation-rubric.md](../ideas/evaluation-rubric.md).
- **Gate:** passes rubric (public record + sources exist + genuine human/psych angle + honest applied takeaway + clears separation policy).

## Stage 1 — Brief  → `01-brief.md`
- Template: [templates/episode-brief.md](../templates/episode-brief.md).
- Working thesis, why now, the three parts in one sentence each, candidate takeaway, top 3 sources already found, risks.
- **Assign:** which approved theme this belongs to, script writer, and **narrator (Carmen or Josh)**.
- **Gate:** Carmen + Josh agree it's worth the research time; theme is approved; narrator assigned.

## Stage 2 — Research dossier  → `02-research-dossier.md` + `03-source-log.csv`
- Template: [templates/research-dossier.md](../templates/research-dossier.md), [templates/source-log.csv](../templates/source-log.csv).
- Full timeline, key figures, every claim with source + tier, open questions, contested points, rights status of any visual.
- **Gate:** every load-bearing claim has ≥1 Tier A/B source; contested points identified; no reliance on Tier C/D.

## Stage 3 — Outline
- Beat sheet against [docs/02-content-format.md](02-content-format.md): hook, narrative acts, reflection, takeaway.
- **Gate:** structure holds without stretching facts; takeaway follows from the case.

## Stage 4 — Script  → `05-script.md`
- Template: [templates/script-template.md](../templates/script-template.md).
- Full narration + on-screen cues + inline source tags `[S12]` linking to the source log.
- **Gate:** self-review complete; every `[S..]` resolves.

## Stage 5 — Fact-check  → `04-fact-check.md`
- Template: [templates/fact-check-sheet.md](../templates/fact-check-sheet.md).
- Done by the person who did **not** write the script. Claim-by-claim: source, tier, verdict (verified / needs work / cut).
- Legal & ethics pass: [docs/04-legal-and-ethics.md](04-legal-and-ethics.md).
- **Gate:** zero unresolved claims; legal checklist clear; sheet signed.

## Stage 6 — Shotlist / B-roll  → `06-shotlist.md`
- Template: [templates/shotlist-broll.md](../templates/shotlist-broll.md).
- Per beat: visual needed, source/rights, on-screen text, caption.
- **Gate:** every visual has a rights status.

## Stage 7 — Record
- The episode's assigned narrator (Carmen or Josh) does VO + on-camera per shotlist. Clean audio pass.
- **Gate:** full take against locked script; pickups noted.

## Stage 8 — Edit
- Assembly → picture lock → sound → captions/lower-thirds → source cards.
- Spanish subtitles (.srt) generated and corrected.
- **Gate:** picture lock reviewed by both; captions accurate.

## Stage 9 — Package  → `07-thumbnail-title.md`, `08-description.md`
- Templates: [templates/thumbnail-title-brief.md](../templates/thumbnail-title-brief.md), [templates/description-and-credits.md](../templates/description-and-credits.md).
- 3 title options, thumbnail, description with **Fuentes principales** block, chapters, tags.
- **Gate:** title/thumbnail honest to the content (no clickbait the body doesn't pay off).

## Stage 10 — Publish  → `09-publish-checklist.md`
- Template: [templates/publish-checklist.md](../templates/publish-checklist.md).
- Final legal/separation tick by Carmen + Josh. Upload, subtitles, chapters, end screen, pinned comment (sources / any caveat). Schedule.

## Stage 11 — Retro  → `10-retro.md`
- Template: [templates/episode-retro.md](../templates/episode-retro.md).
- 48h + 30d: metrics, what worked, corrections issued, process fixes.
- Update [episodes/_STATUS.md](../episodes/_STATUS.md) and [docs/07-publishing-seo-metrics.md](07-publishing-seo-metrics.md) KPI log.

## Roles per stage

`Writer` and `Narrator` are assigned per episode at Stage 1 and can be either Carmen or Josh (they need not be the same person). The fact-checker is always **the one who did not write** that script.

| Stage | Lead | Support |
|-------|------|---------|
| 0–3 research | Writer (Carmen or Josh) | the other |
| 4 script | Writer | the other |
| 5 fact-check | Non-writer | Writer answers |
| 6 shotlist | Josh | Carmen |
| 7 record | Narrator (Carmen or Josh) | the other |
| 8 edit | Josh | other reviews |
| 9 package | Josh | Writer approves title/thumb |
| 10 publish | Josh | Carmen + Josh co-sign |
| 11 retro | Both | — |

Keep a rough balance of narrator assignments across episodes unless a specific story clearly fits one voice.

## Definition of Done

Published + subtitles live + sources in description + pinned comment + `_STATUS.md` updated + retro scheduled.
