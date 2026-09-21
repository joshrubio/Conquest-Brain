# Conquest-Oficial

> **Conquest** (English spelling, always — never "Conquista") · channel **Conquest-Oficial** · handle **`@conquestoficial`** · own new YouTube channel, category *Education*. Renamed from *Éxodo* on 2026-08-31. Brand spec: [brain/03-brand-identity.md](brain/03-brand-identity.md).

A Spanish-language journalistic-documentary YouTube channel — narrated real cases that close on a psychological/human reflection and a surgical, applicable takeaway. Run by two people — **Usuario 001** (writes every script, production, tech) and **Usuario 002** (editorial lead, research direction); ideation is shared. Roles are assignable items, not identities; real names and the split live in [brain/USERS.md](brain/USERS.md). Both founders are Venezuelan journalists, part of the Venezuelan exodus; the name says what comes after the leaving — *the conquest* is the evidentiary work of establishing what's true. It is voice and motive, never an episode subject. Narration is assigned per episode.

Reference format: **Dieck Docs** (Farid Dieck). Standalone project — not a phase of, or funnel for, anything.

**Working here (human or agent)? Start with [AGENTS.md](AGENTS.md)** → it routes you to `brain/INDEX.md` and the rest. Every doc has YAML frontmatter (`summary`, `stage`, `read_when`) so you can find the right file without reading all of them.

## What this repo is

Documentation, templates, per-episode folders, and the `tools/` that run the pipeline. Managed locally + GitHub ([brain/10-repo-and-git-workflow.md](brain/10-repo-and-git-workflow.md)).

## Language policy

- **`brain/`, `research/` analysis** — English.
- **`templates/`, `episodes/`, `ideas/`** — Spanish (the published content is Spanish).
- Commit messages, file/asset names, code comments — English.

## Folder map

| Path | Purpose |
|------|---------|
| `brain/` | Standing rules 00–20 (+ `INDEX.md`, `USERS.md`): charter, editorial/sourcing, format, brand, legal, independence, workflow (12 stages), publishing, tone, reflection, git, visual rhythm, available-material, hook naming, fact-check, AI illustration, edit & delivery, dashboard & advance, monetization, lessons, experimental-clip (Ensayo, canonical). |
| `templates/` | Blank fill-in templates for every stage. |
| `episodes/` | One folder per episode. `_TEMPLATE-episode-folder/` to copy; `E000-EXAMPLE-*` worked reference; `_STATUS.md` master index (written by `advance.py` / `serve.py`). |
| `ideas/` | Two **format tracks** (`tracks.md`): **Documental** (real cases — everything the channel does now) and **Ensayo** (a film / series / game and its reception, or a real case told through its dramatised film — short clips under fair use, `brain/20`). Shared ideation → **idea pool** (`idea-pool.md`, `DOC-`/`ENS-` codes), scored with `idea-rubric.md`. |
| `research/` | Reverse-engineering the Dieck Docs format from transcripts (kept local — copyright). `_books/` holds reference books converted to markdown (gitignored). |
| `tools/` | The pipeline scripts — full index in [tools/README.md](tools/README.md). The **dashboard** (`dash.py` + `serve.py` on `127.0.0.1:8765`) drives everything; `advance.py` is the gate engine; Stage 7 = `pull_assets.py`, Stage 9 = `make_graphics.py` → `kenburns.py` → `trim_talk.py` (the trim room) → `assemble.py` → `edit_timeline.py` (the edit room), optional grade `make_grade.py`; `pickup_room.py` for re-recorded lines. Keys in `tools/.env` (gitignored). |
| `brand/` | `naming-exploration.md`; `assets/` — avatar, banner, music, `grade.cube` (opt-in house LUT). |

## Core non-negotiables (full text in [brain/00-project-charter.md](brain/00-project-charter.md))

1. **Subjects are public and documented** — public figure, historical case or event, company/practice, or documented collective phenomenon; for the **Ensayo** track also a released creative work and its documented public reception (`brain/20`). Never private individuals, never unrecorded cases.
2. **No episode subject drawn from people Usuario 001 or Usuario 002 personally know** — not even anonymized ([brain/05](brain/05-independence-and-coi.md)).
3. **No factual claim without a cited source.** No invented data or quotes.
4. The channel stays **independent in brand, folder, and workflow** — no co-branding or shared identity with any other channel or venture.

## Getting started on a new episode

1. Either founder proposes the idea, assigns a track (Documental / Ensayo), with **3 hook-titles** ([brain/13](brain/13-hook-naming.md)).
2. **Available-material cross-check** ([brain/12](brain/12-available-material-protocol.md)) — public sources only.
3. Add to [ideas/idea-pool.md](ideas/idea-pool.md); score with [ideas/idea-rubric.md](ideas/idea-rubric.md).
4. If it passes: copy `episodes/_TEMPLATE-episode-folder/` → `episodes/E0XX-<slug>/`. Usuario 001 writes; assign narrator in the brief.
5. Work the 12 stages in order from the **dashboard** (`python tools/serve.py` → `http://localhost:8765`) — [brain/06](brain/06-production-workflow.md), [brain/17](brain/17-dashboard-and-advance.md). Each stage has a review page; "Finalizar Stage N" closes the gate, `advance.py` moves on. Fact-check (5) = `factcheck.py` + LLM pass + Usuario 002's sign-off ([brain/14](brain/14-fact-check-protocol.md)); assets (7) = **`07-style-pass.html`** (`pull_assets.py`); edit (9) = graphics → Ken Burns → the **trim room** (`<take>.review.html` — waveform, drag the cuts) → `assemble.py` first cut → the **edit room** (`09-edit.html`) → music → subtitles → 4K master ([brain/16](brain/16-edit-and-delivery.md)).
6. `_STATUS.md` updates itself as gates close.

