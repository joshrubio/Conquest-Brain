# Prompts de ilustración IA — E002 «Toyota / Taiichi Ohno»

> Stage 7 · sub-parte. Protocolo: `brain/15-ai-illustration-protocol.md`.
> **Modo visual del episodio (`brain/12`/`15` v2):** sujeto pobre en material real → el registro de recreación es el recurso **principal**, no la excepción. 19 imágenes, un solo estilo, rótulo en cada aparición.

| Campo | Valor |
|-------|-------|
| ID episodio | E002 |
| Nº de imágenes IA | 19 (registro de recreación — deliberado, `brain/15` regla 4) |
| Carpeta destino | `episodes/E002-toyota-taiichi-ohno/assets/ai/` |
| Nomenclatura | `E002_aiNN_<slug>.png` |
| Salida | ≥ 4K si el generador lo permite; si no, upscale |
| Rótulo en pantalla | `Recreación` (escenas) · `Ilustración — Conquest` (ai02, retrato de Ohno) — discreto, permanente |
| Fecha | 2026-09-11 |

## Bloque de estilo (compartido — va integrado en cada prompt de abajo)

```
Recreación fotográfica de época, estilo documental sobrio. Fotografía
analógica de mediados del siglo XX: grano fino de película, gama de color
apagada y desaturada (marrones, grises, verdes industriales), luz natural
o de nave de fábrica, contraste suave. Encuadre cinematográfico 16:9,
composición tranquila, sin dramatismo. Japón / Estados Unidos, 1920–1985
según la escena. Sin texto legible en ninguna superficie.
```

Excepción de estilo — **ai02 (retrato de Ohno)**: ilustración estilizada, no fotorrealista — grabado / carboncillo monocromo, el bigote como rasgo, para poder repetirla sin cruzar la línea del deepfake (`brain/15` regla 3).

## Negative prompt (compartido)

```
text, letters, words, kanji, signage, watermark, signature, logo, caption,
subtitles, recognizable real person face, identifiable face, portrait
likeness, deepfake, modern clothing, modern car, smartphone, plastic,
fake document, fake newspaper front page, fake photograph of record,
oversaturated, HDR, 3D render, CGI look
```

**Regla de caras (todas las escenas):** ninguna persona real identificable de frente. Sakichi / Kiichirō / Eiji Toyoda / Ohno / Minoura → de espaldas, en silueta, a contraluz, a media distancia o recortados por encima de los hombros. Obreros y figuras anónimas pueden verse, pero de perfil o a distancia media, sin ser retratos.

---

## ai01 — koromo-crisis

- **Beat(s) shotlist:** 1 (HOOK), 30, 32
- **Para qué:** la fábrica de Toyota en la crisis de 1950 — huelga, producción parada. Abre el episodio y reaparece en el beat de la quiebra.
- **Guardar como:** `E002_ai01_koromo-crisis.png`

```
[estilo compartido]
Exterior de una gran nave de fábrica de automóviles japonesa a finales de los
años 40, ladrillo y chapa ondulada, tarde nublada, penumbra. En primer término,
a media distancia y de espaldas, un grupo disperso de obreros con ropa de
trabajo y gorra parados junto a la verja; nadie trabaja. Portón de la fábrica
entreabierto. Sin pancartas legibles. Atmósfera de paro y espera, quietud.
Grano de película, color apagado.
```

---

## ai02 — ohno-portrait

- **Beat(s) shotlist:** 8 (HOOK · «giro»), 40
- **Para qué:** el retrato recurrente de Taiichi Ohno — el «giro» del cold open y su presentación en el pivote. Ilustración, no foto.
- **Guardar como:** `E002_ai02_ohno-portrait.png`

```
Ilustración monocroma estilizada (grabado / carboncillo, líneas firmes, NO
fotorrealista). Busto de un ingeniero japonés de mediados del siglo XX, traje
oscuro sencillo, gafas, bigote recortado como rasgo distintivo. Tres cuartos,
mirada fuera de cuadro, expresión seria y concentrada. Fondo neutro. Que
funcione como icono recurrente del episodio. Sin que sea el retrato exacto de
una persona real: rasgos genéricos + el bigote como motivo.
negative: photorealistic, photograph, color photo, identifiable likeness
```

