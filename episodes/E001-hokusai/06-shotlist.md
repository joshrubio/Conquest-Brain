# Shotlist / B-roll — E001 «Hokusai» (v3)

> Stage 6. Inferida del guion bloqueado (`brain/11-visual-rhythm.md`). **v3 (ritmo brain/11 §2.2) — 2026-09-08.** Reconstrucción de la espina siguiendo el estándar de duración de plano v2 (§2.2): se planifica por DURACIÓN, no por número de beats. Las ventanas de cada sección están medidas sobre la voz entregada (`assets/E001-vo.words.json`, 2530 palabras, 942 s / 15:42). Incorpora las recomendaciones de `09-pacing-audit.md`.
> v2 (2026-09-08, 48 beats sobre el guion v2.0) queda obsoleta: demasiado escasa para 15:42 — `assemble.py` estiraba beats a 60–150 s sobre un visual fijo (dead air).

| Campo | Valor |
|-------|-------|
| ID episodio | E001 |
| Versión de guion | v2.0 (continuidad narrativa) + fact-check L2 2026-09-08 |
| Narrador del episodio | Usuario 002 |
| Responsable | Usuario 001 |
| Fecha | 2026-09-08 |

## Heurística aplicada (`brain/11 §1b + §2.1 + §2.2`)

**Se planifica por duración de plano (`§2.2`).** 117 filas → ~106 beats tras
`align()`/`_repace`, 942 s ÷ ~9 s de media. Ventanas de sección medidas sobre la
VO entregada; `in` es una estimación (assemble re-alinea al `frag` contra los
timestamps de palabra), `dur` sale de la tabla `§2.2`.

**A-roll / B-roll (`§1b`, `§2.6`):** el narrador está a cámara (`acamara`) en el
cierre del cold open, el bumper, cada pivote/bisagra, **la entrada de cada acto**,
un corte de preparación antes de **cada `[PROMISE]` y cada `[PAY]`** (el plano-rima
en sí es B-roll), los beats de opinión/primera persona, **todo el cierre** y la CTA.
**~34 beats a cámara ≈ 31 %** — dentro de la horquilla 30–40 %. Ninguna sección se
queda sin beat A-roll.

**Explicadores (`§2.1` regla 4, revisada 2026-09-08):** gráfico denso = **un beat
sostenido 10–18 s** con build interno + b-roll antes/después, **nunca intercalado**.
EXPLICADOR 1 (ukiyo-e) = `G1_ukiyoe_pipeline` un solo beat (b18, ~13 s), rodeado de
lámina barata (b16) + talla real en vídeo (b17) + corte a cámara (b19). EXPLICADOR 2
(azul de Prusia) = `G3_prussian_blue` (b63) → `G3_blue_route` (b65, ~13 s), gráficos
**distintos**. EXPLICADOR 3 (Manji) = `G3b_signature_manji` un solo beat (b78, ~12 s)
+ la firma real (b79).

**Un `id` de gráfico, una aparición (`§2.1` regla 4b):** el único que se repite es
`G2_names_timeline` — y sólo por la rima PROMISE 1 (b24) → PAY 1 (b91). El cierre
recuerda «los 30 nombres» sólo con la voz.

**PROMISE → PAY (`§2.1` regla 5):** mismo `asset` y `motion` las dos veces.
1 · `G2_names_timeline` / pan-h (b24 → b91). 2 · `E001_ai02_daruma-nagoya-1817`
/ push (b49 → b98). 3 · `beat20_met_57261` / push (b54 → b68). 4 · `E001_ai04_closing-path`
/ push (b88 → b92).

**Reutilización de archivo (`§2.1` regla 4c):** ≤ 3× por vídeo, ≤ 2× por sección
(salvo pareja `PROMISE`→`PAY`). 77 beats B-roll / **50 assets únicos** (ratio 1,5).
Máximo actual 3×: «La gran ola» (b60·66·113), el retrato anciano (b7 + 2 ecos del
cierre), el Fuji rojo, el retrato `beat20_custom_20`, `E001_ai02`/`E001_ai04`
(PROMISE/PAY + 1). Ningún asset adyacente. **Los gráficos no se reutilizan** (4b).
`assemble.py` avisa de un 4º uso o de un 3º en la misma sección.

## A cámara (A-roll · narrador: Usuario 002)

Beats `acamara` (`asset` = `—`, `motion` = `cut`; `assemble.py` recorta la toma de
Stage 8 a la ventana del beat, sin Ken Burns):

**9, 10, 11, 21, 25, 27, 30, 35, 37, 39, 42, 44, 46, 50, 52, 55, 63, 69, 71, 73, 74, 80, 84, 87, 89, 91, 94, 97, 101, 103, 105, 107, 109, 111, 113, 115, 117, 119, 120, 121**

| Aspecto | Valor |
|---------|-------|
| Encuadre | Plano medio corto, mirada a cámara |
| Fondo / luz | Set fijo de serie (`brain/03`) |
| Toma | una sola toma continua (talking-head), ya grabada; cualquier ventana sirve |

## Reparto por sección (beats · segundos)

