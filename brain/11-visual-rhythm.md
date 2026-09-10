---
doc: 11-visual-rhythm
summary: "Shots are planned from the locked script. Plan by SHOT DURATION not beat count (§2.2 golden standard). Beat-placement rules, talking-head cadence (§2.6), portrait/pan handling, the assemble.py hard limits."
stage: [4, 6, 9]
read_when: "marking the script for shots; building the shotlist; setting cut rate in the edit"
pairs_with: [02-content-format, 16-edit-and-delivery, 06-production-workflow]
tools: [shotlist-broll.md]
authority: canonical
---

# 11 — Visual Rhythm & Shot Planning

> **Status: v2 (2026-09) — the shot-duration standard (§2.2) and talking-head cadence (§2.6) are set, calibrated to the 7 Dieck transcripts + the E001 edit lessons.** Section durations are measured; per-shot durations are craft — the §4 reference-video timing is still pending, tighten §2.2 if it differs by >~2 s. v1 (method only, from the E000 script) is superseded.

## 1. The method in one line

**Shots are planned from the locked script, not from watching references.** The script already encodes the visual plan — every subject change, every `[EN PANTALLA]`, every `[EXPLICADOR]`, every `[PROMISE]`/`[PAY]` is a visual beat. Process B is only used once, to calibrate the numbers.

## 1b. A-roll / B-roll — the narrator is on camera

The channel is **talking-head with B-roll**, not pure voice-over. The Stage-8 take
is filmed. A beat's visual is either **A-roll** (the narrator take, `tipo: acamara`)
or **B-roll** (archival / graphic / stock over the same voice).

**A-roll by default** (the face carries these):
- the **cold open** narration to camera, and the **bumper**;
- **pivotes / bisagras** — the hinge lines in and out of context, and between acts;
- **opinion / first-person** beats — "yo creo…", "me llama la atención…", "investigando, descubrí…";
- the **whole close / reflection** (§3), and the **CTA**.

**B-roll by default** (cut away from the face):
- the archival-heavy narrative stretches — a run of dates, a chronology, the subject's work, an event beat-by-beat;
- every `[EXPLICADOR]` (motion graphic, no face);
- every `[EN PANTALLA]`, every named document / number → its graphic.

Cut on meaning, not on a clock: stay on the face while the narrator is *addressing
you*; cut to B-roll the moment the narration is *describing a thing* the viewer
should see. `[PROMISE]`/`[PAY]` stay B-roll (same shot both times, §2.1 rule 5).
Rough split for a biography: ~30–45 % A-roll. `assemble.py` treats an `acamara`
beat as "play the take for this slot" — no Ken Burns, `motion` forced to `cut`.
An A-roll beat runs **as long as the voice needs it** — a piece to camera has no
upper length limit (house format). Only stretched *B-roll/graphic* beats get the
`pace` ⚠ (a still `align()` blew past its plan, or a `gráfico` under 6 s).

## 2. Process A — infer the shotlist from the script (primary, every episode)

This is Stage 6 of the workflow. Input: locked `05-script.md`. Output: `06-shotlist.md`.

