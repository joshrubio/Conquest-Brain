# USERS — slot ↔ person mapping

The rest of `brain/`, `templates/`, `documentación/`, the episode files and the
`tools/` help text are **agnostic**: they refer to **`Usuario 001`** and
**`Usuario 002`**, never to a real name. This file is the *only* place that maps
those slots to real people, and it is the file a new deployment edits first.

## The model

- **Slots are fixed** (`Usuario 001`, `Usuario 002`). Add `Usuario 003…` if a
  deployment has more people.
- **Responsibilities are assignable items**, not identities. The list below is
  *this deployment's* assignment; another team can split them differently
  without touching any other file.
- The HTML review pages (Stage 0 / 7 / 9 / 10) name **no one** — they use role
  words (“revisión editorial”, “aprobación editorial”, “editor”). Only this file
  and [../documentación/configuración-usuarios.md](../documentación/configuración-usuarios.md)
  carry real names.

## This deployment — "Exodo Channel"

| Slot | Person | Contact |
|------|--------|---------|
| Usuario 001 | Josh | joshuerubio@gmail.com |
| Usuario 002 | Carmen | — |

Both are Venezuelan journalists, part of the Venezuelan exodus — the fact that
gives the channel its name and its thesis (`brain/03`). Usuario 002 is also an
ex-university lecturer.

### Responsibility split (this iteration)

| Item | Assigned to |
|------|-------------|
| Writes every script | Usuario 001 |
| Ideation — T02 Exploración | Usuario 001 |
| Production, edit, publishing | Usuario 001 |
| Tech, `tools/` | Usuario 001 |
| Editorial lead, research direction | Usuario 002 |
| Ideation — T01 Historias Inspiradoras | Usuario 002 |
| Fact-check: resolve L2 flags in the script | Usuario 001 |
| Legal / ethics + independence-COI pass | Usuario 002 |
| Narration / on camera | per episode — either slot, logged in `episodes/_STATUS.md` |
| Final publish tick (legal + independence) | both |
| Change to a non-negotiable | both, in git history of the file changed |

## What stays real (never abstracted)

- **Git identity** — commit `author` and the `Co-Authored-By` trailer are a real
  history of a real repo. Not templated.
- **On-camera bumper line** — scripts and the narrative model write it as
  `«Soy [nombre].»`; whoever records fills in their own name.
- **Brand** — `Exodo`, `@exodochannel`, palette, fonts (`brain/03`). The channel
  identity is not a per-user setting.

## Reconfiguring for a new deployment

1. Replace the two tables above with the new team.
2. Re-assign the responsibility items as needed.
3. Nothing else changes — every other file already reads `Usuario 00X`.
