---
doc: tools/README
summary: "The pipeline scripts, ~one per stage. The table below is the index; each script's module docstring has the detail."
stage: all
authority: index
---

# tools/

Small scripts for the episode pipeline. Python 3.11+, deps: `requests`, `pillow`, `PyYAML`; Stage 9 adds `faster-whisper`, `static-ffmpeg`, `numpy`.

| Script | Stage | What it does |
|--------|-------|--------------|
| `factcheck.py` | 5 | Layer 1 deterministic fact-check. `python tools/factcheck.py 05-script.md 03-source-log.csv` → PASS/FAIL. |
| `build_ai_prompts.py` | 7 | Scaffolds `07b-ai-prompts.md` for AI-illustration beats (brain/15). `... E0XX-slug <img-slug> ...` / `... --check`. |
| `pull_assets.py` | 7 | **The Stage-7 hub.** Pulls candidates from free APIs → `07-style-pass.html` (per-beat candidates + AI prompts + intro). See below. |
| `clip_finder.py` | 7 | **Ensayo only** (`brain/20`). Finds + cuts a `cita` beat's excerpt. `--init` scaffolds `07-cite.tsv` from the shotlist's `cita` rows; search (`--media OBRA.mkv [--subs .srt] [--transcribe]` and/or `--clipcafe`) → `07-cite-pass.html` (candidates + thumbnails); `--extract` cuts with ffmpeg (or downloads + treats a clip.cafe pick) → `assets/cite/`, logs `CREDITS.md` + `07-cite-selection.md`. `--check-keys` reports `CLIPCAFE_API_KEY`. ffmpeg; faster-whisper only for `--transcribe`; `requests` only for `--clipcafe`. |
| `make_graphics.py` | 9 | The episode's own graphics (`gráfico` beats). Renders one 4K PNG per row of the shotlist's *Gráficos / motion* table → `assets/graphic/`; 7 ids have a bespoke drawn renderer, the rest a titled card. `--force` · `--id <id>` · `--contact-only`. Pillow. |
| `kenburns.py` | 9 | Orientation-aware Ken Burns on stills, **4K by default**. `... IMAGE --dur 6` or `... E0XX-slug --all`. ffmpeg. |
| `trim_talk.py` | 9 | **The trim room — two phases.** *review* (`... TAKE.mp4 --script 05-script.md`): faster-whisper transcribes, proposes cuts, writes `TAKE.review.html` — the take as a **waveform** with every cut a draggable red block (move / resize edges / ✕ / «✂ corte aquí» / drag empty wave). Autosaves to `serve.py /trim-save`. Renders nothing. *apply* (`--apply`, or the page's «Aplicar corte» → `/trim`): `TAKE.trimmed.mp4` + `TAKE.words.json`. `--apply-now` = both, no review; `--rebuild-page` = regenerate the room, no whisper. faster-whisper + ffmpeg. |
| `edit_review.py` | 9 | `07c-edit.html` — quick pass over raw KB clips + trimmed takes, approve or feedback → `07c-review.txt`. Optional. `... E0XX-slug`. |
| `assemble.py` | 9 | First cut + render engine. Parses the shotlist spine, resolves assets, aligns beats to the VO (un-matched beats spread across gaps; total clamped to VO length) → `09-timeline.json` + `09-rough.mp4`. Bakes `brand/assets/grade.cube` if present. `--preview T0 T1` re-renders a region; `--final` → 4K master. ffmpeg. |
| `make_grade.py` | 9 | House colour grade → `brand/assets/grade.cube` (opt-in; `assemble.py` applies it if the file exists). `--explore FRAME.png` = a labelled grid of every preset on a frame; `--preset NAME --preview FRAME.png` = write the .cube + a raw|graded split. ffmpeg + numpy + pillow. |
| `edit_timeline.py` | 9 | `09-edit.html` — the cutting-room timeline: waveform + a block per beat + inspector (swap/trim/nudge/motion/approve). Renders `09-timeline.json`. `... E0XX-slug`. |
| `find_music.py` | 9 | Ominous-ambient music beds. `... "query"` appends to the pool; ticks in the pass's Music section (or `... --get <id>...`) → `brand/assets/music/`. Jamendo (`JAMENDO_CLIENT_ID`). |
| `idea_review.py` | 0 | `ideas/idea-review.html` — score + pick a hook-title + comment per idea → `idea-review.txt`. |
| `script_review.py` | 4 | `E0XX/05-script.html` — the script as a two-column editor: narration/explicador/promise-pay in the main column, production notes (`EN PANTALLA`/`NOTA`/`HOOK VISUAL`) + editable section durations in a sidebar, reference material (source-log, registers) read-only and collapsed. **Finalizar Stage 4 writes straight to `05-script.md`** — no Claude fold, the only review page that works this way. |
| `research_review.py` | 2 | `E0XX/02-research.html` — walk the source-log + dossier, tick OK/revisar + notes, approve → `02-research.txt`. |
| `package_review.py` | 10 | `E0XX/10-package.html` — pick title, pick thumbnail, review description → `10-package.txt`. `--init` scaffolds `08` + `09`. |
| `metrics.py` / `cost_update.py` | 12 / — | `12-metrics.html` — paste YouTube 48h/30d numbers → KPI-log row + retro block. `cost_update.py` refreshes the token-spend line on the dashboard. |
| `theme.py` | — | **the design system** (CSS tokens + components + HTML wrapper) for every generated page, in one file. Presentation only. Open only to restyle pages — never for pipeline/data work. Not a CLI. |
| `review_ui.py` | — | thin shim re-exporting `theme.py` as `STYLE` / `HELPERS` / `page` for older callers — not a CLI. |
| `pipeline.py` | — | the 12-stage manifest + `_STATUS.md` / `_queue.json` / `_loop.json` I/O — not a CLI. |
| `mediabin.py` | — | locates `ffmpeg` / `ffprobe` (PATH → `static-ffmpeg` → `imageio-ffmpeg`) — imported by the Stage-9 tools, not a CLI. |
| `dash.py` | — | regenerate `dashboard.html` from `_STATUS.md` + folders + KPI log + `_loop.json` heartbeat. |
| `serve.py` | — | `127.0.0.1:8765` — serves the dashboard + review pages (with HTTP Range, so `<audio>`/`<video>` seek); the finish buttons and autosaves POST here. |
| `advance.py` | — | the gate engine: `fold` a stage's decisions, `next` to the following stage. On entering Stage 9 it runs graphics + Ken Burns + the trim review pass. `--drain` for all. |

Stage 9 deps: `faster-whisper`, `static-ffmpeg` (or `ffmpeg` on PATH), `pillow`, `numpy`. `pip install faster-whisper static-ffmpeg numpy pillow`. See [brain/16-edit-and-delivery.md](../brain/16-edit-and-delivery.md).

**Review pages** (`*-review.html` / `10-package.html`, `07-style-pass.html`, `07c-edit.html`) mostly follow the same pattern: a dark browser page with per-item controls, "Finalizar Stage N" → a small `.txt` Claude (or `advance.py`, for the mechanical gates) folds back into the source doc. **`05-script.html` (Stage 4) is the exception** — it writes the edited script straight into `05-script.md` itself, no fold step. The `.html` is gitignored; the exported `.txt` (where one exists) is tracked.

## pull_assets.py

```
python tools/pull_assets.py --check-keys          # report tools/.env keys
python tools/pull_assets.py E0XX-slug --init       # scaffold 07-pull.tsv
python tools/pull_assets.py E0XX-slug              # -> 07-style-pass.md + 07-style-pass.html
# open 07-style-pass.html in a browser, tick thumbnails, "Finalizar Stage 7"
python tools/pull_assets.py E0XX-slug --download   # -> assets/stock|video|archive/, CREDITS.md, rows
```

**`07-style-pass.html`** is the central artifact of Stage 7 — one self-contained page,
three surfaces:
- **Intro row (top)** — the cold open (brain/02 §0). 5 inputs for your own paths/links +
  the suggested `intro` clips + an "intro" checkbox on every card below. Export order:
  own (1–5) → suggested → cards.
- **Left column** — pulled candidates per beat; click a thumbnail to approve it for that
  beat (persists in `localStorage`).
- **Right column** — the `07b-ai-prompts.md` prompts (parsed live): prompt + *copiar
  prompt* + an input for the path/URL of the image you generated.
- **Music section (bottom)** — the Jamendo pool (`find_music.py`) as ticked rows, plus
  *«Recursos propios»*: paste a local path or URL + `título · autor` + a licence
  (`CC0` / `CC-BY` / `CC-BY-SA` — nothing else offered). `--download` fetches it to
  `brand/assets/music/` + logs `LICENSES.md`; a bad/missing licence or no title is skipped.

**Finalizar Stage 7** writes all four surfaces into the episode folder (Chrome/Edge save
dialog; other browsers download it). Then `--download`:
- intro → `assets/intro/intro01…` (screen order) · beats → `assets/{stock,video,archive}/`
  · `ai:` → `assets/ai/<07b filename>` (local path copied, URL fetched)
  · `music:` → `brand/assets/music/` + `LICENSES.md`
- verifies resolution, appends `assets/CREDITS.md`, writes **`07-selection.md`** (the pass
  record — folds into `07-assets.md`), prints manifest rows.

`--download` falls back to `- [x]` lines in `07-style-pass.md` for beats only
(intro + AI need the picker). `07-style-pass.html` is gitignored;
`07-style-pass.md`, `07-picks.txt`, `07-selection.md` are tracked.

Run `build_ai_prompts.py` **before** the pull so the prompts appear in the pass.

`07-pull.tsv` — tab-separated, one row per beat that needs a pulled image/clip
(own-graphics beats don't go here): `beat · kind · source · query · opts`.

- `kind`:
  - `stock` — **video first** (Pexels + Pixabay video), then images fill the rest. A
    found stock clip beats hand-building the b-roll in the edit, so this is the default
    for generic b-roll. `opts motion=no` → images only · `motion=only` → video only.
  - `stock-img` — images only (pexels, pixabay, unsplash, openverse).
  - `video` — pexels + pixabay video only.
  - `intro` — pexels + pixabay video; name the beat `INTRO1`, `INTRO2`… — results go to
    the Intro row of the pass, not a beat. High-impact cold-open footage on the topic.
  - `archive` — the real artifact: met, commons.
- `source`: usually just repeat the kind keyword; or a comma list of specific sources
  (`commons,met` · `pexels-video,unsplash` · …).
- `opts`: `n=3` (total per beat) · `motion=no|only` · `orientation=landscape` ·
  `min=3000` (drop smaller; also filters video by width, e.g. `min=1920`) ·
  `license=cc0,by` (openverse) · `must=hokusai,fuji` (archive only).

**Keys** go in `tools/.env` (gitignored — copy `tools/.env.example`). Without it, only the
keyless sources run (Openverse, Met, Wikimedia Commons). Get them: Pexels `pexels.com/api`, Pixabay
`pixabay.com/api/docs`, Unsplash `unsplash.com/developers` (use the Access Key).

**Known limits**
- Pixabay free API delivers images ≤ 1280 px (inset use only). Its video is fine.
- Wikimedia Commons often carries the same PD scans at higher resolution than Met
  (Great Wave: 8242 px) with cleaner artist metadata — good for isolating a
  specific artist (e.g. Katsushika Ōi vs. Hokusai).
- Archive keyword search is filtered for relevance. Search ranks loosely, so add
  `must=<name>` to force the subject (e.g. `must=hokusai`). A too-narrow query can
  return zero — broaden the query, keep `must`.
- `stock` is generic illustrative b-roll only, never "the real thing" (brain/12).
