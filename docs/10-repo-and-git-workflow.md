# 10 — Repo & Git Workflow

The project lives **locally + GitHub**. This repo (`D:\Youtube`) is the single source of truth for the channel's planning, docs, templates, scripts, and research. No Obsidian, no other tracker.

## Repo

- Local path: `D:\Youtube`
- Default branch: `main`
- Remote: **`https://github.com/joshrubio/Exodo-Brain.git`** (account: `joshrubio`). **Private** (set 2026-08-29). Keep it private — it holds unpublished scripts, editorial internals and the separation policy.
- First push done 2026-08-29 (`main` tracks `origin/main`).

### Day-to-day

```bash
git push          # main already tracks origin/main
```

## What is and isn't versioned

**Versioned (text):** all `docs/`, `templates/`, `ideas/`, `episodes/**/*.md` and `*.csv`, `research/**/*.md`, `README`, `.gitignore`.

**Not versioned (see `.gitignore`):**
- Media and heavy binaries (`.mp4`, `.wav`, `.psd`, project files, …).
- `episodes/**/assets/` contents (archive downloads, exports, renders).
- `research/dieck-docs/transcripts/` — third-party transcripts, copyright, local only.

Large media lives outside git (shared drive / cloud). Reference it from the episode's `06-shotlist.md`, don't commit it.

## Branching

Lightweight:
- Small edits to `docs/`, `ideas/`, `_STATUS.md` → commit straight to `main`.
- A full episode in progress → branch `episode/E0XX-<slug>`, merge to `main` when the episode publishes (or at picture lock). Keeps `main` history readable per episode.
- Format-spec revisions from a transcript study → branch `research/format-v1`.

## Commit messages

English, imperative, scoped:

```
docs: tighten reflection sourcing rule
E007: add research dossier + source log
ideas: approve theme T03 (speculative manias)
status: E004 -> stage 8 (edit)
```

## Cadence

- Commit at every stage gate of an episode (so `_STATUS.md` and the folder move together).
- Push at least daily while anything is in progress.

## Access

- Carmen + Josh: write access.
- No third-party collaborators without a separation-policy review (`docs/05-separation-policy.md`) — scripts name real people before publication.

## Backups

GitHub is the off-machine copy. Additionally keep the media/asset store backed up on its own (git does not hold it).
