# Shotlist / B-roll — E002 «Toyota / Taiichi Ohno»

> Stage 6. Inferida del guion **v2 bloqueado** (`brain/11-visual-rhythm.md` proceso A). Una fila por beat visual. Ningún visual pasa a edición sin estado de derechos (`03-source-log.csv`).

| Campo | Valor |
|-------|-------|
| ID episodio | E002 |
| Versión de guion | v2 (expansión, fact-check 2026-09-10) |
| Narrador del episodio | Usuario 002 |
| Responsable | Usuario 001 |
| Fecha | 2026-09-11 |

## Modo visual del episodio (`brain/12` / `brain/15` v2)

Sujeto pobre en material real: historia de empresa de mediados del s. XX, casi toda la imagen específica de Toyota está con derechos o no existe. **Registro principal = recreación fotográfica + ilustración**, un solo estilo, rótulo en **cada** aparición (`Recreación` para escenas fotorrealistas, `Ilustración — Conquest` para el retrato recurrente de Ohno y los diagramas ilustrados). Nunca una cara fotorrealista generada de una persona real como si fuera su aspecto real (`brain/15` regla 3): Ohno va como **ilustración estilizada recurrente**; Sakichi / Kiichirō / Eiji, de espaldas, a distancia o en silueta dentro de las recreaciones.

**Archivo real (PD) — solo para el contraste y el entorno:** cadena de Ford/Detroit [S13], interior de un supermercado americano de los 50, colas de gasolina de 1973, planta de Fremont años 80, la rendición de agosto de 1945 (NARA). Toda cifra → gráfico propio con rótulo de fuente. El `07b-ai-prompts.md` lleva un bloque por cada `E002_aiNN`.

## Heurística aplicada (`brain/11 §2.1`)

1 beat / frase o cambio de sujeto (~6–8 s narrativa). Todo `[EN PANTALLA]` = beat. Cold open = héroe 8–10 s + 3–5 clips de hook 4–6 s + «giro» + a cámara → negro (`§2.1` 2b). `[EXPLICADOR]` denso = un beat sostenido 10–18 s con movimiento interno, b-roll antes y después, nunca intercalado. `[PROMISE n]`/`[PAY n]` = **mismo `asset` y `motion`**. Cierre = A-roll + imágenes ya vistas, sin archivo nuevo. Cifra → gráfico + rótulo de fuente. Afirmación aproximada → rótulo de salvedad.

**Reparto A-roll:** ~33 % del metraje (biografía, `§2.6`). Cortes a cámara en cada entrada de sección, en cada `[PROMISE]`/`[PAY]`, en las líneas de opinión, y en todo el cierre + CTA.

## A cámara (A-roll · narrador: Usuario 002)

`asset` = `—`, `motion` = `cut`. `assemble.py` recorta la toma continua de Stage 8 a la ventana del beat, sin Ken Burns. Un piece-to-camera no tiene tope de duración (`brain/11 §1b`).

Beats `acamara` (50 de 133 ≈ 38 %): **9, 10, 11, 16, 27, 36, 39, 42, 46, 49, 51, 53, 55, 58, 59, 62, 63, 67, 69, 72, 73, 80, 83, 86, 88, 90, 93, 94, 96, 99, 101, 103, 105, 107, 109, 111, 113, 115, 117, 118, 119, 121, 123, 125, 127, 129, 130, 131, 132, 133**

| Aspecto | Valor |
|---------|-------|
| Encuadre | Plano medio corto, mirada a cámara |
| Fondo / luz | Set fijo de serie (`brain/03`) |
| Toma | una sola toma continua ya grabada; cualquier ventana sirve |

## Timeline — la espina (una fila por beat, en orden de emisión · `assemble.py` / `edit_timeline.py` la parsean)

