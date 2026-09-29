---
title: "Content Capital · Programa · Creación de Contenido L13 — Generación con IA"
type: source
source_type: course-lesson
course: content-capital
module: "Programa · Creación de Contenido"
instructor: "Bernabé Verón (inferido)"
lesson: 13
duration: "20:05"
date_ingested: 2026-09-26
transcript_path: ~/Documents/Deliverables/General/docs/Content-Capital/transcripts/programa/cc-creacion-de-contenido/13-generacion-con-ia.md
tags: [content-capital, cc-cre, ia, edicion, produccion, retention]
status: active
---

## En una línea

Para meter un plano generado con IA en el reel: **Freepik** como suite (un solo pago, muchos modelos de video) → elegir modelo según lo que se necesita → sacar un **fotograma del propio video** como imagen de partida → prompt que describe **primero la cámara y después la acción** → todo al mínimo (720p, 5 s) mientras se itera → acelerar el clip en Premiere para que la acción ya esté pasando cuando llega la frase. Cierra con **modos de fusión** para transiciones de luz y texto.

Instructor: no se presenta. Es la misma serie de edición que abre L8 ("soy editor de Rama", Bernabé Verón) y edita el mismo video del auto que L12 y L14, así que se atribuye a él por inferencia.

## Recorrido de la clase

| Min | Idea |
|---|---|
| 00:00 | Generar video con IA sirve tanto para el hook como para el cuerpo. Depende de lo grabado y de lo que diga el guion. Hay infinitas herramientas; muestra la más simple. |
| 00:39 | **Freepik** (se oye "FreePick"): hay que pagar un plan, sin plan no hay uso. Recomienda **Premium+** ("premio un plus"); el Premium básico alcanza poco; quien meta IA en todos los videos necesita el **Pro**. |
| 01:21 | Por qué gastar en créditos: la IA **depende de iterar**. Al principio no genera lo que querés; cada intento cuesta créditos. |
| 02:01 | Menú **AI Suite** → generador de video. Freepik es un banco de stock que ofrece modelos de otras empresas por API: una suite completa. |
| 03:13 | **Mapa de modelos** según el instructor (grafías dudosas marcadas): **Kling** ("cling") para lo más profesional; **PixVerse** ("PixBers") para lo delirante ("si quieren que un meteorito les caiga"), aunque Kling 2.1 mejoró ahí y permite **multitoma** para escenas movidas; un modelo que se oye "rango" (¿Runway?) no lo recomienda: flojo y con límite corto de caracteres; **Kling 1.6 Standard**, versátil y barato; **MiniMax Director**, deja elegir el control de cámara; **Google Veo 2**, tipo stock profesional pero se rompe con ideas locas; **Veo 3 Fast** zafa; **Veo 3** normal para cosas como el "podcast de mono" de Rama, pero cuesta ~12.000 créditos: "con extrema cautela". |
| 04:25 | Más modelos: uno que se oye "1, 2.2" (probablemente **Wan 2.2**) y **Seedance** ("SIDAN") para tomas muy cinematográficas, igual que **Kling 2.1 Master**; **Hailuo** ("imáxayluo", MiniMax) para movimientos físicos grandes, como una voltereta. |
| 04:57 | Regla: al probar un modelo, **todo al mínimo**. Orden: imagen → prompt con tus palabras → resolución y duración mínimas. |
| 05:33 | **De dónde sale la imagen**: del propio timeline. Busca un tramo "demasiado vacío" y decide que el protagonista baje del auto y explique en una pizarra. |
| 06:00 | Arranca el plano **1-2 s antes de la frase**, porque la IA genera acciones lentas: así, cuando llega la frase, la acción ya está pasando. |
| 06:23 | Apaga con el ojito la capa de texto y la sombra, queda el frame "pelado" y lo exporta con la **camarita** (exportar fotograma) como PNG. |
| 06:44 | En Freepik: **Start with image**. Se quedó sin créditos y pasa a Kling 2.1, más barato. Al cargar la imagen aparece un prompt de cámara por defecto (un zoom in); lo borra. |
| 07:14 | Formato vertical (se ajusta solo a la imagen). Resolución 720p. **Costos que dice**: 5 s a 720p = 300 créditos; 1080p = 500; 10 s = el doble (~1.000). Deja 5 s y 720p. |
| 08:07 | **Advanced settings**: **seed** (semilla), que hace que genere siempre "por el mismo caminito", con resultados parecidos; es opcional. |
| 09:10 | **Negative prompt**: la IA de video "no entiende el no". Escribir "no generes un payaso" produce un payaso. En el campo negativo se escribe solo el objeto ("payaso"), en positivo. Opcional. |
| 10:16 | **Prompt**: primero el movimiento de cámara (cámara en mano, sujeto centrado, leve *camera shake*, se oye "cangel shake"), después la acción (baja del auto, se para junto a una pizarra verde con letras, explica en la calle; la cámara lo sigue y se abre para mostrar hombre, pizarra y auto). |
| 11:51 | Generar entra en una fila de espera. Cada prompt nuevo, con la calidad más baja: la primera sale con fallas y se corrigen en la segunda. Algunos modelos permiten ~360p o 240p, muy barato, solo para ver qué entiende el prompt. 720p "ni se nota" en Premiere. |
| 13:03 | El video sale bien, lo descarga. **Marcá el frame de origen** en el timeline para no perderlo: el primer frame generado tiene que coincidir con ese momento. |
| 13:34 | En Premiere, siempre **un poco más rápido** que la velocidad normal. Prueba 200%, 180% y se queda en ~160% para que llene justo el tramo. |
| 14:22 | Corta, sube las capas de texto y animación por encima del clip de IA y vuelve a activarlas. |
| 15:01 | **Transición de luz** (*light leak*), bajadas de YouTube, con un clic sonoro incluido. La alinea, la gira para cubrir la pantalla. |
| 15:26 | **Modos de fusión** (en Opacidad): cómo se mezclan los píxeles de la capa con todo lo que tiene debajo. **Multiplicar** (primer grupo): lo blanco desaparece, lo oscuro queda. **Pantalla** (segundo grupo): lo oscuro desaparece, lo claro queda; un violeta oscuro no desaparece del todo. |
| 17:26 | Grupo que actúa sobre claros y oscuros: **Superponer** aclara lo de abajo con el blanco y hace desaparecer el negro; **Luz suave**, más sutil, depende de los colores. **Diferencia**: cada color busca su opuesto en el círculo cromático (blanco→negro, naranja→azul). |
| 18:19 | Deja la transición en Pantalla. **Diferencia sobre texto** es un efecto conocido; con fondos grises casi no se nota. |
| 18:56 | Ve el resultado: "estilo mucho más que decente". Esto es lo más simple que da un look profesional. Más capas suman tiempo; para algo más complejo, contratar editor o dedicarle más horas. |