## How the tooling works now

The pipeline is mostly mechanical; a few behaviours are worth knowing before you open a room or start a render.

**Edit room (Stage 9) — `09-timeline.json` is the authored edit.** Each beat owns its `id` and `dur`; `in`/`out` are derived. The room swaps assets, splits/merges/reorders beats, cuts audio, and re-syncs to the voice on demand ([brain/16](brain/16-edit-and-delivery.md)). The aligner is a global fuzzy match of each beat's script line against the recorded words, and a **sync report** says what share of beats actually have their line inside their window — low sync is warned, not hidden.

**Trim cuts are queued, not rendered.** A cut in the trim room or the edit room saves in seconds (`trim_talk.py --soft` refreshes the words and the room's `09-vo.m4a`); the heavy 4K trim renders once, on «Finalizar» / «Renderizar ahora» / `assemble.py --rough|--final`. While cuts are pending the room plays a small **proxy of the original take** and **jumps the cut zones** (red ticks on the timeline) so picture and voice stay in sync. Every audio cut is journalled with a timestamp and **Ctrl+Z / Ctrl+Shift+Z undoes or redoes cuts** exactly, including after a reload.

**The 4K master is built to be gentle on a laptop.** It renders in resumable 10-beat chunks (a crash, sleep or cancel loses at most one chunk), at below-normal priority, using about 60 % of the cores (`CONQUEST_CPU_SHARE` to change it), and holds the PC awake while it runs. Only one render per episode runs at a time; a second request is refused. Keep the laptop plugged in with the lid open — Windows still sleeps on lid close. Just before each final render `assemble.py` writes **`09-final-audit.txt`**: beats out of spine order, low sync or a mismatched opening, assets with rights still `PENDIENTE`, unlabelled AI images. It warns; it never blocks. The render takes what the edit room saved — a file the room chose is never silently replaced by Stage 7.

**Soundtrack rule.** An episode's audio is the narrator's voice plus our own licensed background bed — never music, songs or clip audio from what the episode is about ([brain/16](brain/16-edit-and-delivery.md) §The soundtrack).

**Stage 7 (assets).** Every beat gets its own row and every uncovered beat says why; your own picks and custom URLs override pulled candidates and are downloaded once. AI recreations — including photoreal faces and recreated documents — are a first-class visual register, carried by the `Representación pictórica` label ([brain/15](brain/15-ai-illustration-protocol.md)). Rights decisions per beat live in `07-rights.md`.

**Ensayo and clips.** Clips are the main resource and stills the fallback. Fragments ≤ ~5 s, never two of the same scene back to back, ≤ ~15 % of runtime in total ([brain/20](brain/20-experimental-clip-protocol.md) §4.4). `tools/clip_finder.py` searches a local `.srt`, a whisper transcript or the **clip.cafe API** and cuts the excerpt. A real case can be told with its dramatised film as the scaffold — the narrator follows the film, adds context, and *matiza* what looks too convenient or disputed; facts come from the record, never from the film (`brain/20` §3, Mode B).

**Dashboard loop.** `/atiende` drains the queue of mechanical stages; it stops itself after an hour with no real change.

## Status

- **Brand:** decided (name, channel type, spelling, category, palette, typography, case-file device, 4K). House colour grade = the near-neutral `clean` LUT (`brand/assets/grade.cube`, applied by `assemble.py` if present). To do: secure `@conquestoficial` on IG/TikTok, produce logo SVG + thumbnail template, re-export banner at 2560×1440, trademark clearance (class 41, lawyer, before registering).
- **Format specs (`brain/02`, `08`, `09`) are v1** — validated against 6 Dieck Docs transcripts.
- **Idea pool:** ~23 ideas across both tracks (latest: **ENS-04**, Ray Charles told through *Ray* (2004) — the first film-as-scaffold episode). `python tools/idea_review.py` → `ideas/idea-review.html` for Usuario 002 to score + pick hook-titles.
- **E001 Hokusai** — edit done and package approved; at Stage 11 (publication).
- **E002 Toyota / Taiichi Ohno** — edit closed; the 4K master is rendered (`E002-…-v2.mp4`).
- **E003 Tulipomanía** — Stage 9: assets covered with rights logged, timeline synced to the voice, trim cuts queued.
- **E004 Coca-Cola** — Stage 6 (shotlist).
- **Media stack:** ffmpeg + faster-whisper run locally (via `static-ffmpeg`; `tools/mediabin.py` locates the binaries). Music: Jamendo pool built; pick 3–5 beds from the style pass.