| # | in | dur | sección | tipo | asset | rótulo | motion | marcador | guion (frag.) |
|---|----|-----|---------|------|-------|--------|--------|----------|---------------|
| 1 | 0:00 | 10 | cold open | ia | E002_ai01_koromo-crisis | Recreación | push | HOOK | «primavera de 1950… la fábrica al borde del cierre» |
| 2 | 0:10 | 5 | cold open | stock | intro01 | — | cut | — | «llevan dos meses de huelga» |
| 3 | 0:15 | 5 | cold open | stock | intro02 | — | cut | — | «la producción ha caído un setenta por ciento» |
| 4 | 0:20 | 5 | cold open | ia | E002_ai09_kiichiro-leaves | Recreación | static | — | «el fundador, Kiichirō Toyoda, dimite» |
| 5 | 0:25 | 5 | cold open | archivo | beat5_loc_detroit | — | pan-h | — | «Ford fabrica ocho mil coches al día» |
| 6 | 0:30 | 4 | cold open | gráfico | G2_ford_vs_toyota | Ford 8.000/día · Toyota 40/día (1950) | static | — | «Toyota, en cambio, apenas fabrica cuarenta» |
| 7 | 0:34 | 5 | cold open | gráfico | G1_productivity_gap | «nueve veces»: cifra que circulaba en Japón, 1937–38 | static | — | «un obrero americano producía nueve veces más» |
| 8 | 0:39 | 4 | cold open | ia | E002_ai02_ohno-portrait | Ilustración — Conquest | static | HOOK | «lo que ese hombre va a construir…» (giro → negro) |
| 9 | 0:43 | 7 | cold open | acamara | — | — | cut | HOOK | «para ver cómo, hay que volver a esa fábrica sin dinero» |
| 10 | 0:50 | 4 | bumper | acamara | — | Conquest | cut | — | «Hola, mi nombre es… y esto es Conquest» |
| 11 | 0:54 | 7 | pivote | acamara | — | — | cut | — | «esa fábrica sin dinero no salió de la nada» |
| 12 | 1:01 | 7 | pivote | ia | E002_ai03_sakichi-loom | Recreación | pan-h | — | «el hombre que la fundó no fabricaba coches: fabricaba telares» |
| 13 | 1:08 | 7 | contexto | ia | E002_ai03_sakichi-loom | Recreación | push | — | «Sakichi Toyoda, 1867, hijo de un carpintero; treinta años tras un telar que trabajara solo» |
| 14 | 1:15 | 6 | contexto | ia | E002_ai03_sakichi-loom | Recreación | static | — | «en 1924 lo consigue: el telar automático Tipo G» |
| 15 | 1:21 | 9 | contexto | ia | E002_ai04_loom-autostop | Recreación | static | — | «se para solo: en el instante en que un hilo se rompe, la máquina se detiene» |
| 16 | 1:30 | 6 | contexto | acamara | — | — | cut | — | «quédate con ese detalle: una máquina que se apaga cuando algo va mal» |
| 17 | 1:36 | 7 | contexto | gráfico | G6_toyoda_timeline | — | pan-h | — | «1929: Platt Brothers compra los derechos del telar — cien mil libras» |
| 18 | 1:43 | 7 | contexto | ia | E002_ai05_kiichiro-chevy | Recreación | push | — | «Kiichirō monta un pequeño departamento para hacer automóviles» |
| 19 | 1:50 | 5 | contexto | negro | — | la venta y el coche fueron en paralelo — no un cheque que fundó Toyota | cut | — | (salvedad `[NOTA]` L59) |
| 20 | 1:55 | 7 | contexto | ia | E002_ai05_kiichiro-chevy | Recreación | static | — | «compra un Chevrolet, lo desmonta pieza por pieza y copia el motor» |
| 21 | 2:02 | 6 | contexto | ia | E002_ai06_model-aa | Recreación | pan-h | — | «en 1936 sale su primer coche, el Model AA» |
| 22 | 2:08 | 7 | contexto | gráfico | G5b_name_change | Toyoda → Toyota (1937) | static | — | «le cambian una letra al apellido: de Toyoda a Toyota» |
| 23 | 2:15 | 7 | contexto | ia | E002_ai07_war-trucks | Recreación | pan-h | — | «durante toda la guerra Toyota fabrica camiones para el ejército» |
| 24 | 2:22 | 9 | contexto | ia | E002_ai08_koromo-bombed | Recreación | push | — | «14 de agosto de 1945: un bombardeo destruye una cuarta parte de la fábrica de Koromo» |
| 25 | 2:31 | 7 | contexto | archivo | beat25_nara_surrender | «Rendición de Japón — 15 ago 1945» | static | — | «al día siguiente, la radio emite la voz del emperador» |
| 26 | 2:38 | 5 | contexto | ia | E002_ai07_war-trucks | Recreación | static | — | «dos días después, Toyota vuelve a montar camiones» |
| 27 | 2:43 | 8 | contexto | acamara | — | — | cut | — | «el fundador fija el lema: alcanzar a Estados Unidos en tres años» |
| 28 | 2:51 | 6 | contexto | gráfico | G1_productivity_gap | cifra heredada, no medida (Ohno, 1937–38) | static | — | «en los coches, la distancia era todavía mayor» |
| 29 | 2:57 | 7 | contexto | archivo | beat29_dodge_line | «Línea Dodge — Japón, 1949» | static | — | «un plan de choque contra la inflación; el crédito se corta de golpe» |
| 30 | 3:04 | 6 | contexto | ia | E002_ai01_koromo-crisis | Recreación | push | — | «Toyota se queda sin efectivo para pagar las nóminas» |
| 31 | 3:10 | 8 | contexto | gráfico | G8_1950_rescue | — | static | — | «un grupo de bancos rescata a Toyota con una condición dura» |
| 32 | 3:18 | 7 | contexto | ia | E002_ai01_koromo-crisis | Recreación | pan-h | — | «mil seiscientos "retiros voluntarios"… dos meses de huelga» |
| 33 | 3:25 | 7 | contexto | ia | E002_ai09_kiichiro-leaves | Recreación | push | — | «en junio, Kiichirō Toyoda dimite» |
| 34 | 3:32 | 6 | contexto | ia | E002_ai09_kiichiro-leaves | Recreación | static | — | «murió en 1952, sin llegar a ver lo que su fábrica iba a inventar» |
| 35 | 3:38 | 7 | contexto | archivo | beat35_korea_1950 | «Guerra de Corea — junio de 1950» | pan-h | — | «el 25 de junio de 1950 estalla la guerra de Corea» |
| 36 | 3:45 | 8 | contexto | acamara | — | — | cut | — | «los pedidos caen sobre Toyota como lluvia después de una sequía» |
| 37 | 3:53 | 8 | contexto | gráfico | G8_1950_rescue | bancos + despidos + Corea | push | — | «lo que salva a Toyota no es su fábrica ni ningún método» |
| 38 | 4:01 | 6 | contexto | ia | E002_ai07_war-trucks | Recreación | static | — | «los pedidos de Corea son pan para hoy» |
| 39 | 4:07 | 8 | contexto | acamara | — | — | cut | — | «lo que le dan a Ohno son unos años de respiro para rehacer la fábrica» |
| 40 | 4:15 | 7 | contexto | ia | E002_ai02_ohno-portrait | Ilustración — Conquest | static | — | «en uno de esos talleres está Taiichi Ohno» |
| 41 | 4:22 | 7 | contexto | gráfico | G6_toyoda_timeline | — | pan-h | — | «a la fábrica de coches en 1943; taller de motores en 1949» |
| 42 | 4:29 | 6 | explicador | acamara | — | — | cut | EXPLICADOR 1 | «hay que saber cómo fabricaba coches Estados Unidos» |
| 43 | 4:35 | 7 | explicador | archivo | beat43_loc_detroit | — | pan-h | — | «el sistema de Henry Ford: muy pocos modelos, en cantidades enormes» |
| 44 | 4:42 | 15 | explicador | gráfico | G5_ford_massproduction | — | push | EXPLICADOR 1 | «máquinas gigantes… estampar quinientas mil puertas de una tirada y guardarlas» |
| 45 | 4:57 | 6 | explicador | archivo | beat45_loc_detroit_stock | — | pan-h | — | «almacenes gigantes llenos de piezas esperando» |
| 46 | 5:03 | 8 | explicador | acamara | — | — | cut | — | «Ford las tenía. Toyota, en 1950, no tenía ninguna de las tres» |
| 47 | 5:11 | 7 | pivote | archivo | beat47_rouge_1950 | «Planta River Rouge, Ford — 1950» | pan-h | — | «Eiji Toyoda pasa mes y medio dentro de las fábricas de Ford» |
| 48 | 5:18 | 6 | pivote | gráfico | G2_ford_vs_toyota | Ford 8.000/día · Toyota 40/día | static | — | «Ford, ocho mil coches al día; Toyota, cuarenta» |
| 49 | 5:24 | 6 | pivote | acamara | — | — | cut | — | «"un guijarro frente a una roca"» |
| 50 | 5:30 | 6 | pivote | archivo | beat47_rouge_1950 | — | push | — | «vuelve con una conclusión rara» |
| 51 | 5:36 | 11 | pivote | acamara | — | — | cut | PROMISE 2 | «acaba de ver la fábrica más eficiente del planeta, y va a mandar hacer lo contrario» |
| 52 | 5:47 | 6 | pivote | archivo | beat47_rouge_1950 | — | push | PROMISE 2 | «si es lucidez o el error que hunde la empresa, no se sabrá hasta el final» |
| 53 | 5:53 | 9 | acto 1 | acamara | — | — | cut | — | «de vuelta en Koromo, Ohno hace una cuenta» |
| 54 | 6:02 | 9 | acto 1 | gráfico | G3b_japan_output | 30.000 vehículos en todo 1950 = día y medio de EE.UU. [S03] | push | — | «la industria japonesa entera fabricó unos treinta mil vehículos» |
| 55 | 6:11 | 8 | acto 1 | acamara | — | — | cut | — | «Ohno cambia la pregunta: ¿por qué su fábrica es un caos?» |
| 56 | 6:19 | 9 | acto 1 | ia | E002_ai10_shopfloor-chaos | Recreación | pan-h | — | «cada taller empuja… motores parados semanas esperando al resto del coche» |
| 57 | 6:28 | 8 | acto 1 | gráfico | G4b_month_compressed | el montaje real no empieza hasta el día 17–18 | static | — | «el trabajo de un mes, hecho en diez días de agobio» |
| 58 | 6:36 | 9 | acto 1 | acamara | — | — | cut | — | «Ohno lo describía: "un año de un luchador de sumo en diez días de combates"» |
| 59 | 6:45 | 6 | acto 2 | acamara | — | — | cut | — | «la idea no era suya» |
| 60 | 6:51 | 7 | explicador | gráfico | G6_toyoda_timeline | — | static | EXPLICADOR 2 | «Kiichirō llevaba desde 1937 repitiendo: "justo a tiempo"» |
| 61 | 6:58 | 15 | explicador | gráfico | G7_push_vs_pull | — | push | EXPLICADOR 2 | «cada paso empuja… Ohno hace lo contrario: cada paso solo coge del anterior» |
| 62 | 7:13 | 6 | explicador | acamara | — | — | cut | — | «en vez de empujar, se tira» |
| 63 | 7:19 | 8 | acto 2 | acamara | — | — | cut | — | «¿cómo sabe cada taller cuánto reponer? La herramienta de Ohno» |
| 64 | 7:27 | 5 | acto 2 | ia | E002_ai11_kanban-card | Recreación | static | PROMISE 1 | «una tarjeta. Eso es lo que Ohno pone en el centro de todo» |
| 65 | 7:32 | 16 | explicador | gráfico | G9_kanban_loop | — | push | — | «la ficha viaja con la caja, vuelve al taller de atrás como la orden; sin ficha, no se fabrica» |
| 66 | 7:48 | 6 | acto 2 | ia | E002_ai11_kanban-card | Recreación | static | — | «la fábrica se mueve por lo que de verdad se consume, en tiempo real, sin un ordenador» |
| 67 | 7:54 | 7 | acto 2 | acamara | — | — | cut | PAY 1 | «esa era la tarjeta de cartón» |
| 68 | 8:01 | 6 | acto 2 | ia | E002_ai11_kanban-card | Recreación | static | PAY 1 | «una ficha que va y vuelve dentro de una caja» |
| 69 | 8:07 | 8 | acto 2 | acamara | — | — | cut | — | «Ohno añade una segunda regla, y esta sí es nueva» |
| 70 | 8:15 | 8 | acto 2 | ia | E002_ai12_andon-cord | Recreación | static | — | «cualquier obrero puede parar la línea entera si detecta un fallo» |
| 71 | 8:23 | 7 | acto 2 | ia | E002_ai12_andon-cord | Recreación | push | — | «todo se detiene hasta que se entiende qué ha pasado» |
| 72 | 8:30 | 8 | acto 2 | acamara | — | — | cut | — | «Ohno acaba de atar la producción y la calidad a la misma cuerda» |
| 73 | 8:38 | 8 | acto 2 | acamara | — | — | cut | — | «a Ohno le falta la manera de explicarlo; la gente lo mira como si estuviera del revés» |
| 74 | 8:46 | 6 | acto 2 | archivo | beat74_supermarket_1950s | — | pan-h | PROMISE 4 | «una tienda americana que en Japón todavía no existe» |
| 75 | 8:52 | 8 | acto 2 | ia | E002_ai13_supermarket-slides | Recreación | static | — | «un compañero vuelve de EE.UU. con diapositivas a color: el supermercado» |
| 76 | 9:00 | 7 | acto 2 | archivo | beat76_supermarket_1950s | — | pan-h | — | «el cliente coge de la estantería lo que quiere, y se va» |
| 77 | 9:07 | 7 | acto 2 | archivo | beat77_supermarket_shelves | — | push | — | «alguien mira los huecos y repone lo que se ha llevado la gente» |
| 78 | 9:14 | 12 | acto 2 | gráfico | G10_supermarket_analogy | taller = cliente · taller de atrás = reponedor · ficha = etiqueta del estante | push | PAY 4 | «Ohno oye eso y ve su fábrica» |
| 79 | 9:26 | 6 | acto 2 | ia | E002_ai13_supermarket-slides | Recreación | static | — | «dentro de Toyota lo llaman "el sistema del supermercado"» |
| 80 | 9:32 | 8 | acto 2 | acamara | — | — | cut | — | «el supermercado no le dio la idea; le dio una imagen que cualquiera entendía» |
| 81 | 9:40 | 7 | acto 2 | archivo | beat81_supermarket_1950s | — | pan-h | — | «Ohno no pisaría uno hasta 1956, en un viaje a Estados Unidos» |
| 82 | 9:47 | 7 | acto 2 | ia | E002_ai14_ohno-supermarket | Recreación | pan-h | — | «recorrer en persona los pasillos que llevaba cinco años usando como metáfora» |
| 83 | 9:54 | 10 | acto 3 | acamara | — | — | cut | PROMISE 3 | «esto no lo cambió una reunión: alguien tuvo que meterse en esa fábrica y no salir en veinte años» |
| 84 | 10:04 | 8 | acto 3 | ia | E002_ai10_shopfloor-chaos | Recreación | push | — | «la resistencia más dura venía de los mandos intermedios» |
| 85 | 10:12 | 9 | acto 3 | gráfico | G6b_pull_spread | 1948 → mediados de los 60, taller a taller | pan-h | — | «un almacén lleno de piezas es una manta de seguridad» |
| 86 | 10:21 | 8 | acto 3 | acamara | — | — | cut | — | «en una fábrica que acababa de echar a mil seiscientos, "menos manos" sonaba a amenaza» |
| 87 | 10:29 | 8 | acto 3 | ia | E002_ai16_supplier-daily | Recreación | pan-h | — | «los proveedores tardaron hasta 1955 en aceptar entregar un poco cada día» |
| 88 | 10:37 | 7 | acto 3 | acamara | — | — | cut | — | «una tarjeta kanban no vale nada si el proveedor no puede seguir el ritmo» |
| 89 | 10:44 | 8 | acto 3 | gráfico | G6c_1977_signatures | 1977: Ohno + otros cuatro ingenieros | static | — | «cuando se pusieron por escrito los planos, la firma era de Ohno y otros cuatro» |
| 90 | 10:52 | 8 | acto 3 | acamara | — | — | cut | — | «por el camino se ganó fama de ogro; su forma de enseñar era no enseñar» |
| 91 | 11:00 | 10 | acto 3 | ia | E002_ai15_chalk-circle | Recreación | static | — | «Ohno dibujó un círculo en el suelo: "ponte ahí y mira el proceso"» |
| 92 | 11:10 | 8 | acto 3 | ia | E002_ai15_chalk-circle | Recreación | push | — | «Minoura estuvo de pie dentro de ese círculo ocho horas» |
| 93 | 11:18 | 8 | acto 3 | acamara | — | — | cut | — | «no los datos de un informe, sino los hechos, vistos con tus propios ojos» |
| 94 | 11:26 | 12 | acto 3 | acamara | — | — | cut | — | `[CTA comentar]` «si una limitación te obligó a una forma mejor, cuéntamela en los comentarios» |
| 95 | 11:38 | 8 | acto 3 | gráfico | G6_toyoda_timeline | — | pan-h | — | «para los años sesenta el sistema cubre ya casi toda la empresa» |
| 96 | 11:46 | 8 | acto 3 | acamara | — | — | cut | — | «y entonces, en octubre de 1973, pasa algo que nadie tenía previsto» |
| 97 | 11:54 | 8 | acto 3 | archivo | beat97_gasline_1973 | «Crisis del petróleo — 1973» | pan-h | — | «los países árabes cortan el petróleo, el precio se multiplica» |
| 98 | 12:02 | 7 | acto 3 | archivo | beat98_gasline_1973 | — | static | — | «Japón, que importa casi todo su crudo, es de los más golpeados» |
| 99 | 12:09 | 9 | acto 3 | acamara | — | — | cut | — | «Toyota cae menos y se recupera antes: coches pequeños, sin almacenes llenos» |
| 100 | 12:18 | 10 | acto 3 | gráfico | G7_toyota_gm_scale | — | push | PAY 2 | «la fábrica que no podía permitirse el método de Detroit era la que mejor aguantaba» |
| 101 | 12:28 | 9 | acto 3 | acamara | — | — | cut | PAY 2 | «en 1973, por primera vez, la industria entera pudo ver por qué» |
| 102 | 12:37 | 8 | acto 3 | ia | E002_ai17_toyota-seminars | Recreación | pan-h | — | «el gobierno japonés monta seminarios para estudiar qué hace Toyota» |
| 103 | 12:45 | 8 | acto 3 | acamara | — | — | cut | — | «según Jeffrey Liker, entienden solo una parte de lo que lo hacía funcionar» |
| 104 | 12:53 | 6 | acto 3 | ia | E002_ai18_ohno-book | Recreación | static | — | «en 1978, Ohno publica un libro contándolo él mismo» |
| 105 | 12:59 | 9 | acto 3 | acamara | — | — | cut | — | «y el método sale de Japón» |
| 106 | 13:08 | 8 | acto 3 | archivo | beat106_japanese_cars_us | — | pan-h | — | «los coches pequeños japoneses llevaban años intentando entrar en EE.UU.» |
| 107 | 13:16 | 8 | acto 3 | acamara | — | — | cut | — | «con la crisis del petróleo, pasaron a ser una amenaza para Detroit» |
| 108 | 13:24 | 10 | acto 3 | archivo | beat108_fremont_1980s | «Planta de Fremont, GM — 1984» | pan-h | — | «en 1984, GM y Toyota reabren juntas una fábrica que GM había cerrado en Fremont» |
| 109 | 13:34 | 9 | acto 3 | acamara | — | — | cut | — | «fama de tener la peor plantilla de la industria: absentismo, sabotajes» |
| 110 | 13:43 | 8 | acto 3 | ia | E002_ai19_nummi-line | Recreación | pan-h | — | «Toyota la reabre con casi toda la vieja plantilla y el mismo sindicato» |
| 111 | 13:51 | 10 | acto 3 | acamara | — | — | cut | — | «en dos años, de la peor fábrica de GM a una de las mejores, calidad de Toyota-Japón» |
| 112 | 14:01 | 9 | acto 3 | gráfico | G7b_lean_map | estudio del MIT — 5 años, 14 países (1990) | pan-h | — | «un equipo del MIT le pone nombre en inglés: lean production» |
| 113 | 14:10 | 10 | acto 3 | acamara | — | — | cut | — | «el modelo que casi toda la industria del planeta intenta copiar» |
| 114 | 14:20 | 10 | acto 3 | gráfico | G7_toyota_gm_scale | Toyota ½ de GM en 1990 → mayor fabricante del mundo en 2008 | push | — | «en 2008 fabrica más que GM — fin de 77 años de GM como el nº 1» |
| 115 | 14:30 | 11 | acto 3 | acamara | — | — | cut | — | «dos cosas, para no contar la historia más limpia de lo que fue» |
| 116 | 14:41 | 8 | acto 3 | ia | E002_ai04_loom-autostop | Recreación | static | — | «parar la máquina cuando algo va mal — ¿te acuerdas del telar de Sakichi? — venía de ahí» |
| 117 | 14:49 | 10 | acto 3 | acamara | — | — | cut | — | «Ohno cogió dos ideas de la familia y una imagen de un supermercado; no lo hizo solo» |
| 118 | 14:59 | 12 | cierre | acamara | — | — | cut | — | «es fácil salir de esta historia con la lección equivocada» |
| 119 | 15:11 | 12 | cierre | acamara | — | — | cut | — | «yo no creo que sea el genio ni la disciplina japonesa: era una empresa en quiebra sin salida» |
| 120 | 15:23 | 13 | cierre | gráfico | G11_constraint_mechanism | Acar, Tarakci & van Knippenberg, *J. of Management* (2019) | push | — | «un poco de restricción produce más soluciones nuevas que ninguna» |
| 121 | 15:36 | 13 | cierre | acamara | — | — | cut | — | «demasiada, eso sí, ahoga» |
| 122 | 15:49 | 6 | cierre | ia | E002_ai10_shopfloor-chaos | Recreación | push | — | «no podía escalar como Ford, así que invirtió el flujo» |
| 123 | 15:55 | 10 | cierre | acamara | — | — | cut | — | «hizo del inventario un enemigo; la herramienta fue una tarjeta de cartón» |
| 124 | 16:05 | 5 | cierre | ia | E002_ai11_kanban-card | Recreación | static | — | «una tarjeta de cartón» |
| 125 | 16:10 | 12 | cierre | acamara | — | — | cut | — | «y cuando probaron el método lejos de Japón, con los obreros que GM daba por perdidos, funcionó igual» |
| 126 | 16:22 | 6 | cierre | archivo | beat108_fremont_1980s | — | static | — | (eco NUMMI) |
| 127 | 16:28 | 13 | cierre | acamara | — | — | cut | — | «copiar al que va primero te mantiene, como mucho, en segundo lugar» |
| 128 | 16:41 | 6 | cierre | ia | E002_ai15_chalk-circle | Recreación | static | — | «esa parte —la del círculo de tiza— es la que no se puede copiar» |
| 129 | 16:47 | 14 | cierre | acamara | — | — | cut | — | ‹para llevar› «la próxima vez que te falte el recurso que hace falta…» |
| 130 | 17:01 | 14 | cierre | acamara | — | — | cut | — | «trata esa carencia como el enunciado del problema, no "cómo consigo lo que me falta"» |
| 131 | 17:15 | 12 | cierre | acamara | — | — | cut | — | «cuando hay respuesta, suele ser mejor que la solución cara — y nadie más la tiene» |
| 132 | 17:27 | 10 | cta | acamara | — | — | cut | — | `[CTA compartir]` «si conoces a alguien construyendo algo con menos de lo que debería… mándale este vídeo» |
| 133 | 17:37 | 8 | cta | acamara | — | Conquest · «Fuentes principales» | cut | — | ‹sign-off› «Mi nombre es… y esto fue: cómo Toyota, demasiado pobre para copiar a Detroit, terminó fabricándole los coches al mundo» |