The shotlist's **"Timeline — la espina"** table is the machine-readable spine —
one row per beat (`#`, `in`, `dur`, `sección`, `tipo`, `asset`, `rótulo`,
`motion` `push/pan-h/pan-v/static/zoom/cut`, `marcador` `HOOK/PROMISE n/PAY n/EXPLICADOR n`).
`tools/assemble.py --seed` parses it **once** at Stage-9 entry to seed the
`09-timeline.json` (schema 2), so it has to be complete and clean (see the
template). After seeding, the timeline is the authored artifact — the spine is
not re-consulted; a deliberate *Re-sembrar* is what pulls a spine revision in.
The `frag` column still matters for the seed (it's what `align()` matches);
after seeding it lives on each beat as `vo_anchor`. The prose tables below the
spine are for the human.

### 2.1 Rules for placing a visual beat

1. **One visual beat per sentence or subject change** (new person, place, year, object) — target one every ~6–8 s of narration. Never hold one shot past **§2.2's max** for that section.
2. Every `[EN PANTALLA]` cue in the script → a beat, kept verbatim.
2b. **Cold open (§0) — always this shape, ~35–45 s total** (`brain/02` §0):
   - **1 contextual hero shot** — the episode's own archival / AI image of the subject (E001: the deathbed illustration) — holds ~8–10 s while the VO sets the scene;
   - **3–5 hook B-roll shots** — the selected impact clips + relevant archival, ~4–6 s each, cut a beat quicker than the body, stock video preferred;
   - **the "turn" shot** (~5 s) — the image that flips the premise;
   - **close to camera** (~5–8 s, A-roll) — the thesis line → hard cut to black → **Bumper (§0b)**: one A-roll beat, `Conquest` wordmark + presenter line, 3–6 s.
2c. **A-roll vs B-roll per beat** (§1b): opinion / address-the-viewer / pivote / close / CTA → `acamara`; describing a thing, a date, a chronology → B-roll.
3. Every **named** person / place / document / institution / number → its own archival image or graphic (B-roll).
4. `[EXPLICADOR]` interlude — two shapes, pick by the graphic's **content**:
   - **Simple stage** (a process in 3 boxes, a before/after) → **a sequence**: the graphic built in stages + 2–4 supporting archival shots, ~4–6 sub-beats of ~5 s.
   - **Content-dense** (a data chart, a route map, a timeline, a multi-part diagram the viewer has to *read*) → **one held beat of 10–18 s** with internal motion (a build/reveal, or a slow push) + supporting b-roll **before and after, never intercut mid-graphic**. Rule of thumb: *if it can't be read in 5 s, don't cut away from it in 5 s.*
   A static diagram parked on screen with no motion is the worst dead air there is — the held beat still moves.
4b. **A graphic `id` appears once per video.** Exceptions, tagged in `marcador`: a `PROMISE n`→`PAY n` rhyme, or an `eco` callback in the close. Never the same graphic twice to pad — cut to camera (§2.6).
4c. **An archival asset appears at most ~3× per video and ~2× per section** (a `PROMISE`→`PAY` pair aside). Reuse is normal — the same engraving twice, a portrait in the cold open and again in the close — but a fourth time reads as running out of pictures. When a section keeps wanting the same shot, rotate the pool (a different Fuji print, another portrait) or cut to camera. `assemble.py` flags a 4th use / a 3rd-in-section.
5. `[PROMISE]` and its `[PAY]` → **the same shot both times** (visual rhyme). Keep them B-roll even inside an A-roll stretch. **A-roll cutaway right before each** (§2.6).
6. **Close / reflection** → **A-roll** in chunks of ~10–14 s (the narrator makes the point to camera), cutting to *already-seen* images (~4–6 s) as illustration; no new archival.
7. Every **number** → an own-made graphic with an on-screen source label.
8. Every **disputed or approximate** claim → an on-screen caveat caption ("cifras aproximadas — las fuentes varían").
9. **Never the same asset on two consecutive beats** (except a deliberate PROMISE→PAY). If a stretch has few distinct assets, break it with a talking-head cutaway (§2.6), not by repeating a shot.

### 2.2 Shot-duration standard (v2 — the golden standard)

**Plan by shot duration, not by beat count.** The number of beats then falls out
of the episode's length — the *feel* is the same at 10, 15 or 25 minutes.

Section durations are calibrated to the 7 Dieck transcripts (`research/dieck-docs/structure-analysis.md`):
hooks run **28–52 s**, the CTA boilerplate **15–42 s**, narrative + interludes
55–70 % of runtime. Per-shot durations are craft, calibrated to the genre
(Dieck / Vox / Johnny Harris cut at ~7–9 s average — not a trailer, not a
slideshow); tighten in §4 once a reference video is timed.

| Section | shot: min – **target** – max (s) | direction note |
|---------|-----------------------------------|----------------|
| **Cold open** (35–45 s total) | 4 – **6** – 10 | hero contextual holds 8–10 s, then 3–5 hook shots at 4–6 s, the turn, close to camera — §2.1 rule 2b |
| Bumper | one A-roll · 3–6 | «Soy X, esto es Conquest» |
| Context / era setup | 4 – **6** – 10 | maps + period archival with a slow move; an explainer can sit here |
| **Narrative acts** (B-roll) | 4 – **7** – 11 | one shot per sentence / subject change |
| **A-roll** (talking head) | 8 – **12** – 18 | hold the face; cut to B-roll when the VO *describes something to see* |
| **Explainer / graphic** | dense: held 10 – **14** – 18 · simple: sub-beats 3 – **5** – 8 | content-dense graphic (chart / map / diagram to *read*) = one held beat with internal motion; simple stage = short sub-beats + support. One graphic id, one appearance (§2.1 rule 4 + 4b) |
| "N theories" module | 3 – **5** – 8 | brisk; one card + support per position |
| **Close / reflection** (A-roll) | 8 – **12** – 18 | slow; the cutaways to *already-seen* images run 4–6 s |
| **CTA** | 15–25 s total · 1–2 shots | to camera + wordmark |

Aim **~30–40 % of runtime on camera** for a biography. At a ~8 s average that
is roughly **~100–115 beats for a 15-minute episode** (~135 for 20 min, ~70 for
10). Reuse of assets across beats is expected — the count is beats, not unique
assets (E000 reuses one engraving 3×). **Limits `assemble.py` applies:** at
**seed** it merges any B-roll shot under **2.8 s** / A-roll under **2.5 s** and
collapses two identical shots in a row (`tidy_subfloor`). On every later
**rebuild** it only *flags* (never mutates): `pace` on a `gráfico` beat under
**5 s** or a non-A-roll beat over **20 s** / **2.5× its section target** (⚠ in
the room), `dup` on a graphic id reused without a `PROMISE`/`PAY`/`eco` tag or an
archival asset over-used. A sub-floor beat the editor put there on purpose is
kept — the room's *Ordenar sub-mínimos* button re-runs the tidy on demand. A
still is still **never static**; the same asset on two consecutive beats is
still avoided.

### 2.3 Visual-type menu (what fills a beat)

- **Narrator on camera (A-roll, `tipo: acamara`)** — the default for opinion, address-to-viewer, pivotes, the close and the CTA (§1b). Filmed at Stage 8; `assemble.py` plays the take for the beat's slot, no move.
- Archival photo / engraving / painting (public domain preferred).
- Archival video / newsreel.
- Document — page, headline, filing, ledger — with a zoom to the relevant line.
- Own-made graphic: chart, timeline, diagram, animated map, counter.
- Plain text card — a quote, a date, a caveat, a chapter marker.
- Free stock footage/photo — generic b-roll only (`brain/12`); **preferred in the cold-open visual hook** and anywhere a real moving shot beats hand-animating a still.
- **No** dramatized-film clips as if they were record; **no** AI/reenactment unless labeled ([brain/04](04-legal-and-ethics.md), [brain/08](08-tone-of-voice.md)). *(The **Ensayo** track uses brief copyrighted clips **as commentary on the work itself**, under [brain/20](20-experimental-clip-protocol.md) §4 — stills-first, ≤~10 s, mirror/zoom/crop/grade, audio replaced. That is not "clip as record" — the clip is the thing being analysed.)*

### 2.4 Motion & treatment defaults

- **Every still moves** — `assemble.py` never renders a static frame. Default `push` (slow zoom-in); `pan-h` for a panorama, `pan-v` for a portrait/tall image (the move *is* how the whole image is seen — never black bars + a small picture). `cut` (no move) only on a frame-ratio still that is deliberately a hard hold. **Graphics** always get a `push` (or their build) — never `cut`/`static`, a held graphic that doesn't move is dead air.
- **Video B-roll** (`.mp4` in `stock`/`archivo`/`video`) plays straight — no Ken Burns, `motion: cut`. If the clip is a bit shorter than the beat `assemble.py` **slows it to fit** (up to ~2.6×); only loops it when it's far too short.
- **Fill, never letterbox.** A too-tall or too-wide asset fills the frame and the move travels the overflow. `assemble.py` auto-picks `pan-v` / `pan-h` from the asset's aspect ratio; the shotlist `motion` is a hint it can override.
- Documents: start wide, push to the cited line.
- Hard cuts between beats; fades only at section breaks. A J-cut (next beat's VO starts under the outgoing picture) only at an A→B or B→A change.
- On-screen text, grade, letterbox, no-source-cards: per `brain/16` §On-screen text + §Look, which apply `brain/03`.

### 2.5 Rights gate (unchanged from `templates/shotlist-broll.md`)

No visual enters the edit without a rights status in `03-source-log.csv`. Every on-screen number carries a source label. Every reused-from-a-film image is replaced with a real archival equivalent or cut — **except** on the **Ensayo** track, where a brief clip logged as `cita — crítica/comentario (fair use)` under [brain/20](20-experimental-clip-protocol.md) §4 is allowed within its budget.

### 2.6 Talking-head cadence — the narrator carries the rhythm

The A-roll take is a **structural tool**, not just for opinion beats. Cut to camera at:

- **every act / section entry** — the narrator re-anchors the viewer as the story turns;
- **every `[PROMISE]` and every `[PAY]`** — an A-roll cutaway right before each (the promise/pay B-roll shot itself stays the visual rhyme, §2.1 rule 5);
- **the whole close** and the **CTA** (§1b);
- **any B-roll stretch of ~60 s+ that has few distinct assets** — break it with a talking-head cutaway rather than repeating a shot or holding one too long. The recorded take covers the entire VO, so any window can be used.

A-roll target ~**30–40 %** of runtime. Under 25 % and the video feels like a slideshow with narration; over 45 % and it's a lecture. `assemble.py` reports the A-roll share; the shotlist review page shows a warning if a section has no A-roll beat.

## 3. Deriving the "visual plan" while still writing (Stage 4)

The writer can pre-mark the script so Stage 6 is fast:
- Put an `[EN PANTALLA]` line at every subject change, not only the dramatic ones.
- Note "‹dato → gráfico›" next to every number.
- Note "‹mismo plano que PROMISE›" at every `[PAY]`.
- Note "‹a cámara›" on the opinion / address-the-viewer / pivote beats and the whole close (§1b) — everything else defaults to B-roll.
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
7. Fill the table below. Convert to **seconds per shot** and compare with §2.2's per-shot targets — update §2.2 if they differ by more than ~2 s. (§2.2 is already v2 from the transcripts + the E001 edit; this pass only refines the per-shot numbers.)

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

Browser tools can't watch YouTube reliably here (renderer freezes on play — tried 2026-08-28). A human watching 3 minutes with a stopwatch is more reliable anyway. **If hard numbers are ever needed:** `yt-dlp` the file locally + **PySceneDetect** for a cut list, cross-referenced with transcript timestamps (video stays local/gitignored).

## 6. Output

The shotlist template ([templates/shotlist-broll.md](../templates/shotlist-broll.md)) carries the §2.1 rules inline. Worked example: [episodes/E000-EXAMPLE-ejemplo/06-shotlist.md](../episodes/E000-EXAMPLE-ejemplo/06-shotlist.md).
