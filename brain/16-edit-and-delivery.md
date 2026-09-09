---
doc: 16-edit-and-delivery
summary: "Stage 9, deliberately minimal. Graphics -> Ken Burns -> trim (transcript-reviewed, 2 phases) -> b-roll -> music -> subtitles. 4K, optional house grade LUT, export -14 LUFS. If an effect isn't in this doc it doesn't go in."
stage: [9]
read_when: "editing the video; assembling b-roll; the music bed; export settings"
pairs_with: [03-brand-identity, 11-visual-rhythm, 06-production-workflow]
tools: [make_graphics.py, kenburns.py, trim_talk.py, edit_review.py, assemble.py, edit_timeline.py, make_grade.py, find_music.py]
authority: canonical
---

# 16 — Edit & Delivery (Stage 9)

Deliberately minimal. **If an effect isn't in this doc, it doesn't go in the episode.** No lower-thirds system, no source cards, no transitions beyond a hard cut and a section fade. One house grade (`brain/03`), applied whole. The rigor is in the script and the sourcing, not in the motion graphics.

Per-episode files: `07c-edit.md` (checklist, from `templates/edit-checklist.md`) · `07c-edit.html` (raw-clip review, generated) · `07c-review.txt` (raw-clip approvals) · **`09-edit.html`** (the timeline, generated) · **`09-timeline.json`** (the edit — tracked; `beats[].dur_lock`/`slot` carry the edit-room overrides) · `09-decisions.txt` (changelog — tracked) · `09-take.mp4` (take proxy, gitignored).

## The run

Stage 7 assets are chosen; Stage 8 footage is in. **Entering Stage 9,
`advance.py` runs the graphics + Ken Burns + the trim *review pass* + a first
`assemble.py`/`edit_timeline.py`.** Best-effort: if ffmpeg / faster-whisper
aren't on the box the stage still advances — you run the missing step by hand.
Then:

1. **Ken Burns clips + own graphics** — `tools/make_graphics.py` renders the `gráfico` beats, `tools/kenburns.py --all` turns the Stage 7 stills (+ AI images) into moving clips → `assets/kb/`. *(auto on Stage-9 entry)*
2. **Trim — two phases, reviewed on a waveform** — the transcription drives every cut, so you check it before the cut is baked:
   - *review* — `tools/trim_talk.py <take> --script 05-script.md` transcribes and **proposes** cuts (lead-in / tail-out silence, inter-word pauses `> --gap`, fillers, retakes) → `<take>.review.html` (the trim room) + `<take>.words.raw.json` + `<take>.cuts.json` (the proposal) + `<take>.review.m4a` (scrub proxy) + `<take>.peaks.json` (waveform). **Renders nothing.** *(auto on Stage-9 entry; dashboard: «Recortar la voz» on the episode card at Stage 8–9)*
   - The **trim room** (`<take>.review.html`): the take drawn as a waveform, every cut a red block you **drag to move, drag the edges to resize, ✕ to delete**; **drag on empty waveform = a new cut** (retakes, repeated lines); a word-boundary magnet keeps edges clean. Transcript synced below (click a word or the wave = play from there; words inside a cut strike through live). Zoom in for 0.1 s precision. **«Aplicar corte»** → `serve.py /trim`. Self-contained — no CDN.
   - *apply* — `/trim` writes `<take>.cuts.json`, spawns `trim_talk.py <take> --apply` → `<take>.trimmed.mp4` + `<take>.words.json`, then re-aligns the timeline, **detached** (writes `<take>.apply.done`). *(`--apply-now` = both phases with the auto proposal, no review; `--rebuild-page` regenerates the trim room from an existing transcription, no whisper.)*