| Sección | beats | seg | nota de ritmo (`§2.2`) |
|---------|-------|-----|------------------------|
| cold open | 9 | 51 | héroe 10 s + 5 clips de hook 4–6 s + giro + a cámara → negro |
| bumper | 1 | 4 | 1 beat A-roll, «Hola, mi nombre es…» + wordmark |
| pivote | 5 | 31 | bisagra a cámara + mapas/época con movimiento lento |
| explicador (1) | 6 | 47 | secuencia G1 (3 etapas) + archivo + corte a cámara |
| contexto | 5 | 33 | aprendizaje + PROMISE 1 |
| acto 1 | 25 | 227 | narrativa B-roll ~7–9 s + cortes a cámara en opinión/mito |
| acto 2 | 5 | 36 | deudas del nieto + PROMISE 3 |
| acto 3 | 17 | 128 | 36 vistas / Ola / EXPLICADOR 2 / PAY 3 / opinión a cámara |
| acto 4 | 19 | 126 | nota de 1834 / escalera de edades / EXPLICADOR 3 / incendio / Ōi / PROMISE 4 |
| acto 5 | 10 | 77 | muerte 1849 / PAY 1 / japonismo / PAY 2 |
| cierre | 17 | 164 | A-roll en tramos de ~12–15 s, cortando a imágenes ya vistas 4–6 s |
| cta | 2 | 18 | a cámara + rótulo «Fuentes principales» |
| **Total** | **117 filas → ~109 beats** | **942** | **A-roll ~31 %** · 50 assets B-roll únicos |

## Timeline — la espina (una fila por beat, en orden de emisión · `assemble.py` / `edit_timeline.py` la parsean)

