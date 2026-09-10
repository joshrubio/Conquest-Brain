---
doc: 14-fact-check-protocol
summary: "Stage 5, fully automated. L1 deterministic (factcheck.py) + L2 agent edit-pass that applies the fixes. No human step, no sign-off."
stage: [5]
read_when: "fact-checking a script; running the L2 pass; setting up the fact-check tools"
pairs_with: [01-editorial-and-sourcing, 04-legal-and-ethics, 06-production-workflow]
tools: [factcheck.py, fact-check-auto-prompt.md]
authority: canonical
---

# 14 — Fact-Check Protocol

Stage 5. **Fully automated. No human step.** Two passes:

- **L1 deterministic** — `tools/factcheck.py`. Consistency only. Must `PASS`.
- **L2 agent edit-pass** — an LLM reads the script + the source-log and **applies the corrections directly to `05-script.md`**, logging every change.

The script goes to record when L1 is `PASS` and the L2 pass has run and written its changelog. No sign-off, no manual flag-resolution.

**Accepted trade-off:** no second pair of human eyes on factual accuracy. The safeguards are (a) every load-bearing claim already carries a `[S..]` to a Tier A/B source from Stage 2, (b) L1 catches every broken/missing tag mechanically, (c) L2 re-reads every claim against its source and rewrites what doesn't hold, (d) the legal/ethics + independence/COI checklist is still ticked by a human once, at Stage 11, before upload.

## Layer 1 — Deterministic pass

`tools/factcheck.py` on `05-script.md` + `03-source-log.csv`. No judgement.

1. Every `[S..]` tag resolves to a row in `03-source-log.csv`.
2. Every source-log row has a `tier` (A/B/C/D) and a `rights_status`.
3. **Orphan-claim heuristic:** sentences with a number, date, proper noun, or quotation marks but **no `[S..]`** → candidate unsourced claims.
4. **Tier check:** every claim whose only `[S..]` is Tier C/D → must be upgraded or reframed as disputed.
5. Reports counts.

Output: `04-factcheck-auto.md` (Layer 1 section), `PASS` / `FAIL`.

**Gate:** `PASS` — zero unresolved tag/tier errors; every orphan candidate either tagged in the script or confirmed non-factual by L2.

## Layer 2 — Agent edit-pass

Run by the agent (this session, or a subagent): `templates/fact-check-auto-prompt.md` — script + source-log in. The model:

1. **Analyses** every claim against its `[S..]` source, plus interpretation-as-fact, quotes, hedging, pop-psychology, and legal/ethics/COI risk (six tables → `04-factcheck-auto.md`). **Cited authorities:** every named psychologist / theorist / study in the script (esp. dense on the Ensayo track, `brain/09` §"Ensayo") is cross-checked against `research/citation-shelf.md` — on the shelf and `Verified` ✅, attributed by the right field, and the claim matches the shelf's wording. A citation not on the shelf, or on it but unverified, is a flag: add + verify against the primary source, or cut the specificity.
2. **Produces exact corrections** — for every `desajuste`, `sin tag`, missing hedge, over-stated claim, unmarked translation, or interpretation-as-fact: the precise old text → new text.
3. The agent **applies each correction to `05-script.md`** and writes the **Changelog** table in `04-factcheck-auto.md` (what changed, why, which line).

Rules the L2 pass follows:
- **The LLM is not a source** ([01](01-editorial-and-sourcing.md) §9). A correction can only tighten the script to what the *cited source* supports, add a hedge, add an attribution, or cut a line — **never add a new fact**.
- A claim the source can't support and that can't be hedged or attributed → **cut it or mark it disputed on screen**, don't guess.
- **L2 resolves everything now — it does not create a "verify later" queue.** A claim it can't confirm from the source-log description is hedged, attributed, or cut *in this pass*. The only thing that waits is the **table-6** legal/ethics/COI/dignity judgement (below). "Would be nice to double-check against the book" is not a blocker — if the pass wants to note a recoverable trim, that goes in the script's own notes as an optional future improvement, never as a gate.
- Legal/ethics/COI flags that need a judgement call (a defamation risk, a sensitive-topic handling question) → **leave the line, flag it loudly in the Changelog** for the Stage 11 human tick. Don't silently "fix" those.

**Gate:** L1 `PASS` + L2 pass run + Changelog written → Stage 6.

## Files

| File | Pass |
|------|------|
| `tools/factcheck.py` → `04-factcheck-auto.md` (L1) | 1 |
| `templates/fact-check-auto-prompt.md` → `04-factcheck-auto.md` (L2 tables + Changelog) + edits to `05-script.md` | 2 |

## Roadmap

- Now: L1 script; L2 run by the agent from the prompt, edits applied hand-in-loop.
- Next: `tools/factcheck.py --l2` calls an LLM API, writes the L2 tables + a machine-readable diff, and with `--apply` patches `05-script.md` in one command. `[S..]` contiguity check. Source-URL link-rot check.
