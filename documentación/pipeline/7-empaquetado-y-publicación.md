---
doc: pipeline/7-empaquetado-y-publicación
summary: "Stages 10-11: título (patrón Dieck), miniatura, bloques obligatorios de la descripción, el tick legal/COI, la subida, cadencia."
audience: "producción"
mirrors: [brain/07, brain/13]
authority: guide
---

# Empaquetado y publicación (Stages 10–11)

El episodio está bloqueado (picture lock). Falta el envoltorio: título, miniatura, descripción, y la subida.

Reglas: `brain/07-publishing-seo-metrics.md`, `brain/13-hook-naming.md`, `brain/04-legal-and-ethics.md`. Herramienta: `tools/package_review.py`.

---

## Stage 10 — Paquete → `08-thumbnail-title.md`, `09-description.md`

### 1 · Scaffold

```
python tools/package_review.py E0XX-slug --init
```

Crea `08` + `09` desde plantilla y trae los **3 hook-titles** del `idea-pool.md` (los que se redactaron en el Stage 0, Protocolo 2). Se rellenan a mano.

### 2 · La página

```
python tools/package_review.py E0XX-slug
```

→ **`10-package.html`**. En el navegador (lo abre un usuario, 001 o 002):

- **Título:** elige uno de los 3 candidatos, o escribe «otro». Patrón Dieck: `<Gancho> | <Sujeto> | Documental`. El gancho lleva la tensión; el sujeto y «Documental» lo anclan. Una o dos palabras en mayúscula para énfasis está bien; nunca TODO EN MAYÚSCULAS, nunca una pregunta falsa que el vídeo no responde.
- **Miniatura:** elige la variante de `assets/thumb/` o pega una ruta. Un solo sistema (`brain/03`): imagen del sujeto + el grade de casa + una línea de Playfair o el dispositivo de expediente, acento dorado en una palabra. ≤ 4 palabras de texto, alto contraste, legible a 320px. Imagen de archivo o un fotograma del propio caso. Sin flechas, sin caras de susto, sin círculos rojos.
- **Descripción:** editable en la caja. «Fuentes principales» se auto-construye de `03-source-log.csv` (filas Tier A/B).
- **3 aprobaciones:** título OK · miniatura OK · descripción OK.

**Exportar 10-package.txt** → Claude lo pliega en `08` + `09`.

### La descripción — bloques obligatorios

1. Resumen de 2–3 frases.
2. **Fuentes principales** — con viñetas, de `03-source-log.csv` (Tier A/B). Siempre presente.
3. Capítulos (timestamps): Gancho / actos de la narrativa / Reflexión / Para llevar. Ayuda al análisis de retención por sección.
4. CTA suave del canal (suscríbete / próximo episodio). **Ningún enlace ni pitch de terceros.**
5. Créditos (licencia de música, archivo, investigación).
6. Línea de registro de correcciones, si la hay.

Plantilla: `templates/description-and-credits.md`.

### El gate de Stage 10

- [ ] Título y miniatura honestos con el contenido (ningún clickbait que el cuerpo no pague)
- [ ] Las 3 aprobaciones marcadas en `10-package.txt`

---

## Stage 11 — Publicación → `10-publish-checklist.md`

Plantilla: `templates/publish-checklist.md` (copiada a la carpeta del episodio).

### El tick final

**Nada se sube** sin el visto (un usuario, 001 o 002) en las secciones legal y de independencia/COI del checklist (`brain/04`):

- Sujeto elegible (figura pública / caso histórico / empresa documentada), no persona privada.
- Nadie que el equipo conozca, ni anonimizado. La idea no vino de un tip privado.
- Sin difamación no soportada. Sin menores identificables.
- Rótulos de IA / recreación presentes en cada aparición.
- Sin pitch externo.

### La subida

Subir · subtítulos `.srt` · capítulos · pantalla final · **comentario fijado** (fuentes / cualquier salvedad) · programar.

### Cadencia (propuesta, no fijada)

- **Lanzamiento:** 1 episodio / 3 semanas mientras el pipeline es nuevo (el cuello de botella es investigación + fact-check, no la edición).
- **Objetivo estable:** 1 episodio / 2 semanas.
- Mejor retener un episodio que sacarlo con un fact-check abierto.
- Se fija la cadencia tras 3 episodios publicados, con los datos del retro.

### Definition of Done

Publicado + subtítulos vivos + fuentes en la descripción + comentario fijado + `episodes/_STATUS.md` actualizado + retro programada.

---

Relacionado: [6-la-edición](6-la-edición.md) · [8-retro-y-métricas](8-retro-y-métricas.md) · [modelo-narrativo/7-titular-con-gancho](../modelo-narrativo/7-titular-con-gancho.md).
