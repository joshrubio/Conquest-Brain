# tools/

Small scripts for the episode pipeline. Python 3.11+, deps: `requests`, `reportlab`, `pillow`, `PyYAML`.

| Script | Stage | What it does |
|--------|-------|--------------|
| `factcheck.py` | 5 | Layer 1 deterministic fact-check. `python tools/factcheck.py 05-script.md 03-source-log.csv` → PASS/FAIL. |
| `build_ai_prompts.py` | 7 | Scaffolds `07b-ai-prompts.md` for AI-illustration beats (docs/15). `... E0XX-slug <img-slug> ...` / `... --check`. |
| `pull_assets.py` | 7 | Candidate pull from free APIs (Met, AIC, Pexels, Pixabay, Unsplash, Openverse). See below. |
| `build_idea_pitch.py` | 0 | Renders `ideas/idea-pool.md` as a pitch PDF for Carmen. Data is inline — sync by hand. |

## pull_assets.py

```
python tools/pull_assets.py --check-keys          # report tools/.env keys
python tools/pull_assets.py E0XX-slug --init       # scaffold 07-pull.tsv
python tools/pull_assets.py E0XX-slug              # -> 07-candidates.md + 07-candidates.html
# open 07-candidates.html in a browser, tick thumbnails, "Exportar 07-picks.txt"
python tools/pull_assets.py E0XX-slug --download   # -> assets/stock|video|archive/, CREDITS.md, rows
```

**Picker UX:** `07-candidates.html` is a self-contained two-column Stage-7 surface.
- **Left** — pulled candidates per beat; click a thumbnail to select (persists in `localStorage`).
- **Right** — the `07b-ai-prompts.md` prompts (parsed live). Each panel: the prompt +
  a *copiar prompt* button + an input for the path/URL of the image you generated. For
  beats the pull couldn't cover.
- **Exportar 07-picks.txt** writes both — ticked candidates *and* filled AI paths — into
  the episode folder (Chrome/Edge save dialog; other browsers download it).

`--download` reads `07-picks.txt` if present (else `- [x]` lines in `07-candidates.md`
for the candidates only). Candidate picks → `assets/stock|video|archive/`; `ai:` rows →
`assets/ai/<07b filename>` (local path is copied, URL is fetched), verified + added to
the manifest as *ilustración propia (IA)*. `07-candidates.html` is gitignored;
`07-candidates.md` and `07-picks.txt` are tracked.

Run `build_ai_prompts.py` **before** the pull so the prompts appear in the picker.

`07-pull.tsv` — tab-separated, one row per beat that needs a pulled image/clip
(own-graphics beats don't go here): `beat · kind · source · query · opts`.

- `kind`:
  - `stock` — **video first** (Pexels + Pixabay video), then images fill the rest. A
    found stock clip beats hand-building the b-roll in the edit, so this is the default
    for generic b-roll. `opts motion=no` → images only · `motion=only` → video only.
  - `stock-img` — images only (pexels, pixabay, unsplash, openverse).
  - `video` — pexels + pixabay video only.
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
