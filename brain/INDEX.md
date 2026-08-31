---
doc: INDEX
summary: "Router for brain/. Read this first, then open the 1–3 docs it points you to instead of all 18."
stage: all
read_when: "always — this is the entry point to the standing rules"
authority: index
---

# brain/ — index

The **standing rules** for Conquest-Oficial. English, terse. Each file has YAML
frontmatter (`summary`, `stage`, `read_when`, `pairs_with`, `tools`) — grep it to
find the right doc. **Don't read all 18.** Use the routing table.

## Routing — "I am about to…"

| Task | Read (in order) |
|------|-----------------|
| understand the whole project | `00`, `06` |
| judge / score an idea | `../ideas/idea-rubric.md`, `12`, `13`, `05` |
| name an idea / pick a title | `13`, `07` |
| research a case / build the source-log | `01`, `05`, `12` |
| outline an episode | `02`, `09` |
| write the script | `02`, `08`, `09`, `01` · pass: `tools/script_review.py` → `05-script.html` |
| write the close / reflection (any register) | `09`, `08`, `01` |
| fact-check a script | `14`, `01`, `04` |
| build the shotlist | `11`, `02`, `06` (Stage 6) |
| pick assets / images / music | `12`, `15`, `03` |
| write AI-image prompts | `15`, `03` |
| edit the video | `16`, `11`, `03` |
| thumbnail / description / publish | `07`, `03`, `13`, `04` |
| run a retro | `07`, `06` (Stage 12) |
| run the pipeline day to day / a gate won't close | `17` |
| commit / git question | `10` |
| who is Usuario 001/002 | `USERS.md` |
| anything legal / a living person / a sensitive topic | `04`, `05` |

## The docs

| # | Doc | Governs | One-liner |
|---|-----|---------|-----------|
| 00 | project-charter | all | mission, the 4 non-negotiables, what the project is / isn't |
| 01 | editorial-and-sourcing | 2·4·5 | uncited-claim rule, source tiers A–D, quotes, corrections, AI-not-a-source |
| 02 | content-format | 3·4 | episode anatomy (cold open→bumper→pivot→narrative→close→CTA), length, required devices |
| 03 | brand-identity | 3·7·9·10 | name, palette, grade, typography, case-file device, 4K rule, no-source-cards rule, thumbnails |
| 04 | legal-and-ethics | 5·11 | subject eligibility, defamation, minors, sensitive topics, disclosure checklist |
| 05 | independence-and-coi | 0·5·11 | off-limits subjects, the public-documentation test, research hygiene |
| 06 | production-workflow | all | the 12 gated stages, the 5 review pages, per-stage roles, Definition of Done |
| 07 | publishing-seo-metrics | 10·11·12 | cadence, title/thumbnail rules, description blocks, KPIs + KPI log |
| 08 | tone-of-voice | 4 | register, first-person investigator, neutral Spanish, uncertainty phrasing, never-do list |
| 09 | reflection-rules | 1·3·4 | the close in forms A/B/C × four registers (psych / practical / philosophical / religious), the surgical test, failure modes |
| 10 | repo-and-git-workflow | all | repo layout, what's versioned, branching, commit-message convention |
| 11 | visual-rhythm | 4·6·9 | shots planned from the locked script; beat rates; visual-type menu |
| 12 | available-material-protocol | 0·2·7 | PD archives list, per-idea worksheet, stock rules, music licensing, subject-with-no-photo |
| 13 | hook-naming | 0·10 | Dieck title anatomy, hook types, templates, ethical rules |
| 14 | fact-check-protocol | 5 | fully automated — L1 deterministic + L2 agent edit-pass that applies the fixes; no human step |
| 15 | ai-illustration-protocol | 7 | AI only where nothing real exists; one style/episode; label always; no real faces, no fake docs |
| 16 | edit-and-delivery | 9 | Ken Burns→trim→review→b-roll→music→subs; 4K; house grade; export −14 LUFS |
| 17 | dashboard-and-advance | all | dashboard.html + serve.py + advance.py — one-click gate hand-off; the /loop; _STATUS.md |
| — | USERS | all | the only slot→person map; slots fixed, responsibilities assignable |

## Canonical homes (where a rule lives once, everyone else points)

| Rule | Home |
|------|------|
| subjects are public | `01` §3 (+ `00` non-negotiable #1) |
| COI / no one you know / public-doc test | `05` |
| no on-screen source cards · 4K fallback · house grade | `03` |
| music licence (CC-BY / BY-SA / CC0 only) | `12` §Audio |
| foreshadowing phrase toolkit | `08` §6 |
| close forms A/B/C (detail) | `09` |
| title / hook pattern | `13` |
| AI-illustration rules | `15` |

## Maintaining this file

When you add or change a rule: edit the doc, its frontmatter `summary`, and its
row here. When you add a doc: add frontmatter + a routing entry + a table row.