## Detalle por beat (para el humano — no se parsea)

| # | Visual necesario | Origen | Fuente [ID] | Estado de derechos | Notas |
|---|------------------|--------|-------------|--------------------|-------|
| 1, 30, 32 | Fábrica de Koromo 1950 / obreros en huelga | recreación fotográfica | S04 (hecho) | Recreación propia — rótulo | mismo `asset` ai01; encuadre exterior, penumbra, sin rostros legibles |
| 4, 33, 34 | Kiichirō sale de la fábrica / dimite | recreación | S05 | Recreación — rótulo | de espaldas / silueta (persona real, `brain/15` r3) |
| 5, 43, 45 | Cadena de montaje de Ford / Detrot años 40–50 | Library of Congress (FSA/OWI, Detroit Publishing) | S13 | **dominio público** | localizar signatura por imagen |
| 8, 40 | Retrato de Ohno | ilustración estilizada recurrente | S08/S09 (contexto) | Ilustración — Conquest | motivo del bigote; **no** foto real animada |
| 12–14 | Sakichi en el telar Tipo G | recreación | S17 | Recreación — rótulo | taller textil de los años 1920; Sakichi de espaldas |
| 15, 116 | El hilo se rompe → el telar se detiene | recreación / macro | S17, S14 | Recreación — rótulo | plano detalle de la lanzadera parándose; es el *plant* del jidoka |
| 18, 20 | Kiichirō y unos ingenieros desmontando un Chevrolet | recreación | S20 | Recreación — rótulo | garaje / taller años 30 |
| 21 | El Toyoda Model AA (1936) | recreación / ilustración del coche | S20 | Recreación — rótulo | el coche, no personas |
| 23, 26, 38 | Cadena de camiones de guerra de Toyota | recreación | S19, S03 | Recreación — rótulo | nave de fábrica, camiones militares años 40 |
| 24 | La planta de Koromo bombardeada (ago 1945) | recreación | S19 | Recreación — rótulo | una cuarta parte destruida; humo, estructura abierta |
| 25 | La rendición del 15 ago 1945 (radio / multitud) | NARA / archivo aliado | S19 (contexto) | dominio público (obra del gobierno de EE.UU.) | verificar la pieza exacta |
| 29 | Titular de la «línea Dodge» (Japón, 1949) | recreación de titular / prensa japonesa | S03 | Recreación — rótulo (marcar traducción) | gráfico propio de titular si no hay PD |
| 35 | Guerra de Corea, junio de 1950 | archivo militar de EE.UU. | S03 (contexto) | dominio público | camiones del ejército de EE.UU. |
| 47, 50, 52 | Planta River Rouge de Ford, 1950 | archivo (Ford publica imágenes de Rouge; o Detroit PD) | S06 | PD / cita breve 1b-ii | mismo `asset` beat47 (PROMISE 2: idéntico) |
| 56, 84, 122 | Taller de Toyota en caos: motores parados, almacenes desbordados | recreación | S03 | Recreación — rótulo | mismo `asset` ai10 |
| 64, 66, 68, 124 | La tarjeta *kanban* en una caja de piezas | recreación / macro | S14 | Recreación — rótulo | PROMISE 1 (b64) = PAY 1 (b68): `asset` + `motion` idénticos |
| 70, 71 | Un obrero tira del cable que para la línea (*andon*) | recreación | S14 | Recreación — rótulo | mano en el cable; luz que se enciende |
| 74, 76, 77, 81 | Interior de un supermercado americano años 50 | LOC / archivos de revistas | S07 (contexto) | PD parcial / stock ilustrativo | PROMISE 4 (b74): plano de entrada |
| 75, 79 | Un colega enseña diapositivas a color del supermercado | recreación | S14 | Recreación — rótulo | sala de reunión años 50, proyector de diapositivas |
| 82 | Ohno recorre un pasillo de supermercado en EE.UU. (1956) | recreación | S07 | Recreación — rótulo | de espaldas |
| 91, 92, 128 | Minoura de pie en el círculo de tiza | recreación | S12 | Recreación — rótulo | planta de fábrica; el círculo en el suelo |
| 97, 98 | Colas de gasolina, 1973 | archivo de prensa / gobierno de EE.UU. | S03 (contexto) | PD / cita breve | icónico y muy disponible |
| 106 | Coches japoneses en un concesionario / puerto de EE.UU., años 60–70 | archivo de prensa | S02 (contexto) | cita breve 1b | genérico |
| 108, 126 | Planta de Fremont / NUMMI | prensa / AP años 80 | S22 | cita breve 1b (fair use) | exterior; **dignidad** (§ Para Stage 11) |
| 110 | Cadena de montaje de NUMMI en marcha | recreación | S22, S02 | Recreación — rótulo | obreros en una línea ordenada |
| 102, 104 | Seminarios del gobierno / Ohno con su libro | recreación | S12, S14 | Recreación — rótulo | sala de conferencias; el libro |

