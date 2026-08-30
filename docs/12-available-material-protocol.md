# 12 — Available-Material Protocol (Protocol 1)

Runs **during ideation**, before an idea can be approved. Purpose: never write a script for a story we can't illustrate. "Available" means **public domain** (or our own graphics) — no paid archives for now.

## The rule

An idea is not approved until someone has confirmed, against real archive listings, that there is enough **public-domain** visual material — or a workable own-graphics plan — to carry the episode.

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
- All have free APIs → `tools/pull_assets.py` hits them at Stage 7 (see `docs/06` Stage 7), ~3 candidates/beat, and writes **`07-photography-pass.html`** — the central Stage-7 artifact (per-beat candidates + AI prompts + cold-open intro). Keys (Pexels, Pixabay, Unsplash) go in `tools/.env` (gitignored); Openverse / Met / Wikimedia Commons / AIC need no key.
- **Prefer video.** A `stock` beat searches Pexels/Pixabay **video first**; images only fill what video didn't. A usable clip found here is inserted directly in the edit instead of hand-building a b-roll move over a still.
- Archive sources: **Met**, **Wikimedia Commons** (often higher-res than Met, cleaner artist metadata), **AIC**. Known limits: **Pixabay** free API caps images at ~1280 px (inset only); **AIC** IIIF CDN can block `--download` from some networks (its page + Download button always works). Pexels/Unsplash/Met/Commons deliver full resolution.
- Stock is illustrative, not evidentiary — use it where a viewer reads it as a cutaway, not as "here is the real thing". If in doubt, a discreet label or an own-graphic is safer.
- Attribution: Pexels + Unsplash require crediting the platform and the author in `09-description.md`; `--download` logs every pulled item to `assets/CREDITS.md`.

**Audio / music** — a monetised video is **commercial** use + a sync/derivative. Usable: **CC0 / PD**, **CC-BY** (credit required), **CC-BY-SA** (credit + share-alike). **Not** anything with **NC** or **ND**.
- **YouTube Audio Library** (in Studio) and **Pixabay Music** — free, commercial-cleared, mostly no attribution. Browse-only, no API. Best for the channel's fixed 3–5 beds (`docs/16` move 4).
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

**Not as a primary device:** photoreal AI "bringing a portrait to life". Tone risk for a rigor channel, needs a prominent on-screen label ([04-legal-and-ethics.md](04-legal-and-ethics.md) §8), often uncanny. At most one deliberate moment, labelled.

Any AI-generated, AI-animated, or colourised visual carries an on-screen label — always.

## Sign-off

The idea's track owner (Carmen for T01, Josh for T02) ticks the worksheet. Recorded in the idea-pool row and carried into `01-brief.md`. Re-checked at Stage 2 (research dossier) when the exact beats are known — `06-shotlist.md` then resolves each beat to a specific item.

## Per-episode artifacts

- `material-search.md` — this protocol's output at ideation / Stage 2: does enough PD material exist, what's weak, the video question, how to depict a subject with no photograph, and any fact-check findings the search turned up. **Feasibility, not selection.**
- `07-assets.md` — **Stage 7**, after fact-check + shotlist. The per-image manifest: a direct download link per archival beat + Josh's **photography pass** (resolution / condition / colour / series fit). See [06-production-workflow.md](06-production-workflow.md) Stage 7 and [templates/asset-manifest.md](../templates/asset-manifest.md).
- `07b-ai-prompts.md` — **Stage 7**, only if the photography pass leaves beats with no PD image and no own-graphic. Copy-paste AI-illustration prompts. See [15-ai-illustration-protocol.md](15-ai-illustration-protocol.md).
