# 14 — Fact-Check Protocol

Stage 5 of the pipeline. Usuario 001 writes **every** script, so the "checker ≠ writer" principle is preserved by **Usuario 002's sign-off** plus two automated passes that run before that sign-off.

Three layers, in order. The script does not proceed to record until all three clear.

## Layer 1 — Deterministic pass (automated)

`tools/factcheck.py` runs on `05-script.md` + `03-source-log.csv`. No judgement — pure consistency.

Checks:
1. Every `[S..]` tag in the script resolves to a row in `03-source-log.csv`.
2. Every source-log row has a `tier` (A/B/C/D) and a `rights_status`.
3. **Orphan-claim heuristic:** flags sentences that contain a number, a date, a proper noun, or quotation marks but carry **no `[S..]` tag** — candidate unsourced claims for a human to check.
4. **Tier check:** lists every claim whose only `[S..]` points to a Tier C/D source → must be upgraded or reframed as disputed.
5. Reports counts: claims tagged, sources by tier, orphan candidates, C/D-only claims.

Output: `04-factcheck-auto.md` (Layer 1 section) with `PASS` / `FAIL` and the flag list.

**Gate:** Layer 1 must be `PASS` (zero unresolved tag/tier errors; every orphan candidate either tagged or confirmed non-factual).

## Layer 2 — LLM-assisted pass (automated first draft)

Usuario 001 runs [templates/fact-check-auto-prompt.md](../templates/fact-check-auto-prompt.md): paste the script + the source-log, get back a structured claims table.

The prompt asks the model to:
- Extract every factual claim and the `[S..]` it cites.
- For each: does the cited source (by its description) *plausibly* support the claim? → `supported` / `mismatch` / `can't tell from description`.
- Flag interpretation stated as fact (especially in the reflection / close).
- Flag quotes not marked as translated.
- Flag claims that should be hedged ("se dice…", "no hay pruebas concluyentes…").
- Flag popular-psychology claims and any quote that smells apocryphal.

**The LLM is not a source** ([01-editorial-and-sourcing.md](01-editorial-and-sourcing.md) §9). Its output is a **to-do list**. Every flag is re-verified by a human against the real source before it is cleared.

Output: appended to `04-factcheck-auto.md` (Layer 2 section).

**Gate:** every Layer 2 flag has a resolution noted by a human.

## Layer 3 — Human sign-off (Usuario 002)

Usuario 002 (did not write the script) works [templates/fact-check-sheet.md](../templates/fact-check-sheet.md) → `04-fact-check.md`:
- Reviews Layers 1 + 2 output; resolves every open flag against real Tier A/B sources.
- Spot-checks a sample of `supported` claims directly (don't trust the machine's "supported" blindly).
- Runs the **legal & ethics** ([04](04-legal-and-ethics.md)) and **independence/COI** ([05](05-independence-and-coi.md)) passes — these stay fully human.
- Signs.

**Gate (hard):** `04-fact-check.md` signed by Usuario 002; zero open items; legal + independence/COI clear.

## What "automated" means here

Layers 1 and 2 are the automation — they turn a blank-page review into a triage of pre-found flags, and they run in minutes. Layer 3 stays human because the channel's whole value is verified journalism and a model's "supported" is not a verification.

## Files

| File | Layer | Who |
|------|-------|-----|
| `tools/factcheck.py` | 1 | script |
| `04-factcheck-auto.md` (in episode folder) | 1 + 2 output | script + LLM |
| `templates/fact-check-auto-prompt.md` | 2 | Usuario 001 runs |
| `templates/fact-check-sheet.md` → `04-fact-check.md` | 3 | Usuario 002 |

## Roadmap

- v1 (now): `factcheck.py` for Layer 1; a prompt for Layer 2 run manually.
- Later: wrap Layer 2 in a script that calls an LLM API and writes `04-factcheck-auto.md` in one command; add a check that `[S..]` numbering is contiguous; pull source URLs and check they still resolve (link-rot).
