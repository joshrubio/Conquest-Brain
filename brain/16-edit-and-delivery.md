---
doc: 16-edit-and-delivery
summary: "Stage 9, deliberately minimal. Ken Burns -> trim -> review -> b-roll -> music -> subtitles. 4K, house grade, export -14 LUFS. If an effect isn't in this doc it doesn't go in."
stage: [9]
read_when: "editing the video; assembling b-roll; the music bed; export settings"
pairs_with: [03-brand-identity, 11-visual-rhythm, 06-production-workflow]
tools: [kenburns.py, trim_talk.py, edit_review.py, assemble.py, edit_timeline.py, find_music.py]
authority: canonical
---

# 16 — Edit & Delivery (Stage 9)

Deliberately minimal. **If an effect isn't in this doc, it doesn't go in the episode.** No lower-thirds system, no source cards, no transitions beyond a hard cut and a section fade. One house grade (`brain/03`), applied whole. The rigor is in the script and the sourcing, not in the motion graphics.

Per-episode files: `07c-edit.md` (checklist, from `templates/edit-checklist.md`) · `07c-edit.html` (raw-clip review, generated) · `07c-review.txt` (raw-clip approvals) · **`09-edit.html`** (the timeline, generated) · **`09-timeline.json`** (the edit — tracked) · `09-decisions.txt` (changelog — tracked).

## The run

Stage 7 assets are chosen; Stage 8 footage is in. Then:

1. **Ken Burns clips** — `tools/kenburns.py --all` turns the Stage 7 stills (+ AI images) into moving clips → `assets/kb/`.
2. **Trim** — `tools/trim_talk.py` cuts silences + fillers from each Stage 8 take → `<take>.trimmed.mp4` + `<take>.words.json` (word timings on the trimmed timeline).
3. **Raw-clip review** *(optional but recommended)* — `tools/edit_review.py` → `07c-edit.html`: watch every KB clip + trimmed take on its own, tick OK or write a fix. Catches a bad KB move before it hits the timeline.
4. **First cut + timeline** — `tools/assemble.py E0XX-slug` (auto, no agent):
   - parses the **"Timeline — la espina"** table in `06-shotlist.md`
   - resolves each beat's `asset` id to a file via `07-selection.md` + the `assets/` folders
   - if a trimmed VO exists, **aligns every beat to real VO time** (fuzzy-matches its script fragment against `*.words.json`); otherwise uses the shotlist's planned times
   - writes `09-timeline.json` + a 720p proxy (`09-rough.mp4`) + a waveform
   Then **`tools/edit_timeline.py`** renders **`09-edit.html`** — the cutting-room timeline: the waveform spine, a block per beat, a scrubbable proxy, and a per-beat inspector (swap asset · trim · nudge · Ken Burns motion · regen note · approve). Usuario 001 works it in the browser — drag, trim, preview a region — **no tokens**. **Finalizar Stage 9** POSTs `09-timeline.json`; Claude applies the regen notes (`kenburns.py` per fix) and `assemble.py --final` renders the 4K master.
5. **Background music** — one ominous-ambient bed under the whole thing, ducked −5 dB under the VO (`assemble.py` mixes it on `--final`).
6. **Subtitles** — `.srt` from the trimmed VO, hand-corrected against `05-script.md`.

Then: house grade (applied by `assemble.py --final`), export, picture-lock review.

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
- `[PLANT]` / `[PAY]`: identical move both times.

## 2. Trim — `tools/trim_talk.py`

- Input: the take(s) from Stage 8 (one or several video files).
- `faster-whisper` transcribes each → word-level timestamps.
- Cuts: **silence** gaps longer than `--gap` (default 0.6 s) → trimmed to ~0.15 s of room; **filler** words from a Spanish list (`eh`, `este`, `o sea`, `pues` at a phrase start, false starts) — conservative, standalone only.
- **Smooth, not aggressive:** 120–180 ms of padding kept around every retained span; a pause under 0.4 s is never cut; an 8 ms audio fade at each join kills clicks.
- Output per take: `<take>.trimmed.mp4` + `<take>.cuts.md` (transcript, cuts marked) + `<take>.words.json` (surviving words with their time on the trimmed timeline — `assemble.py` aligns beats against this). Corrections re-run it with `--keep MM:SS`.
- Multi-take: trim each; `assemble.py` concatenates in script order and offsets each take's word times.