## Gráficos / motion — guion de cada uno

| id | Beat(s) | Qué muestra | Datos (fuente [ID]) | Rótulo de fuente / salvedad | Notas de estilo |
|----|---------|-------------|---------------------|-----------------------------|-----------------|
| G1_productivity_gap | 7, 28 | Un obrero de EE.UU. ≈ 9 obreros de Japón (y «al menos ×10» en el automóvil) | [S14] | «cifra que a Ohno le *contaron* en 1937–38, no una medición» | pictograma de figuras; **rótulo de salvedad obligatorio** |
| G2_ford_vs_toyota | 6, 48 | 8.000 coches/día (Ford) vs 40 (Toyota), 1950 | [S06] | «producción diaria, 1950» | barras a escala real; la de Toyota casi invisible |
| G3b_japan_output | 54 | 30.000 vehículos = toda la industria japonesa en 1950 ≈ 1,5 días de EE.UU. | [S03] | «Japón, año 1950 completo» | una barra minúscula junto a un bloque «EE.UU., día y medio» |
| G4b_month_compressed | 57 | Calendario del mes: el montaje real solo arranca el día 17–18 | [S03] | — | barra de progreso que salta al final del mes |
| G5_ford_massproduction | 44 | EXPLICADOR 1: máquina dedicada → 500.000 puertas → almacén → cadena | [S12] | etiquetas del diagrama | animación 2D por pasos, ~15 s; el bloque visual más largo del acto |
| G5b_name_change | 22 | Toyoda 豊田 → Toyota トヨタ (1937) | [S20] | «1937» | tarjeta de texto animada; 8 trazos |
| G6_toyoda_timeline | 17, 41, 60, 95 | Línea de tiempo maestra 1867 → 2008 (Sakichi · Platt · dpto. auto · guerra · crisis del 50 · pull desde 1948 · Deming · 1973 · lean 1990 · 2008) | [S17][S18][S20][S03][S02][S23] | fechas | **la espina visual del episodio** — se ilumina el tramo que toca cada vez; reutilización deliberada (`§4b` excepción «eco»), `assemble.py` avisará `dup` |
| G6b_pull_spread | 85 | 1948 → mediados de los 60: el método se extiende taller a taller siguiendo los ascensos de Ohno | [S03] | años | mismo lenguaje que G6, sub-tramo |
| G6c_1977_signatures | 89 | 1977: los planos del método, firmados por Ohno + 4 ingenieros | [S03] | «1977» | 5 firmas apareciendo |
| G7_push_vs_pull | 61 | EXPLICADOR 2: empujar (se amontona) vs. tirar (cada paso coge del anterior) | [S03][S14] | «empujar → tirar» | animación 2D, ~15 s |
| G9_kanban_loop | 65 | El ciclo de la ficha: caja vacía → ficha vuelve → se fabrica esa cantidad → caja llena | [S14] | — | bucle animado, ~16 s |
| G10_supermarket_analogy | 78 | taller de delante = cliente · taller de atrás = reponedor · ficha = etiqueta del estante | [S14][S03] | — | PAY 4; superpone la fábrica sobre unos estantes |
| G7_toyota_gm_scale | 100, 114 | Cuota / producción Toyota vs GM, 1950 → 1990 (½) → 2008 (rebasa) | [S02][S23] | «producción mundial · cifras 1990 y 2008» | dos líneas que se cruzan en 2008; reutilización deliberada (curva completándose) |
| G7b_lean_map | 112 | Estudio del MIT: 5 años, 14 países | [S02] | «*The Machine That Changed the World*, 1990» | mapa con 14 puntos |
| G8_1950_rescue | 31, 37 | Las 3 cosas que salvan a Toyota en 1950: préstamos de la banca + 1.600 despidos + pedidos de la guerra de Corea | [S03] | — | tres bloques; **el método NO está** |
| G11_constraint_mechanism | 120 | U invertida: algo de restricción > ninguna restricción para la innovación; demasiada ahoga | [S16] | «Acar, Tarakci & van Knippenberg, *J. of Management* (2019)» | curva simple; registro del cierre |