---

## ai03 — sakichi-loom

- **Beat(s) shotlist:** 12, 13, 14
- **Para qué:** Sakichi Toyoda y el telar automático Tipo G (1924) — el origen de Toyota.
- **Guardar como:** `E002_ai03_sakichi-loom.png`

```
[estilo compartido]
Interior de un taller textil japonés de los años 1920. Un telar mecánico de
madera y acero de gran tamaño en funcionamiento, hilos tensados en el urdido,
lanzadera. A un lado, de espaldas y a media distancia, la figura de un inventor
con kimono de trabajo observando la máquina, cara no visible. Luz de ventana
alta, polvo de algodón en el aire, tonos madera y sepia. Grano de película.
```

---

## ai04 — loom-autostop

- **Beat(s) shotlist:** 15, 116 (eco del cierre)
- **Para qué:** el detalle que planta el *jidoka* — el telar se detiene solo cuando un hilo se rompe.
- **Guardar como:** `E002_ai04_loom-autostop.png`

```
[estilo compartido]
Plano detalle macro del mecanismo de un telar mecánico de los años 20: un solo
hilo de urdimbre roto colgando, y justo debajo la pieza de paro automático
accionada, la lanzadera detenida a media carrera. Todo lo demás quieto. Luz
lateral dura, poca profundidad de campo, foco en el hilo roto. Metal y madera
gastados. Sin texto.
```

---

## ai05 — kiichiro-chevy

- **Beat(s) shotlist:** 18, 20
- **Para qué:** Kiichirō Toyoda montando el departamento de automóviles — el primer motor por ingeniería inversa de un Chevrolet (años 30).
- **Guardar como:** `E002_ai05_kiichiro-chevy.png`

```
[estilo compartido]
Interior de un taller de máquinas japonés de los años 30. Sobre bancos de
trabajo, un motor de automóvil de seis cilindros desmontado pieza por pieza,
ordenado como un despiece; un chasis de coche americano de los años 30 al fondo,
parcialmente desmontado. Dos hombres con bata de ingeniero inclinados sobre las
piezas, de espaldas / de perfil, caras no visibles. Herramientas, calibres. Luz
de nave, tonos grises y aceite. Grano de película.
```

---

## ai06 — model-aa

- **Beat(s) shotlist:** 21
- **Para qué:** el primer coche de pasajeros de Toyota, el Model AA (1936).
- **Guardar como:** `E002_ai06_model-aa.png`

```
[estilo compartido]
Un sedán japonés de 1936, líneas aerodinámicas de la época (inspirado en los
americanos de mediados de los 30), carrocería oscura, aparcado en el patio de
una fábrica. Tres cuartos delantero, sin ocupantes, sin logotipos legibles.
Luz de mañana nublada, adoquín húmedo. Fotografía de época, color apagado,
grano de película.
```

---

## ai07 — war-trucks

- **Beat(s) shotlist:** 23, 26, 38
- **Para qué:** Toyota fabricando camiones para el ejército japonés durante la guerra.
- **Guardar como:** `E002_ai07_war-trucks.png`

```
[estilo compartido]
Interior de una nave de montaje de camiones a principios de los años 40. Una
fila de camiones militares de cabina sencilla en distintas fases de montaje,
chasis y cabinas. Obreros a media distancia, de perfil, monos de trabajo, gorra.
Luz de claraboya polvorienta, tonos verde militar y gris acero. Sin insignias
legibles. Grano de película.
```

---

## ai08 — koromo-bombed

- **Beat(s) shotlist:** 24
- **Para qué:** el bombardeo del 14 de agosto de 1945 — una cuarta parte de la planta de Koromo destruida.
- **Guardar como:** `E002_ai08_koromo-bombed.png`

```
[estilo compartido]
Una parte de una nave de fábrica japonesa tras un bombardeo, agosto de 1945:
cubierta hundida, vigas de acero retorcidas, un ala en pie y otra abierta al
cielo, cascotes. Sin fuego, sin personas, primeras horas de la mañana, luz
plana. Contención, no espectáculo. Blanco y negro tirando a sepia, grano
grueso de película de la época.
```

