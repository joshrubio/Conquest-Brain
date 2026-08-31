# Fact-check (Stage 5)

Usuario 001 escribe **todos** los guiones, así que el principio "el que revisa no es el que escribe" se preserva con **la firma de Usuario 002** más dos pasadas automáticas que corren antes de esa firma.

Tres capas, en orden. El guion no pasa a grabación hasta que las tres despejan.

Regla: `brain/14-fact-check-protocol.md`. Producto: `04-factcheck-auto.md` (L1+L2) + `04-fact-check.md` (L3, firmado).

---

## Layer 1 — Pasada determinista (automática)

`python tools/factcheck.py 05-script.md 03-source-log.csv`

Sin juicio — pura consistencia. Comprueba:

1. **Toda `[S..]` del guion resuelve** a una fila de `03-source-log.csv`.
2. Toda fila del source-log tiene `tier` (A/B/C/D) y `rights_status`.
3. **Heurística de afirmación huérfana:** marca frases que contienen un número, una fecha, un nombre propio o comillas **pero no llevan `[S..]`** → candidatas a claim sin fuente, para que un humano las revise.
4. **Chequeo de tier:** lista toda claim cuya única `[S..]` apunta a Tier C/D → hay que subirla de tier o reformularla como en disputa.
5. Reporta conteos: claims etiquetadas, fuentes por tier, huérfanas candidatas, claims solo-C/D.

**Gate:** L1 debe ser `PASS` (cero errores de etiqueta/tier sin resolver; cada huérfana candidata o bien etiquetada o bien confirmada como no-factual).

Detalle de la herramienta en `herramientas/1-factcheck` (2ª pasada).

---

## Layer 2 — Pasada asistida por LLM (primer borrador automático)

Usuario 001 corre `templates/fact-check-auto-prompt.md`: pega el guion + el source-log, recibe una tabla estructurada de claims.

El prompt pide al modelo:
- Extraer toda claim factual y la `[S..]` que cita.
- Para cada una: ¿la fuente citada (por su descripción) sostiene *plausiblemente* la claim? → `supported` / `mismatch` / `no se puede saber por la descripción`.
- Marcar interpretación enunciada como hecho (sobre todo en la reflexión / cierre).
- Marcar citas no marcadas como traducidas.
- Marcar claims que deberían ir hedged ("se dice…", "no hay pruebas concluyentes…").
- Marcar claims de psicología popular y cualquier cita que huela a apócrifa.

**El LLM no es una fuente** (`brain/01` §9). Su output es una **lista de tareas**. Cada marca se re-verifica contra la fuente real antes de darla por despejada.

**Gate:** cada marca de L2 tiene una resolución anotada por un humano.

### Lo que L2 encontró en E001 (ejemplo real)

En el guion de Hokusai, L2 marcó 39 claims, y de esas encontró:
- **2 errores reales:** la escala de edades del prefacio decía "a los 100" cuando el original dice "a los 110"; y una inconsistencia interna de fechas de la serie del Fuji.
- **3 claims poco sostenidas:** "Japón cerrado", la población de Edo, la anécdota del papel de embalar.

Los errores se corrigieron; la anécdota se enmarcó como lo que es ("se cuenta —y puede que la historia esté algo pulida—").

---

## Layer 3 — Firma humana (Usuario 002)

Usuario 002 (no escribió el guion) trabaja `templates/fact-check-sheet.md` → `04-fact-check.md`:

- Revisa el output de L1 + L2; resuelve cada marca abierta **contra fuentes reales Tier A/B**.
- **Spot-check** de una muestra de claims marcadas `supported` — no confía a ciegas en el "supported" de la máquina.
- Corre la pasada **legal y ética** (`brain/04`) y la de **independencia / conflicto de interés** (`brain/05`) — estas se quedan 100% humanas.
- Firma.

**Gate (duro):** `04-fact-check.md` firmado por Usuario 002; cero ítems abiertos; legal + COI despejados.

### La hoja de Usuario 002 — qué contiene

| Bloque | Qué |
|--------|-----|
| Tabla de claims | # · línea/tiempo del guion · afirmación · fuente citada [ID] · tier · ¿2ª fuente independiente? · veredicto · acción |
| Chequeo legal/ético | sujeto elegible · sin difamación no soportada · sin menores identificables · sin pitch externo · rótulos IA/recreación planeados |
| Chequeo de independencia | nadie que conozcamos · no procede de tip privado · "¿contable íntegra desde documentación pública por alguien ajeno?" → Sí |
| Ítems abiertos | (deben quedar en cero) |
| Firma | Usuario 002 + fecha |

---

## Qué significa "automatizado" aquí

L1 y L2 son la automatización — convierten una revisión de página en blanco en un triaje de marcas ya encontradas, y corren en minutos. **L3 se queda humana** porque el valor entero del canal es periodismo verificado, y un "supported" de un modelo no es una verificación.

## Si aparece un error después de publicar

Ver [modelo-narrativo/8-rigor-y-fuentes](../modelo-narrativo/8-rigor-y-fuentes.md) §9: comentario fijado + nota en descripción + tarjeta si es material, registrado en el retro. Nunca re-subir en silencio.
