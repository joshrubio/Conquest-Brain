---
doc: 10-repo-and-git-workflow
summary: "Repo layout, what is / isn't versioned, branching, commit-message convention, cadence, backups."
stage: all
read_when: "committing; unsure what belongs in git; setting up the repo"
pairs_with: [06-production-workflow]
authority: canonical
---

# 10 — Repo & Git Workflow

The project lives **locally + GitHub**. This repo (`D:\Conquest-Brain` locally) is the single source of truth for the channel's planning, docs, templates, scripts, and research. No Obsidian, no other tracker.

## Repo

- Local path: `D:\Conquest-Brain` (was `D:\Exodo-brain`; before that `D:\Youtube`). **Rename the folder on disk to match** — nothing in the repo hard-codes the path except this line.
- Default branch: `main`
- Remote: **`https://github.com/joshrubio/Conquest-Brain.git`** (account: `joshrubio`). Rename the GitHub repo `Exodo-Brain → Conquest-Brain`, then `git remote set-url origin https://github.com/joshrubio/Conquest-Brain.git` (GitHub redirects the old URL, but update it). **Private** (set 2026-08-29) — it holds unpublished scripts, editorial internals, real names.
- First push done 2026-08-29 (`main` tracks `origin/main`).

### Day-to-day

```bash
git push          # main already tracks origin/main
```

## What is and isn't versioned

**Versioned (text):** all `brain/`, `templates/`, `ideas/`, `episodes/**/*.md` and `*.csv`, `research/**/*.md`, `README`, `.gitignore`.

**Not versioned (see `.gitignore`):**
- Media and heavy binaries (`.mp4`, `.wav`, `.psd`, project files, …).
- `episodes/**/assets/` contents (archive downloads, exports, renders).
- `research/dieck-docs/transcripts/` — third-party transcripts, copyright, local only.

Large media lives outside git (shared drive / cloud). Reference it from the episode's `06-shotlist.md`, don't commit it.

## Branching

Lightweight:
- Small edits to `brain/`, `ideas/`, `_STATUS.md` → commit straight to `main`.
- A full episode in progress → branch `episode/E0XX-<slug>`, merge to `main` when the episode publishes (or at picture lock). Keeps `main` history readable per episode.
- Format-spec revisions from a transcript study → branch `research/format-v1`.

## Commit messages

English, imperative, scoped:

```
brain: tighten reflection sourcing rule
E007: add research dossier + source log
ideas: approve theme T03 (speculative manias)
status: E004 -> stage 8 (edit)
```

## Cadence

- Commit at every stage gate of an episode (so `_STATUS.md` and the folder move together).
- Push at least daily while anything is in progress.

## Access

- Usuario 001 + Usuario 002: write access.
- No third-party collaborators without an independence/COI review ([brain/05](05-independence-and-coi.md)) — scripts name real people before publication.

## Backups

GitHub is the off-machine copy. Additionally keep the media/asset store backed up on its own (git does not hold it).
