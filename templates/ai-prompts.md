---
doc: ai-prompts
summary: "Copy-paste AI-image prompts (episode style block already merged) + the exact filename to save each as."
stage: [7]
fills: "07b-ai-prompts.md"
rule: [15]
authority: template
---

# Prompts de ilustración IA — E0XX «<título>»

> **Stage 7 · sub-parte.** Protocolo: `brain/15-ai-illustration-protocol.md`. Solo para beats del shotlist marcados ❌ en `07-assets.md` (sin imagen PD y sin gráfico propio).
> Los prompts ya llevan el bloque de estilo integrado → **copy y paste** directo al generador. Cada uno dice **cómo nombrar el archivo**.

| Campo | Valor |
|-------|-------|
| ID episodio | E0XX |
| Nº de imágenes IA | N (= beats ❌ en `07-assets.md`) |
| Carpeta destino | `episodes/E0XX-<slug>/assets/ai/` |
| Nomenclatura | `E0XX_aiNN_<slug>.png` |
| Salida | ≥ 4K si el generador lo permite; si no, upscale |
| Rótulo en pantalla | `Ilustración — Exodo` (o «recreación»), discreto, legible |
| Fecha | AAAA-MM-DD |

## Estilo de ESTE episodio (compartido — ya está dentro de cada prompt)

> Se elige por episodio (`brain/15` regla 1). Puede ser un registro de ilustración de época (p. ej. ukiyo-e), pictórico, o **recreación fotorrealista cinematográfica**. Lo que sirva a la historia y pegue con el material real del episodio + el look del canal (`brain/03`). 3–5 líneas.

```
<pegar aquí el bloque de estilo del episodio>
```

## Negative prompt (compartido)

```
text, letters, words, watermark, signature, logo, caption
<si el estilo NO es fotorrealista, añade:> photorealistic, photograph, 3D, CGI, render
<siempre:> recognizable real person face, deepfake, fake document, fake newspaper, fake photograph
```

---

## ai01 — <slug>

- **Beat(s) shotlist:** …
- **Para qué:** …
- **Guardar como:** `E0XX_ai01_<slug>.png`

```
<bloque de estilo>

<descripción de la escena: qué se ve, encuadre, luz, y — si hay una persona
real — de espaldas / silueta / distancia, cara no visible>
```

---

## ai02 — <slug>

- **Beat(s) shotlist:** …
- **Para qué:** …
- **Guardar como:** `E0XX_ai02_<slug>.png`

```
<bloque de estilo>

<escena>
```

---

## Después de generar

1. Usuario 001: 3–4 variantes por prompt → elegir la que más pega con el set → guardar con el nombre exacto en `assets/ai/`.
2. `python tools/build_ai_prompts.py E0XX-<slug> --check` para ver qué falta.
3. Claude añade las filas IA a `07-assets.md` y anota el rótulo en `09-description.md`.
