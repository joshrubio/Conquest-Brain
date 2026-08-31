# Fact-check — Layer 2 prompt (LLM-assisted)

> `brain/14-fact-check-protocol.md` Layer 2 — the last check before record (there is no Layer 3). Usuario 001 pastes the script + the source-log into an LLM using the prompt below; the output goes into `04-factcheck-auto.md` and **every flag is resolved in the script** (correction applied, or dismissed with a one-line reason). **The LLM is not a source** — a flag is a to-do to check against the real source, not a verdict.

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

### 6. Legal / ético / independencia (banderas, no dictamen)
Señala riesgos evidentes para revisión humana antes de publicar (`brain/04`, `brain/05`):
| # | Línea | Riesgo | Tipo |
Tipo: `difamación` (afirmación negativa sobre persona viva sin fuente fuerte / sin atribuir) · `alegación-sin-desenlace` (se acusa, no se dice cómo acabó) · `menor-identificable` · `tema-sensible` (suicidio/abuso/violencia sin sobriedad o sin nota de ayuda) · `sujeto-privado` (parece persona privada, no figura pública) · `pitch-externo` · `dignidad` (mofa, monólogo interior inventado como hecho).

### 7. Resumen
- Nº de afirmaciones factuales: __
- `desajuste`: __ · `no se puede saber`: __ · `sin tag`: __
- Banderas en tablas 2–6: __
- Lo más urgente de revisar (máx. 5 puntos):

No inventes fuentes. No des una afirmación por verificada. Si algo no se puede evaluar con la descripción del source-log, dilo.
```

---

## Después de correr el prompt

1. Pega la salida en `04-factcheck-auto.md` bajo `## Layer 2 — LLM`.
2. Resuelve **cada bandera** contra la fuente real (no contra el modelo): aplica la corrección en `05-script.md`, o descártala con una línea de motivo, y anótalo en la columna **Resolución**.
3. Gate: L1 `PASS` + cero banderas sin resolver. No hay más pasadas — el guion pasa a grabación.