3. **Raw-clip review** *(optional but recommended)* — `tools/edit_review.py` → `07c-edit.html`: watch every KB clip + trimmed take on its own, tick OK or write a fix. Catches a bad KB move before it hits the timeline.
4. **First cut + timeline** — `tools/assemble.py E0XX-slug` (auto, no agent):
   - parses the **"Timeline — la espina"** table in `06-shotlist.md`
   - resolves each beat's `asset` id to a file via `07-selection.md` + the `assets/` folders
   - if a trimmed VO exists, **aligns every beat to real VO time** (fuzzy-matches its script fragment against `*.words.json`); otherwise uses the shotlist's planned times
   - writes `09-timeline.json` + a 720p proxy (`09-rough.mp4`) + a waveform
   Then **`tools/edit_timeline.py`** renders **`09-edit.html`** — the cutting-room timeline: the waveform spine, a block per beat, a scrubbable proxy, and a per-beat inspector (swap asset · lock duration · nudge · reorder · Ken Burns motion · regen note · approve). Usuario 001 works it in the browser — drag, resize, reorder, preview a region — **Guardar** autosaves and the overrides survive rebuilds; **no tokens**. **Finalizar Stage 9** POSTs `09-timeline.json`; Claude applies the regen notes and `assemble.py --final` renders the 4K master.
5. **Background music** — one ominous-ambient bed under the whole thing, ducked −5 dB under the VO (`assemble.py` mixes it on `--final`).
6. **Subtitles** — `.srt` from the trimmed VO, hand-corrected against `05-script.md`.

Then: house grade — **opt-in**: if `brand/assets/grade.cube` exists, `assemble.py` bakes it in with `lut3d` (proxy and master); no file → render untouched. `tools/make_grade.py` generates the .cube from ~8 constants and can preview it on a frame (`--preview frame.png`). Export, picture-lock review.

## Tooling — the timeline is ours; DaVinci is the escape hatch

Steps 1–4 are the tools above; the assembly + duck + grade + −14 LUFS all live in
`assemble.py`'s ffmpeg graph. If a given episode needs frame-level craft the
timeline can't give (a J-cut, a montage, motion graphics), take `09-timeline.json`
into **DaVinci Resolve** (via its MCP) as a starting point — the placement is
already done, so Claude doesn't re-place 45 clips by hand. Most episodes never
need it; the format is hard-cuts-in-script-order with one grade.

## Resolution — 4K target, graceful fallback

**Target 4K (3840×2160).** The timeline stays 4K. A shot that can't fill it — a still smaller than 4K, a stock clip only available in 1080 — drops to the next step down for that shot only (inset / static / minimal upscale), not the whole project. `kenburns.py` defaults to `--res 4k` and renders a too-small still **static on black** rather than upscaling it.

---

## 1. Ken Burns on stills — `tools/kenburns.py`

Stills only (video already moves). The move is chosen from the image's **real aspect ratio** (in `07-selection.md`) against the 16:9 frame:

| Image (W:H) | Move | Why |
|-------------|------|-----|
| ~16:9 — ratio 0.90 – 1.90 | slow push-in, 1.00 → 1.10 | safe default |
| wide panorama — ratio > 1.90 | horizontal pan across the full width, no zoom | uses the whole image |
| portrait — ratio < 0.90 | vertical pan (default top → bottom; `--dir up` to end on a face) | reveals a tall image |
| small — long side < the 4K frame | **static**, centred on a dark card, no move | not enough pixels to move at 4K |

- `python tools/kenburns.py E0XX-slug --all` → every still in `assets/{archive,stock,ai}/` named `beatNN_*` → `assets/kb/beatNN_<slug>.mp4` at 4K.
- Duration defaults to 5 s; per-clip `--dur` / `--move` / `--dir` overrides come from Usuario 001's review feedback.
- `[PROMISE]` / `[PAY]`: identical move both times.

## 2. Trim — `tools/trim_talk.py`

- Input: the take(s) from Stage 8 (one or several video files — audio-only also works).
- `faster-whisper` transcribes each → word-level timestamps. **The transcript is
  reviewed before any cut is applied** (`<take>.review.html`) — it drives every
  cut *and* the script-coverage check, so a wrong transcription = wrong edit.
