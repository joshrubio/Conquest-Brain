---
doc: 12-available-material-protocol
summary: "Never write for a story you can't illustrate. Public-domain archives list, a fair-use tier for contemporary figures with no PD alternative, the per-idea worksheet, stock rules, music licensing, subject-with-no-photograph."
stage: [0, 2, 7]
read_when: "judging an idea's feasibility; planning assets; licensing music; a subject with no surviving likeness"
pairs_with: [06-production-workflow, 15-ai-illustration-protocol, 03-brand-identity]
tools: [pull_assets.py, find_music.py]
authority: canonical
---

# 12 — Available-Material Protocol (Protocol 1)

Runs **during ideation**, before an idea can be approved. Purpose: never write a script for a story we can't illustrate. "Available" means **public domain** (or our own graphics) — no paid archives for now.

## The rule

An idea is not approved until someone has confirmed, against real archive listings, that there is enough **public-domain** visual material — or a workable own-graphics plan, or the fair-use tier below — to carry the episode.

## Protocol 1b — fair use for contemporary figures (no PD alternative exists)

PD-first stays the default whenever it's available — most subjects have it. This tier exists only for the case PD genuinely can't cover: a **living public figure or active company from roughly the digital era**, where every likeness is under someone's copyright by default. What most creators do informally (grab a press photo, drop it in), the channel does deliberately, with rules:

- **Allowed:** brief, transformative use of copyrighted press photography, official corporate images, and video clips (interviews, testimony, press conferences) — for identification and commentary, never as a substitute for the whole visual track. Fits squarely in fair-use commentary/news-reporting doctrine (US); the practical risk on YouTube is a Content ID flag, not a legal claim — expect the odd flag, dispute it if it's clearly fair use.
- **Preference order:** (1) the subject's own self-published material — official press kit, company blog images, their own social posts (least risk, least ambiguity); (2) our own screen recordings of a publicly accessible product/website — that's our footage, not reuse of anyone else's; (3) brief press photography/video under fair use; (4) motion graphics / own illustration as the fallback that's always available.
- **Always transformative:** graded into the house look, cut into the case-file device, cropped/motion-treated — never a raw, unedited slideshow of someone else's photos carrying a beat on its own.
- **Still absolute, no exception:** never reproduce anything that could pass as a fabricated document or record; never a photoreal AI-generated stand-in for a real identifiable person (`brain/15` governs AI illustration regardless of this tier).
- **Video specifically:** government-produced recordings (a federal photographer, an official congressional feed) are often PD outright — check per clip; a private broadcaster's feed of the same event usually isn't PD but is squarely fair-use territory for brief, commentated excerpts.
- **Log it like anything else:** the worksheet below still gets filled — mark `Rights` as `fair use — breve/transformador` instead of PD/CC, one line on the rationale (commentary/news reporting on a public figure) in `07-selection.md` / `CREDITS.md`, same as any other asset.

## Archives we check (public domain / open)

**Images, prints, documents**
- Wikimedia Commons (filter: PD / CC0)
- Library of Congress — Prints & Photographs, Chronicling America (newspapers)
- U.S. National Archives (NARA)
- The National Archives (UK); Imperial War Museum (non-commercial / PD items)
- Europeana (filter: "can use freely")
- NYPL Digital Collections (public-domain filter)
- Rijksmuseum, The Met Open Access, Getty Open Content, Smithsonian Open Access (CC0)
- Gallica (BnF), Deutsche Digitale Bibliothek
- Flickr Commons ("no known copyright restrictions")
- NASA, NOAA (PD by default)
- The Public Domain Review (curated leads)

**Moving image (archival)**
- Internet Archive (archive.org) — incl. Prelinger Archives (PD stock/ephemeral film)
- NARA motion pictures; Library of Congress film
- Wikimedia Commons video