**Reutilizaciones deliberadas** (`assemble.py` avisará; son a propósito): `G1` y `G2` (cold open → pago en el pivote, rima); `G6_toyoda_timeline` (la espina, se ilumina un tramo distinto cada vez); `G7_toyota_gm_scale` (la curva se completa en el 2008); `ai01`, `ai04`, `ai10`, `ai11`, `ai15`, `beat47_rouge`, `beat108_fremont` (ecos del cierre y parejas PROMISE→PAY). Ningún `asset` en beats consecutivos.

## Música / sonido

| Cue | Sección | Pista (librería + licencia) | Notas |
|-----|---------|-----------------------------|-------|
| M1 | Cold open | lecho ambiental bajo — CC0/CC-BY (por elegir en el pase de estilo) | sin percusión; entra sobre el plano 1 |
| M2 | Pivote + narrativa | lecho neutro, −20…−24 dB bajo la voz | baja intensidad; sin melodía marcada |
| M3 | Cierre (desde el «para llevar», beat 129) | pieza más cálida / mínima | entra en el para-llevar; `brain/16` §5 |
| — | Bumper (beat 10) | **silencio** | sin música (`brain/16`) |
| — | CTA | cola de M3 o silencio | — |

## Faltantes / a conseguir (para el pase de estilo, Stage 7)

