---
doc: 00-empieza-aquí
summary: "Orientación: qué es el proyecto en 5 frases, en qué orden leer las guías, mapa del repo, reglas de oro."
audience: "cualquiera que se sume al equipo"
mirrors: [brain/INDEX, brain/06]
authority: guide
---

# Empieza aquí

Esta carpeta son **guías para leer y aprender**. No son reglas —las reglas viven en `brain/`, escritas en corto y en inglés—. Aquí explicamos, con ejemplos y en español, *cómo se piensa y se hace* un episodio de Exodo Channel y cómo funcionan las herramientas.

Cuando aparezca un término técnico que también existe en `brain/`, lo dejamos con su nombre original entre paréntesis la primera vez —así puedes saltar a la regla exacta si la necesitas—.

## ¿Para quién es esto?

- **Usuario 002** — para dominar el modelo narrativo, tu papel editorial y la investigación.
- **Usuario 001** — todo lo anterior + producción, herramientas y edición.
- **Cualquiera que se sume al equipo** — este archivo es su primer día.

> **`Usuario 001` / `Usuario 002`** son *slots*, no nombres. El sistema es agnóstico
> para poder clonarse a otro canal. Quién es quién y qué hace cada uno vive en
> [configuración-usuarios.md](configuración-usuarios.md) (y su gemelo técnico
> `brain/USERS.md`) — los únicos dos archivos con nombres reales.

## El proyecto en cinco frases

1. Exodo Channel es un canal de YouTube en español: **documentales narrados de casos reales** que cierran con una reflexión psicológica y una idea aplicable.
2. Referencia de formato: **Dieck Docs** (Farid Dieck). Adoptamos su *estructura*, no su nivel de fuentes —el nuestro es más alto—.
3. **Usuario 001 escribe todos los guiones.** El fact-check es automático (L1 + L2); el guionista resuelve las banderas. Usuario 002 dirige la línea editorial y la investigación. Ambos narran (se asigna por episodio).
4. Los sujetos son **públicos**: figuras públicas, casos históricos, empresas con documentación pública verificable. Nunca individuos privados, nunca gente que conozcamos.
5. **Ninguna afirmación sin fuente.** Cada dato lleva una etiqueta `[S..]` que apunta al registro de fuentes.

## Cómo leer estas guías

**Si vas a escribir un guion** (Usuario 001 y Usuario 002), lee en orden:

| # | Guía | Qué aprendes |
|---|------|--------------|
| 1 | [modelo-narrativo/1-anatomía-de-un-episodio](modelo-narrativo/1-anatomía-de-un-episodio.md) | Las 6 secciones y sus tiempos |
| 2 | [modelo-narrativo/2-cold-open-y-bumper](modelo-narrativo/2-cold-open-y-bumper.md) | El gancho de los primeros 40 segundos |
| 3 | [modelo-narrativo/3-la-espina-narrativa](modelo-narrativo/3-la-espina-narrativa.md) | Cronología, actos, foreshadowing, interludios |
| 4 | [modelo-narrativo/4-el-cierre](modelo-narrativo/4-el-cierre.md) | Las tres formas de cerrar (A / B / C) |
| 5 | [modelo-narrativo/5-reflexión-sin-moralina](modelo-narrativo/5-reflexión-sin-moralina.md) | Aterrizar una idea sin predicar |
| 6 | [modelo-narrativo/6-tono-y-voz](modelo-narrativo/6-tono-y-voz.md) | Cómo suena Exodo |
| 7 | [modelo-narrativo/7-titular-con-gancho](modelo-narrativo/7-titular-con-gancho.md) | Nombrar el episodio para que se vea |
| 8 | [modelo-narrativo/8-rigor-y-fuentes](modelo-narrativo/8-rigor-y-fuentes.md) | Tiers, `[S..]`, verdad vs. leyenda pulida |

**Si vas a producir o editar**, sigue con:

- [pipeline/1-las-12-etapas](pipeline/1-las-12-etapas.md) — el recorrido completo, quién hace qué, dónde están los "gates".
- [pipeline/2-de-idea-a-episodio](pipeline/2-de-idea-a-episodio.md) · [pipeline/3-los-3-protocolos](pipeline/3-los-3-protocolos.md) · [pipeline/4-fact-check](pipeline/4-fact-check.md)
- [pipeline/5-pase-de-estilo](pipeline/5-pase-de-estilo.md) · [pipeline/6-la-edición](pipeline/6-la-edición.md) · [pipeline/7-empaquetado-y-publicación](pipeline/7-empaquetado-y-publicación.md) · [pipeline/8-retro-y-métricas](pipeline/8-retro-y-métricas.md)
- [herramientas/0-instalación-y-claves](herramientas/0-instalación-y-claves.md) — qué instalar y cómo conseguir las claves de API. *(2ª pasada)*
- [herramientas/2-pull_assets](herramientas/2-pull_assets.md) — la herramienta central del Stage 7. *(2ª pasada)*

## Mapa del repositorio

```
Exodo/  (antes "Youtube")
  brain/            reglas permanentes, 00–16 + USERS.md (inglés, en corto)
  documentación/   ESTO — guías para aprender (español) · configuración-usuarios.md
  templates/       plantillas en blanco de cada etapa
  episodes/        una carpeta por episodio · _TEMPLATE-* para copiar · E000-EXAMPLE-* de referencia
  ideas/           el pool de ideas y las rúbricas
  research/        el análisis de Dieck Docs (transcripciones locales, no se suben)
  tools/           los scripts que mueven el pipeline
  brand/           el nombre, los assets, la música
```

## Reglas de oro (si solo recuerdas esto)

1. **Ninguna afirmación sin fuente.** Si no lo puedes citar, no va en el guion.
2. **Solo casos públicos y documentados.** Nunca alguien que conozcamos, nunca un chivatazo privado.
3. **La reflexión nombra un mecanismo, no da un sermón.**
4. **El fact-check es automático.** L1 (`factcheck.py`) + L2 (prompt LLM de banderas); el guionista resuelve cada bandera en el guion. Sin firma de segundo usuario.
5. **La miniatura y el título no prometen un giro que el vídeo no paga.**
