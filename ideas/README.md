# Sistema de temas e ideas

Dos niveles. Una idea de video **no** se produce si no cuelga de un **tema aprobado**.

```
TEMA (área recurrente)  ──filtro──►  aprobado / vetado
   │
   └─ IDEA de video individual  ──rúbrica──►  aprobada / incubando / descartada
                                                   │
                                                   └─ carpeta de episodio E0XX
```

## Nivel 1 — Temas / topics

Un **tema** es un área recurrente que el canal puede cubrir muchas veces (ej.: "manías especulativas", "fundadores que cayeron", "persuasión y sectas", "inventos que mintieron sobre lo que hacían").

- Registro: [themes.md](themes.md)
- Filtro para aceptar o vetar un tema: [theme-rubric.md](theme-rubric.md)
- Criterios clave: encaje con la tesis del canal, ¿hay suficientes casos con registro público para sostener una serie?, riesgo de tono, y **política de separación** (`docs/05-separation-policy.md`).

## Nivel 2 — Ideas de videos individuales

Una **idea** es un caso concreto (una figura, un caso histórico, una empresa) dentro de un tema aprobado.

- Pool: [idea-pool.md](idea-pool.md)
- Rúbrica por idea: [evaluation-rubric.md](evaluation-rubric.md) (7 filtros eliminatorios + puntuación /21)

## Flujo

1. ¿El caso encaja en un tema ya aprobado en `themes.md`? Si no hay tema → primero pasar el tema por `theme-rubric.md`.
2. Añadir la idea a `idea-pool.md` con su `tema`.
3. Correr `evaluation-rubric.md`. ≥14 y eliminatorios OK → `aprobada`.
4. Al arrancar: copiar `episodes/_TEMPLATE-episode-folder/` → `episodes/E0XX-<slug>/`, actualizar `episodes/_STATUS.md`.