- [ ] Signaturas LOC concretas para la cadena de Ford/Detroit [S13] (beats 5, 43, 45).
- [ ] Pieza PD de la rendición del 15 ago 1945 (NARA) — beat 25.
- [ ] Interior de supermercado americano años 50 en PD, o stock ilustrativo (beats 74, 76, 77, 81).
- [ ] Colas de gasolina 1973 en PD (beats 97, 98).
- [ ] Fremont/NUMMI años 80: prensa (AP/Getty) bajo cita breve 1b — o recreación si el riesgo Content ID no compensa (beats 108, 126).
- [ ] Imágenes que Ford / Toyota publican de la planta Rouge (1b-ii, orden de preferencia 1) — beats 47, 50, 52.
- [ ] `07b-ai-prompts.md`: un bloque por `E002_aiNN` (ai01–ai19), un solo estilo (recreación fotográfica de época, grano, sin rostros legibles de personas reales).
- [ ] Música: correr `find_music.py` y elegir 2–3 lechos en el pase de estilo.

## Gate Stage 6

- [x] La tabla **Timeline — la espina** completa y parseable (`#`, `in`, `dur`, `sección`, `tipo`, `asset`, `motion`, `marcador`, `frag`)
- [x] Todo visual con un origen y un estado de derechos previsto (columna «Detalle por beat») — se cierra contra `03-source-log.csv` en Stage 7
- [x] Toda cifra en gráfico con fuente [ID] y, donde aplica, rótulo de salvedad (G1, G2, G3b)
- [x] `PROMISE n` y `PAY n` con el mismo `asset` y `motion` — 1 (b64→b68), 2 (b51/52→b100/101), 4 (b74→b78 comparten el motivo supermercado); 3 (b83) se paga en el cierre (b128) + el círculo
- [x] Sin clip de película dramatizada como registro histórico; recreaciones e ilustraciones rotuladas en cada aparición (`brain/12`/`15` v2)
- [x] Cold open: 1 héroe + 5 planos de hook + giro + a cámara → negro; hook + bumper ≤ ~50 s (beats 1–10)
- [x] Reparto A-roll ~38 % (50 beats `acamara` de 133); cada sección tiene A-roll
- [ ] `assemble.py --seed` parsea la espina sin error — **verificar en Stage 9**
- [ ] Firma de un usuario para pasar a Stage 7
