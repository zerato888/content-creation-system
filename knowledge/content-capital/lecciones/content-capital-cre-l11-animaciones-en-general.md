---
title: "Content Capital · Programa · Creación de Contenido L11 — Animaciones en General"
type: source
source_type: course-lesson
course: content-capital
module: "Programa · Creación de Contenido"
instructor: "Bernabé Verón"
lesson: 11
duration: "25:13"
date_ingested: 2026-09-26
transcript_path: ~/Documents/Deliverables/General/docs/Content-Capital/transcripts/programa/cc-creacion-de-contenido/11-animaciones-en-general.md
tags: [content-capital, cc-cre, produccion, edicion, premiere, retention]
status: active
---

## En una línea

Una animación es guardar un valor en un momento, otro valor en otro momento, y dejar que Premiere complete lo del medio. Con eso arma todo: **texto que aparece palabra por palabra con el efecto Transformar (5 fotogramas, suavizado, curva tirada a la izquierda, desenfoque de movimiento) guardado como preset**, emojis de Apple que entran con un rebote de escala, B-roll oscuro y desaturado, **zooms con capa de ajuste** y transiciones con sonido de Premiere Composer.

Instructor: **Bernabé Verón** (ver [[content-capital-cre-l08-introduccion]]). Tutorial de pantalla sin capturas.

## Recorrido de la clase

| Min | Idea |
|---|---|
| 00:00 | Animación = conjunto de fotogramas que muestran movimiento. Empieza por texto. |
| 00:29 | Las 3 pistas por defecto quedan cortas: clic derecho → **Agregar pistas** (3 de video y 3 de audio). Comprimirlas al máximo. |
| 00:57 | Toma una frase de los subtítulos y la separa en bloques: "Disculpa" sola, y "me encanta tu auto" agrupada. |
| 01:21 | Pasar el texto de subtítulo a texto normal: Propiedades de texto → de **párrafo a punto**. Queda como un gráfico libre, "como un título". Alineado arriba y a la izquierda, después centrado en pantalla. |
| 02:16 | **Tamaño o fuente por palabra**: si seleccionás una palabra, el cambio se aplica solo a ella. Ejemplo: una palabra en **Times New Roman Italic**, más grande. |
| 02:45 | Comprimir el interletrado y el interlineado para encajar el bloque, agregar espacios para que parezca alineado a la izquierda sin serlo, y "tu auto" en otro color (naranja). Tipografías y colores: los de tu paleta o marca. |
| 03:26 | Así queda "muy quieto, muy soso, muy estático". Objetivo: que las palabras **aparezcan mientras se dicen**. |
| 03:41 | Cortar el clip de texto donde entra cada palabra, subir los pedazos de pista para diferenciarlos y cambiarles el color de etiqueta (clic derecho → Etiqueta). En cada pedazo se borran las palabras que todavía no se dijeron. |
| 04:30 | **Preset de animación**: un preset es una configuración guardada, como la de Lumetri de L9. Acá se aplica un efecto, se anima y se guarda. |
| 04:58 | La lógica del keyframe: guardar información en un momento y otra en otro; el programa rellena el medio. |
| 05:27 | Efectos → **Transformar**: mueve el objeto desde el efecto, sin mover la capa. |
| 05:52 | Contar **5 fotogramas**: flechas del teclado de a 1, o **Shift + flecha** de a 5. |
| 06:15 | Activar el **relojito** de Posición (en Transformar) en el fotograma final. Volver 5 fotogramas y bajar el texto. Aparecen los dos puntos (keyframes). No hace falta volver a tocar el reloj: basta con cambiar el valor. Premiere completa lo intermedio (100 → 75 → 50 → 25 → 0). |
| 07:20 | Mejorarla: seleccionar los dos keyframes → clic derecho → **Interpolación temporal → Suavizar entrada**, y lo mismo con **Suavizar salida**. |
| 07:48 | Con la flechita se abren las **curvas**. Lineal = velocidad constante, "muy robótico". Suavizado = curva más suave. |
| 08:14 | Alejar más el punto de partida. En Transformar, desactivar "usar el ángulo de obturación de la composición" y subir el **ángulo de obturación** al máximo: aparece un **desenfoque de movimiento** que da coherencia. |
| 08:46 | **Tirar la curva toda a la izquierda**: arranca muy rápido y termina lo más suave posible. "Un toque mucho más fluido". |
| 09:01 | Sumar dos keyframes de **opacidad** (0 → 100) para una aparición más suave todavía. |
| 09:22 | Guardar: clic derecho en Transformar → **Guardar ajuste preestablecido**, con nombre ("preset sub"), descripción opcional y **tipo**. |
| 09:57 | Tipos de preset: **Escala** (la animación se estira a la duración del clip), **Anclar al punto de entrada** (arranca igual al inicio de cada clip) y **Anclar al punto de salida** (se pega al final). Para una entrada: anclar al punto de entrada. |
| 11:14 | Aplicarlo: buscar el preset en Efectos y arrastrarlo sobre cada subtítulo. A él, en los subtítulos, "personalmente no me gusta mucho". Se pueden armar otras (que entren todas desde el costado). |
| 12:05 | Se pueden apilar dos Transformar: uno de entrada y otro que baja la opacidad a 0 al final (aparece y desaparece). Ese preset hay que guardarlo como **Escala**; si no, en un subtítulo largo desaparece a la mitad. No recomienda sumar esa complejidad por ahora. |
| 13:22 | **ERROR típico**: aplicar el preset a un bloque que ya contiene una palabra animada ("me" + "encanta"). La palabra aparece dos veces. Solución: en ese bloque apagar el **relleno** de la palabra repetida, no borrarla (si la borrás, el resto se corre), y reubicar los pedazos. |
| 14:20 | Efecto **Resplandor** (el audio dice "resplandor de br", quizá "Brillo"): umbral de luminancia al mínimo para que tome todos los colores, subir brillo, radio y saturación. No le gusta usar un color de tinte. Se copia a todo el bloque de subtítulo. |
| 15:43 | **Emojis o imágenes PNG**: los emojis, "un clásico siempre que sean estilo Apple". Se sacan de **emojipedia.org** agregando "/apple". Corazón para "me encanta" y otro para la pregunta. |
| 16:26 | Se recortan a lo que dura cada frase, se les pone etiqueta de color y se ubican e inclinan un poco. |
| 17:15 | Animación del emoji con Transformar (también sirve el preset de subtítulos, porque aplica a imágenes). **Escala 0 → ~120 → 100** al entrar la palabra: un rebote. Desenfoque de movimiento con el ángulo de obturación. Se guarda como preset "pop", anclado al punto de entrada. |
| 18:51 | **B-roll**: donde el audio menciona videos, mete un clip viral bajado de TikTok (elegido porque no tenía títulos encima) de una chica que se acerca a preguntar por autos. |
| 19:13 | En Lumetri: **saturación a 0**, bajar exposición y sombras. "Puede parecer feo, muy oscuro", pero es lo más correcto visualmente: el blanco resalta y queda **minimalista y elegante**. |
| 19:40 | También puede ir en color. Si queda muy oscuro tiende a verse saturado: bajar un poco o enfriarlo. |
| 20:01 | **Zoom**: en Proyecto, clic derecho → Nuevo elemento → **Capa de ajuste**. Lo que le apliques afecta a todo lo que está debajo (ejemplo: desenfoque gaussiano sobre video, texto y viñeta). |
| 21:01 | En videos grabados a mano no hacen falta muchos zooms: el dinamismo ya viene del movimiento de cámara. De vez en cuando, sí. |
| 21:16 | Zoom con Transformar sobre la capa de ajuste: keyframes de **Escala y Posición**, 3 fotogramas, escala ~130, cara centrada. |
| 21:50 | Así queda "muy robótico": tirar las curvas a la izquierda. Con la escala, cuidado de no pasarse hacia abajo. |
| 22:25 | Zoom inverso más adelante: copiar los keyframes, llevarlos adelante e invertirlos. |
| 23:13 | **Transiciones**: Ventana → Extensiones → **Premiere Composer** → Starter Pack → Transiciones. Básicas pero funcionan "muy, muy bien". Se pueden adaptar a tu marca. Usa un zoom y otra. Vienen **con efecto de sonido**. |
| 24:17 | Cierre: todo lo que tiene relojito se puede animar. Una vez que lo automatizás, tu contenido tiene "un estilo mucho más que decente". Sigue con las animaciones de fondo blanco. |

