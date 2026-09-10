---
doc: 15-ai-illustration-protocol
summary: "Recreation / AI imagery where real material is missing, scarce, or rights-locked — may carry most of a material-poor episode. One style per episode, on-screen label every time, never a photoreal real-person face, never a fabricated document."
stage: [7]
read_when: "a shotlist beat has no real image and no own-graphic; writing AI prompts"
pairs_with: [12-available-material-protocol, 04-legal-and-ethics, 03-brand-identity]
tools: [build_ai_prompts.py, pull_assets.py]
authority: canonical
---

# 15 — AI Illustration Protocol

Runs **inside Stage 7** ([06-production-workflow.md](06-production-workflow.md)), whenever the style pass concludes a beat has **no viable public-domain image and no own-graphic plan** — because none was ever made, or because every surviving image is rights-locked. It produces a copy-paste prompt document so Usuario 001 can generate the images and drop them back in. "AI illustration" here covers both AI-generated and hand-commissioned recreation / illustration — the rules below apply to both; the AI ones additionally follow the prompt-document workflow.

## When it triggers

At Stage 7, after the style pass, some `07-assets.md` rows are ❌ (no PD source, e.g. an event with no contemporary depiction, or a person with no usable likeness). If those beats also can't be an own-made graphic (chart / map / text card), they become **AI-illustration beats**.

**AI is not a shortcut past *sourcing*.** Every fact still needs its Tier A/B source, and a recreation of an undocumented moment must invent nothing the record doesn't support. But it **is** a legitimate way to carry the **visual** track when real footage is missing, too scarce, or entirely rights-locked: an event no one depicted, a place we can't photograph, an abstract idea, or a 20th-century company / institution history whose every photo sits behind copyright. A labelled recreation or illustration is the honest option in all of those — and for a genuinely material-poor subject it can be most of the episode.

## Hard rules

1. **One style per episode.** Decided at Stage 7, written into `07b-ai-prompts.md` as a single style block merged into every prompt, so the set reads as one system. It can be a period-illustration register (ukiyo-e for Hokusai, so the AI sits next to the real prints), a painterly look, or **photorealistic cinematic recreation** — whichever serves the story and matches the episode's real material and the channel look ([brain/03](03-brand-identity.md) §Visual identity). A **register**, never "in the style of [living artist/studio]".
2. **On-screen label, every appearance** — `Ilustración — Conquest` or `Recreación`, discreet but legible. **More important when photoreal**, not less. Same rule as reenactments / colourised visuals ([04-legal-and-ethics.md](04-legal-and-ethics.md) §8).
3. **Invents nothing that reads as fact.**
   - **Scenes, places, events, atmosphere, abstract shots:** allowed, photoreal or not, with the label.
   - **The photoreal face of an identifiable real person, as their likeness:** not allowed — pure invention of how someone looked, deepfake-adjacent. Use the figure from behind / in silhouette / at distance, a clearly non-photoreal impression labelled as such, or a real portrait (then it's not AI).
   - **Documents, records, newspapers, photographs-of-record:** never fabricated. A photoreal "1721 report page" is a forgery.
4. **Only where no *usable* real image exists** — none was made, or every one is rights-locked, or what survives is too thin to carry the beat — and an own-graphic (chart / map / card) doesn't fit. For a well-documented subject this still means real archival is the base and recreation is a few beats. For a **material-poor subject** (mid-20th-century company history, pre-1960 non-Western figure), the recreation / illustration register may carry the **majority** of the visual track — a deliberate choice made at Stage 0/2 and written into `01-brief.md`, never a drift discovered in the edit.

## How the count is set

The number of AI images = the count of shotlist beats flagged in `07-assets.md` as **no PD image + no own-graphic**. It comes from the locked script → shotlist → asset manifest, not from a wish for more visuals. Typical: 2–6 for a well-documented subject. For a material-poor subject it can be many times that, **by design** — the check then is *consistency and labelling* (one register, every shot marked), not the count. What still signals a real problem: AI standing in for something that **is** well documented — i.e. nobody did the archive search.

## The prompt document — `07b-ai-prompts.md`

Scaffolded by `tools/build_ai_prompts.py`, then the **episode style** and the scene text are written (by Usuario 001 or Claude). Template: [templates/ai-prompts.md](../templates/ai-prompts.md). It contains:

- **Header:** episode, output spec, save folder, naming convention.
- **The episode style block** — chosen for *this* episode (rule 1), 3–5 lines. Ties to the channel look ([brain/03](03-brand-identity.md) §Visual identity) and the episode's real archival material. Merged into every prompt below it.
- **Negative prompt** — shared. When the style is *not* photoreal, it excludes photoreal; when the style *is* photoreal, it still excludes text/watermark/faces-of-real-people and anything that would make it read as an actual archival photo.
- **One block per image:** an ID (`aiNN`), the shotlist beat(s), what it's for, the **full copy-paste prompt** (episode style already merged in), the negative prompt, and the exact **filename to save as**.

## Folder + naming

- Images go to **`episodes/E0XX-<slug>/assets/ai/`** (created by the script; gitignored — images stay local).
- Filename: **`E0XX_aiNN_<slug>.png`** — e.g. `E001_ai01_deathbed-room.png`. The `aiNN` and `<slug>` match the block in `07b-ai-prompts.md`, so when Usuario 001 saves a file with that name, it's unambiguous which prompt it answers.

## Round trip

1. Style pass flags the ❌ beats → `python tools/build_ai_prompts.py E0XX-<slug> <slug1> …` scaffolds `07b-ai-prompts.md` (**before `pull_assets.py`**, so the prompts render in the picker's right column).
2. Claude writes each scene (framing, what's depicted, face-avoidance).
3. In `07-style-pass.html`, Usuario 001 generates 3–4 variants per prompt, picks the best match for the set, pastes the path into that prompt's input.
4. **Finalizar Stage 7** → `pull_assets.py --download` copies each into `assets/ai/` as `E0XX_aiNN_<slug>`, prints the manifest row. Claude folds the rows into `07-assets.md` + notes the label in `09-description.md`.

## Gate (part of Stage 7)

- [ ] Every AI beat has a prompt block and a generated, named file in `assets/ai/`
- [ ] The set is stylistically consistent (one style block)
- [ ] No AI image shows a recognisable real-person face or a fabricated document
- [ ] Every AI image has an on-screen label planned in `06-shotlist.md`
- [ ] `07-assets.md` updated with the AI rows; credits noted
