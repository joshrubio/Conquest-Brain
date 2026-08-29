# Manifiesto de recursos — E0XX «<título>»

> **Stage 7.** Resuelve cada beat archivístico del shotlist a **una imagen concreta**, con enlace directo, y registra el **pase de fotografía** (¿encaja con la estética del vídeo?). Los beats de gráfico propio no van aquí — van al brief de diseño.
> Depende de: `06-shotlist.md` (los beats) · `docs/03` §Visual direction (el look/grade de la serie) · `material-search.md` (qué existe).

| Campo | Valor |
|-------|-------|
| ID episodio | E0XX |
| Responsable | Josh |
| Look de referencia | (grade / grano / letterbox / tratamiento de la serie — de `docs/03`) |
| Salida de resolución | 4K (long edge ≥ ~4000 px para plano completo; menos para inserto) |
| Fecha | AAAA-MM-DD |

## Flujo

1. **Pull de candidatos** (automatizable) — por cada beat archivístico del shotlist, buscar 1–3 imágenes concretas: enlace directo al objeto, museo, nº de objeto, licencia, resolución máx.
2. **Pase de fotografía** (Josh, manual) — por cada candidato, verdict con los criterios de abajo.
3. **Manifiesto final** — una fila por imagen **aceptada**, con nombre de archivo local tras descargar.

## Criterios del pase de fotografía

Marca cada candidato:

- **Resolución** — ¿suficiente para el uso (plano completo vs. inserto) y para hacer push-in / parallax sin deshacerse?
- **Estado** — manchas (foxing), roturas, recorte del papel, decoloración: ¿aceptable o distrae?
- **Color** — ¿coherente con el grade del episodio? Las impresiones ukiyo-e varían mucho entre tiradas y entre escaneos de museo (unas cálidas, otras frías, otras con más contraste).
- **Encuadre / márgenes** — ¿el escaneo trae el margen del papel, sellos de coleccionista, montura? ¿lo queremos o lo recortamos a sangre?
- **Coherencia de secuencia** — las imágenes que van juntas en un tramo, ¿parecen de la misma familia (misma calidad de escaneo, mismo tratamiento)?
- **Veredicto** — ✅ aceptada · ⚠️ dudosa (anota qué falta) · ❌ rechazada (motivo)

## Manifiesto

| # | Beat(s) shotlist | Qué es | Enlace directo al objeto | Museo / nº | Licencia | Resolución | Pase de fotografía | Archivo local |
|---|------------------|--------|--------------------------|------------|----------|------------|--------------------|---------------|
| 1 | | | | | CC0 / PD / licencia / ⚠️ | | ✅/⚠️/❌ + nota | `assets/…` |
| 2 | | | | | | | | |

## Gráficos propios (no van en el manifiesto — resumen para el brief de diseño)

| Gráfico | Beat(s) | Qué muestra | Datos / fuente [ID] |
|---------|---------|-------------|---------------------|
| G1 | | | |

## Huecos / a conseguir

- [ ] …

## Gate Stage 7

- [ ] Cada beat archivístico del shotlist tiene una imagen **aceptada** o un plan B (gráfico propio)
- [ ] Toda imagen con licencia clara (CC0 / PD / licencia obtenida)
- [ ] Coherencia de color/estado revisada por tramos, no solo por imagen
- [ ] Créditos de cortesía anotados para el bloque de descripción (`09-description.md`)
- [ ] Descargas hechas a `assets/` con nombres consistentes
