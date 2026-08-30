# Prompts de ilustración IA — E0XX «<título>»

> **Stage 7 · sub-parte.** Protocolo: `docs/15-ai-illustration-protocol.md`. Solo para beats del shotlist marcados ❌ en `07-assets.md` (sin imagen PD y sin gráfico propio).
> Los prompts ya llevan el bloque de estilo integrado → **copy y paste** directo al generador. Cada uno dice **cómo nombrar el archivo**.

| Campo | Valor |
|-------|-------|
| ID episodio | E0XX |
| Nº de imágenes IA | N (= beats ❌ en `07-assets.md`) |
| Carpeta destino | `episodes/E0XX-<slug>/assets/ai/` |
| Nomenclatura | `E0XX_aiNN_<slug>.png` |
| Salida | ≥ 4K si el generador lo permite; si no, upscale |
| Rótulo en pantalla | `Ilustración — Éxodo` (o «recreación»), discreto, legible |
| Fecha | AAAA-MM-DD |

## Bloque de estilo (compartido — ya está dentro de cada prompt)

```
<pegar aquí el bloque de estilo del episodio — derivado de docs/03 §Visual
direction + el aspecto del archivo real del episodio, para que las IA peguen
con los prints/fotos reales. Sumi-e / xilografía por defecto. NO fotorrealista.>
```

## Negative prompt (compartido)

```
photorealistic, photograph, hyperrealistic, 3D, CGI, render, modern clothing,
text, watermark, signature, visible detailed human face, western oil painting,
anime, neon, lens flare, HDR
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

1. Josh: 3–4 variantes por prompt → elegir la que más pega con el set → guardar con el nombre exacto en `assets/ai/`.
2. `python tools/build_ai_prompts.py E0XX-<slug> --check` para ver qué falta.
3. Claude añade las filas IA a `07-assets.md` y anota el rótulo en `09-description.md`.
