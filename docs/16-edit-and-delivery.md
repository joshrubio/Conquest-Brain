# 16 — Edit & Delivery (Stage 9)

Deliberately minimal. **If an effect isn't in this doc, it doesn't go in the episode.** No lower-thirds system, no source cards, no transitions beyond a hard cut and a section fade. One house grade (`docs/03`), applied whole. The rigor is in the script and the sourcing, not in the motion graphics.

Per-episode files: `07c-edit.md` (checklist, from `templates/edit-checklist.md`) · `07c-edit.html` (review surface, generated) · `07c-review.txt` (Josh's approvals + feedback).

## The run

Stage 7 assets are chosen; Stage 8 footage is in. Then:

1. **Ken Burns clips** — `tools/kenburns.py --all` turns the Stage 7 stills (+ AI images) into moving clips → `assets/kb/`.
2. **Trim** — `tools/trim_talk.py` cuts silences + fillers from each Stage 8 take → `<take>.trimmed.mp4`.
3. **Review** — `tools/edit_review.py` builds **`07c-edit.html`**: every KB clip and every trimmed take with a `<video>` preview, an *aprobado* checkbox and a feedback box. Josh approves each or writes what to fix; **Exportar 07c-review.txt** → Claude re-runs the tool per the feedback → regenerate the page → repeat until **all approved**.
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
- Duration defaults to 5 s; per-clip `--dur` / `--move` / `--dir` overrides come from Josh's review feedback.
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
- **Cold open (§0):** 2–5 clips from `assets/intro/` in numbered order, hard-cut on the narration beat (`docs/02` §0). Last shot holds ½ s → cut to black.
- **Bumper (§0b):** 3–6 s black + `Exodo` wordmark + presenter line. No music.
- Reused beats (`[PLANT]` / `[PAY]`): the **same** clip/frame both times.

## 5. Background music — `tools/find_music.py`

- **Brief: ominous ambient.** Atmosphere, not dread, not a mystery stinger. Instrumental, low, slow, minimal or no melody, no vocals, no percussion spikes, loops cleanly.
### Licence — a monetised YouTube video is **commercial** use

A track only works for us if its licence allows **commercial use** *and* using it as a video soundtrack (a sync / derivative). That means:
- **OK:** CC0 / public domain (no strings) · **CC-BY** (must credit the artist + licence in `09-description.md`) · **CC-BY-SA** (credit + the "share-alike" ask).
- **NOT OK:** anything with **NC** (non-commercial) or **ND** (no-derivatives).
- **Jamendo:** its free catalogue is per-track CC — many are BY-NC (unusable). `find_music.py` filters to BY / BY-SA / CC0 only. Jamendo's paid "Jamendo Licensing" is a separate product and is **not** required for CC-BY tracks.
- **Zero-hassle, no attribution:** **YouTube Audio Library** (inside Studio) and **Pixabay Music** (`pixabay.com/music`) — both browse-only, no API. For a channel that reuses 3–5 beds forever, picking them by hand here is fine.

### The tool

- `find_music.py` queries **Jamendo** (free `JAMENDO_CLIENT_ID` in `tools/.env`; no key → Openverse fallback), keeping only BY / BY-SA / CC0. `python tools/find_music.py "dark ambient drone cinematic"` **appends** to `brand/assets/music/candidates.md` (an accumulating pool — run several queries).
- The pool then shows as the **Music section at the bottom of `07-style-pass.html`** — audition inline, tick what to keep. Early on, keep them all; the channel settles on 3–5. `--download` (or `find_music.py --get <id> ...`) pulls the ticked tracks → `brand/assets/music/` + `LICENSES.md` (exact licence + required attribution per track).
- **Per episode:** one bed under the whole piece, sitting ~20–24 dB under the VO peak; duck −4 to −6 dB under speech. A second, slightly warmer track may enter at the close (M3, `docs/02` §3). **No music in the bumper.**
- The same 3–5 tracks every episode until a retro (`docs/06` Stage 12) says to refresh them.

## 6. Subtitles

- `.srt` generated from the **trimmed VO** (whisper on the trimmed file, or `trim_talk.py`'s transcript re-timed to the trimmed timeline), then **hand-corrected against `05-script.md`** — every number, name, and `[S..]`-backed claim must read exactly as written.
- 1–2 lines, ≤ 42 characters/line, minimum 1 s on screen. Spanish, `.srt`. Non-negotiable every episode (`docs/07` §Subtitles).

---

## On-screen text — minimal

- **No source cards.** Every citation lives in `09-description.md` «Fuentes principales» + the pinned comment. Nothing on screen says "fuente: …".
- On screen only: the **case-file device** (`EXPEDIENTE: CASO 00XX …`, Courier Prime — `docs/03`), **chapter / section cards** (Playfair), and the **AI / reenactment label** — `Ilustración — Exodo` or `Recreación`, permanent, every appearance (`docs/15`, `docs/04` §8).

## Look / grade — from `docs/03` §Visual identity

Apply the house grade to the whole timeline: **dark, warm, desaturated ~15–20%**, blacks lifted slightly warm; fine constant **film grain** at low opacity; subtle **spotlight vignette**. Documents on an aged-paper / newspaper underlay. Palette and typography per `docs/03`. No letterbox unless a source clip forces it (pad to frame on `#100D09`, never stretch).

## Export

- **4K (3840×2160)** target; drop to the highest resolution all sources actually support if 4K would mean upscaling most of the timeline. fps 24 or 30 — lock at brand.
- H.264 or H.265, high bitrate; stereo AAC 320 kbps.
- Loudness **−14 LUFS** integrated (YouTube target), true peak ≤ −1 dBTP.
- Filename `E0XX-<slug>-vN.mp4`.

## Review loop

KB + trim signed off in `07c-edit.html` → b-roll + music assembled → **picture lock** (no further timing changes) → Carmen watches once, end to end, against `05-script.md` and `docs/04` (labels present, claims accurate, dignity) → signs in `07c-edit.md` → sound + `.srt` finalised → Stage 10.

## Gate (Stage 9)

- [ ] Every KB clip and every trimmed take **APROBADO** in `07c-review.txt`
- [ ] Only the moves in this doc — no other effects, transitions, or grade
- [ ] Every shotlist beat has its asset on screen; cold open 2–5 shots + bumper on black
- [ ] Ken Burns move matches each image's orientation; `[PLANT]`/`[PAY]` identical
- [ ] One music bed, ducked under the VO; no music in the bumper; track licences logged
- [ ] AI / reenactment / colourised labelled on every appearance
- [ ] `.srt` generated and hand-corrected against `05-script.md`
- [ ] −14 LUFS integrated; 4K (or best common resolution); picture lock signed by Carmen in `07c-edit.md`