---

## ai09 — kiichiro-leaves

- **Beat(s) shotlist:** 4 (cold open), 33, 34
- **Para qué:** Kiichirō Toyoda dimite en junio de 1950 asumiendo la responsabilidad de los despidos; muere en 1952.
- **Guardar como:** `E002_ai09_kiichiro-leaves.png`

```
[estilo compartido]
Un hombre trajeado de mediana edad, de espaldas, cruzando solo el patio vacío
de una fábrica hacia la salida, abrigo al brazo, tarde gris de 1950. Cámara
detrás, a distancia media, cara nunca visible. Nave de fábrica al fondo,
ventanas apagadas. Sensación de despedida silenciosa. Color apagado, grano de
película.
```

---

## ai10 — shopfloor-chaos

- **Beat(s) shotlist:** 56, 84, 122 (eco del cierre)
- **Para qué:** el taller de Toyota antes del método — motores parados esperando, almacenes intermedios desbordados, cada taller a su ritmo.
- **Guardar como:** `E002_ai10_shopfloor-chaos.png`

```
[estilo compartido]
Interior de un taller de fábrica de coches japonés de principios de los 50,
desordenado: motores terminados apilados en el suelo bajo lonas esperando,
estanterías y palés de piezas amontonados hasta bloquear los pasillos, una
cinta de montaje parada al fondo. Uno o dos obreros a media distancia, de
perfil. Luz de nave irregular, tonos grises y óxido. Sensación de atasco.
Grano de película.
```

---

## ai11 — kanban-card

- **Beat(s) shotlist:** 64 (PROMISE 1), 66, 68 (PAY 1), 124 (eco del cierre)
- **Para qué:** la tarjeta *kanban* — el «trozo de cartón» en el centro del sistema.
- **Guardar como:** `E002_ai11_kanban-card.png`

```
[estilo compartido]
Plano detalle: una tarjeta de cartón rectangular, gastada y con las esquinas
dobladas, metida en un soporte metálico sujeto a una caja industrial de piezas
de acero de los años 50. La caja sobre un carro de fábrica. Sin texto legible
en la tarjeta (rejilla y marcas impresas, ilegibles). Luz lateral suave, foco
en la tarjeta, fondo de taller desenfocado. Cartón, metal, grano de película.
```

---

## ai12 — andon-cord

- **Beat(s) shotlist:** 70, 71
- **Para qué:** el derecho a parar la línea — un obrero tira del cable y la cadena entera se detiene.
- **Guardar como:** `E002_ai12_andon-cord.png`

```
[estilo compartido]
Una mano y un antebrazo con manga de mono de trabajo tirando de un cable /
cordón que cuelga sobre una cadena de montaje de automóviles de los años 50 o
60. Encima, una lámpara de aviso encendida. La cinta, quieta. Fondo: la línea
detenida, alguna figura a distancia girándose. Cara no visible. Luz de nave,
color apagado, foco en la mano y el cable. Grano de película.
```

---

## ai13 — supermarket-slides

- **Beat(s) shotlist:** 75, 79
- **Para qué:** un compañero de Toyota, vuelto de EE.UU. hacia 1951–52, enseña diapositivas a color de un supermercado americano.
- **Guardar como:** `E002_ai13_supermarket-slides.png`

```
[estilo compartido]
Una sala de reuniones austera de una fábrica japonesa, principios de los 50, a
oscuras. Un proyector de diapositivas sobre la mesa lanza sobre una pantalla /
pared la imagen a color de un pasillo de supermercado americano lleno de
estantes. Alrededor, de espaldas y en silueta, tres o cuatro hombres trajeados
mirando la proyección. Contraste entre el gris de la sala y el color vivo de la
diapositiva. Grano de película.
```

---

## ai14 — ohno-supermarket

- **Beat(s) shotlist:** 82
- **Para qué:** Ohno recorre por fin un supermercado americano en persona, 1956.
- **Guardar como:** `E002_ai14_ohno-supermarket.png`