| # | in | dur | sección | tipo | asset | rótulo | motion | marcador | guion (frag.) |
|---|----|-----|---------|------|-------|--------|--------|----------|---------------|
| 1 | 0:00 | 10 | cold open | ia | beat1_custom_1 | Ilustración — Conquest | push | HOOK | «un hombre de unos 88 años se estaba muriendo» |
| 2 | 0:10 | 5 | cold open | stock | intro02 | — | cut | — | «en un cuarto de alquiler de Edo» |
| 3 | 0:15 | 5 | cold open | stock | intro04 | — | cut | — | «llevaba más de 70 años dibujando» |
| 4 | 0:20 | 4 | cold open | stock | beat2 | — | cut | — | «había publicado miles de imágenes» |
| 5 | 0:24 | 5 | cold open | archivo | beat3_commons_5576388 | — | zoom | — | «una ola curvada como una garra» |
| 6 | 0:29 | 4 | cold open | stock | intro03 | — | cut | — | «una de las imágenes japonesas más reproducidas del mundo» |
| 7 | 0:33 | 6 | cold open | archivo | beat4_commons_124369341 | — | pan-v | — | «lo último que pidió no fue a despedirse de nadie» |
| 8 | 0:39 | 4 | cold open | negro | — | 5 años… / 10 años… | cut | — | «cinco años más dicen unas versiones» |
| 9 | 0:43 | 10 | cold open | acamara | — | — | cut | HOOK | «voy a intentar convencerte de lo contrario» |
| 10 | 0:53 | 4 | bumper | acamara | — | Conquest | cut | — | «Hola, mi nombre es» |
| 11 | 0:57 | 4 | pivote | acamara | — | — | cut | — | «Para situarnos» |
| 12 | 1:01 | 7 | pivote | archivo | beat7_commons_127164101 | — | pan-h | — | «nace hacia 1760 en el distrito de Katsushika» |
| 13 | 1:08 | 7 | pivote | archivo | beat13_custom_13 | — | pan-h | — | «Japón lleva más de un siglo prácticamente cerrado al exterior» |
| 14 | 1:15 | 6 | pivote | archivo | beat14_custom_14 | — | push | — | «es probablemente la ciudad más grande del mundo» |
| 15 | 1:21 | 12 | pivote | gráfico | G8_edo_population | ~1 millón — las fuentes varían | push | — | «cerca de un millón de personas» |
| 16 | 1:33 | 8 | explicador | archivo | beat14_commons_1499270 | — | pan-v | — | «va a ser el oficio de Hokusai los 70 años siguientes; grabados hechos para venderse barato» |
| 17 | 1:41 | 7 | explicador | archivo | woodblock_carving | — | cut | — | «el artista entrega un dibujo, un tallador lo copia sobre planchas de madera, una por cada color» |
| 18 | 1:48 | 13 | explicador | gráfico | G1_ukiyoe_pipeline | — | push | EXPLICADOR 1 | «un impresor estampa estas planchas encima de otra; la firma es del dibujante» |
| 19 | 2:01 | 9 | explicador | acamara | — | — | cut | — | «el artista no toca la madera ni la tinta» |
| 20 | 2:10 | 7 | contexto | archivo | beat11_met_37189 | — | push | — | «entra, como aprendiz, en el taller de un maestro conocido» |
| 21 | 2:17 | 6 | contexto | archivo | beat10_commons_77578681 | — | pan-h | — | «especializado en retratos de actores de teatro» |
| 22 | 2:23 | 6 | contexto | archivo | beat11_custom_11 | — | zoom | — | «la escuela le da un nombre de trabajo» |
| 23 | 2:29 | 5 | contexto | acamara | — | — | cut | PROMISE 1 | «va a ser el primero de una lista larguísima» |
| 24 | 2:34 | 11 | contexto | gráfico | G2_names_timeline | ~30 nombres — recuento aproximado | pan-h | PROMISE 1 | «el nombre no es suyo, es de la casa» |
| 25 | 2:45 | 11 | acto 1 | acamara | — | — | cut | — | «La primera vez que empieza de cero» |
| 26 | 2:56 | 9 | acto 1 | archivo | beat12_met_53446 | — | push | — | «En 1793 muere» |
| 27 | 3:05 | 8 | acto 1 | archivo | beat10_commons_77578681 | — | pan-h | — | «estudiando el estilo de talleres rivales» |
| 28 | 3:13 | 10 | acto 1 | acamara | — | — | cut | — | «no hay un documento que lo confirme» |
| 29 | 3:23 | 8 | acto 1 | archivo | beat14_commons_26134200 | — | pan-h | — | «estampa europea que entraba por Nagasaki» |
| 30 | 3:31 | 8 | acto 1 | archivo | beat16_custom_16 | — | pan-v | — | «dibujo de la calle, de la gente corriente» |
| 31 | 3:39 | 9 | acto 1 | archivo | beat31_custom_31 | — | pan-h | — | «Alrededor de 30 nombres artísticos en total» |
| 32 | 3:48 | 9 | acto 1 | archivo | beat14_commons_10969306 | — | zoom | — | «traspasar más de un nombre suyo a un discípulo» |
| 33 | 3:57 | 10 | acto 1 | acamara | — | — | cut | — | «cada nombre nuevo coincidía con un cambio» |
| 34 | 4:07 | 8 | acto 1 | archivo | beat11_met_37189 | — | pan-h | — | «una exploración en su manera de dibujar» |
| 35 | 4:15 | 14 | acto 1 | acamara | — | — | cut | — | «un genio ignorado que mal vendía láminas» |
| 36 | 4:29 | 9 | acto 1 | archivo | beat22_custom_22 | — | push | — | «tuvo nombre, tuvo público» |
| 37 | 4:38 | 10 | acto 1 | acamara | — | — | cut | — | «lo que no tuvo nunca fue estabilidad» |
| 38 | 4:48 | 9 | acto 1 | archivo | beat20_custom_20 | — | pan-v | — | «fue pobre, pobre de verdad, con estrecheces reales» |
| 39 | 4:57 | 10 | acto 1 | gráfico | G9_moves_map | ~93 mudanzas — origen incierto | push | — | «se cuenta que se mudó unas 93 veces» |
| 40 | 5:07 | 8 | acto 1 | acamara | — | — | cut | — | «la cifra hay que cogerla con pinza» |
| 41 | 5:15 | 9 | acto 1 | archivo | beat41_custom_41 | — | pan-h | — | «porque no llegaba fin de mes» |
| 42 | 5:24 | 9 | acto 1 | acamara | — | — | cut | — | «Así llega a los 50 años» |
| 43 | 5:33 | 10 | acto 1 | stock | swap_43_ab25d7b0 | — | pan-v | — | «publica lo que le da fama de verdad, los Hokusai Manga» |
| 44 | 5:43 | 7 | acto 1 | acamara | — | — | cut | — | «no se trata de un comic o un manga» |
| 45 | 5:50 | 9 | acto 1 | archivo | manga_detail | — | pan-h | — | «gente trabajando, animales, olas, plantas» |
| 46 | 5:59 | 10 | acto 1 | ia | E001_ai02_daruma-nagoya-1817 | Ilustración — Conquest | push | — | «en la ciudad de Nagoya, monta un espectáculo» |
| 47 | 6:09 | 8 | acto 1 | archivo | beat18_custom_18 | — | zoom | — | «figuras diminutas sobre granos de arroz» |
| 48 | 6:17 | 6 | acto 1 | acamara | — | — | cut | PROMISE 2 | «Le gustaba que lo vieran hacerlo a Hokusai le gustaba lo grande» |
| 49 | 6:31 | 10 | acto 2 | acamara | — | — | cut | — | «con sesenta y muchos años, le cae encima la peor racha» |
| 50 | 6:41 | 8 | acto 2 | archivo | swap_50_2c93b043 | — | push | — | «Hokusai las asume y las paga un nieto, hijo de una de sus hijas, contrae deudas» |
| 51 | 6:56 | 5 | acto 2 | acamara | — | — | cut | — | «solo que ahora, sin la energía de los treinta» |
| 52 | 7:01 | 6 | acto 2 | archivo | swap_52_fe3149b3 | — | push | PROMISE 3 | «Setenta años, arruinado por las deudas del nieto» |
| 53 | 7:07 | 8 | acto 3 | archivo | beat22_custom_22 | — | pan-h | — | «publica la serie 36 vistas del monte Fuji» |
| 54 | 7:15 | 7 | acto 3 | gráfico | G_36to46 | 36 → 46 | push | — | «Digo 36, pero acabaron siendo 46» |
| 55 | 7:22 | 7 | acto 3 | archivo | beat23_custom_23 | — | push | — | «El Fuji desde un campo de arroz» |
| 56 | 7:29 | 6 | acto 3 | archivo | fuji_barrel_met36500 | — | pan-h | — | «entre los andamios de un tonelero» |
| 57 | 7:35 | 7 | acto 3 | archivo | beat24_commons_39740407 | — | push | — | «El Fuji rojo contra el cielo despejado» |
| 58 | 7:42 | 7 | acto 3 | archivo | beat25_commons_2646210 | — | zoom | — | «una ola inmensa con la cresta abierta en garras de espuma» |
| 59 | 7:49 | 6 | acto 3 | acamara | — | — | cut | — | «tenía unos 70 años cuando hizo Detente y mírala un momento» |
| 60 | 8:04 | 9 | acto 3 | gráfico | G3_prussian_blue | — | push | EXPLICADOR 2 | «importado de Europa por qué esa serie se ve como se ve; un pigmento azul sintético» |
| 61 | 8:19 | 13 | acto 3 | gráfico | G3_blue_route | — | pan-h | EXPLICADOR 2 | «llega por Nagasaki a un precio que permite usarlo para la producción en masa; Hokusai construye una buena parte de las 36 vistas sobre ese azul nuevo» |
| 62 | 8:32 | 8 | acto 3 | archivo | beat25_commons_2646210 | — | zoom | EXPLICADOR 2 | «la imagen más japonesa que conoces está hecha en parte con tecnología europea recién llegada» |
| 63 | 8:41 | 7 | acto 3 | acamara | — | — | cut | PAY 3 | «el hombre arruinado por las deudas del nieto, el que llevaba medio siglo cambiándose el nombre» |
| 64 | 8:48 | 8 | acto 3 | archivo | swap_64_fe3149b3 | — | push | PAY 3 | «hizo eso a los 70» |
| 65 | 8:56 | 14 | acto 3 | acamara | — | — | cut | — | «medio siglo de trabajo y una mala racha así es como suele pasar» |
| 66 | 9:16 | 9 | acto 3 | acamara | — | — | cut | — | «¿alguna vez te ha pasado algo así? déjame en los comentarios» |
| 67 | 9:25 | 10 | acto 4 | archivo | swap_67_53a18ff6 | — | push | — | «en 1834 publica otro libro sobre el Fuji y al final añade una nota firmada de su puño» |
| 68 | 9:35 | 9 | acto 4 | acamara | — | — | cut | — | «que desde los 73 empezaba a entender un poco cómo están hechos los animales, las plantas dice en esencia, y esto es una traducción nuestra, que nada de lo que ha hecho antes de los 70 merecía la pena» |
| 69 | 9:50 | 16 | acto 4 | gráfico | G4_age_ladder | traducción propia | pan-v | — | «que a los 80 lo haría mucho mejor, a los 90 penetraría el sentido de las cosas, a los 100 lo extraordinario, y a los 110 cada punto y cada línea que trazara estarían vivos» |
| 70 | 10:06 | 7 | acto 4 | archivo | swap_70_81b0d516 | — | pan-h | — | «lo escribió a los 74 años, y ya había hecho la gran ola» |
| 71 | 10:13 | 10 | acto 4 | acamara | — | — | cut | — | «su balance es: todavía no sé nada, pero voy en la dirección correcta» |
| 72 | 10:10 | 12 | acto 4 | gráfico | G3b_signature_manji | traducción propia | push | EXPLICADOR 3 | «firmaba muchas de sus obras tardías con un nombre nuevo no era falsa modestia… algo así como el viejo loco por la pintura» |
| 73 | 10:28 | 5 | acto 4 | acamara | — | — | cut | — | «el viejo que sigue obsesionado con esto» |
| 74 | 10:33 | 8 | acto 4 | ia | E001_ai03_studio-fire-night | Ilustración — Conquest | push | — | «hacia 1839 un incendio destruyó su casa taller» |
| 75 | 10:41 | 6 | acto 4 | archivo | edo_fire_print | — | pan-h | — | «los incendios eran frecuentes en el Edo de casas de madera» |
| 76 | 10:47 | 6 | acto 4 | acamara | — | — | cut | — | «igual que a los 33, igual que a los 70» |
| 77 | 10:53 | 8 | acto 4 | archivo | swap_77_0790ca34 | — | pan-h | — | «sus últimos años los pasa trabajando con su hija» |
| 78 | 11:01 | 7 | acto 4 | acamara | — | — | cut | — | «salió en realidad de su mano» |
| 79 | 11:08 | 5 | acto 4 | archivo | beat37_custom_37 | — | pan-v | — | «una pregunta que probablemente no se cierre nunca» |
| 80 | 11:13 | 5 | acto 4 | acamara | — | — | cut | PROMISE 4 | «Quédate con esta imagen porque es la última» |
| 81 | 11:18 | 13 | acto 4 | ia | E001_ai04_closing-path | Ilustración — Conquest | push | PROMISE 4 | «sentado a dibujar junto a su hija» |
| 82 | 11:31 | 7 | acto 5 | gráfico | G7_death_card | 88 o 90, según el cómputo japonés | push | — | «Hokusai muere en Edo en 1849, con unos 88 años» |
| 83 | 11:38 | 8 | acto 5 | acamara | — | — | cut | PAY 1 | «se había cambiado el nombre unas 30 veces buscando el que correspondiera a lo que se había hecho en cada etapa» |
| 84 | 11:56 | 6 | acto 5 | archivo | swap_84_c2e5dd83 | Ilustración — Conquest | push | PAY 4 | «cuando él mismo se había puesto de plazo hasta los 110 y murió sin encontrarlo, pidiendo 5 o 10 años más para por fin hacerlo bien» |
| 85 | 12:02 | 9 | acto 5 | acamara | — | — | cut | — | «y entonces, medio siglo después de su muerte, pasa lo que él quería y no llegó a ver: sus estampas empiezan a llegar a Europa» |
| 86 | 12:11 | 7 | acto 5 | archivo | japonisme_packing_paper | — | pan-h | — | «se cuenta que algunos viajaron como papel de embalar, protegiendo cerámica japonesa» |
| 87 | 12:15 | 4 | acto 5 | archivo | vangogh_japonaiserie | — | pan-h | — | «como llegaran, tallaron sobre una generación de artistas que buscaba otra forma de mirar. Monet colgó» |
| 88 | 12:23 | 8 | acto 5 | archivo | lamer_cover | — | push | — | «en 1905 Claude Debussy publicó» |
| 89 | 12:31 | 5 | acto 5 | acamara | — | — | cut | PAY 2 | «casi todo pasó cuando él ya no estaba acabó siendo visto por más gente» |
| 90 | 12:48 | 10 | cierre | acamara | — | — | cut | — | «un hombre que trabaja toda su vida, lo perdió casi todo tres veces y se murió sin sentirse a la altura dicho a los 88 suena a fracaso» |
| 91 | 13:06 | 10 | cierre | acamara | — | — | cut | — | «yo creo que es casi lo contrario y tiene que ver con cómo Hokusai medía su trabajo» |
| 92 | 13:16 | 8 | cierre | archivo | swap_92_1a8716a5 | — | push | — | «en la vida hay dos maneras de medir cualquier cosa en la que trabajes» |
| 93 | 13:24 | 12 | cierre | acamara | — | — | cut | — | «la primera pregunta tiene solo dos respuestas y las dos terminan mal una es preguntarte, ya llegué; la otra, ¿me estoy acercando?» |
| 94 | 13:43 | 12 | cierre | acamara | — | — | cut | — | «o has llegado y se acabó el camino y toca averiguar qué haces con los años que te quedan» |
| 95 | 13:55 | 15 | cierre | gráfico | G6_mastery_curve | — | push | — | «la segunda pregunta no se agota nunca; perseguir y demostrar lo que ya vales, o perseguir y aprender sin un punto final» |
| 96 | 14:10 | 14 | cierre | acamara | — | — | cut | — | «puso la meta a los 110, que sabía que no iba a alcanzarla y si nos guiamos por lo que Hokusai dejó escrito, la nota de 1834, los 30 nombres, la firma del viejo loco» |
| 97 | 14:32 | 13 | cierre | ia | E001_ai04_closing-path | Ilustración — Conquest | push | — | «y eso, en vez de hundirlo, fue lo que lo mantuvo delante del papel a los 88, después de los incendios, las deudas, las constantes mudanzas» |
| 98 | 14:45 | 13 | cierre | acamara | — | — | cut | — | «hay un dicho: consigue trabajar de lo que te gusta y no tendrás que trabajar un solo día de tu vida» |
| 99 | 15:06 | 13 | cierre | acamara | — | — | cut | — | «la pregunta no es ya llegué, sino ¿esto que estoy haciendo me va a llevar a mi meta?» |
| 100 | 15:19 | 7 | cierre | archivo | beat25_commons_2646210 | — | zoom | — | «¿en qué punto de ese futuro se encuentra tu granola?» |
| 101 | 15:26 | 9 | cierre | acamara | — | — | cut | — | «pero a los 88 todavía tenía donde ir; visto el recorrido de su obra, eso no es una vida frustrada Hokusai nunca llegó a donde quería, al menos en vida» |
| 102 | 15:42 | 8 | cta | acamara | — | — | cut | — | «Hokusai se dio 10 años; tú, ¿cuánto te darías?» |
| 103 | 15:50 | 12 | cta | acamara | — | Fuentes principales | cut | — | «si te ha gustado este vídeo, suscríbete al canal» |

