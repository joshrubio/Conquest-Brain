# Configuración de usuarios

Todo el sistema —reglas (`brain/`), plantillas, guías, archivos de episodio, la
ayuda de las herramientas— habla de **`Usuario 001`** y **`Usuario 002`**, nunca
de un nombre real. Así el sistema es **agnóstico**: se puede clonar para otro
canal cambiando un solo archivo.

Este documento y su gemelo técnico [`brain/USERS.md`](../brain/USERS.md) son los
**únicos dos sitios** donde aparecen las personas reales.

## La idea

- **Los slots son fijos:** `Usuario 001`, `Usuario 002` (y `Usuario 003…` si el
  equipo crece).
- **Las responsabilidades son ítems asignables**, no una identidad. La lista de
  abajo es el reparto *de esta iteración*; otro equipo puede repartirlo distinto
  sin tocar ningún otro archivo.
- **Las páginas de revisión HTML no nombran a nadie.** Usan palabras de rol:
  «revisión editorial», «aprobación editorial», «editor». El nombre real solo
  vive aquí.

## Este canal — "Exodo Channel"

| Slot | Persona |
|------|---------|
| Usuario 001 | Josh — escribe los guiones, producción, edición, publicación, tech, `tools/`, ideación T02. |
| Usuario 002 | Carmen — lead editorial, dirección de investigación, ideación T01, firma del fact-check (capa 3), pasada legal/ética + independencia. |

Los dos son **periodistas venezolanos**, parte del éxodo venezolano —el hecho que
le da nombre y tesis al canal (`brain/03`)—. Usuario 002 fue además profesora
universitaria.

### Reparto de responsabilidades (esta iteración)

| Ítem | Asignado a |
|------|------------|
| Escribe todos los guiones | Usuario 001 |
| Ideación — T02 Exploración | Usuario 001 |
| Producción, edición, publicación | Usuario 001 |
| Tech, `tools/` | Usuario 001 |
| Lead editorial, dirección de investigación | Usuario 002 |
| Ideación — T01 Historias Inspiradoras | Usuario 002 |
| Firma del fact-check (capa 3) | Usuario 002 |
| Pasada legal/ética + independencia/COI | Usuario 002 |
| Narración / a cámara | por episodio — cualquiera de los dos, se anota en `episodes/_STATUS.md` |
| Visto final de publicación (legal + independencia) | los dos |
| Cambiar un no-negociable | los dos, registrado en el historial git del archivo |

## Lo que NO se abstrae (se queda con datos reales)

- **Identidad git** — el `author` de los commits y el trailer `Co-Authored-By`
  son el historial real de un repo real. No se plantillea.
- **Línea del bumper en cámara** — los guiones y el modelo narrativo la escriben
  como `«Soy [nombre].»`; quien graba pone su propio nombre.
- **La marca** — `Exodo`, `@exodochannel`, la paleta, las tipografías
  (`brain/03`). La identidad del canal no es un ajuste por usuario.

## Clonar el sistema para otro canal

1. Cambia las dos tablas de arriba (y las de `brain/USERS.md`) por el equipo nuevo.
2. Reparte los ítems de responsabilidad como haga falta.
3. Nada más cambia: el resto de archivos ya dice `Usuario 00X`.

---

Relacionado: [`pipeline/1-las-12-etapas.md`](pipeline/1-las-12-etapas.md) (roles por etapa) ·
[`00-empieza-aquí.md`](00-empieza-aquí.md).