## Frameworks que aparecen

- Nuevo propuesto: animación básica con keyframes para reels (Transformar, 3-5 fotogramas, suavizado, curva a la izquierda, desenfoque de movimiento, preset anclado a la entrada).
- Nuevo propuesto: capas visuales de retención en edición: texto por palabra, emojis pop, B-roll oscuro, zooms y transiciones con sonido.
- [[content-capital-cre-l09-primeros-pasos-en-adobe-premiere]] (la lógica de preset de Lumetri se reutiliza para animaciones).

## Ejemplos mostrados en pantalla

- No hay capturas. Por el audio: la frase "Disculpa / me encanta / tu auto" armada como título tipográfico (Times New Roman Italic en una palabra, "tu auto" en naranja), con resplandor; emojis de Apple (corazón y uno de pregunta); un B-roll de TikTok en blanco y negro oscuro; dos zooms sobre la cara y dos transiciones de Premiere Composer.
- Los ajustes exactos de curvas y posiciones dependen de lo que se ve.

## Tareas y herramientas

- Armar y guardar al menos un preset de entrada de texto y uno "pop" para imágenes.
- Emojipedia (versión Apple) para emojis PNG.
- Premiere Composer, Starter Pack de transiciones (ver [[content-capital-cre-l10-premiere-composer-extension]]).

## Citas clave

- "Muy quieto, muy soso, muy estático." (03:34), sobre el texto sin animar.
- "Así de oscuro queda muy muy bien." (19:49), sobre el B-roll.

## Lo que no se procesó

- El nombre exacto del efecto de brillo (14:20) no se entiende por el audio.
- Cómo invierte los keyframes del segundo zoom (22:31) se ve en pantalla, no se narra.
- El B-roll bajado de TikTok es un ejemplo del instructor; el curso no habla de derechos de uso.
