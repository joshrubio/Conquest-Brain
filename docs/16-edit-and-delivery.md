# 16 — Edit & Delivery (Stage 9)

Deliberately minimal. **Five moves, in order. If an effect isn't on this list, it doesn't go in the episode.** No lower-thirds system, no colour grade, no transitions beyond a hard cut and a section fade. The rigor is in the script and the sourcing, not in the motion graphics.

| # | Move | Tool | Consumes |
|---|------|------|----------|
| 1 | **Trim** the take(s) | `tools/trim_talk.py` | Stage 8 recordings |
| 2 | **B-roll** on the marked beats | manual | `06-shotlist.md` + `07-selection.md` |
| 3 | **Ken Burns** on stills (orientation-aware) | `tools/kenburns.py` | `07-selection.md` |
| 4 | **Background music** bed | `tools/find_music.py` (once) | `brand/assets/music/` |
| 5 | **Subtitles** `.srt` | whisper + hand-correct | trimmed VO + `05-script.md` |

Then: minimal source cards, export, review.

Per-episode file: `07c-edit.md` (from `templates/edit-checklist.md`).

---

## 1. Trim — `tools/trim_talk.py`

- Input: the take(s) from Stage 8 (one or several video files).
- `faster-whisper` transcribes each → word-level timestamps.
- Cuts:
  - **silence** gaps longer than `--gap` (default 0.6 s) → trimmed to ~0.15 s of room;
  - **filler** words/sounds from a Spanish list (`eh`, `este`, `o sea`, `pues` at a phrase start, false starts) — conservative, and always shown for veto.
- **Smooth, not aggressive:** 120–180 ms of padding kept around every retained span; a pause under 0.4 s is never cut; an 8 ms audio fade at each join kills clicks.
- Output per take: `<take>.trimmed.mp4` + `<take>.cuts.md` — the transcript with every cut marked. Josh reads it, vetoes bad cuts (`--keep MM:SS`), re-runs.
- Multi-take: trim each, then assemble in script order (§ sections of `05-script.md`).

## 2. B-roll

- `06-shotlist.md` marks which beats are archival / stock / AI; `07-selection.md` names the file. Drop each asset on its beat, over the VO.
- **Video clips:** cut to length. No speed ramp, no filter, no zoom. Loop only if the clip is shorter than the beat *and* the loop point is invisible.
- **Cold open (§0):** 2–5 clips from `assets/intro/` in numbered order, hard-cut on the narration beat (`docs/02` §0). Last shot holds ½ s → cut to black.
- **Bumper (§0b):** 3–6 s black + `Éxodo` wordmark + presenter line. No music.
- Reused beats (`[PLANT]` / `[PAY]`): the **same** clip/frame both times.

## 3. Ken Burns on stills — `tools/kenburns.py`

Stills only (video already moves). The move is chosen from the image's **real aspect ratio** (in `07-selection.md`) against the 16:9 frame:

| Image (W:H) | Move | Why |
|-------------|------|-----|
| ~16:9 — ratio 0.90 – 1.90 | slow push-in, 1.00 → 1.10 | safe default |
| wide panorama — ratio > 1.90 | horizontal pan across the full width, no zoom | uses the whole image |
| portrait — ratio < 0.90 | vertical pan (default top → bottom; `--dir up` to end on a face) | reveals a tall image |
| small / inset — long side < 1920 px | **static**, centred on a dark card, no move | not enough pixels to move |

- Duration = the beat length. Direction / move can be overridden per beat in `07c-edit.md`.
- `[PLANT]` / `[PAY]`: identical move both times.
- Output: `assets/kb/beatNN_<slug>.mp4` at channel resolution.

## 4. Background music — `tools/find_music.py` (run once for the channel)

- **Brief: ominous ambient.** Atmosphere, not dread, not a mystery stinger. Instrumental, low, slow, minimal or no melody, no vocals, no percussion spikes, loops cleanly.
### Licence — a monetised YouTube video is **commercial** use

