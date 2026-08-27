# research/

Working analysis that feeds the `docs/` specs. Not published, not part of any episode.

## dieck-docs/

Reverse-engineering the reference format (Farid Dieck — *Dieck Docs*) so that `docs/02-content-format.md`, `docs/08-tone-of-voice.md` and `docs/09-reflection-rules.md` are grounded in real structure, not assumption.

- `dieck-docs/transcripts/` — raw transcripts, one file per video: `NN-slug.txt`. Add a source line at the top (video title + URL + retrieval date). **Do not commit long verbatim transcripts to the public GitHub repo** — see note below.
- `dieck-docs/structure-analysis.md` — the analysis worksheet. Fill one block per video, then write the synthesis.

## Method

1. Collect 5–8 transcripts spanning different Dieck Docs episodes.
2. For each: mark timestamps of hook / narrative acts / reflection start / takeaway / outro; note % of runtime per section; note attribution habits, sentence rhythm, how the reflection is entered and exited, how the takeaway is linked.
3. Synthesize: what is consistent across all of them (→ becomes a rule), what varies (→ becomes a choice).
4. Update the three `docs/` files; bump their `Status: v0` line to `v1 — validated against N transcripts (date)`.

## Copyright / repo note

Transcripts are copyrighted by their author. Keep them **local only** or in a **private** analysis area — add `research/dieck-docs/transcripts/` to `.gitignore` before the repo goes public if it will be public. The *analysis* (our observations, %s, structure notes) is ours and can be committed.
