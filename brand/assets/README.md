# brand/assets

Identidad fijada (`brain/03-brand-identity.md`). Contenido actual:
- `conquest-avatar.png` — avatar del canal (1254×1254). Fuente de `favicon.ico` / `favicon-32.png` / `apple-touch-icon.png` (`tools/theme.py` los sirve en cada página generada).
- `conquest-banner.png` — banner del canal.
- `favicon.ico`, `favicon-32.png`, `apple-touch-icon.png` — generados del avatar (Pillow, `im.save(..., sizes=[...])`); regenerar si el avatar cambia.
- `music/` — pool de Jamendo para las pistas de fondo.

Pendiente: logo.svg propio, plantillas de miniatura/lower-third/tarjeta de fuente, re-exportar el banner a 2560×1440 (ver `README.md` raíz, sección Estado).

Marca independiente — sin solape con ninguna otra marca o canal.
