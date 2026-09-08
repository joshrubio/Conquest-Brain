# Fact-check — E0XX

> `brain/14`. **Fully automated, no human step.**
>
> - **L1** — `python tools/factcheck.py 05-script.md 03-source-log.csv > 04-factcheck-auto.md`
> - **L2** — the agent runs `templates/fact-check-auto-prompt.md`, pastes Part A + C below, **applies Part B to `05-script.md`**, fills the Changelog.
>
> **Gate:** L1 `PASS` + Changelog written → Stage 6.

## Layer 1 — deterministic

(salida de factcheck.py)

## Layer 2 — analysis (Parts A + C of the prompt)

(tablas 1–6 + resumen)

## Changelog — corrections applied to 05-script.md

| # | Antes (verbatim) | Después | Motivo |
|---|------------------|---------|--------|
| | | | |

## Para revisión humana (Stage 11)

Riesgos legales/éticos/COI que L2 no puede resolver — se marcan también en `10-publish-checklist.md`.

| Línea | Riesgo | Tipo |
|-------|--------|------|
| | | |
