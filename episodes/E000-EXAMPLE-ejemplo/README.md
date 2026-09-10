# E000 — EJEMPLO ILUSTRATIVO (no se produce ni se publica)

Carpeta de referencia: muestra **cómo se rellenan los archivos de un episodio** con la estructura v1 (`brain/02` · `brain/08` · `brain/09` · `templates/script-template.md`).

**No es un episodio real.** Caso usado como vehículo: **la Burbuja de los Mares del Sur (South Sea Company, 1720)** — dominio público total, sin personas vivas, registro documental abundante. Elegido además porque contiene los tres retos típicos de fuentes:
1. cifras muy repetidas que hay que verificar (cotizaciones de la acción);
2. una cita apócrifa famosa (la frase de Newton sobre "la locura de la gente") — se usa **como ejemplo de lo que NO citamos**;
3. historiografía moderna (Hoppit) que corrige el mito de la "locura de las masas".

## Qué hay aquí

| Archivo | Qué demuestra |
|---------|---------------|
| `01-brief.md` | Brief Stage 1 completo: **track Documental**, **3 hook-titles** (`brain/13`), cross-check de material (`brain/12`), forma de cierre A, estructura, riesgos. |
| `02-research-dossier.md` | Cronología, afirmaciones de carga con tier, puntos disputados, la cita apócrifa marcada. |
| `03-source-log.csv` | Registro de fuentes con tier y estado de derechos. Fuentes reales; localización exacta marcada como *a completar*. |
| `04-factcheck-auto.md` | Salida de Layer 1 (`tools/factcheck.py`) + hueco de Layer 2 (`brain/14`). |
| `05-script.md` | Guion de ejemplo en estructura v1: cold open → pivote a contexto → narrativa con explicador y foreshadowing promise/pay → cierre forma A → CTA. Anotado. |
| `06-shotlist.md` | Shotlist inferida del guion (26 beats), con la heurística documentada. |

## Aviso

Las cifras y citas del guion de ejemplo llevan tag `[S..]` pero **no están verificadas**: es material didáctico. Antes de cualquier uso real pasaría por el fact-check L1+L2 de verdad.
