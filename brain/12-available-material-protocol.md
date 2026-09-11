---
doc: 12-available-material-protocol
summary: "Never write for a story you can't illustrate. Public-domain archives list, a fair-use tier for rights-managed subjects with no PD alternative (digital-era figures AND 20th-century company histories), recreation/illustration as a first-class way to carry a material-poor episode, the Stage 7 pull rule (one row per beat, never 'sin fila', empty-after-refinement escalates to a recreation), a citation tier for copyrighted film/TV, the per-idea worksheet, stock rules, music licensing, subject-with-no-photograph."
stage: [0, 2, 7]
read_when: "judging an idea's feasibility; planning assets; licensing music; a subject with no surviving likeness"
pairs_with: [06-production-workflow, 15-ai-illustration-protocol, 03-brand-identity]
tools: [pull_assets.py, find_music.py]
authority: canonical
---

# 12 — Available-Material Protocol (Protocol 1)

Runs **during ideation**, before an idea can be approved. Purpose: never write a script for a story we can't illustrate. "Available" means **public domain**, **our own graphics**, or **a deliberate recreation / illustration plan** ([15-ai-illustration-protocol.md](15-ai-illustration-protocol.md)) — no paid archives for now.

## The rule

An idea is not approved until someone has confirmed there is a workable way to carry the **whole** episode visually: enough **public-domain** material, an **own-graphics** plan, a deliberate **recreation / illustration** register ([15](15-ai-illustration-protocol.md)), the fair-use tier below, or any mix of them. What fails the gate is a stretch of the likely spine with **no plan at all** behind it — not "the real photos are under copyright", which the recreation register now covers.

## Protocol 1b — fair use where the only images are rights-managed (no PD alternative)

PD-first stays the default whenever it's available — most subjects have it. This tier is for the case PD genuinely can't cover: **the images exist but every one of them is under someone's copyright by default.** Two shapes of that:

- **1b-i — digital-era living figure / active company** (Anthropic, OpenAI, Musk): every likeness is a rights-managed press photo, an official corporate image, or a broadcast clip.
- **1b-ii — 20th-century company / institution history** (Toyota/Ohno, LEGO, Nintendo pre-console, Adidas vs Puma): the founder, the factory, the early product were photographed, but the images sit in a corporate archive or a press agency (Getty, AP, Kyodo…) and aren't public domain **yet**. Check PD-by-age **first, per jurisdiction** — it varies a lot (Japan: photographs published before 1957 are PD; US: works published before 1930, and many 1930–1963 works whose copyright was never renewed; UK: 70 years). A real archive check often turns up more PD than expected. What's left after that check is 1b.

What most creators do informally (grab a press photo, drop it in), the channel does deliberately, with rules:

- **Allowed:** brief, transformative use of copyrighted press photography, official corporate images, and video clips (interviews, testimony, press conferences) — for identification and commentary, never as a substitute for the whole visual track. Fits squarely in fair-use commentary/news-reporting doctrine (US); the practical risk on YouTube is a Content ID flag, not a legal claim — expect the odd flag, dispute it if it's clearly fair use.
- **Preference order:** (1) the subject's **own published material** — for a living company: press kit, blog images, social posts; **for a company history: the company's own anniversary/heritage book, museum, and press-room archive** — they publish those images precisely so the story gets retold (least risk, least ambiguity); (2) our own screen recordings of a publicly accessible product/website — that's our footage, not reuse of anyone else's; (3) brief press photography/video under fair use; (4) motion graphics / own illustration / light 2.5D on the few stills that exist — the fallback that's always available.
- **Context and contrast are often PD even when the subject isn't:** the competitor's mass-production line, the era, the place, government-documented events around the story. Illustrate the *contrast* from PD; reserve fair use for what's specifically about the subject.
- **Fair use does not fix volume.** Rights-managed stills held under fair use count toward the **~30% "unlicensed images" ceiling** in the Minimum bar below — past that it's substitution, not commentary, and it draws a stream of Content ID claims that demonetise the video (which also kills any `brain/18` CPM case for it). Score **P7 low** for these subjects and lean the plan on own graphics + the company's own published imagery.
- **Always transformative:** graded into the house look, cut into the case-file device, cropped/motion-treated — never a raw, unedited slideshow of someone else's photos carrying a beat on its own.
- **Still absolute, no exception:** never reproduce anything that could pass as a fabricated document or record; never a photoreal AI-generated stand-in for a real identifiable person (`brain/15` governs AI illustration regardless of this tier).
- **Video specifically:** government-produced recordings (a federal photographer, an official congressional feed) are often PD outright — check per clip; a private broadcaster's feed of the same event usually isn't PD but is squarely fair-use territory for brief, commentated excerpts.
- **Log it like anything else:** the worksheet below still gets filled — mark `Rights` as `fair use — breve/transformador` instead of PD/CC, one line on the rationale (commentary / news reporting on a public figure or a documented company history) in `07-selection.md` / `CREDITS.md`, same as any other asset.