## Detalle por beat — derechos (para el humano — no se parsea)

| asset | Visual | Origen | Fuente [ID] | Derechos |
|-------|--------|--------|-------------|----------|
| E001_ai02_daruma-nagoya-1817 · E001_ai03_studio-fire-night · E001_ai04_closing-path | ilustración IA (`assets/ai/`) | `07b-ai-prompts.md` | — | **IA — rótulo permanente «Ilustración — Conquest»** (`brain/15`). Sin cara fotorrealista. *(ai01 deathbed-room retirado: el beat 1 usa vídeo stock)* |
| beat1_custom_1 | ilustración IA — anciano en el futón mirando el amanecer por la shoji (cuarto de alquiler de Edo) | generada / propia | **IA — rótulo «Ilustración — Conquest»** (`brain/15`). Sin cara. Cambiada en la sala 2026-09-09 (antes: vídeo stock Pexels 31385442) |
| beat3_commons_5576388 · beat25_commons_2646210 | «La gran ola frente a Kanagawa» (detalle / completa) | Wikimedia Commons | S09 | **CC0 / dominio público** |
| beat24_commons_39740407 | «Fuji rojo» (*Gaifū kaisei*) | Wikimedia Commons / Google Art Project | S09 | CC0 / dominio público |
| beat22_custom_22 · beat23_custom_23 | láminas de las *36 vistas* (hoja general · Fuji desde arrozal) | The Met Open Access | S09 | CC0 / dominio público |
| beat16_custom_16 | páginas de los *Hokusai Manga* | archivo propio (escaneo PD) | S10 | dominio público (pre-1900) |
| beat32_custom_32 · beat32_met_78803 | colofón / lámina de *Cien vistas del monte Fuji* (1834) | The Met / escaneo 1834 | S01 | texto primario, dominio público (1834) |
| beat4_commons_124369341 · beat20_met_57261 · beat34_custom_34 | retrato de Hokusai anciano · retrato ~60 · firma «Manji» | Commons / The Met | S16, S13 | dominio público — **confirmar ficha del objeto** |
| beat10_commons_77578681 · beat11_met_37189 · beat11_custom_11 · beat12_met_53446 · beat14_commons_1499270 · beat14_commons_26134200 | grabados de la escuela Katsukawa / actores / *urushi-e* | The Met / Cleveland / Commons | S03 | CC0 / dominio público |
| beat7_commons_127164101 · beat7_met_37248 · beat8_commons_77570475 | mapa de Edo · panorama de época (biombo Kanō) | Commons / The Met | S02, S20 | dominio público |
| beat37_custom_37 | escena nocturna de Katsushika Ōi | reproducción PD | S11 | dominio público — **confirmar** (la de Ōta Memorial NO es open access) |
| lamer_cover | portada de *La Mer* (Durand, 1905) | partitura PD | S19, S14 | dominio público (1905) |
| beat13_custom_13 · beat14_custom_14 · beat31_custom_31 · beat41_custom_41 | ilustraciones cambiadas en la sala (2026-09-09) — si son IA, rótulo «Ilustración — Conquest» | propias / IA | — | pendiente confirmar |
| beat18_custom_18 | miniatura sobre grano de arroz | archivo propio (relato tradicional) | S17 | ilustrativo — rótulo «cuentan» |
| beat2 · intro02 · intro03 · intro04 | b-roll del cold open (habitación / invierno / cerezos / time-lapse) | stock (Pixabay/Pexels vídeo) | — | licencia stock — crédito en `09-description.md` |
| G1…G9 · G_36to46 · negro / cards | gráfico propio | Conquest | ver tabla de gráficos | propio |
| woodblock_carving · chinese_tradition_painting(**no usado en v3**) · name_seal_transfer · manga_detail · fuji_barrel_met36500 · edo_fire_print · japonisme_packing_paper · vangogh_japonaiserie | archivo aún por descargar | ver «Faltantes» | S03, S05, S07, S09, S10, S18, S19 | **pendiente** |

