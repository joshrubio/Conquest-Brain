# 15 — AI Illustration Protocol

Runs **inside Stage 7** ([06-production-workflow.md](06-production-workflow.md)), only when the photography pass concludes a beat has **no viable public-domain image and no own-graphic plan**. It produces a copy-paste prompt document so Josh can generate the images and drop them back in.

## When it triggers

At Stage 7, after the photography pass, some `07-assets.md` rows are ❌ (no PD source, e.g. an event with no contemporary depiction, or a person with no usable likeness). If those beats also can't be an own-made graphic (chart / map / text card), they become **AI-illustration beats**.

**AI is not a shortcut past sourcing.** It is only for beats where *nothing real exists* and a stylised drawing is the honest option anyway.

## Hard rules

1. **Stylised, clearly not photographic.** The house register is **sumi-e / woodblock** (ink-wash, carved line, limited palette, paper texture) — it sits next to the real archival prints and reads on its own as *illustration*. No photoreal, no 3D, no oil-painting realism.
2. **On-screen label, every time it appears** — `Ilustración — Éxodo` (or «recreación»), discreet but legible. Same rule as reenactments / colourised visuals ([04-legal-and-ethics.md](04-legal-and-ethics.md) §8).
3. **Invents nothing.** No recognisable face of a real person (figures are seen from behind, in silhouette, at distance, or the face is obscured). No fabricated documents, no invented "this is how the trial looked" with specific detail. Only atmosphere, events with no surviving depiction, or abstract/metaphor shots.
4. **Only where no PD image exists.** The real archival material stays the base. An episode is mostly real prints/photos/graphics with a *few* AI beats, never the reverse.
5. **One consistent style across the set.** All AI images in an episode share the same style block so they read as one system.
6. **Style borrows a public-domain tradition, not a living artist.** No "in the style of [living artist]" prompts.

## How the count is set

The number of AI images = the count of shotlist beats flagged in `07-assets.md` as **no PD image + no own-graphic**. It comes from the locked script → shotlist → asset manifest, not from a wish for more visuals. Typical: 2–6 per episode. If it's more than ~8, the episode probably has a sourcing problem — stop and reassess.

## The prompt document — `07b-ai-prompts.md`

Scaffolded by `tools/build_ai_prompts.py`, then the scene text is written (by Josh or Claude). Template: [templates/ai-prompts.md](../templates/ai-prompts.md). It contains:

- **Header:** episode, the **shared style block** (set once, derived from `docs/03` §Visual direction + the episode's real archival look), output spec, the save folder, the naming convention.
- **One block per image:** an ID (`aiNN`), which shotlist beat(s) it covers, what it's for, the **full copy-paste prompt** (style block already merged in), the negative prompt, and the exact **filename to save as**.

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