## Frameworks que aparecen

- Nuevo propuesto: [[broll-con-ia-en-el-reel]] (suite de modelos, frame del timeline como imagen de partida, cámara → acción, todo al mínimo, acelerar y adelantar el clip)
- Nuevo propuesto: [[edicion-simple-premiere-look-profesional]] (modos de fusión, transiciones de luz, "lo más simple que se ve pro")

## Ejemplos mostrados en pantalla

No hay capturas. Por el audio se sabe que muestra la tabla de planes de Freepik, el AI Suite con la lista de modelos de video, el panel de configuración (resolución, duración, advanced settings con seed y negative prompt) y el timeline de Premiere con el video del auto del bloque anterior. Los costos exactos por modelo y la lista completa de modelos dependen de lo que se ve.

## Tareas y herramientas

- Freepik (plan Premium+ o Pro) → AI Suite → generador de video.
- Modelos nombrados: Kling 1.6 Standard / 2.1 / 2.1 Master, PixVerse, MiniMax Director, Hailuo, Google Veo 2 / Veo 3 Fast / Veo 3, Seedance, Wan 2.2 (dudoso), "rango" (dudoso).
- Premiere: exportar fotograma (ícono de cámara), marcador en el frame de origen, velocidad/duración ~160%, modos de fusión en Opacidad.
- Pack de transiciones de luz bajado de YouTube.

## Citas clave

- "La inteligencia artificial no entiende el no." (09:10)
- "Es un juego de iteración esto." (12:52)

## Lo que no se procesó

- Los nombres de varios modelos están deformados por el reconocimiento ("rango", "1, 2.2"); se dejaron como se oyen con la lectura probable.
- El costo del 10 s a 1080p lo dice sin mirar el número ("no estoy con suficiente crédito"); es aproximado.
- Los precios y la lista de modelos son de la fecha de grabación; no se verificaron.
