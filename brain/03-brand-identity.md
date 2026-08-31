---
doc: 03-brand-identity
summary: "Name, palette, grade, typography, case-file device, wordmark, 4K rule, no-source-cards rule, thumbnail system."
stage: [3, 7, 9, 10]
read_when: "designing anything on screen; the grade; thumbnails; titles/wordmark"
pairs_with: [02-content-format, 16-edit-and-delivery, 07-publishing-seo-metrics]
authority: canonical
---

# 03 — Brand Identity

**Name: Exodo** — no accent, ever (prose, subtitles, wordmark, handles).
**Channel: Exodo Channel** · handle **`@exodochannel`** (`@exodoofficial` is taken on YouTube).
Chosen 2026-08-28. Full option trail + rationale + trademark notes: [brand/naming-exploration.md](../brand/naming-exploration.md).

## Name & founder story

*Éxodo* = a mass departure. For the two founders it is literal — they are **Venezuelan journalists**, part of the ~7.7M-person Venezuelan exodus (real names in [USERS.md](USERS.md)). The name carries the thesis: the gap between the official version and what actually happened, told by people who left because the official version was a lie.

The founder story is **voice and motive** — channel About, a pinned intro video, the reflection — **never an episode subject** (see [05-independence-and-coi.md](05-independence-and-coi.md) §1). "Exodo" must never be used to tell a private migration story.

**Trademark:** a 2026-08 web check found no registered class-41 mark for a Spanish documentary channel. Launching is low risk; *registering* the mark waits for a lawyer (EUIPO + national + WIPO).

## Decisions

- **Channel type:** own new YouTube channel — not a segment inside anyone else's. **Standalone**: no co-branding, cross-posting, or "by X" tag on screen.
- **Category (YouTube):** *Education* — Farid Dieck's lane.
- **Brand type:** independent show brand, no real person's name (both founders narrate; scales).
- **Output resolution:** 4K (3840×2160). The **canonical rule**: the timeline stays 4K; a shot that can't fill it drops to its best *for that shot only* (`brain/16` applies it).
- **No on-screen source cards** — the **canonical rule**: every citation lives in the description «Fuentes principales» + pinned comment. On screen only: the AI/reenactment label (`brain/15`), chapter/section cards, and the case-file device.
- Subjects are public — see [01-editorial-and-sourcing.md](01-editorial-and-sourcing.md) §3 and [00-project-charter.md](00-project-charter.md).

## Visual identity

Derived from the launch assets ([brand/assets/exodo-avatar.png](../brand/assets/exodo-avatar.png), [exodo-banner.png](../brand/assets/exodo-banner.png)).

### Palette

| Role | Hex | Use |
|------|-----|-----|
| Ground | `#100D09` | backgrounds, letterbox, the dark field behind the wordmark |
| Surface | `#1E1A14` | cards, panels |
| Bone | `#ECE3CE` | primary text, the wordmark, key light |
| Gold | `#C9A15A` | accent only — reticle lines, rules, one highlighted word, the CTA |
| Sepia | `#4A3B28` | aged-paper midtones, document underlay |
| Ember | `#8A5A2A` | rare warm highlight (a lamp, a fire) |

Restrained. Gold is a spice, not a base. No pure white, no pure black.

### Grade / treatment  (canonical — `brain/11` and `brain/16` apply it)

- **Dark, warm, desaturated.** Lift blacks slightly to warm; pull saturation down ~15–20%; a gentle warm cast overall.
- **Film grain** — fine, constant, low opacity. **Spotlight vignette** — subtle, centred on the focal point.
- **Documents / archival:** on an aged-paper or newspaper-clipping underlay; slight rotation, torn/taped edges allowed. Real scans, never faked (`brain/15`).
- **Motifs:** thin gold circle (lens/target reticle), registration crosshairs, faint typewriter text in the margins.
- Applied uniformly so archival and graphics read as one piece. No letterbox unless a source clip forces it (pad to frame on `#100D09`, never stretch).

### Case-file device (the recurring signature)

Every episode opens its context with a file-card frame, Courier Prime, gold rule:

```
EXPEDIENTE: CASO 00XX
SUJETO:     <nombre>
LUGAR:      <lugar o "Desconocido">
FECHA:      <año o "Clasificado">
```

The reflection/close may use the interview-transcript style (`ENTREVISTADOR: … / ENTREVISTADO: …`, Courier Prime, one word underlined in gold). Deliberate, not every beat.

### Typography  (all Google Fonts — free, commercial use OK)

| Slot | Face | Where |
|------|------|-------|
| Display | **Playfair Display** (Didone, high contrast) | the wordmark register; big section titles; "Documental" |
| Text / UI | **Montserrat** | chapter cards, the tagline, any lower-third, subtitles styling reference |
| Signature mono | **Courier Prime** | the EXPEDIENTE card, interview-transcript text |
| Accent script | **Caveat** | handwritten margin notes («¿Qué pasó realmente?») — sparing |

### Narrator on camera

Rare — only the applied-takeaway moment (`brain/02` §3, form A). When used: **centred, medium shot (waist-up), plain dark background, soft key from one side.** No desk, no set dressing.

### Wordmark

"EXODO" in the Playfair-style Didone serif, the **X** stretched into the pivot letter. Optional "— CHANNEL —" underneath in letter-spaced Montserrat / gold. On bone or on ground; never on a busy photo without a scrim.

### Tagline

**"Historias reales. Preguntas profundas. Verdades que importan."**

## Assets  (`brand/assets/`)

| File | State |
|------|-------|
| `exodo-avatar.png` | 1254×1254 — YouTube avatar (export 800×800 for upload) |
| `exodo-banner.png` | 1672×941 — **re-export at 2560×1440** (safe area 1546×423) |
| logo (svg + png, transparent) | to produce — vectorise the wordmark |
| `end-card.png` / lower-third template | to produce — minimal, per this doc |
| thumbnail template | to produce — see below |

### Thumbnail system

One layout, every episode: subject image (archival or a still) + the house grade + the case-file device or a single line of Playfair, gold accent on one word. Text ≤ 4 words, high contrast, readable at 320px. No arrows, no shocked faces, no red circles. Consistent enough that the channel reads as one body of work in a grid.

## Checklist before first publish

- [x] Name / channel type / spelling / category — decided
- [x] Avatar + banner in `brand/assets/` (banner needs a 2560×1440 re-export)
- [x] Palette / grade / typography / case-file device — set (this doc)
- [ ] Handle `@exodochannel` secured on YouTube + IG + TikTok
- [ ] Logo SVG + minimal lower-third + thumbnail template produced
- [ ] Trademark clearance (class 41) via a lawyer — before registering, not before launching
