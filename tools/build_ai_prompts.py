#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_ai_prompts.py — scaffold the AI-illustration prompt doc for an episode.
Protocol: docs/15-ai-illustration-protocol.md

Usage:
    python tools/build_ai_prompts.py E0XX-slug <img-slug-1> <img-slug-2> ...
        creates episodes/E0XX-slug/assets/ai/ and scaffolds
        episodes/E0XX-slug/07b-ai-prompts.md with one block per slug.
        (Refuses to overwrite an existing 07b unless --force.)

    python tools/build_ai_prompts.py E0XX-slug --check
        lists which E0XX_aiNN_*.png files exist in assets/ai/ vs. the doc.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes"

STYLE_DEFAULT = """<DEFINIR EL ESTILO DE ESTE EPISODIO — docs/15 regla 1. 3-5 lineas.
Ejemplos de registro: ukiyo-e / xilografia (encaja con archivo de prints);
carboncillo / grabado; pictorico sobrio; recreacion fotorrealista
cinematografica, paleta apagada, luz natural, 16:9. Elegir uno y ser
consistente en todo el episodio.>"""

NEGATIVE = """text, letters, words, watermark, signature, logo, caption,
recognizable real person face, deepfake, fake document, fake newspaper,
fake photograph
<si el estilo NO es fotorrealista, anadir: photorealistic, photograph, 3D, CGI, render>"""

FNAME_RE = re.compile(r"^([A-Za-z0-9]+)_ai(\d{2})_([a-z0-9-]+)\.(png|jpg|jpeg|webp|tif|tiff)$", re.I)


def ep_id(slug: str) -> str:
    m = re.match(r"(E\d+)", slug)
    return m.group(1) if m else slug.split("-")[0]


def block(eid, n, s):
    fn = f"{eid}_ai{n:02d}_{s}"
    return f"""## ai{n:02d} — {s}

- **Beat(s) shotlist:** …
- **Para qué:** …
- **Guardar como:** `{fn}.png`

```
<PEGAR BLOQUE DE ESTILO>

<ESCENA: qué se ve, encuadre, luz. Si hay una persona real → de espaldas /
silueta / distancia, cara NO visible.>
```

---
"""


def scaffold(slug, img_slugs, force):
    d = EP_DIR / slug
    if not d.is_dir():
        sys.exit(f"no existe: {d}")
    eid = ep_id(slug)
    ai = d / "assets" / "ai"
    ai.mkdir(parents=True, exist_ok=True)
    (ai / "README.txt").write_text(
        f"# Imagenes IA de {eid}. Nombres: {eid}_aiNN_<slug>.png (ver ../../07b-ai-prompts.md).\n"
        "# Gitignored. Rotulo en pantalla obligatorio (docs/15 regla 2).\n", encoding="utf-8")

    out = d / "07b-ai-prompts.md"
    if out.exists() and not force:
        sys.exit(f"ya existe {out.name} — usa --force para regenerar")

    blocks = "\n".join(block(eid, i + 1, s) for i, s in enumerate(img_slugs))
    text = f"""# Prompts de ilustración IA — {eid}

> Stage 7 · sub-parte. Protocolo: `docs/15-ai-illustration-protocol.md`.
> Prompts con el bloque de estilo integrado → copy y paste. Cada uno dice cómo nombrar el archivo.

| Campo | Valor |
|-------|-------|
| ID episodio | {eid} |
| Nº de imágenes IA | {len(img_slugs)} |
| Carpeta destino | `episodes/{slug}/assets/ai/` |
| Nomenclatura | `{eid}_aiNN_<slug>.png` |
| Salida | ≥ 4K si el generador lo permite; si no, upscale |
| Rótulo en pantalla | `Ilustración — Éxodo` (o «recreación»), discreto, legible |
| Fecha | (rellenar) |

## Bloque de estilo (compartido)

```
{STYLE_DEFAULT}
```

## Negative prompt (compartido)

```
{NEGATIVE}
```

---

{blocks}
## Después de generar

1. Corre `python tools/pull_assets.py {slug}` — estos prompts salen en la columna derecha de `07-photography-pass.html`.
2. Por prompt: 3–4 variantes → elige la que más pega con el set → pega su ruta/URL en el input del prompt.
3. «Exportar 07-picks.txt» → `python tools/pull_assets.py {slug} --download` copia cada imagen a `assets/ai/` con su nombre e imprime la fila de manifiesto.
4. Claude añade las filas IA a `07-assets.md` y anota el rótulo en `09-description.md`.
"""
    out.write_text(text, encoding="utf-8")
    print(f"creado  {out.relative_to(ROOT)}")
    print(f"creado  {(ai).relative_to(ROOT)}/")
    print(f"\nsiguiente: escribir la escena de cada prompt ai01..ai{len(img_slugs):02d}")


def check(slug):
    d = EP_DIR / slug
    eid = ep_id(slug)
    doc = d / "07b-ai-prompts.md"
    if not doc.exists():
        sys.exit(f"no hay {doc.name}")
    want = re.findall(r"^## (ai\d{2}) — (\S+)", doc.read_text(encoding="utf-8"), re.M)
    have = {}
    ai = d / "assets" / "ai"
    if ai.is_dir():
        for f in ai.iterdir():
            m = FNAME_RE.match(f.name)
            if m:
                have[f"ai{int(m.group(2)):02d}"] = f.name
    print(f"{eid} — {len(want)} prompts, {len(have)} imagenes\n")
    for aid, s in want:
        mark = "OK  " if aid in have else "  · "
        print(f"  {mark}{aid} {s:28s} {have.get(aid, '(falta)')}")
    extra = set(have) - {a for a, _ in want}
    for a in sorted(extra):
        print(f"  ??  {a} {have[a]}  (no está en el doc)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    slug = args[0]
    rest = args[1:]
    if "--check" in rest:
        check(slug)
    else:
        force = "--force" in rest
        slugs = [a for a in rest if not a.startswith("--")]
        if not slugs:
            sys.exit("da al menos un slug de imagen, p. ej. deathbed-room")
        scaffold(slug, slugs, force)
