---
doc: 07-publishing-seo-metrics
summary: "Cadence, title/thumbnail rules (pointers), description blocks, chapters, tags, KPIs + the KPI log."
stage: [10, 11, 12]
read_when: "packaging, publishing, or running a retro; setting cadence"
pairs_with: [13-hook-naming, 03-brand-identity, 06-production-workflow]
tools: [package_review.py]
authority: canonical
---

# 07 — Publishing, SEO & Metrics

## Cadence (proposed, not locked)

- **Launch cadence:** 1 episode / 3 weeks while the pipeline is new (research + fact-check are the bottleneck, not the edit).
- **Target once stable:** 1 episode / 2 weeks.
- Better to hold an episode than to ship one with an open fact-check.
- Lock the cadence after 3 published episodes, using the retro data.

## Titles & thumbnails

- **Title** — pattern, hook types, rules, A/B: [brain/13](13-hook-naming.md). 3 candidates per episode in `08-thumbnail-title.md` (from the Stage 0 hook-titles); pick with Usuario 002. Honest to the body; ≤ ~70 chars.
- **Thumbnail** — one system: [brain/03](03-brand-identity.md) §Thumbnail system. ≤ 4 words, readable at 320px, no arrows/shock-faces/red-circles. Title and thumbnail don't repeat the same words.

## Description — required blocks

Template: [templates/description-and-credits.md](../templates/description-and-credits.md).

1. 2–3 sentence summary.
2. **Fuentes principales** — bulleted, from `03-source-log.csv` (Tier A/B). Always present. **All citations live here** — no source cards on screen.
3. Chapters (timestamps) — map to the format: Hook / Narrative acts / Reflexión / Para llevar. Helps per-section retention analysis.
4. Soft channel CTA. **No third-party link or pitch.**
5. Credits (music licence, archival, research).
6. Correction log line if any.

## Tags & metadata

- Spanish keywords tied to the subject and to "historia", "caso real", "documental".
- Category: **Education** (`brain/03`).
- Language: Spanish. Add auto-translate titles only if quality is acceptable.

## Subtitles

- Spanish .srt, hand-corrected, every episode. Non-negotiable for accessibility and retention.

## KPIs (log in table below after each retro)

| Metric | Why | Early read |
|--------|-----|--------------|
| Avg. view duration % | Format/pacing health | > 45% good for 15–25 min |
| Retention at "Reflexión" marker | Does the audience stay for the payoff | Watch for cliff |
| Retention at "Para llevar" marker | Is the takeaway landing | — |
| CTR | Title/thumbnail honesty + pull | 4–8% typical |
| Returning viewers | Series stickiness | Trend up |
| Comments quality | Are we provoking thought vs. outrage | Qualitative |
| Subscribers / 1k views | Audience-building efficiency | Trend up |

Vanity views alone are not the goal — audience that returns is.

## KPI log

| Episode | Pub date | Length | Views 30d | AVD % | CTR % | Subs gained | Notes |
|---------|----------|--------|-----------|-------|-------|-------------|-------|
| E000 EXAMPLE | — | — | — | — | — | — | reference only |

## Publishing checklist

See [templates/publish-checklist.md](../templates/publish-checklist.md) — copied into each episode folder as `10-publish-checklist.md`.
