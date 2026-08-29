# Fact-check — Layer 2 prompt (LLM-assisted)

> `docs/14-fact-check-protocol.md` Layer 2. Josh pastes the script + the source-log into an LLM using the prompt below. Output goes into `04-factcheck-auto.md` (Layer 2 section). **The LLM is not a source** — every flag it raises is a to-do for a human to re-verify against the real source.

---

## PROMPT (paste everything below, then the two documents)

```
Eres un verificador de datos para un canal de documentales periodísticos. NO eres una fuente: tu trabajo es señalar qué revisar, no dar por buena ninguna afirmación.

Te doy dos documentos:
1. Un GUION en markdown. Cada frase factual debería llevar un tag [S..] (p. ej. [S03]).
2. Un SOURCE-LOG en CSV: id, claim_or_use, source_title, author, publisher, date, tier (A/B/C/D), url_or_reference, exact_location, rights_status, notes.

Produce SOLO estas tablas, en español, sin preámbulo:

### 1. Afirmaciones factuales
Una fila por afirmación factual del guion (fechas, cifras, "dijo", "hizo", relaciones causales, "la empresa…", "el tribunal…").
| # | Línea/sección | Afirmación (resumida) | [S..] citado | ¿La fuente citada (por su descripción en el source-log) respalda plausiblemente la afirmación? | Veredicto |
Veredicto: `respalda` / `desajuste` (la fuente no encaja con la afirmación) / `no se puede saber por la descripción` / `sin tag` (afirmación factual sin [S..]).

### 2. Interpretación presentada como hecho
Frases de la reflexión/cierre (o de la narrativa) que afirman una interpretación como si fuera un hecho establecido, sin marco tipo "una lectura posible…", "esto sugiere…".
| # | Línea | Frase | Reescritura sugerida (con marco interpretativo) |

### 3. Citas textuales
| # | Cita en el guion | ¿Marcada como traducción si procede? | ¿Atribución + fecha presentes? | Riesgo de cita apócrifa (sí/no + por qué) |

### 4. Afirmaciones que deberían ir matizadas
Cosas dichas con seguridad que probablemente merecen "se dice…", "según algunas fuentes…", "no hay pruebas concluyentes de…".
| # | Línea | Afirmación | Matiz sugerido |

### 5. Psicología popular / conceptos
Cualquier concepto psicológico, estadística llamativa o "dato curioso" que suene a mito o a divulgación sin respaldo (p. ej. "usamos el 10% del cerebro", "la regla de las 10.000 horas").
| # | Línea | Afirmación | Nota |

### 6. Resumen
- Nº de afirmaciones factuales: __
- `desajuste`: __ · `no se puede saber`: __ · `sin tag`: __
- Banderas en tablas 2–5: __
- Lo más urgente de revisar (máx. 5 puntos):

No inventes fuentes. No des una afirmación por verificada. Si algo no se puede evaluar con la descripción del source-log, dilo.
```

---

## Después de correr el prompt

1. Pega la salida en `04-factcheck-auto.md` bajo `## Layer 2 — LLM`.
2. Josh o Carmen resuelve cada bandera contra la **fuente real** (no contra el modelo) y anota la resolución.
3. Solo entonces Carmen abre `04-fact-check.md` (Layer 3).
