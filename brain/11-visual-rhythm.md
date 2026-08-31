# 11 — Visual Rhythm & Shot Planning

> **Status: v1 — method set, not yet video-calibrated.** Built from: process A (shot planning inferred from the E000 script, see `episodes/E000-EXAMPLE-ejemplo/06-shotlist.md`) + standard documentary-edit craft. Process B (direct observation of a reference video) could not be run in the automated browser — YouTube playback freezes the renderer (see §5). Refine to v2 after a manual calibration pass (§4).

## 1. The method in one line

**Shots are planned from the locked script, not from watching references.** The script already encodes the visual plan — every subject change, every `[EN PANTALLA]`, every `[EXPLICADOR]`, every `[PLANT]`/`[PAY]` is a visual beat. Process B is only used once, to calibrate the numbers.

## 2. Process A — infer the shotlist from the script (primary, every episode)

This is Stage 6 of the workflow. Input: locked `05-script.md`. Output: `06-shotlist.md`.

### 2.1 Rules for placing a visual beat

1. **One visual beat every ~2–3 sentences of narration**, or wherever the *subject* of the sentence changes (new person, place, year, object).
2. Every `[EN PANTALLA]` cue in the script → a beat, kept verbatim.
2b. **Cold open** → the `[HOOK VISUAL]` list in the script is 2–5 beats, hard-cut on the narration beat, **stock video preferred** over a push-in on a still. The last is the "turn" shot. **Bumper (§0b)** = one beat: black + `Exodo` wordmark, 3–6 s, no motion.
3. Every **named** person / place / document / institution / number → its own archival image or graphic.
4. `[EXPLICADOR]` interlude → one motion-graphic / diagram sequence. **No talking head.** Budget it as the single longest visual block (~60–140 s).
5. `[PLANT]` and its `[PAY]` → **the same shot both times** (visual rhyme; the viewer recognizes the image and the callback lands).
6. **Close / reflection** → reuse images already shown; no new archival. Optional: the episode's only narrator-on-camera moment, on the applied takeaway.
7. Every **number** → an own-made graphic with an on-screen source label.
8. Every **disputed or approximate** claim → an on-screen caveat caption ("cifras aproximadas — las fuentes varían").

### 2.2 Beat-rate targets (v1 — calibrate in §4)

| Section | Beats per minute | Feel |
|---------|------------------|------|
| Cold open (hook) | 10–12 · 2–5 shots in 20–40 s, video preferred | fast, montage-like |
| Bumper | 1 shot, 3–6 s | black, still, a breath |
| Context + era setup | 6–8 | steady |
| Narrative acts | 7–9 | steady, quickens toward the turn |
| Explainer interlude | 3–5 | slower; one idea builds |
| "N theories" module | 8–10 | brisk, one card per position |
| Close / reflection | 4–6 | slow; lets the idea land |
| CTA | 1–2 | one card |

For a 20-minute episode that's roughly **150–180 distinct visual beats**. Not 180 unique assets — reuse is expected (the E000 example reuses one engraving 3× and one chart 3×).

### 2.3 Visual-type menu (what fills a beat)

- Narrator on camera (talking head) — **rare**, reserved for the takeaway.
- Archival photo / engraving / painting (public domain preferred).
- Archival video / newsreel.
- Document — page, headline, filing, ledger — with a zoom to the relevant line.
- Own-made graphic: chart, timeline, diagram, animated map, counter.
- Plain text card — a quote, a date, a caveat, a chapter marker.
- Free stock footage/photo — generic b-roll only (`brain/12`); **preferred in the cold-open visual hook** and anywhere a real moving shot beats hand-animating a still.
- **No** dramatized-film clips as if they were record; **no** AI/reenactment unless labeled ([brain/04](04-legal-and-ethics.md), [brain/08](08-tone-of-voice.md)).

### 2.4 Motion & treatment defaults

- Stills: slow Ken Burns (push-in or lateral). Hard cuts between beats; fades only at section breaks.
- Documents: start wide, push to the cited line.
- **No source captions on screen** — citations go in the description (`brain/03`, `brain/16`). The case-file device (`EXPEDIENTE: CASO 00XX`) and chapter cards are the only recurring text.
- Grade/grain/letterbox: the house look from `brain/03` §Visual identity — dark, warm, desaturated, fine grain, subtle vignette; applied uniformly so archival and graphics read as one piece.

### 2.5 Rights gate (unchanged from `templates/shotlist-broll.md`)

No visual enters the edit without a rights status in `03-source-log.csv`. Every on-screen number carries a source label. Every reused-from-a-film image is replaced with a real archival equivalent or cut.

## 3. Deriving the "visual plan" while still writing (Stage 4)

The writer can pre-mark the script so Stage 6 is fast:
- Put an `[EN PANTALLA]` line at every subject change, not only the dramatic ones.
- Note "‹dato → gráfico›" next to every number.
- Note "‹mismo plano que PLANT›" at every `[PAY]`.
A script marked this way *is* 80% of the shotlist.

## 4. Process B — video calibration pass (manual, run ONCE, then per major style change)

Automated browser tools can't do this reliably (§5). Usuario 001 runs it by hand on **one** reference video (recommend T05 McDonald's, `research/dieck-docs/candidates.md`). ~20–30 min.

**Protocol:**
1. Open the reference video. Watch the first **3 minutes** with a stopwatch and a notepad.
2. Every time the picture changes, make a tally mark with the timestamp. At 3:00, count: tally ÷ 3 = **beats/min for the cold open + start of narrative**.
3. Note for each ~30 s block: dominant visual type (archival photo / video / graphic / text card / talking head), and whether the narrator ever appears on camera.
4. Note the cold-open treatment: how many shots in the first 20–30 s, what kind, any text-on-screen, any grade/letterbox.
5. Note recurring motifs: channel bug, caption style, chapter cards, transition style.
6. Repeat step 2 for a 2-minute stretch in the **middle** (a narrative act) and 2 minutes of the **close**.
7. Fill the table below and update §2.2 if the observed rates differ by more than ~2 beats/min. Bump this file to v2.

**Calibration results (fill in):**

| Section sampled | Observed beats/min | Dominant visual types | Notes |
|-----------------|--------------------|-----------------------|-------|
| Cold open (0:00–0:30) | | | |
| Narrative start (0:30–3:00) | | | |
| Narrative middle (sample) | | | |
| Close (sample) | | | |
| Narrator on camera at all? | | | |
| Recurring motifs | | | |

## 5. Why not automated

Tried (2026-08-28): in-app browser subagent (crashed the session twice) and Claude-in-Chrome MCP (YouTube renderer froze on play; paused frames never buffered; black player). Not pursued further — the value is calibration only, and a human watching 3 minutes is more reliable than screenshot sampling anyway.

**If hard numbers are ever needed** (exact cuts/min, shot-length distribution): `yt-dlp` the file locally + run **PySceneDetect** for a cut list, then cross-reference with the transcript timestamps. Video files stay local/gitignored, same as the transcripts.

## 6. Output

The shotlist template ([templates/shotlist-broll.md](../templates/shotlist-broll.md)) carries the §2.1 rules inline. Worked example: [episodes/E000-EXAMPLE-ejemplo/06-shotlist.md](../episodes/E000-EXAMPLE-ejemplo/06-shotlist.md).
