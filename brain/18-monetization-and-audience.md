---
doc: 18-monetization-and-audience
summary: "CPM/RPM signal by content category and audience geography — a non-blocking tiebreaker at ideation, never a reason to bend E6/E7 or the charter."
stage: [0]
read_when: "proposing or scoring an idea in Stage 0; picking a track/angle when two ideas tie on the rubric"
pairs_with: [00-project-charter, "../ideas/idea-rubric.md", "../ideas/tracks.md", 13-hook-naming]
authority: canonical
---

# 18 — Monetization & Audience Signal

A second, **non-blocking** lens on ideation: given the channel is Spanish-language,
which category and which likely audience geography an idea leans toward changes
its YouTube RPM by an order of magnitude. This doc turns that into two small tags
per idea — nothing here overrides `brain/00`'s non-negotiables or the rubric's
eliminatorios. If a stronger-RPM angle would mean bending a fact or forcing a
moral (E7), the honest version wins, full stop.

## Why this exists

Spanish is a huge-reach, low-average-CPM language: most Spanish-language YouTube
views come from Latin America, where CPM runs **$0.5–2**. But two slices of the
same language pay far more: **Spain** (~$14 CPM / ~$4 RPM) and **US Hispanics**
watching Spanish-language content from inside the US ad market (blended
**$3–6 RPM**, 2–3× the LATAM average, because US advertisers bid through
Spanish-language inventory to reach them). Category matters just as much as
geography: a "pure" history/biography documentary tops out around $4–8 CPM,
while the same documentary craft applied to a fraud, a criminal cover-up, or a
business/money story runs $12–25+ CPM.

*(Figures are third-party estimates, drift constantly, and are never official
YouTube numbers — see Sources. Once the channel has real AdSense data, prefer
Analytics' own RPM by country/video over this table. Re-check every ~6 episodes.)*

## Audience tiers (Spanish-language)

| Tier | Geography | Approx. RPM | Note |
|------|-----------|-------------|------|
| **1** | Spain · US Hispanics (viewed from inside the US) | $3–6+ | the two pockets of real value in the language |
| **2** | Rest of Spanish-speaking Europe (negligible volume) | — | not a targeting lever, too small |
| **3** | Rest of Latin America (Mexico, Argentina, Colombia, …) | $0.5–2 | most of the reach, least of the pay |

**What skews a video toward Tier 1 without changing the format:** subjects with
international name-recognition (global brands, US/European historical figures,
cases that made international news) surface more to Spain/US-Hispanic feeds than
hyper-local stories. This is a *distribution* lever, not a license to invent
international relevance a case doesn't have.

## Category tiers (documentary/narrated content)

| Tier | Category archetype | Approx. CPM | Typical Conquest fit |
|------|--------------------|-------------|----------------------|
| **A — alta** | Fraud / financial crime · business & money · true-crime-adjacent institutional failure | $12–25+ | cases with a financial-fraud or criminal core (Talidomida, manías especulativas, empresas que mintieron) |
| **B — media** | Education / science explainer · engineering failure with casualties · legal/regulatory | $6–12 | disasters, cover-ups, regulation stories; companies where the money angle carries the episode; most **Ensayo** obra-como-suceso ideas (a ban, a lawsuit, an industry shift) |
| **C — baja** | "Pure" history, art, or personal biography with no crime/money/institutional-failure spine | $3–8 | biographies like Hokusai; most **Ensayo** obra-como-sujeto ideas (film/work criticism) — strong fit, weaker CPM |

The tier is **orthogonal to the track** — a Documental and an Ensayo can each be
A, B or C. A case doesn't have to be re-angled to move tiers — most fraud / mania /
institutional-failure material is naturally Tier A/B already, and most
company / money / founder material sits A/B too. The tier mainly flags the
minority of ideas — usually pure-arts/pure-history biographies and film-criticism
essays — that are editorially strong but structurally low-CPM, so that's known
going in, not discovered after Stage 9.

**Ensayo episodes that use copyrighted clips** carry an extra RPM haircut: Content
ID claims redirect ad revenue on the clip-bearing portions. Score them assuming
that haircut (detail: [20-experimental-clip-protocol.md](20-experimental-clip-protocol.md) §5) —
softened, not erased, by the channel already targeting Tier-1 geography.

## How it's used

At Stage 0, each idea in `ideas/idea-pool.md` carries two tags (see
`idea-rubric.md` §Monetización): **Categoría CPM** (A/B/C, from the table above)
and **Audiencia esperada** (Tier 1 / mixta / Tier 3, from the geography table).
`tools/idea_review.py` shows both as badges on the review page.

These tags are **informational, not scored** — they don't touch the eliminatorios
or the /21. They matter only as a **tiebreaker**: when two ideas score within a
point of each other, or when picking which of several "incubando" ideas to
promote next, prefer the higher tier. They never justify:
- inventing or exaggerating a financial/criminal angle a case doesn't have (E7),
- picking a subject outside the charter's public-figure / public-record rule (E1–E2) to chase reach,
- skewing a hook-title dishonestly toward international relevance (`brain/13`).

## Sources (2026, third-party estimates — re-check periodically)

- [FluxNote — YouTube CPM Latin America by country](https://fluxnote.io/guides/youtube-cpm-latin-america-by-country)
- [Lenos — YouTube CPM & RPM rates by country and niche](https://www.lenostube.com/en/youtube-cpm-rpm-rates/)
- [OutlierKit — Most profitable YouTube niches (RPM data)](https://outlierkit.com/blog/most-profitable-youtube-niches)
- [MilX — Countries with the highest YouTube CPM](https://milx.app/en/cases/in-what-countries-cpm-are-the-highest)
- [Marketing Charts — Advertisers follow Hispanic audiences to YouTube](https://www.marketingcharts.com/television-236900)