## Protocol 1c — citation tier for copyrighted film / TV

> **The Ensayo track ([brain/20](20-experimental-clip-protocol.md)) is the home for
> this now.** §1c stays here as the narrow exception for a **Documental** beat that
> genuinely comments on a specific work (Ensayo Mode B is the same shape). Full
> workflow — footage doctrine, budgets, discovery, treatment — is `brain/20` §4;
> the §1c fold into a pointer is still pending (`brain/20` §6).

For the case a beat is **commentary on a specific film, series, or scene itself** — we are analysing that work, not borrowing its footage to illustrate an unrelated story. Using a *Wall Street* clip to dress a real fraud we're narrating is pure illustrative use: weakest fair-use footing and a near-certain Content ID claim. Don't. This tier is only for "here is the scene we're actually talking about".

**PD-first still applies.** Films with lapsed or non-renewed copyright (large corpus on Internet Archive / archive.org — pre-1929 outright, plus much of pre-1964 US film that was never renewed) carry **no claim at all** and can be used like any archival source. Check copyright status per title before reaching for anything under studio rights.

When the work genuinely is under copyright:

- **Allowed:** brief excerpts of a copyrighted film/series **for criticism and commentary on that work** — US fair-use criticism/commentary doctrine, the strongest category there is. Never as a substitute for our own visual track.
- **Brief means brief:** a few seconds per clip; as a rule no single excerpt over ~10s and no episode more than ~60s of copyrighted film footage in total. If the edit needs more than that, the beat is leaning on someone else's work — rebuild it.
- **Never load-bearing:** a copyrighted clip never carries a beat on its own. Narration runs over it, original audio ducked hard or replaced, cut into the case-file device, graded into the house look. A raw, unedited excerpt playing clean is out — same transformation bar as 1b.
- **Monetisation is not assumed on that episode.** Expect a Content ID claim on any recognisable studio clip; the realistic outcome is revenue on that video redirected to the claimant, not a strike. Dispute where the commentary case is clear. Any episode using this tier is flagged in `01-brief.md` and scored assuming **its AdSense may be zero** — see [brain/18](18-monetization-and-audience.md). If the case only works financially with AdSense, don't build it on studio clips.
- **Discovery ≠ rights.** clip.cafe (paid API), PlayPhrase, YARN, OpenSubtitles etc. are research tools for *finding* a scene or line — they grant no licence and are never wired into `pull_assets.py` as an asset source the way stock is. What we publish is our own excerpt of a work we can point to, logged below.
- **Still absolute, no exception:** never anything that could pass as a fabricated document or record; never a photoreal AI stand-in for a real identifiable person (`brain/15` governs regardless).
- **Log it like anything else:** worksheet row filled, `Rights` marked `cita — crítica/comentario (fair use)`, with the title, distributor, and scene identified; one line on the rationale (commentary/criticism on that specific work) in `07-assets.md` / `CREDITS.md`.

**Sign-off:** because this tier trades away an episode's ad revenue, **both** Usuario 001 and Usuario 002 tick it — recorded in the idea-pool row and `01-brief.md`, same as the other protocols.

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
- **A track you found yourself** goes in via the *«Recursos propios»* rows of the Music section of `07-style-pass.html` — path/URL + `título · autor` + licence (`CC0` / `CC-BY` / `CC-BY-SA` only). `--download` refuses anything else. Same standard as the Jamendo pool: exact licence + attribution logged in `brand/assets/music/LICENSES.md`, credited in the description.
- Every track: exact licence + attribution in `brand/assets/music/LICENSES.md` and the video description.

**Our own**
- Charts, timelines, diagrams, animated maps, text cards — always available; cite the underlying data source in `03-source-log.csv`.

**Recreation / AI illustration** — where real material is missing, too scarce, or entirely rights-locked; may carry a large share of a material-poor episode, always labelled, one style. See [15-ai-illustration-protocol.md](15-ai-illustration-protocol.md).

## Worksheet (fill per idea — goes in `idea-pool.md` notes + the brief)

| Need | Found? | Archive + item ref | Rights | If not found |
|------|--------|--------------------|--------|--------------|
| Portrait(s) of key figure(s) | | | PD / CC0 / CC-__ | own illustration? public statue/plaque photo? |
| Period photos of place / event | | | | own map/graphic |
| Documents (filings, letters, records, headlines) | | | | — usually PD if old / government |
| Moving image of the era | | | | stills + motion graphics |
| Data for any chart | | | | own graphic, cite source |

