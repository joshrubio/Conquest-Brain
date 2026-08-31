---
doc: 14-fact-check-protocol
summary: "Stage 5. L1 deterministic (factcheck.py) + L2 LLM-assisted (prompt). The writer resolves every flag. No human sign-off layer."
stage: [5]
read_when: "fact-checking a script; setting up or running the fact-check tools"
pairs_with: [01-editorial-and-sourcing, 04-legal-and-ethics, 06-production-workflow]
tools: [factcheck.py, fact-check-auto-prompt.md]
authority: canonical
---

# 14 — Fact-Check Protocol

Stage 5. **Two layers, both automated. No human sign-off layer** — the L2 pass is the last check before record.

- **L1 deterministic** — a script. Consistency only.
- **L2 LLM-assisted** — a prompt. Flags claims, interpretation-as-fact, quotes, hedging, pop-psych, and obvious legal/ethics/COI risks.
- Then the writer **resolves every L2 flag in the script** and records what was done.

The script does not go to record until L1 is `PASS` and no L2 flag is left unresolved.

## Layer 1 — Deterministic pass

`tools/factcheck.py` on `05-script.md` + `03-source-log.csv`. No judgement.

1. Every `[S..]` tag resolves to a row in `03-source-log.csv`.
2. Every source-log row has a `tier` (A/B/C/D) and a `rights_status`.
3. **Orphan-claim heuristic:** sentences with a number, date, proper noun, or quotation marks but **no `[S..]`** → candidate unsourced claims.
4. **Tier check:** every claim whose only `[S..]` is Tier C/D → upgrade or reframe as disputed.
5. Reports counts.

Output: `04-factcheck-auto.md` (Layer 1 section), `PASS` / `FAIL`.

**Gate:** `PASS` — zero unresolved tag/tier errors; every orphan candidate either tagged in the script or confirmed non-factual.

## Layer 2 — LLM-assisted pass

[templates/fact-check-auto-prompt.md](../templates/fact-check-auto-prompt.md): script + source-log in, six flag tables out (pasted into `04-factcheck-auto.md`):

1. **Factual claims** — each with its `[S..]`; `respalda` / `desajuste` / `no se puede saber` / `sin tag`.
2. **Interpretation stated as fact** — + a suggested interpretive rewrite.
3. **Quotes** — translation marked? attribution + date? apocryphal risk?
4. **Claims that should be hedged.**
5. **Pop-psychology / mythy stats.**
6. **Legal / ethics / independence risks** — defamation, allegation with no outcome, identifiable minor, sensitive-topic handling, private subject, external pitch, dignity ([brain/04](04-legal-and-ethics.md), [brain/05](05-independence-and-coi.md)).

**The LLM is not a source** ([01](01-editorial-and-sourcing.md) §9). A flag is a to-do to check against the real source, not a verdict.

## Resolving the flags

Usuario 001 (the writer) goes through every flag and either:
- **applies the fix** in `05-script.md` (correct a date, add a hedge, reframe an interpretation, cut an unsourced line, add an on-screen attribution), or
- **dismisses it** with a one-line reason (e.g. "el guion ya lo marca como tradición").

Recorded in the **Resolución** table of `04-factcheck-auto.md`.

**Gate:** L1 `PASS` + zero unresolved L2 flags. The legal/ethics + independence/COI **checklist** is ticked once more at Stage 11 ([templates/publish-checklist.md](../templates/publish-checklist.md)) before upload.

## Files

| File | Layer |
|------|-------|
| `tools/factcheck.py` → `04-factcheck-auto.md` (L1) | 1 |
| `templates/fact-check-auto-prompt.md` → `04-factcheck-auto.md` (L2 + Resolución) | 2 |

## Roadmap

- Now: L1 script; L2 prompt run by hand + manual resolution.
- Next: wrap L2 in a script that calls an LLM API and writes the L2 section in one command; `[S..]` contiguity check; source-URL link-rot check.