```
[estilo compartido]
Interior de un supermercado estadounidense de mediados de los 50: pasillo largo
de estantes llenos, suelo encerado, carteles de oferta (ilegibles). En primer
término, de espaldas y a media distancia, un hombre japonés bajo con traje y
sombrero, solo, mirando los estantes con atención, un carrito vacío. Cara no
visible. Luz fluorescente fría, colores de la época algo apagados. Grano de
película.
```

---

## ai15 — chalk-circle

- **Beat(s) shotlist:** 91, 92, 128 (eco del cierre)
- **Para qué:** el «círculo de Ohno» — Minoura de pie ocho horas dentro de un círculo de tiza mirando el proceso.
- **Guardar como:** `E002_ai15_chalk-circle.png`

```
[estilo compartido]
Planta de una fábrica de coches japonesa, años 60. En el suelo de hormigón, un
círculo dibujado con tiza. Dentro, de pie e inmóvil, un ingeniero joven con
camisa blanca y corbata, de espaldas o de perfil, mirando hacia una cadena de
montaje que funciona al fondo. Cara no visible. Luz de nave. Contraste entre la
quietud de la figura y el movimiento borroso de la línea. Grano de película.
```

---

## ai16 — supplier-daily

- **Beat(s) shotlist:** 87
- **Para qué:** los proveedores tardaron hasta 1955 en aceptar entregar un poco cada día en vez de un camión al mes.
- **Guardar como:** `E002_ai16_supplier-daily.png`

```
[estilo compartido]
El muelle de carga de una fábrica, mediados de los 50. Una furgoneta pequeña
descargando unas pocas cajas de piezas metálicas — una entrega modesta, no un
camión lleno. Un operario de perfil recogiéndolas con un carro. Primera hora de
la mañana, luz rasante. Tonos grises y azules de trabajo. Grano de película.
```

---

## ai17 — toyota-seminars

- **Beat(s) shotlist:** 102
- **Para qué:** el gobierno japonés monta seminarios para estudiar el método de Toyota (años 70).
- **Guardar como:** `E002_ai17_toyota-seminars.png`

```
[estilo compartido]
Una sala de conferencias llena, años 70, vista desde el fondo por encima de las
cabezas del público (nucas, trajes). Al frente, una pizarra con un diagrama de
flechas dibujado a mano (ilegible) y una figura señalándolo, de espaldas. Luz
de tubo fluorescente, moqueta y madera de la época, tonos marrones. Grano de
película.
```

---

## ai18 — ohno-book

- **Beat(s) shotlist:** 104
- **Para qué:** en 1978 Ohno publica su libro contando el sistema.
- **Guardar como:** `E002_ai18_ohno-book.png`

```
[estilo compartido]
Plano detalle cenital: un libro de tapa dura sobrio de finales de los 70 sobre
una mesa de madera, junto a unas gafas y un lápiz. Sobrecubierta lisa, sin
título legible. Luz de flexo cálida, sombra larga. Papel y tela gastados.
Grano de película.
```

---

## ai19 — nummi-line

- **Beat(s) shotlist:** 110
- **Para qué:** la cadena de NUMMI (Fremont, 1984) funcionando con la vieja plantilla de GM y el método de Toyota.
- **Guardar como:** `E002_ai19_nummi-line.png`

```
[estilo compartido]
Interior de una planta de montaje de automóviles estadounidense a mediados de
los 80: una cadena ordenada y despejada, carrocerías en fila, estaciones de
trabajo limpias, paneles de tarjetas en la pared (ilegibles). Obreros
estadounidenses variados con mono y guantes trabajando de perfil, a distancia
media. Luz industrial homogénea, tonos neutros, sensación de orden. Grano de
película sutil.
```

---

## Después de generar

1. `python tools/pull_assets.py E002-toyota-taiichi-ohno` — estos prompts salen en la columna derecha de `07-style-pass.html`.
2. Por prompt: 3–4 variantes → elige la que más pega con el set → pega su ruta/URL en el input del prompt.
3. «Finalizar Stage 7» → `python tools/pull_assets.py E002-toyota-taiichi-ohno --download` copia cada imagen a `assets/ai/` con su nombre e imprime la fila de manifiesto.
4. Claude añade las filas IA a `07-assets.md` y anota el rótulo en `09-description.md`.