**Free stock (generic illustrative b-roll only)** — a modern lab, hands typing, waves, a city at night: **not** the specific real place/event (that's archival). Free/CC0/permissive only, no paid stock:
- Images: Pexels, Pixabay, Unsplash, Openverse
- Video: Pexels Videos, Coverr, Mixkit
- All have free APIs → `tools/pull_assets.py` hits them at Stage 7 (`brain/06`), ~3 candidates/beat, into `07-style-pass.html`. Keys + per-source quirks (resolution caps, CDN blocks): `tools/README.md`.
- **Prefer video.** A `stock` beat searches Pexels/Pixabay **video first**; images fill what video didn't. A usable clip goes straight into the edit instead of a hand-built move over a still.
- Archive sources: **Met**, **Wikimedia Commons**.
- Stock is illustrative, not evidentiary — use it where a viewer reads it as a cutaway, not "here is the real thing". If in doubt, label it or use an own-graphic.
- Attribution: Pexels + Unsplash need platform + author credited in `09-description.md`; `--download` logs every item to `assets/CREDITS.md`.

**Audio / music** — a monetised video is **commercial** use + a sync/derivative. Usable: **CC0 / PD**, **CC-BY** (credit required), **CC-BY-SA** (credit + share-alike). **Not** anything with **NC** or **ND**.
- **YouTube Audio Library** (in Studio) and **Pixabay Music** — free, commercial-cleared, mostly no attribution. Browse-only, no API. Good for the channel's fixed 3–5 beds.
- Jamendo — per-track CC (many are BY-NC → unusable); `tools/find_music.py` filters to BY / BY-SA / CC0. Its paid "Jamendo Licensing" is **not** needed for CC-BY.
- Musopen (PD classical) · Free Music Archive / ccMixter — CC, log the exact licence.
- Every track: exact licence + attribution in `brand/assets/music/LICENSES.md` and the video description.

**Our own**
- Charts, timelines, diagrams, animated maps, text cards — always available; cite the underlying data source in `03-source-log.csv`.

**AI illustration** — only where nothing real exists; see [15-ai-illustration-protocol.md](15-ai-illustration-protocol.md).

## Worksheet (fill per idea — goes in `idea-pool.md` notes + the brief)

| Need | Found? | Archive + item ref | Rights | If not found |
|------|--------|--------------------|--------|--------------|
| Portrait(s) of key figure(s) | | | PD / CC0 / CC-__ | own illustration? public statue/plaque photo? |
| Period photos of place / event | | | | own map/graphic |
| Documents (filings, letters, records, headlines) | | | | — usually PD if old / government |
| Moving image of the era | | | | stills + motion graphics |
| Data for any chart | | | | own graphic, cite source |

**Minimum bar:** every load-bearing beat of the likely narrative has at least one real PD visual OR an own-made graphic that fully covers it. If more than ~30% of the episode would be "narrator over a black screen" or unlicensed images, the idea fails E8.

## Practical consequences (this shapes what we can make now)

- **Favours:** pre-~1930 subjects (photos frequently PD by age), government-documented cases, historical corporate/engineering cases, anything with court records or archives.
- **Harder right now:** recent events, living people whose only images are rights-managed, anything that needs modern broadcast footage. Possible, but leans heavily on own graphics — score P7 low.

## Subject with no photograph (pre-photography or no likeness survives)

Common for T01/T02 (Semmelweis, Hokusai, Tulipmania, Radium-era…). Layered approach, most honest first:

1. **Contemporary depictions** — portraits, engravings, busts, plaques made in the subject's lifetime or soon after. Usually few (2–4) → reuse deliberately as a motif.
2. **How they were shown by others / showed themselves** — self-portraits, caricatures, courtroom sketches, a figure in their own work. Primary-source, on-brand.
3. **The act, in close-up (reconstruction)** — hands, tools, the object being made/used. Shows the person working without needing a face. Low risk.
4. **Light 2.5D parallax** on portrait stills (layer separation, subtle motion, no face manipulation). Gives life without crossing into reenactment.
5. **A recurring stylised illustration** of the subject for journey / timeline / abstract sequences — clearly an illustration, labelled once. Needs an illustrator.

**Not as a primary device:** photoreal AI "bringing a portrait to life". At most one deliberate, labelled moment — full rules in [15-ai-illustration-protocol.md](15-ai-illustration-protocol.md).

## Sign-off

The idea's track owner (Usuario 002 for T01, Usuario 001 for T02) ticks the worksheet. Recorded in the idea-pool row and carried into `01-brief.md`. Re-checked at Stage 2 (research dossier) when the exact beats are known — `06-shotlist.md` then resolves each beat to a specific item.

## Per-episode artifacts

- `material-search.md` — this protocol's output at ideation / Stage 2. **Feasibility, not selection:** does enough PD material exist, what's weak, the video question, how to depict a subject with no photograph.
- `07-assets.md` / `07b-ai-prompts.md` — Stage 7 selection + AI prompts. See [06-production-workflow.md](06-production-workflow.md) Stage 7.