## 3. Raw-clip review — `tools/edit_review.py` → `07c-edit.html`  *(optional)*

- Scans `assets/kb/*.mp4` and `assets/*.trimmed.mp4`. Per clip: `<video>` preview · `aprobado` · free-text fix.
- Use it to catch a bad KB move or a bad trim **before** the timeline. Its FIX lines feed the same `kenburns.py` / `trim_talk.py --keep` re-runs.
- Skippable — the timeline's inspector (step 4) has the same approve/fix per clip, in context. Keep it for a fast first pass over many raw clips.

## 4. First cut + timeline — `assemble.py` → `edit_timeline.py` → `09-edit.html`

**`assemble.py E0XX-slug`** (python, no agent):
- parses the **"Timeline — la espina"** table in `06-shotlist.md` (one row per beat: `#`, `in`, `dur`, `sección`, `tipo`, `asset`, `rótulo`, `motion`, `marcador`, guion frag.)
- resolves `asset` ids to files via `07-selection.md` + `assets/{kb,stock,video,intro,archive,ai,graphic}/`
- **aligns to the VO** when a trimmed take exists (fuzzy-matches each beat's frag against `*.words.json`); makes the timeline monotonic (each beat runs until the next begins)
- writes **`09-timeline.json`** + `09-rough.mp4` (720p proxy) + `09-wave.b64` (waveform PNG)

**`edit_timeline.py E0XX-slug`** renders **`09-edit.html`** — the cutting room:
- VO waveform (fixed) + section bands + one block per beat, width ∝ duration, coloured by kind; `PLANT`/`PAY` + `EXPLICADOR` marked; uncovered beats flagged
- a scrubbable 720p proxy; a per-beat **inspector**: swap asset · trim (drag edge or ±) · nudge ±frames · Ken Burns motion (`push`/`pan-h`/`pan-v`/`static`/`zoom`/`cut`) · a regen note for Claude · approve
- drag a block to reposition (snaps to a word boundary); wheel = scroll, Ctrl+wheel = zoom, Shift+wheel = fast scroll; minimap to navigate
- **Previsualizar región** re-renders that stretch of the proxy (`assemble.py --preview`) — seconds, not a full render
- **Finalizar Stage 9** → POSTs `09-timeline.json` (+ a `09-decisions.txt` changelog). Claude applies the regen notes (`kenburns.py` per beat) and runs `assemble.py --final` for the 4K master. Beats still `sin cubrir` block the final render.

**Rules that don't move** (`assemble.py` enforces or the human keeps):
- **Video clips:** cut to length. No speed ramp, no filter. Loop only if shorter than the beat *and* the loop point is invisible.
- **Cold open (§0):** the `intro` clips in numbered order, hard-cut on the narration beat. Last shot holds ½ s → cut to black.
- **Bumper (§0b):** 3–6 s black + `Conquest` wordmark + presenter line. No music.
- Reused beats (`PLANT n` / `PAY n`): the **same** `asset` and `motion` both times (the shotlist spine sets this; the timeline keeps it).

## 5. Background music — `tools/find_music.py`

- **Brief: ominous ambient.** Atmosphere, not dread, not a mystery stinger. Instrumental, low, slow, minimal or no melody, no vocals, no percussion spikes, loops cleanly.
- **Licence:** CC0 / CC-BY / CC-BY-SA only — a monetised video is commercial + sync use; NC/ND are out. Full rule + sources in [brain/12](12-available-material-protocol.md) §Audio. `find_music.py` (Jamendo, key in `tools/.env`) filters to those and **appends** to `brand/assets/music/candidates.md`; the pool then shows in the **Music section of `07-style-pass.html`**. `--download` pulls ticked tracks → `brand/assets/music/` + `LICENSES.md` (exact licence + attribution).
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
- [ ] Ken Burns `motion` matches each image's orientation; `PLANT n`/`PAY n` share `asset` + `motion`
- [ ] One music bed, ducked under the VO; no music in the bumper; track licences logged
- [ ] AI / reenactment / colourised labelled on every appearance (`rótulo` set in the spine)
- [ ] 4K master rendered; `.srt` generated and hand-corrected against `05-script.md`
- [ ] −14 LUFS integrated; 4K (or best common resolution); picture lock signed by Usuario 002 in `07c-edit.md`
