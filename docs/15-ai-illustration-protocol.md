# 15 — AI Illustration Protocol

Runs **inside Stage 7** ([06-production-workflow.md](06-production-workflow.md)), only when the photography pass concludes a beat has **no viable public-domain image and no own-graphic plan**. It produces a copy-paste prompt document so Josh can generate the images and drop them back in.

## When it triggers

At Stage 7, after the photography pass, some `07-assets.md` rows are ❌ (no PD source, e.g. an event with no contemporary depiction, or a person with no usable likeness). If those beats also can't be an own-made graphic (chart / map / text card), they become **AI-illustration beats**.

**AI is not a shortcut past sourcing.** It is only for beats where *nothing real exists* — an event no one depicted, a place we can't photograph, an abstract idea — and a drawn or recreated shot (labelled) is the honest option anyway.

## Hard rules

1. **Style is chosen per episode** — decided at Stage 7, written into `07b-ai-prompts.md`, and **consistent within the episode** (one style block, every image). It can be a period-illustration register (e.g. ukiyo-e for Hokusai, so the AI sits next to the real prints), a painterly look, or a **photorealistic cinematic recreation**. Pick the one that serves the story and matches the episode's real material and the channel look ([docs/03](03-brand-identity.md) §Visual direction).
2. **On-screen label, every time it appears** — `Ilustración — Éxodo` or `Recreación`, discreet but legible. **More important when the style is photoreal**, not less — the viewer must never mistake it for archival footage or a real photograph. Same rule as reenactments / colourised visuals ([04-legal-and-ethics.md](04-legal-and-ethics.md) §8).
3. **Invents nothing that reads as fact.**
   - **Scenes, places, events, atmosphere, abstract/metaphor shots:** allowed, photoreal or not, with the label.
   - **The face of an identifiable real person, rendered photoreal and presented as their likeness:** not allowed. There is no photo, so it is pure invention of how someone looked — deepfake-adjacent, and corrosive for a channel whose value is verified fact. Use: the figure from behind / in silhouette / at distance, OR a clearly non-photoreal artist's impression labelled as such, OR a real portrait if one exists (then it's not AI).
   - **Documents, records, newspapers, photographs-of-record:** never fabricated by AI. A photoreal "1721 report page" or "1930s clipping" is a forgery.
4. **Only where no real image exists** and no own-graphic works. The real archival material stays the base — an episode is mostly real prints/photos/graphics with a *few* AI beats, never the reverse.
5. **One consistent style across the episode's set** — same style block for every AI image so they read as one system.
6. **Style is a register, not a copy of a living artist.** Public-domain traditions (ukiyo-e, chiaroscuro, etc.) or generic descriptors ("cinematic photoreal, muted", "charcoal illustration") — never "in the style of [living artist/studio]".

## How the count is set

The number of AI images = the count of shotlist beats flagged in `07-assets.md` as **no PD image + no own-graphic**. It comes from the locked script → shotlist → asset manifest, not from a wish for more visuals. Typical: 2–6 per episode. If it's more than ~8, the episode probably has a sourcing problem — stop and reassess.

## The prompt document — `07b-ai-prompts.md`

Scaffolded by `tools/build_ai_prompts.py`, then the **episode style** and the scene text are written (by Josh or Claude). Template: [templates/ai-prompts.md](../templates/ai-prompts.md). It contains:

- **Header:** episode, output spec, save folder, naming convention.
- **The episode style block** — chosen for *this* episode (rule 1), 3–5 lines. Ties to the channel look ([docs/03](03-brand-identity.md) §Visual direction) and the episode's real archival material. Merged into every prompt below it.
- **Negative prompt** — shared. When the style is *not* photoreal, it excludes photoreal; when the style *is* photoreal, it still excludes text/watermark/faces-of-real-people and anything that would make it read as an actual archival photo.
- **One block per image:** an ID (`aiNN`), the shotlist beat(s), what it's for, the **full copy-paste prompt** (episode style already merged in), the negative prompt, and the exact **filename to save as**.

## Folder + naming

- Images go to **`episodes/E0XX-<slug>/assets/ai/`** (created by the script; gitignored — images stay local).
- Filename: **`E0XX_aiNN_<slug>.png`** — e.g. `E001_ai01_deathbed-room.png`. The `aiNN` and `<slug>` match the block in `07b-ai-prompts.md`, so when Josh saves a file with that name, it's unambiguous which prompt it answers.

## Round trip

1. Stage 7 photography pass flags the ❌ beats.
2. `python tools/build_ai_prompts.py E0XX-<slug> <slug1> <slug2> …` → creates `assets/ai/` and scaffolds `07b-ai-prompts.md`.
3. Claude writes the scene text for each prompt (framing, what's depicted, face-avoidance).
4. Josh copy-pastes each prompt into the generator, makes 3–4 variants, picks the one that best matches the set, saves as `E0XX_aiNN_<slug>.png` in `assets/ai/`.
5. `python tools/build_ai_prompts.py E0XX-<slug> --check` → lists which files exist vs. the doc.
6. Claude reads `assets/ai/`, adds the accepted AI images to `07-assets.md` as rows (licence = «ilustración propia (IA) — rótulo en pantalla»), and notes the label in `09-description.md` credits.

## Gate (part of Stage 7)

- [ ] Every AI beat has a prompt block and a generated, named file in `assets/ai/`
- [ ] The set is stylistically consistent (one style block)
- [ ] No AI image shows a recognisable real-person face or a fabricated document
- [ ] Every AI image has an on-screen label planned in `06-shotlist.md`
- [ ] `07-assets.md` updated with the AI rows; credits noted