- Proposed cuts (**a proposal, not the edit** — the trim room is where you finish it):
  - **lead-in / tail-out silence** — the take almost always opens and closes on dead air.
  - **silence** gaps longer than `--gap` (default 0.45 s) → asymmetric pad: **~0.26 s kept *after* a word**, ~0.10 s before the next (whisper marks word-ends short, so a symmetric pad clips the tail of the word — this was a real bug).
  - **filler** words from a Spanish list (`eh`, `este`, `o sea`, `pues`…) — conservative, standalone only, `--no-fillers` to skip.
  - **retakes / false starts** (`--no-retakes` to skip) — recording in one long take with mistakes is expected. A run of ≥4 words re-said near-verbatim (≥74%) **within `--retake-window` s** (default 13) → the earlier attempt + any fumble is cut. Auto-detection is deliberately imperfect; **the trim room is the real control** — drag a cut over the bad take on the waveform.
- **Smooth, not aggressive:** a pause under 0.45 s is never cut; a 10 ms audio fade at each join kills clicks.
- Phase 1 output: `<take>.words.raw.json` (all words, original timeline) · `<take>.cuts.json` (the proposal, then whatever the trim room saved) · `<take>.cuts.md` (readable transcript with cuts marked) · `<take>.review.m4a` (audio proxy) · `<take>.peaks.json` (waveform, ~3000 buckets from ffmpeg PCM) · `<take>.review.html`.
- Phase 2 output (`--apply`): `<take>.trimmed.mp4` + `<take>.words.json` (surviving words on the trimmed timeline — `assemble.py` aligns beats against this).
- **`--script 05-script.md`** — the review page lists any script line that **no surviving span covers well** (cut entirely, always flubbed, or transcribed oddly). That's the re-record list.
- `--keep MM:SS` protects a span in phase 1 (also applies to retake cuts).
- Multi-take: review + apply each; `assemble.py` concatenates in script order and offsets each take's word times.

## 3. Raw-clip review — `tools/edit_review.py` → `07c-edit.html`  *(optional)*

- Scans `assets/kb/*.mp4` and `assets/*.trimmed.mp4`. Per clip: `<video>` preview · `aprobado` · free-text fix.
- Use it to catch a bad KB move or a bad trim **before** the timeline. Its FIX lines feed the same `kenburns.py` / `trim_talk.py --keep` re-runs.
- Skippable — the timeline's inspector (step 4) has the same approve/fix per clip, in context. Keep it for a fast first pass over many raw clips.

## 4. First cut + timeline — `assemble.py` → `edit_timeline.py` → `09-edit.html`

