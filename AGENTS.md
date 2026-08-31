# AGENTS.md — start here

You're in the **Conquest-Oficial** repo: a Spanish-language journalistic-documentary
YouTube pipeline (planning, rules, templates, per-episode folders, and the
`tools/` that run it). Reference format: Farid Dieck's *Dieck Docs*.

**Don't read the whole repo.** Every doc has YAML frontmatter (`summary`,
`stage`, `read_when`, `pairs_with`). Load an index, then open the 1–3 files it
points you to.

## Read first

| Then you want to… | Open |
|-------------------|------|
| know the standing rules | **`brain/INDEX.md`** — routes you to ~2 of the 18 rule docs |
| know what episode is where | `episodes/_STATUS.md` |
| fill in a stage | `templates/INDEX.md` |
| learn the system in prose (ES) | `documentación/00-empieza-aquí.md` |
| run a pipeline script | `tools/README.md` |
| judge/score an idea | `ideas/README.md` + `ideas/idea-rubric.md` |
| know who Usuario 001 / 002 are | `brain/USERS.md` |
| change how the dashboard / pages **look** | `tools/theme.py` — and only that |

## The dashboard's design is quarantined

All CSS/HTML chrome for every generated page lives in **one** file,
`tools/theme.py` (presentation only — no pipeline logic, no data). Everything
else — `dash.py`, `pipeline.py`, the review tools — builds *structure* and
imports the look from there.

**Consequence for you:** when you read the dashboard's output (`_STATUS.md`,
`episodes/_queue.json`, `_exports/*.json`, the `*.txt` exports) or fold a gate,
you never open a styled file and the design never enters your context. Only open
`tools/theme.py` if the task is literally "restyle the pages".

## Layout

| Dir | What | Language |
|-----|------|----------|
| `brain/` | standing rules 00–16 + `USERS.md` — the canon | EN, terse |
| `templates/` | one blank fill-in per stage | ES |
| `episodes/` | one folder per episode; `_TEMPLATE-episode-folder/` to copy; `_STATUS.md` is the master index; `E000-EXAMPLE-*` is a worked reference | ES |
| `documentación/` | human guides — the same rules in prose, with examples | ES |
| `tools/` | the scripts (+ `.env` for API keys, gitignored) | — |
| `ideas/` | the idea pool + the scoring rubric + the two tracks | ES |
| `research/` | reverse-engineering the Dieck format from transcripts (local only) | EN analysis |
| `brand/` | name exploration, assets, music | — |

## Rules of the road

- **Language:** `brain/` + `research/` analysis = English. `templates/`,
  `episodes/`, `ideas/`, `documentación/` = Spanish. Commit messages, file /
  asset names, code comments = English.
- **`Usuario 001` / `Usuario 002` are slots, not people.** Real names live only
  in `brain/USERS.md` and `documentación/configuración-usuarios.md`.
- **Any gate can be signed by one person.** There is no second-reviewer
  requirement anywhere.
- **Git:** commit only when asked; branch off `main` first; end commit messages
  with the `Co-Authored-By` trailer (see `brain/10`).
- **The 12 stages are gated** — don't start one until the previous gate passes
  (`brain/06`).
- **When you change a rule:** edit the doc, its frontmatter `summary`, and its
  row in the relevant `INDEX.md`.

## The pipeline in one line

idea (`ideas/`) → brief → research (`02` + `03-source-log.csv`) → outline →
script (`05`) → fact-check (L1 `factcheck.py` + L2 prompt, no sign-off) →
shotlist (`06`) → assets + style pass (`07-style-pass.html`) → record → edit
(`kenburns` → `trim` → `07c-edit.html` → b-roll → music → subs) → package
(`10-package.html`) → publish → retro.
