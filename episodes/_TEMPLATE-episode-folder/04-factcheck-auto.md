# Fact-check — E0XX

> `brain/14`. Two layers, both automated; there is **no Layer 3 human sign-off**.
>
> - **L1** — `python tools/factcheck.py 05-script.md 03-source-log.csv > 04-factcheck-auto.md`
> - **L2** — run `templates/fact-check-auto-prompt.md`, paste the output below.
>
> Then resolve **every** L2 flag: apply the fix in `05-script.md`, or dismiss it with a one-line reason. Record it in the Resolución column / list.
>
> **Gate:** L1 `PASS` + zero unresolved flags → the script goes to record.

## Layer 1 — deterministic

(salida de factcheck.py)

## Layer 2 — LLM

(salida del prompt)

## Resolución de banderas

| Bandera (tabla · #) | Qué se hizo | Guion actualizado |
|---------------------|-------------|-------------------|
| | | |
