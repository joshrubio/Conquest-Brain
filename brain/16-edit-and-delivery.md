---
doc: 16-edit-and-delivery
summary: "Stage 9, deliberately minimal. Ken Burns -> trim -> review -> b-roll -> music -> subtitles. 4K, house grade, export -14 LUFS. If an effect isn't in this doc it doesn't go in."
stage: [9]
read_when: "editing the video; assembling b-roll; the music bed; export settings"
pairs_with: [03-brand-identity, 11-visual-rhythm, 06-production-workflow]
tools: [kenburns.py, trim_talk.py, edit_review.py, find_music.py]
authority: canonical
---

# 16 — Edit & Delivery (Stage 9)

Deliberately minimal. **If an effect isn't in this doc, it doesn't go in the episode.** No lower-thirds system, no source cards, no transitions beyond a hard cut and a section fade. One house grade (`brain/03`), applied whole. The rigor is in the script and the sourcing, not in the motion graphics.

Per-episode files: `07c-edit.md` (checklist, from `templates/edit-checklist.md`) · `07c-edit.html` (review surface, generated) · `07c-review.txt` (Usuario 001's approvals + feedback).

## The run

Stage 7 assets are chosen; Stage 8 footage is in. Then:

1. **Ken Burns clips** — `tools/kenburns.py --all` turns the Stage 7 stills (+ AI images) into moving clips → `assets/kb/`.
2. **Trim** — `tools/trim_talk.py` cuts silences + fillers from each Stage 8 take → `<take>.trimmed.mp4`.
3. **Review** — `tools/edit_review.py` builds **`07c-edit.html`**: every KB clip and every trimmed take with a `<video>` preview, an *aprobado* checkbox and a feedback box. Usuario 001 approves each or writes what to fix; **Exportar 07c-review.txt** → Claude re-runs the tool per the feedback → regenerate the page → repeat until **all approved**.
4. **B-roll assembly** — only once step 3 is all-green. Lay each beat's asset on the VO timeline per `06-shotlist.md` + `07-selection.md`. Cold open = `assets/intro/` clips + bumper.
5. **Background music** — one ominous-ambient bed under the whole thing, ducked under the VO.
6. **Subtitles** — `.srt` from the trimmed VO, hand-corrected against `05-script.md`.

Then: house grade, export, picture-lock review.

## Tooling — Claude first, DaVinci later if needed

Steps 1–3 are the tools above. Steps 4–5 (assembly + mix) we try to do with **Claude driving ffmpeg**. If timing b-roll to the VO proves too fiddly that way, we integrate the **DaVinci Resolve MCP** and move the assembly there — the review tools (`kenburns` / `trim_talk` / `edit_review`) don't change.

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
- Output per take: `<take>.trimmed.mp4` + `<take>.cuts.md` (transcript with every cut marked). Corrections from the review re-run it with `--keep MM:SS`.
- Multi-take: trim each, then assemble in script order.

## 3. Review — `tools/edit_review.py` → `07c-edit.html`

- Scans `assets/kb/*.mp4` and `assets/*.trimmed.mp4` (+ `*.cuts.md`).
- Per clip: `<video>` preview · `aprobado` checkbox · free-text feedback (KB: «más lento» / «empieza a la izquierda» / «dir arriba» / «déjalo estático» / «dura 4 s»; trim: «mantener la pausa en 00:12» / «cortar antes en 02:03» / «no cortes el "eh" de 03:04»).
- **Exportar 07c-review.txt** → each line `kb|trim  <id>  APROBADO | FIX: <texto>`.
- Claude reads it, re-runs `kenburns.py` (per-clip flags) / `trim_talk.py` (`--keep …`) for every FIX, regenerates the page. Loop until every row is APROBADO.
- Only then does step 4 (b-roll) start.

## 4. B-roll assembly

- `06-shotlist.md` marks which beats are archival / stock / AI; `07-selection.md` names the file (a KB clip for stills, the stock/intro clip for video). Lay each on its beat, over the VO.
- **Video clips:** cut to length. No speed ramp, no filter, no zoom. Loop only if the clip is shorter than the beat *and* the loop point is invisible.
- **Cold open (§0):** 2–5 clips from `assets/intro/` in numbered order, hard-cut on the narration beat (`brain/02` §0). Last shot holds ½ s → cut to black.
- **Bumper (§0b):** 3–6 s black + `Exodo` wordmark + presenter line. No music.
- Reused beats (`[PLANT]` / `[PAY]`): the **same** clip/frame both times.

## 5. Background music — `tools/find_music.py`

- **Brief: ominous ambient.** Atmosphere, not dread, not a mystery stinger. Instrumental, low, slow, minimal or no melody, no vocals, no percussion spikes, loops cleanly.
- **Licence:** CC0 / CC-BY / CC-BY-SA only — a monetised video is commercial + sync use; NC/ND are out. Full rule + sources in [brain/12](12-available-material-protocol.md) §Audio. `find_music.py` (Jamendo, key in `tools/.env`) filters to those and **appends** to `brand/assets/music/candidates.md`; the pool then shows in the **Music section of `07-style-pass.html`**. `--download` pulls ticked tracks → `brand/assets/music/` + `LICENSES.md` (exact licence + attribution).
- **Per episode:** one bed under the whole piece, ~20–24 dB under the VO peak; duck −4 to −6 dB under speech. A second, warmer track may enter at the close (M3, `brain/02` §3). **No music in the bumper.** Same 3–5 beds every episode until a retro says to refresh.

## 6. Subtitles

- `.srt` generated from the **trimmed VO** (whisper on the trimmed file, or `trim_talk.py`'s transcript re-timed to the trimmed timeline), then **hand-corrected against `05-script.md`** — every number, name, and `[S..]`-backed claim must read exactly as written.
- 1–2 lines, ≤ 42 characters/line, minimum 1 s on screen. Spanish, `.srt`. Non-negotiable every episode (`brain/07` §Subtitles).

---

## On-screen text — minimal

On screen only: the **case-file device** (`EXPEDIENTE: CASO 00XX …`, Courier Prime), **chapter / section cards** (Playfair), and the **AI / reenactment label** (`Ilustración — Exodo` or `Recreación`, permanent, every appearance — `brain/15`, `brain/04` §8). **No source cards** (`brain/03`).

## Look / grade

The house grade from [brain/03](03-brand-identity.md) §Grade, applied to the whole timeline so archival and graphics read as one piece.

## Export

- **4K** target (see §Resolution); fps 24 or 30 — lock at brand.
- H.264 or H.265, high bitrate; stereo AAC 320 kbps.
- Loudness **−14 LUFS** integrated (YouTube target), true peak ≤ −1 dBTP.
- Filename `E0XX-<slug>-vN.mp4`.

## Review loop

KB + trim signed off in `07c-edit.html` → b-roll + music assembled → **picture lock** (no further timing changes) → Usuario 002 watches once, end to end, against `05-script.md` and `brain/04` (labels present, claims accurate, dignity) → signs in `07c-edit.md` → sound + `.srt` finalised → Stage 10.

## Gate (Stage 9)

- [ ] Every KB clip and every trimmed take **APROBADO** in `07c-review.txt`
- [ ] Only the moves in this doc — no other effects, transitions, or grade
- [ ] Every shotlist beat has its asset on screen; cold open 2–5 shots + bumper on black
- [ ] Ken Burns move matches each image's orientation; `[PLANT]`/`[PAY]` identical
- [ ] One music bed, ducked under the VO; no music in the bumper; track licences logged
- [ ] AI / reenactment / colourised labelled on every appearance
- [ ] `.srt` generated and hand-corrected against `05-script.md`
- [ ] −14 LUFS integrated; 4K (or best common resolution); picture lock signed by Usuario 002 in `07c-edit.md`