**`assemble.py E0XX-slug`** (python, no agent):
- parses the **"Timeline — la espina"** table in `06-shotlist.md` (one row per beat: `#`, `in`, `dur`, `sección`, `tipo`, `asset`, `rótulo`, `motion`, `marcador`, guion frag.)
- resolves `asset` ids to files via `07-selection.md` + `assets/{kb,stock,video,intro,archive,ai,graphic}/`
- **`tipo: acamara`** (A-roll, `brain/11` §1b) → the beat plays the **trimmed take** for its slot; `motion` forced to `cut`, no Ken Burns, no asset lookup. The take is both the VO spine and the A-roll video. *(Single continuous take only for now — multi-take A-roll needs per-take offset mapping.)*
- **aligns to the VO** when a trimmed take exists (fuzzy-matches each beat's frag against `*.words.json` — needs ≥3 consecutive word matches; frags that are stage directions never anchor); un-matched beats are **spread across the gap between aligned neighbours** by shotlist `dur`; total **clamped to the VO length**. Monotonic (each beat runs until the next begins).
- **enforces the rhythm** (`brain/11` §2.2): merges any beat under **2.5 s** into its neighbour and collapses two identical shots in a row (kills the millisecond flashes and the pile-ups); flags `pace` on any non-A-roll beat over **20 s** or 2.5× its section target (⚠ marker in the edit room); every still gets a Ken Burns move (**never static**); `pan-v`/`pan-h` auto-picked from the asset's aspect ratio so a portrait **fills the frame and travels** instead of sitting small on black; museum scans >4320 px are downscaled to `assets/_proxy/` first.
- an A-roll beat that still ends up past the trimmed take → rendered black (never a fatal seek), with a warning.
- writes **`09-timeline.json`** + `09-rough.mp4` (720p proxy) + `09-wave.b64` (waveform) + `09-vo.m4a` (VO audio proxy) + **`09-take.mp4`** (720p proxy of the narrator take, for the live page's continuous `#face`); music bed sits at **−30 dB** under the VO.

**`edit_timeline.py E0XX-slug`** renders **`09-edit.html`** — the cutting room:
- VO waveform (fixed) + section bands + one block per beat, width ∝ duration, coloured by kind; `PROMISE`/`PAY` + `EXPLICADOR` marked; uncovered flagged; **`pace` beats ⚠**; **edited beats** (locked duration / reordered) get a dashed outline.
- **two preview modes:** *en vivo* (default) plays `09-vo.m4a` + music bed live; the narrator take (`09-take.mp4`) runs continuously as a hidden `#face`, shown on `acamara` beats (no per-beat seek); stills/clips swap one at a time — no render, no Ken Burns/grade. *corte renderizado* plays `09-rough.mp4`.
- a per-beat **inspector**: **swap asset** (picker over `assets/` + paste a path/URL → `beat_asset.py` fetches it, re-points the spine row, pins the id → file in `assets/_index.json` and syncs `07-picks.txt` so a re-download can't undo it) · **lock a duration** (± or drag the right grip — steals from the next beat, capped at its floor) · nudge ±frames · Ken Burns motion · regen note · approve · ↺ reset.
- **reorder**: drag a beat block past a neighbour — it takes that time window (the VO stays; only which picture shows when changes). Stored as a `slot` sort-key.
- **Guardar** autosaves (debounced): `dur_lock` / `slot` / `nudge` / `approved` / `fix` → `/tl-save` → the server re-runs `build_timeline` (`align()` then `_apply_edits`) and returns the recomputed timeline. **The overrides survive every later rebuild** (prev-merge keeps them).
- **Previsualizar región** / **Renderizar borrador** save first, then re-render (`assemble.py --preview` / `--rough`).
- **Finalizar Stage 9** → flushes the save, POSTs `09-timeline.json` (+ `09-decisions.txt`). Claude applies regen notes + `assemble.py --final` for the 4K. Beats `sin cubrir` block the final render.

**Rules that don't move** (`assemble.py` enforces or the human keeps):
- **A-roll / B-roll** (`brain/11` §1b): cut to the face when the narrator is *addressing the viewer* (opinion, pivote, close, CTA); cut to B-roll when the narration *describes a thing to see*. Hard cuts; a J-cut (VO of the next beat starts a beat early under the outgoing picture) is allowed at an A→B or B→A change and nowhere else.
- **Video clips:** cut to length. No speed ramp, no filter. Loop only if shorter than the beat *and* the loop point is invisible.
- **Cold open (§0), ~35–45 s:** 1 contextual hero shot (8–10 s) + 3–5 `intro` hook clips (4–6 s) + the "turn" shot + close to camera → cut to black. (`brain/11` §2.1 rule 2b)
- **Bumper (§0b):** 3–6 s black + `Conquest` wordmark + presenter line. No music.
- Reused beats (`PROMISE n` / `PAY n`): the **same** `asset` and `motion` both times (the shotlist spine sets this; the timeline keeps it).

## 5. Background music — `tools/find_music.py`

- **Brief: ominous ambient.** Atmosphere, not dread, not a mystery stinger. Instrumental, low, slow, minimal or no melody, no vocals, no percussion spikes, loops cleanly.
- **Licence:** CC0 / CC-BY / CC-BY-SA only — a monetised video is commercial + sync use; NC/ND are out. Full rule + sources in [brain/12](12-available-material-protocol.md) §Audio. `find_music.py` (Jamendo, key in `tools/.env`) filters to those and **appends** to `brand/assets/music/candidates.md`; the pool then shows in the **Music section of `07-style-pass.html`**.
- **Your own track** — the Music section also has *«Recursos propios»* rows: paste a local path or URL + `título · autor` + a licence (`CC0` / `CC-BY` / `CC-BY-SA` only — the field offers nothing else). `--download` fetches it to `brand/assets/music/` and logs the licence + attribution in `LICENSES.md`; a track with a disallowed or missing licence, or no title/author, is **skipped with a warning**, not downloaded.
- `--download` pulls every ticked / pasted track → `brand/assets/music/` + `LICENSES.md` (exact licence + attribution — carried into `09-description.md`).
- **Per episode:** one bed under the whole piece, ~20–24 dB under the VO peak; duck −4 to −6 dB under speech. A second, warmer track may enter at the close (M3, `brain/02` §3). **No music in the bumper.** Same 3–5 beds every episode until a retro says to refresh.

## 6. Subtitles

- `.srt` generated from the **trimmed VO** (whisper on the trimmed file, or `trim_talk.py`'s transcript re-timed to the trimmed timeline), then **hand-corrected against `05-script.md`** — every number, name, and `[S..]`-backed claim must read exactly as written.
- 1–2 lines, ≤ 42 characters/line, minimum 1 s on screen. Spanish, `.srt`. Non-negotiable every episode (`brain/07` §Subtitles).

---

## On-screen text — minimal

On screen only: the **case-file device** (`EXPEDIENTE: CASO 00XX …`, Courier Prime), **chapter / section cards** (Playfair), and the **AI / reenactment label** (`Ilustración — Conquest` or `Recreación`, permanent, every appearance — `brain/15`, `brain/04` §8). **No source cards** (`brain/03`).

## Look / grade

The house grade from [brain/03](03-brand-identity.md) §Grade, applied to the whole timeline so archival and graphics read as one piece.

## Export

- **4K** target (see §Resolution); fps 24 or 30 — lock at brand.
- H.264 or H.265, high bitrate; stereo AAC 320 kbps.
- Loudness **−14 LUFS** integrated (YouTube target), true peak ≤ −1 dBTP.
- Filename `E0XX-<slug>-vN.mp4`.

## Review loop

Timeline finalised in `09-edit.html` (every beat covered + approved) → Claude
applies regen notes + `assemble.py --final` → **picture lock** (no further timing
changes) → Usuario 002 watches once, end to end, against `05-script.md` and
`brain/04` (labels present, claims accurate, dignity) → signs in `07c-edit.md` →
`.srt` finalised → Stage 10.

## Gate (Stage 9)

- [ ] Every beat in `09-timeline.json` has an `asset`/`file` (0 `sin cubrir`) and is `approved`
- [ ] Only the moves in this doc — no other effects, transitions, or grade
- [ ] Cold open = `intro` clips in order + bumper on black
- [ ] Ken Burns `motion` matches each image's orientation; `PROMISE n`/`PAY n` share `asset` + `motion`
- [ ] One music bed, ducked under the VO; no music in the bumper; track licences logged
- [ ] AI / reenactment / colourised labelled on every appearance (`rótulo` set in the spine)
- [ ] 4K master rendered; `.srt` generated and hand-corrected against `05-script.md`
- [ ] −14 LUFS integrated; 4K (or best common resolution); picture lock signed by Usuario 002 in `07c-edit.md`
