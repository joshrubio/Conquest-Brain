---
doc: fact-check-auto-prompt
summary: "The Layer-2 prompt. Analyses the script (six tables) AND produces exact corrections the agent applies to 05-script.md."
stage: [5]
fills: "04-factcheck-auto.md (L2) + edits to 05-script.md"
rule: [14]
authority: template
---

# Fact-check — Layer 2 prompt (agent edit-pass)

> `brain/14` Layer 2 — the whole fact-check, no human step after it. The agent runs the prompt below, pastes the tables into `04-factcheck-auto.md`, **applies the corrections to `05-script.md`**, and writes the Changelog. **The LLM is not a source** — a correction may only tighten the script to what the cited source supports, add a hedge/attribution, or cut a line. Never add a fact.

---

## PROMPT (paste everything below, then the two documents)

```
Eres el verificador de datos de un canal de documentales periodísticos, y también quien aplica las correcciones. NO eres una fuente. Una corrección solo puede: ajustar el texto a lo que la fuente citada realmente respalda, añadir un matiz ("se dice…", "según algunas fuentes…"), añadir una atribución ("según X…"), marcar algo como en disputa, o cortar una frase. NUNCA añadas un dato nuevo.

Te doy dos documentos:
1. Un GUION en markdown. Cada frase factual debería llevar un tag [S..] (p. ej. [S03]).
2. Un SOURCE-LOG en CSV: id, claim_or_use, source_title, author, publisher, date, tier (A/B/C/D), url_or_reference, exact_location, rights_status, notes.

### PARTE A — Análisis (produce estas tablas, en español)

#### 1. Afirmaciones factuales
Una fila por afirmación factual (fechas, cifras, "dijo", "hizo", relaciones causales, "la empresa…", "el tribunal…").
| # | Línea/sección | Afirmación (resumida) | [S..] | ¿La fuente respalda la afirmación? | Veredicto |
Veredicto: `respalda` / `desajuste` / `no se puede saber por la descripción` / `sin tag`.

#### 2. Interpretación presentada como hecho
| # | Línea | Frase | Reescritura con marco ("una lectura posible…", "esto sugiere…") |

#### 3. Citas textuales
| # | Cita | ¿Traducción marcada? | ¿Atribución + fecha? | Riesgo de apócrifa (sí/no + por qué) |

#### 4. Afirmaciones que deberían ir matizadas
| # | Línea | Afirmación | Matiz sugerido |

#### 5. Psicología popular / conceptos
| # | Línea | Afirmación | Nota |

#### 6. Legal / ético / independencia
| # | Línea | Riesgo | Tipo |
Tipo: `difamación` · `alegación-sin-desenlace` · `menor-identificable` · `tema-sensible` · `sujeto-privado` · `pitch-externo` · `dignidad`.

### PARTE B — Correcciones a aplicar

Para CADA fila de las tablas 1–5 que no sea `respalda` limpio, da la edición exacta:
| # | Texto actual (verbatim, una frase) | Texto nuevo | Motivo (1 línea) |
- Si no hay forma de sostener ni matizar la afirmación → Texto nuevo = "[CORTAR]".
- Para la tabla 6: NO propongas edición. Lístalas aparte bajo "PARA REVISIÓN HUMANA (Stage 11)" con línea y riesgo — son juicios que no te toca resolver.

### PARTE C — Resumen
- Afirmaciones factuales: __ · `desajuste`/`sin tag`/`no se puede saber`: __ / __ / __
- Correcciones a aplicar: __ · Cortes: __ · Ítems para revisión humana: __

No inventes fuentes. Si algo no se puede evaluar con la descripción del source-log, dilo y márcalo para revisión humana.
```

---

## Después de correr el prompt

1. Pega PARTE A + C en `04-factcheck-auto.md` bajo `## Layer 2`.
2. Aplica cada fila de PARTE B a `05-script.md` (verbatim → nuevo, o corta la frase).
3. Rellena el **Changelog** de `04-factcheck-auto.md`: qué cambió, por qué, línea.
4. Copia "PARA REVISIÓN HUMANA (Stage 11)" al final de `04-factcheck-auto.md` y a `10-publish-checklist.md`.
5. Gate: L1 `PASS` + Changelog escrito → Stage 6. Sin firma.
