---
doc: pipeline/4-fact-check
summary: "Stage 5, 100% automático. L1 determinista + L2 (el agente analiza y aplica las correcciones al guion). Sin firma, sin paso humano."
audience: "guionista, agente"
mirrors: [brain/14]
authority: guide
---

# Fact-check (Stage 5)

**100% automático. No hay paso humano en esta fase.** Dos pasadas:

- **L1** — `tools/factcheck.py`, determinista, pura consistencia. Debe dar `PASS`.
- **L2** — el agente lee el guion + el source-log y **aplica las correcciones directamente a `05-script.md`**, dejando un changelog.

El guion pasa a grabación cuando L1 = `PASS` y la pasada L2 ha corrido y escrito su changelog. Sin firma.

Regla: `brain/14`. Producto: `04-factcheck-auto.md` (L1 + L2 + changelog + lista para revisión humana).

## El trade-off aceptado

No hay un segundo par de ojos humanos sobre la exactitud factual. Los seguros son:
- cada afirmación de carga ya lleva `[S..]` a una fuente Tier A/B desde el Stage 2;
- L1 caza mecánicamente toda etiqueta rota o ausente;
- L2 re-lee cada afirmación contra su fuente y reescribe lo que no encaja;
- el pase legal/ético + independencia/COI lo sigue marcando un humano una vez, en Stage 11, antes de subir.

---

## Layer 1 — Pasada determinista

`python tools/factcheck.py 05-script.md 03-source-log.csv`

1. Toda `[S..]` del guion resuelve a una fila del source-log.
2. Toda fila tiene `tier` (A/B/C/D) y `rights_status`.
3. **Heurística de huérfana:** frases con número / fecha / nombre / comillas **sin `[S..]`**.
4. **Chequeo de tier:** claim cuya única `[S..]` es C/D → subir de tier o marcar disputada.
5. Conteos.

**Gate:** `PASS`.

---

## Layer 2 — Pasada del agente que edita

El agente (esta sesión o un subagente) corre `templates/fact-check-auto-prompt.md`:

**Parte A — análisis** (6 tablas → `04-factcheck-auto.md`): afirmaciones factuales, interpretación como hecho, citas, matices, psicología popular, riesgos legales/éticos/COI.

**Parte B — correcciones exactas:** por cada fila que no sea `respalda` limpio, el texto verbatim actual → el texto nuevo. Reglas:
- una corrección solo puede **ajustar el texto a lo que la fuente respalda**, añadir un matiz, añadir una atribución, o **cortar** la frase — nunca añadir un dato;
- lo que no se puede sostener ni matizar → `[CORTAR]` o marcar disputado en pantalla;
- los riesgos legales/éticos/COI que piden un juicio → **no los toca**; van a la lista "Para revisión humana (Stage 11)".

**El agente aplica** cada corrección a `05-script.md` y rellena el **Changelog** de `04-factcheck-auto.md`.

**Gate:** L1 `PASS` + changelog escrito → Stage 6.

### Lo que L2 encontró en E001 (ejemplo real)

L2 analizó 39 afirmaciones:
- **2 errores reales** → corrección aplicada: la escala de edades del prefacio decía "a los 100" cuando el original dice "a los 110"; e inconsistencia de fechas de las 36 vistas del Fuji.
- **3 claims poco sostenidas** → matizadas: "Japón cerrado", la población de Edo, la anécdota del papel de embalar ("se cuenta que…").

## Si aparece un error después de publicar

Ver [modelo-narrativo/8-rigor-y-fuentes](../modelo-narrativo/8-rigor-y-fuentes.md) §9: comentario fijado + nota en descripción + tarjeta si es material, registrado en el retro. Nunca re-subir en silencio.
