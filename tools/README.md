# tools/

Small scripts for the episode pipeline. Python 3.11+, deps: `requests`, `reportlab`, `pillow`, `PyYAML`.

| Script | Stage | What it does |
|--------|-------|--------------|
| `factcheck.py` | 5 | Layer 1 deterministic fact-check. `python tools/factcheck.py 05-script.md 03-source-log.csv` → PASS/FAIL. |
| `build_ai_prompts.py` | 7 | Scaffolds `07b-ai-prompts.md` for AI-illustration beats (docs/15). `... E0XX-slug <img-slug> ...` / `... --check`. |
| `pull_assets.py` | 7 | **The Stage-7 hub.** Pulls candidates from free APIs → `07-photography-pass.html` (per-beat candidates + AI prompts + intro). See below. |
| `kenburns.py` | 9 | Orientation-aware Ken Burns on stills, **4K by default**. `... IMAGE --dur 6` or `... E0XX-slug --all`. ffmpeg. |
| `trim_talk.py` | 9 | Trim silences + fillers from a take. `python tools/trim_talk.py TAKE.mp4` → `TAKE.trimmed.mp4` + `TAKE.cuts.md`. faster-whisper. |
| `edit_review.py` | 9 | Build `07c-edit.html` — watch every KB clip + trimmed take, approve or feedback → `07c-review.txt`. `... E0XX-slug`. |
| `find_music.py` | 9 | Ominous-ambient music beds. `... "query"` appends to the pool; ticks in the pass's Music section (or `... --get <id>...`) → `brand/assets/music/`. Jamendo (`JAMENDO_CLIENT_ID`). |
| `idea_review.py` | 0 | `ideas/idea-review.html` — Carmen scores + picks a hook-title + comments per idea → `idea-review.txt`. |
| `package_review.py` | 10 | `E0XX/10-package.html` — pick title, pick thumbnail, review description with Carmen → `10-package.txt`. `--init` scaffolds `08` + `09`. |
| `review_ui.py` | — | shared dark-theme HTML shell for the review pages (not a CLI). |

Stage 9 deps: `ffmpeg` on PATH, `faster-whisper`, `pillow`. See [docs/16-edit-and-delivery.md](../docs/16-edit-and-delivery.md).

**Review pages** (`*-review.html` / `10-package.html`, `07-photography-pass.html`, `07c-edit.html`) all follow the same pattern: a dark browser page with per-item controls, "Exportar" → a small `.txt` Claude folds back into the source doc. The `.html` is gitignored; the exported `.txt` is tracked.

## pull_assets.py

```
python tools/pull_assets.py --check-keys          # report tools/.env keys
python tools/pull_assets.py E0XX-slug --init       # scaffold 07-pull.tsv
python tools/pull_assets.py E0XX-slug              # -> 07-photography-pass.md + 07-photography-pass.html
# open 07-photography-pass.html in a browser, tick thumbnails, "Exportar 07-picks.txt"
python tools/pull_assets.py E0XX-slug --download   # -> assets/stock|video|archive/, CREDITS.md, rows
```

**`07-photography-pass.html`** is the central artifact of Stage 7 — one self-contained page,
three surfaces:
- **Intro row (top)** — the cold open (docs/02 §0). 5 inputs for your own paths/links +
  the suggested `intro` clips + an "intro" checkbox on every card below. Export order:
  own (1–5) → suggested → cards.
- **Left column** — pulled candidates per beat; click a thumbnail to approve it for that
  beat (persists in `localStorage`).
- **Right column** — the `07b-ai-prompts.md` prompts (parsed live): prompt + *copiar
  prompt* + an input for the path/URL of the image you generated.

**Exportar 07-picks.txt** writes all three into the episode folder (Chrome/Edge save
dialog; other browsers download it). Then `--download`:
- intro → `assets/intro/intro01…` (screen order) · beats → `assets/{stock,video,archive}/`
  · `ai:` → `assets/ai/<07b filename>` (local path copied, URL fetched)
- verifies resolution, appends `assets/CREDITS.md`, writes **`07-selection.md`** (the pass
  record — folds into `07-assets.md`), prints manifest rows.

`--download` falls back to `- [x]` lines in `07-photography-pass.md` for beats only
(intro + AI need the picker). `07-photography-pass.html` is gitignored;
`07-photography-pass.md`, `07-picks.txt`, `07-selection.md` are tracked.

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
  - `archive` — the real artifact: met, commons, aic.
- `source`: usually just repeat the kind keyword; or a comma list of specific sources
  (`commons,met` · `pexels-video,unsplash` · …).
- `opts`: `n=3` (total per beat) · `motion=no|only` · `orientation=landscape` ·
  `min=3000` (drop smaller; also filters video by width, e.g. `min=1920`) ·
  `license=cc0,by` (openverse) · `must=hokusai,fuji` (archive only).

**Keys** go in `tools/.env` (gitignored — copy `tools/.env.example`). Without it, only the
keyless sources run (Openverse, Met, AIC). Get them: Pexels `pexels.com/api`, Pixabay
`pixabay.com/api/docs`, Unsplash `unsplash.com/developers` (use the Access Key).

**Known limits**
- Pixabay free API delivers images ≤ 1280 px (inset use only). Its video is fine.
- Wikimedia Commons often carries the same PD scans at higher resolution than Met
  (Great Wave: 8242 px) with cleaner artist metadata — good for isolating a
  specific artist (e.g. Katsushika Ōi vs. Hokusai).
- AIC's IIIF CDN can 403 `--download` from some networks/CI. The candidate URL is
  still correct — it downloads fine from a normal browser; if the tool fails on an
  `aic` pick, open its page and use the Download button.
- Archive keyword search is filtered for relevance. Search ranks loosely, so add
  `must=<name>` to force the subject (e.g. `must=hokusai`). A too-narrow query can
  return zero — broaden the query, keep `must`.
- `stock` is generic illustrative b-roll only, never "the real thing" (docs/12).