## Gráficos / motion — guion de cada uno

**Cada `gráfico` con contenido que hay que leer = UN beat sostenido de 10–18 s
con movimiento interno (build o push lento), b-roll de apoyo antes/después, nunca
intercalado (`brain/11 §2.1.4`).** Ningún `id` se repite salvo callback marcado
(`PROMISE`/`PAY`/`eco`). `make_graphics.py` rinde un PNG por `id`; el build
animado llega después (memoria `graphics-entrance-animation-plan`).

| id | Beat | Qué muestra | Datos (fuente [ID]) | Rótulo / salvedad | Notas de estilo |
|----|------|-------------|---------------------|-------------------|-----------------|
| G8_edo_population | 15 (12 s) | tarjeta de cifra: Edo ~1 millón de habitantes hacia 1780–1800 | S20 | «~1 millón — las fuentes varían» | tarjeta de número; el número cuenta al entrar; S20 aún sin fuente cerrada |
| G1_ukiyoe_pipeline | 18 (13 s) | cadena del grabado: dibujante → tallador → impresor + editor; la firma «viaja» al plano final. **Un solo beat sostenido**, el diagrama se construye en fases dentro del beat | S02 | — (proceso) | isométrico simple; b16 (lámina barata) y b17 (talla real) preparan, b19 a cámara cierra |
| G2_names_timeline | 24 PROMISE 1 · 91 PAY 1 | línea de tiempo de los ~30 nombres, una obra bajo cada uno. Rima visual **PROMISE 1 (b24) → PAY 1 (b84)** — misma animación las dos veces. El cierre recuerda «los 30 nombres» sólo con la voz, sin re-mostrar el gráfico | S05 | «~30 nombres — recuento aproximado» | horizontal, scroll lento; único `id` que aparece 2×, y sólo por la rima |
| G9_moves_map | 39 (10 s) | mapa esquemático de Edo con las ~93 mudanzas como puntos + hilo serpenteante | S06 | «~93 mudanzas — origen incierto» | (era el «G3» de `07-assets.md`) |
| G_36to46 | 56 (7 s) | contador «36 → 46» + rejilla de 46 láminas (36 + 10 tenues) | S09 | — | tipográfico |
| G3_prussian_blue | 63 (8 s) | la muestra de azul de Prusia se llena; más intenso que los azules vegetales | S18 | — | muestra de color; sin fechas duras si S18 no las cierra |
| G3_blue_route | 65 (10 s) | ruta Europa → Nagasaki → Edo; el pigmento viaja y el precio cae. 2ª mitad del EXPLICADOR 2, beat propio sostenido | S18 | — | mapa de ruta; b61 (Fuji rojo) prepara, b62 (la ola) cierra |
| G3b_signature_manji | 78 (12 s) | la firma «Gakyō Rōjin Manji» aparece en kanji → romaji → glosa «el viejo loco por la pintura». **Un beat**, se construye dentro | S13 | «traducción propia» | caligrafía → gloss; b73 (firma real en una lámina) cierra |
| G4_age_ladder | 75 (16 s) | escala del prefacio: 73 → 80 → 90 → 100 → **110** destacado, los peldaños suben con la VO. **Un beat sostenido** | S01 | «traducción propia» | escalera ascendente; b70 (detalle animales/plantas) cierra |
| G6_mastery_curve | 105 (15 s) | metas de demostrar (ego, con techo) vs. aprender (maestría, abierta); las dos curvas se dibujan en el mismo beat, sobre la explicación de Dweck. **Sin source card** | S15 (Nicholls 1984 / Dweck 2006) | — (cita en la descripción, `brain/03`) | dos curvas; va justo donde la voz resume «perseguir y demostrar vs. perseguir y aprender» |
| G7_death_card | 89 (7 s) | «Edo, 1849 · ~88 años» | S12 | «88 o 90, según el cómputo japonés» | tarjeta de texto sobre negro; push lento (nunca `cut`) |

