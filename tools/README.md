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
python tools/pull_assets.py E0XX-slug --init      # scaffold 07-pull.tsv
python tools/pull_assets.py E0XX-slug             # -> 07-candidates.md
# tick the keepers "- [x]" in 07-candidates.md, then:
python tools/pull_assets.py E0XX-slug --download  # -> assets/, CREDITS.md, manifest rows
python tools/pull_assets.py --check-keys
```

`07-pull.tsv` — tab-separated, one row per beat that needs a pulled image/clip
(own-graphics beats don't go here): `beat · kind (stock|archive|video) · source · query · opts`.

- `source`: comma list or a group keyword — `stock` = pexels,pixabay,unsplash,openverse · `archive` = met,aic · video only does pexels,pixabay.
- `opts`: `n=4` · `orientation=landscape` · `min=3000` (drop candidates whose long side is smaller) · `license=cc0,by` (openverse) · `must=hokusai,fuji` (archive only — every term must appear in artist/title/tags).

**Keys** go in `tools/.env` (gitignored — copy `tools/.env.example`). Without it, only the
keyless sources run (Openverse, Met, AIC). Get them: Pexels `pexels.com/api`, Pixabay
`pixabay.com/api/docs`, Unsplash `unsplash.com/developers` (use the Access Key).

**Known limits**
- Pixabay free API delivers images ≤ 1280 px (inset use only). Its video is fine.
- AIC blocks direct image download from some networks/CI — the candidate URL is still
  correct; open the artwork page and use its Download button, or run the tool from a
  normal connection.
- Archive keyword search is filtered for relevance. Museum search engines rank
  loosely, so add `must=<name>` to force the subject (e.g. `must=hokusai`).
  A too-narrow query can return zero — broaden the query, keep `must`.
- `stock` is generic illustrative b-roll only, never "the real thing" (docs/12).
