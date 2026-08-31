---
doc: pipeline/8-retro-y-métricas
summary: "Stage 12: cuándo (48h + 30d), los KPI, el KPI log, qué produce el retro (fixes de proceso), revisiones cada ~5 episodios."
audience: "ambos"
mirrors: [brain/07]
authority: guide
---

# Retro y métricas (Stage 12)

La última etapa cierra el bucle: qué funcionó, qué se corrige en el *proceso* (no solo en el episodio), y qué dicen los números.

Regla: `brain/07-publishing-seo-metrics.md`, `brain/06` Stage 12. Producto: `11-retro.md` (plantilla `templates/episode-retro.md`).

## Cuándo

Dos cortes: **a las 48 h** y **a los 30 días** de publicar. El de 48 h es señal temprana (CTR, primeros minutos de retención); el de 30 d es el juicio real.

## Qué se mira — los KPI

| Métrica | Por qué | Lectura temprana |
|---------|---------|------------------|
| Duración media de visionado (%) | Salud del formato / ritmo | > 45% bien para 15–25 min |
| Retención en el marcador «Reflexión» | ¿Se queda la audiencia para el pago? | Ojo al acantilado |
| Retención en el marcador «Para llevar» | ¿Aterriza el takeaway? | — |
| CTR | Honestidad + tirón de título/miniatura | 4–8% típico |
| Espectadores que vuelven | Pegajosidad de la serie | Tendencia al alza |
| Calidad de comentarios | ¿Provocamos pensamiento o indignación? | Cualitativo |
| Suscriptores / 1k visitas | Eficiencia construyendo audiencia | Tendencia al alza |

**Las visitas por sí solas no son el objetivo — la audiencia que vuelve, sí.**

## El registro

Cada retro añade una fila al **KPI log** de `brain/07`:

| Episode | Pub date | Length | Views 30d | AVD % | CTR % | Subs gained | Notes |
|---------|----------|--------|-----------|-------|-------|-------------|-------|

## Qué produce el retro

1. **Qué funcionó / qué no** — en el gancho, la estructura, el cierre, la miniatura.
2. **Correcciones emitidas** — si apareció un error tras publicar: comentario fijado + nota en la descripción + tarjeta si es material. Registrado aquí. Nunca re-subir en silencio (ver [modelo-narrativo/8-rigor-y-fuentes](../modelo-narrativo/8-rigor-y-fuentes.md) §9).
3. **Fixes de proceso** — la tabla más importante: `| Cambio propuesto | Archivo de brain/ a editar | Responsable |`. Si el retro no cambia una regla o una plantilla, probablemente no se ha mirado bien.

## Revisiones periódicas (no por episodio)

Cada ~5 episodios publicados:

- ¿Se inclina todo hacia un track (T01 / T02)?
- ¿Los hooks siguen funcionando (CTR)?
- ¿Algún subtema de Exploración deriva a tono sensacionalista?
- Fijar / revisar la cadencia (`brain/07`).

## Actualizar el estado

`episodes/_STATUS.md` pasa a `publicado`; se añade la fila al KPI log. El episodio está cerrado.

---

Relacionado: [7-empaquetado-y-publicación](7-empaquetado-y-publicación.md) · [1-las-12-etapas](1-las-12-etapas.md) · [2-de-idea-a-episodio](2-de-idea-a-episodio.md).