A track only works for us if its licence allows **commercial use** *and* using it as a video soundtrack (a sync / derivative). That means:
- **OK:** CC0 / public domain (no strings) · **CC-BY** (must credit the artist + licence in `09-description.md`) · **CC-BY-SA** (credit + the "share-alike" ask).
- **NOT OK:** anything with **NC** (non-commercial) or **ND** (no-derivatives).
- **Jamendo:** its free catalogue is per-track CC — many are BY-NC (unusable). `find_music.py` filters to BY / BY-SA / CC0 only. Jamendo's paid "Jamendo Licensing" is a separate product and is **not** required for CC-BY tracks.
- **Zero-hassle, no attribution:** **YouTube Audio Library** (inside Studio) and **Pixabay Music** (`pixabay.com/music`) — both browse-only, no API. For a channel that reuses 3–5 beds forever, picking them by hand here is fine.

### The tool

- `find_music.py` queries **Jamendo** (free `JAMENDO_CLIENT_ID` in `tools/.env`; no key → Openverse fallback), keeping only BY / BY-SA / CC0. `python tools/find_music.py "dark ambient drone cinematic"` → `brand/assets/music/candidates.md`; Josh auditions the previews, picks **3–5**, `python tools/find_music.py --get <id> <id> ...` → `brand/assets/music/` + `brand/assets/music/LICENSES.md` (exact licence + required attribution per track).
- **Per episode:** one bed under the whole piece, sitting ~20–24 dB under the VO peak; duck −4 to −6 dB under speech. A second, slightly warmer track may enter at the close (M3, `docs/02` §3). **No music in the bumper.**
- The same 3–5 tracks every episode until a retro (`docs/06` Stage 12) says to refresh them.

## 5. Subtitles

- `.srt` generated from the **trimmed VO** (whisper on the trimmed file, or `trim_talk.py`'s transcript re-timed to the trimmed timeline), then **hand-corrected against `05-script.md`** — every number, name, and `[S..]`-backed claim must read exactly as written.
- 1–2 lines, ≤ 42 characters/line, minimum 1 s on screen. Spanish, `.srt`. Non-negotiable every episode (`docs/07` §Subtitles).

---

## Source cards (minimal)

A claim gets an **on-screen** citation only if it is: a direct quote, a contested/approximate number, or a named document/record. Everything else is credited in `09-description.md` «Fuentes principales».
- Format: small lower-third, `Autor — Obra / Año`. Exact style frozen in `docs/03` §Visual direction (**pending**).
- **AI / reenactment / colourised:** permanent on-screen label every appearance — `Ilustración — Éxodo` or `Recreación` (`docs/15`, `docs/04` §8). Not optional, not once.

## Look / grade — PENDING `docs/03` §Visual direction

Until the house look is locked: **no grade, no letterbox, no film grain, no vignette.** Straight cut, consistent export. Lower-third / source-card / typography styles come from `docs/03` when it exists. Revisit this section then.

## Export

- Channel resolution from `docs/03` (1080p or 4K — **pending**). fps 24 or 30 — lock at brand.
- H.264 or H.265, high bitrate; stereo AAC 320 kbps.
- Loudness **−14 LUFS** integrated (YouTube target), true peak ≤ −1 dBTP.
- Filename `E0XX-<slug>-vN.mp4`.

## Review loop

Josh assembles → **picture lock** (no further timing changes) → Carmen watches once, end to end, against `05-script.md` and `docs/04` (labels present, claims accurate, dignity) → signs in `07c-edit.md` → sound + `.srt` finalised → Stage 10.

## Gate (Stage 9)

- [ ] Only the five moves used — no other effects, transitions, or grade
- [ ] Every shotlist beat has its asset on screen; cold open 2–5 shots + bumper on black
- [ ] Ken Burns move matches each image's orientation; `[PLANT]`/`[PAY]` identical
- [ ] One music bed, ducked under the VO; no music in the bumper; track licences logged
- [ ] AI / reenactment / colourised labelled on every appearance
- [ ] `.srt` generated and hand-corrected against `05-script.md`
- [ ] −14 LUFS integrated; channel resolution; picture lock signed by Carmen in `07c-edit.md`
