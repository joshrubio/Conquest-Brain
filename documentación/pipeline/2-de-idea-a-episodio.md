# De idea a episodio (Stage 0)

Cómo nace un episodio: alguien propone, se nombra con gancho, se comprueba que hay material, se puntúa, y —si pasa— se convierte en carpeta.

Archivos: `ideas/tracks.md`, `ideas/idea-pool.md`, `ideas/idea-rubric.md`. Regla: `brain/06` Stage 0.

## Los dos tracks

Cada idea pertenece a uno. Son fijos —no hay rúbrica que apruebe tracks—.

| Track | Dueño de ideación | Qué es | Cierre habitual |
|-------|-------------------|--------|-----------------|
| **T01 Historias Inspiradoras** | Usuario 002 | biografías y trayectorias — personas, empresas, familias, productos, métodos — por lo que revelan sobre construir, persistir, crear | A o B, rara vez C |
| **T02 Exploración** | Usuario 001 | todo lo demás — errores de ingeniería, fraudes, empresas que mintieron, sectas, manías, inventores saboteados, migración histórica | A, B o C según el caso |

Un mismo caso puede ir a **cualquier track** según el ángulo y la forma de cierre. Se fija en la ideación, junto con el hook-title.

## El proceso, paso a paso

### 1 · Propuesta

El dueño del track propone la idea con:
- un **track** asignado,
- **3 hook-titles** estilo Dieck (ver [modelo-narrativo/7-titular-con-gancho](../modelo-narrativo/7-titular-con-gancho.md)),
- una nota de por qué el ángulo humano es genuino.

### 2 · Cross-check de material (Protocolo 1)

Antes de puntuar: ¿hay material de dominio público —fotos, documentos, footage— para ilustrar el episodio? Se rellena la hoja de `brain/12`. **Sin material, no hay episodio.** Detalle en [3-los-3-protocolos](3-los-3-protocolos.md).

### 3 · Los tres requisitos previos

| # | Requisito |
|---|-----------|
| R1 | Track asignado |
| R2 | Hook-title redactado |
| R3 | Cross-check de material completo |

### 4 · Los ocho eliminatorios (todos SÍ)

| # | Filtro |
|---|--------|
| E1 | El sujeto es figura pública / caso histórico / empresa-práctica (no persona privada). |
| E2 | Existe registro público documentado (no solo rumores). |
| E3 | Hay ≥3 fuentes Tier A/B localizables antes de empezar. |
| E4 | Nadie que Usuario 001 o Usuario 002 conozcan está involucrado o es identificable — ni anonimizado. |
| E5 | La idea no procede de un tip privado (o se re-obtuvo íntegra desde material público). |
| E6 | La historia **se sostiene sola**, sin necesidad del cierre. |
| E7 | Se puede contar **sin torcer hechos** para que encaje una moraleja. |
| E8 | El cross-check confirma que hay con qué ilustrarlo. |

**Cualquier NO → se descarta o vuelve a incubar. Sin excepciones.**

### 5 · La puntuación (0–3 cada uno, mínimo 14/21)

| # | Criterio |
|---|----------|
| P1 | Fuerza del hook-title (¿clic honesto?) |
| P2 | Fuerza narrativa (arco, giro, desenlace) |
| P3 | Calidad y accesibilidad de las fuentes |
| P4 | Ángulo psicológico / humano genuino |
| P5 | Cierre (A/B/C) honesto y con fuerza |
| P6 | Relevancia para los públicos del canal |
| P7 | Material de dominio público disponible |

### 6 · La decisión

- **≥14 + todos los eliminatorios SÍ + R1–R3 hechos** → `aprobada` → pasa a Brief.
- **10–13** → `incubando`: falta hook, material o ángulo.
- **<10** → `descartada`.

### 7 · La revisión de Usuario 002 (review page)

`python tools/idea_review.py` → `ideas/idea-review.html`. Usuario 002 ve las 21 ideas del pool, y por cada una: elige el hook-title más fuerte, pone veredicto (aprobar / incubar / descartar), su propia /21, y un comentario. Exporta `idea-review.txt` → Claude lo pliega en `idea-pool.md`.

### 8 · Idea aprobada → carpeta

```
copiar episodes/_TEMPLATE-episode-folder/ → episodes/E0XX-<slug>/
estado en idea-pool.md → "en producción (E0XX)"
añadir la fila a episodes/_STATUS.md
```

## Cuándo matar una idea

Sé despiadado. Una idea muere si:
- **E6 falla:** la historia solo es interesante por el cierre. Eso es una moraleja con maquillaje, no un episodio.
- **E7 falla:** para que la reflexión funcione hay que exagerar o comprimir. El caso te pide mentir un poco — no.
- **P3 = 0–1:** las fuentes son frágiles o de una sola versión (típico con archivo corporativo: la empresa cuenta su propia historia). Riesgo de hagiografía (`brain/01`).
- **P7 = 0:** todo tendría que ser gráfico propio. El episodio sería "narrador sobre pantalla negra".

El pool tiene una sección **"En espera"** para ideas con un buen hook pero un freno real (riesgo legal, material, o el hook no sostiene un episodio entero — mejor un short).

## El equilibrio entre tracks

Cada ~5 episodios publicados: ¿se inclina todo hacia un track? ¿los hooks siguen funcionando (CTR)? ¿algún subtema de Exploración deriva a tono sensacionalista?
