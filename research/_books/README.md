# research/_books/ — reference books, local only

Copyrighted books used to **verify** claims for the dossiers and scripts. Kept
local, **never committed** (`.gitignore`), same as `research/dieck-docs/transcripts/`.

## Why this folder exists

Reading a book PDF through Claude's Read tool renders each page as an image
(~1.5k+ tokens/page, 20-page cap) — useless for a 400-page book. Converting the
PDF to Markdown once makes the text greppable and cheap to read in targeted
chunks.

## Workflow

```bash
pip install 'markitdown[pdf]'
python -m markitdown "ohno-tps.pdf"        > research/_books/ohno-tps.md
python -m markitdown "cusumano-1985.pdf"   > research/_books/cusumano-1985.md
python -m markitdown "liker-toyota-way.pdf" > research/_books/liker-toyota-way.md
```

Then Claude greps/reads only the relevant chapters (e.g. Cusumano's 1949–50
crisis chapter, Liker's genchi-genbutsu / "Ohno circle" section).

## Rules

- **Never commit** the PDFs or the `.md` conversions. This folder is gitignored
  except this README.
- Cite the book properly in `03-source-log.csv` (title, author, publisher, year,
  **page number** from the conversion).
- The script quotes only **short excerpts** under fair use (`brain/01` §4,
  `brain/04` §5). The conversion is a research aid, not a text to reproduce.
- Claude's summary of a book is **not a source** (`brain/01` §9) — the citation
  points at the book, and a human confirms the load-bearing ones.

## Current

| File | Source-log ID | Used for |
|------|---------------|----------|
| `ohno-tps.md` | S01 | Toyota/Ohno (E002) — the primary; his own account |
| `cusumano-1985.md` | S03 | E002 beats 22–24 — independent academic chronology |
| `liker-toyota-way.md` | S12 | E002 beat 20 — the "Ohno circle", 20 years of shop-floor friction |