**Minimum bar:** every load-bearing beat of the likely narrative has something planned that covers it — a real PD visual, an own-made graphic, or a recreation / illustration shot. The idea fails E8 only when a stretch of the spine has **no plan**, or when it would lean past ~30% on **not-cleared** images (unlicensed **or** held under Protocol 1b fair use). That ~30% ceiling is about *someone else's* copyrighted stills; our own labelled recreations and illustrations do **not** count toward it (they carry their own honesty cost — the label — not a rights cost).

## Practical consequences (this shapes what we can make now)

- **Favours:** pre-~1930 subjects (photos frequently PD by age), government-documented cases, historical corporate/engineering cases, anything with court records or archives.
- **Rights-heavier — leans on Protocol 1b + own graphics + the recreation register, score P7 low:** recent events and living people whose only images are rights-managed (1b-i); **mid-20th-century company histories** whose imagery sits in a corporate/agency archive and isn't PD yet (1b-ii — Toyota, LEGO, Nintendo pre-console, Adidas/Puma); anything needing modern broadcast footage. **Still very makeable** — the recreation / illustration register (`brain/15`) exists for exactly this. P7 scores the *rights friction*, not the feasibility; a strong recreation plan can carry these.

## Subject with no photograph (pre-photography or no likeness survives)

Common (Semmelweis, Hokusai, Tulipmania, Radium-era…). Layered approach, most honest first:

1. **Contemporary depictions** — portraits, engravings, busts, plaques made in the subject's lifetime or soon after. Usually few (2–4) → reuse deliberately as a motif.
2. **How they were shown by others / showed themselves** — self-portraits, caricatures, courtroom sketches, a figure in their own work. Primary-source, on-brand.
3. **The act, in close-up (reconstruction)** — hands, tools, the object being made/used. Shows the person working without needing a face. Low risk.
4. **Light 2.5D parallax** on portrait stills (layer separation, subtle motion, no face manipulation). Gives life without crossing into reenactment.
5. **A recurring stylised illustration** of the subject for journey / timeline / abstract sequences — clearly an illustration, labelled once. Needs an illustrator.

**A recurring recreation / illustration register *can* be a primary device** when the subject's real imagery is genuinely scarce or rights-locked (mid-20th-century company histories, pre-1960 non-Western subjects) — decided at Stage 0/2, written into the brief, one style, labelled every appearance ([15](15-ai-illustration-protocol.md)). The one thing that stays out even then: a photoreal AI **face of an identifiable real person** offered as their actual likeness (`brain/15` rule 3) — use a real portrait, a clearly non-photoreal impression, or frame away from the face.

## Stage 7 pull — no beat left uncovered

`07-pull.tsv` gets **one row per shotlist beat** whose `tipo` is `archivo`/`stock`/`kb` — no exceptions, cold-open hook beats included (they're ordinary beats in the pull, not a separate intro pool). `ia`/`gráfico`/`acamara`/`negro` beats are covered another way and don't go here. A beat sitting at "sin fila" in `07-style-pass.html` means exactly one thing: **nobody wrote a row for it yet** — never that something is already assigned.

If a row comes back with 0 candidates, or only weak ones: refine the query (broader terms, drop a `must=`/`min=` filter, try a different source) and re-run **just that row** — `python tools/pull_assets.py <slug> --beats 5,12` — instead of the whole spec (it merges with the last run; other beats' results are untouched). If a beat is still empty after ~2 rounds of refinement, the answer isn't to leave it blank or force a bad fit: **it becomes a recreation** — set its `tipo` to `ia` in `06-shotlist.md`, add a prompt block to `07b-ai-prompts.md` ([brain/15](15-ai-illustration-protocol.md)), and delete its row here. This is the same recreation register the episode may already be leaning on (§ above) — a hard-to-find beat is just one more instance of "real material doesn't exist for this," not a special case.

## Sign-off

Whoever proposed the idea ticks the worksheet. Recorded in the idea-pool row and carried into `01-brief.md`. Re-checked at Stage 2 (research dossier) when the exact beats are known — `06-shotlist.md` then resolves each beat to a specific item.

## Per-episode artifacts

- `material-search.md` — this protocol's output at ideation / Stage 2. **Feasibility, not selection:** does enough PD material exist, what's weak, the video question, how to depict a subject with no photograph.
- `07-assets.md` / `07b-ai-prompts.md` — Stage 7 selection + AI prompts. See [06-production-workflow.md](06-production-workflow.md) Stage 7.