## Música / sonido

| Cue | Sección | Pista (librería + licencia) | Notas |
|-----|---------|-----------------------------|-------|
| M1 | Cold open (1–9) | (por elegir — YouTube Audio Library / Pixabay Music) | sin letras; tensión contenida, corta en el negro del bumper |
| M2 | Narrativa (12–98) | (por elegir) | lecho bajo la voz, muy bajo; sube levemente en «La gran ola» (60–62) |
| M3 | Cierre (99–114) | (por elegir) | entra en el «para llevar» (110); nada en la coda CTA |

## Faltantes / a conseguir

**Assets nuevos usados en la espina v3 que NO existen todavía en `assets/`:**

- [ ] **`intro02`** — clip de intro, santuario nevado en invierno. Descargar **Pexels 36365140** → `assets/intro/intro02_*.mp4` (`07-picks.txt` `custom:2`; escribir fila `intro` en `07-pull.tsv` y re-correr `pull_assets.py --download`; `assemble.py` casa por prefijo).
- [ ] **`intro03`** — flores de cerezo, Japón histórico. Descargar **Pexels 31387395** → `assets/intro/intro03_*.mp4` (`custom:3`).
- [ ] **`intro04`** — Japón time-lapse. Descargar **Pexels 31453316** → `assets/intro/intro04_*.mp4` (`custom:4`).
  *(Descartar de los 5 picks: Pexels 19757067 «escaleras» y 20293162 «embarcadero» — encajan flojo con las imágenes que nombra la voz. El huérfano `intro01_pexelsv_8808479.mp4` NO se usa en v3; el beat 4 usa `beat2_pixabayv_10378.mp4`.)*
- [ ] **`woodblock_carving`** — plano de talla de una plancha de madera (cuchilla sobre boj). Stock, o Commons *Woodblock printing in Japan*. Beat 17 (EXPLICADOR 1). *(descargado como vídeo `beat17_*` si `07-picks.txt` lo trae)*
- [x] **`name_seal_transfer`** — el beat 32 usa ahora `beat14_commons_10969306` (*Brocade with Sack and Seal*, Brooklyn, PD) — motivo de sello. Si aparece un grabado temprano con firma «Shunrō» legible (The Met «Shunro»), mejora el plano.
- [ ] **`manga_detail`** — segunda página / recorte de detalle de los *Hokusai Manga* (una figura, no la hoja entera), distinta de `beat16_custom_16`. The Met Open Access («Hokusai Manga»). Beat 45.
- [x] **`fuji_barrel_met36500`** — «El Fuji en el barril del tonelero» (*Fujimigahara in Owari Province*). Descargado: Commons `MET DP141033` (The Met obj. 56214, CC0) → `assets/archive/beat58_custom_58.jpg` *(re-descargar con el nuevo nº de beat)*. Beat 56.
- [ ] **`G3_blue_route`** — gráfico propio: ruta Europa → Nagasaki → Edo del azul de Prusia + caída de precio (2ª mitad del EXPLICADOR 2). Beat 61. **Renderer hecho** (`make_graphics.py`), pendiente pulir.
- [ ] **`G_36to46`** — gráfico contador «36 → 46» + rejilla. Beat 54. **Renderer hecho.**
- [ ] **`G8_edo_population`** — tarjeta de cifra «Edo ~1 millón». Beat 15. **Renderer hecho.** Requiere cerrar **S20** (fuente de población de Edo ~1780–1800).
- [ ] **`G9_moves_map`** — mapa de Edo con las ~93 mudanzas. Beat 39. **Renderer hecho.**
- [ ] **`edo_fire_print`** — incendio urbano en Edo / bomberos (*hikeshi*). LOC *Japanese fine prints pre-1915* (`?q=fire`, TIFF) o The Met. Beat 75.
- [ ] **`japonisme_packing_paper`** — estampas usadas como papel de embalar / cajas de cerámica japonesa (puede ser gráfico propio o foto stock ilustrativa; relato «se cuenta»). Beat 86.
- [x] **`vangogh_japonaiserie`** — Van Gogh, *Brug in de regen (naar Hiroshige)*, 1887 (Van Gogh Museum, PD, Google Art Project) → `assets/archive/beat95_custom_95.jpg` *(re-descargar con el nuevo nº de beat)*. Beat 87. Ref S19. *(Monet/Giverny: sin fuente PD → se cubre con este plano + la portada de La Mer; no recibe beat propio.)*
- [ ] **`chinese_tradition_painting`** — *(retirado de la espina en v3 para no inflar el acto 1; recuperar si se consigue una pintura de tradición china de referencia, The Met / Commons).*

**Confirmaciones de ficha (heredadas de v2):**

- [ ] Retrato de Hokusai anciano (S16) → confirmar objeto de `beat4_commons_124369341` / `beat20_met_57261`.
- [ ] Escena nocturna de Ōi (S11) → confirmar que `beat37_custom_37` es open access / PD.
- [ ] «La gran ola» — cerrar nº de objeto de la impresión elegida (`03-source-log.csv` S09, 2ª ficha).
- [ ] S19 — verificar Monet coleccionaba Hokusai en concreto; Van Gogh copió composiciones japonesas (genérico, OK).
- [ ] S20 — fuente concreta de población de Edo para `G8_edo_population`.

## Gate Stage 6

- [x] La tabla **Timeline — la espina** está completa: toda fila con `#`, `in`, `dur`, `sección`, `tipo`, `asset`, `motion`, `marcador`, `frag`
- [x] Se planifica por **duración de plano** (`brain/11 §2.2`): ~114 filas → ~94 beats tras `align`/`_repace`, 942 s ÷ ~10 s; ningún beat B-roll > 20 s ni > 2,5× el objetivo de su sección
- [x] Reparto A-roll / B-roll (`§1b`): ~30 beats `acamara` ≈ **37 %** (horquilla 30–40 %); ninguna sección sin beat A-roll
- [x] Cold open con la forma de `brain/02 §0`: héroe contextual (beat 1, vídeo, ~6 s) + 5 planos de hook 4–6 s + giro (beat 7) + a cámara (beat 9) → negro con rótulo (beat 8) → bumper (beat 10); hook+bumper ≤ 55 s
- [x] `[EXPLICADOR]` (`brain/11 §2.1.4`): gráfico denso = **1 beat sostenido** 10–18 s con build interno + b-roll antes/después, nunca intercalado (EXPL 1 · G1 b18 · EXPL 2 · G3_prussian b60 + G3_blue_route b61 · EXPL 3 · G3b b72)
- [x] Ningún `id` de gráfico dos veces salvo callback marcado: **sólo G2** (PROMISE 1 b24 → PAY 1 b84)
- [x] `PROMISE n` / `PAY n` con el mismo `asset` y `motion` (1 · G2/pan-h · 2 · ai02/push · 3 · beat20_met_57261/push · 4 · ai04/push); corte a cámara de preparación antes de cada uno
- [x] Nunca el mismo `asset` en dos beats consecutivos salvo las parejas PROMISE→PAY (verificado en la generación)
- [x] `frag` = corte **verbatim** de la VO entregada (`assets/E001-vo.words.json`), no del borrador del guion, para que `align()` de `assemble.py` case
- [x] Reenactments / IA con `rótulo` en pantalla («Ilustración — Conquest», 3 planos: ai02·ai03·ai04)
- [x] Toda cifra dudosa → gráfico propio con rótulo de salvedad (G8 ~1 millón, G2 ~30 nombres, G9 ~93 mudanzas, G7 88/90)
- [x] Ningún `gráfico` < 6 s: los densos son beats sostenidos 10–18 s (`assemble.py` marca ⚠ si `align` comprime uno)
- [~] Todo visual con estado de derechos — la mayoría PD/CC0; 12 assets nuevos pendientes en «Faltantes» + confirmaciones S11/S16/S19/S20
- [x] Sin clip de película dramatizada como registro histórico
