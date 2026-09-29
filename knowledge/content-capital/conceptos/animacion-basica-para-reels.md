---
title: "Animación básica para reels: keyframes, presets y escenas póster (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-cre-l10, cc-cre-l11, cc-cre-l12, cc-cre-l08]
source_count: 4
created: 2026-09-26
updated: 2026-09-26
tags: [content-capital, cc-cre, framework, checklist, plantilla, edicion, premiere, animacion, retention, creatividad]
status: developing
---

## En una línea

Toda animación es **un valor en un momento, otro valor en otro, y Premiere completa el medio**. Con el efecto Transformar en 3-5 fotogramas, suavizado, curva tirada a la izquierda y desenfoque de movimiento, guardado como preset, se arman texto por palabra, emojis con rebote, zooms y escenas de fondo blanco que primero se diseñan como póster.

## Qué es y por qué funciona (según el curso)

- Un texto quieto se ve "muy quieto, muy soso, muy estático". El objetivo es que las palabras **aparezcan mientras se dicen** ([[content-capital-cre-l11-animaciones-en-general|CRE L11]] 03:26).
- **Keyframe**: guardás información en un momento y otra en otro; el programa rellena lo intermedio (CRE L11 04:58, 06:15).
- **Transformar** mueve el objeto desde el efecto, sin mover la capa (CRE L11 05:27).
- Lineal = velocidad constante, "muy robótico". Con la curva **toda a la izquierda** arranca rápido y termina suave: da un toque "como premium" (CRE L11 07:48, 08:46; [[content-capital-cre-l12-edicion-practica|CRE L12]] 15:57).
- **Un preset** es una configuración guardada: animás una vez y después arrastrás (CRE L11 04:30).
- "Un video no es más que una imagen en movimiento" (CRE L12 03:43): la forma fácil de animar bien es **armar la imagen primero y animarla después**.
- Todo lo que tiene relojito se puede animar (CRE L11 24:17). Con práctica, cada escena lleva ~30 min (CRE L12 19:46).

## Cuándo usarlo / cuándo no

- **Sí**: frases clave del guion, tramos vacíos, momentos donde la frase pide una imagen.
- **Zooms: pocos** si el video está grabado a mano; el dinamismo ya viene del movimiento de cámara (CRE L11 21:01).
- **Subtítulos animados**: se puede, pero al instructor no le gusta en subtítulos (CRE L11 11:14).
- **Entrada + salida en un mismo preset**: posible, pero no lo recomienda por ahora (CRE L11 12:05).
- **Siempre** con los subtítulos debajo, para poder sacar la animación sin rehacer nada (CRE L12 01:36).
- Base previa: [[edicion-simple-premiere-look-profesional]].

## Pasos

**A. Preset de entrada (texto o imagen)** (CRE L11 05:27–11:14)

1. Efectos → **Transformar** sobre el clip.
2. Contar **5 fotogramas** (flechas de a 1, **Shift + flecha** de a 5).
3. En el fotograma final, activar el relojito de **Posición**; volver 5 fotogramas y desplazar el objeto.
4. Seleccionar los dos keyframes → Interpolación temporal → **Suavizar entrada** y **Suavizar salida**.
5. Abrir la curva y **tirarla toda a la izquierda**.
6. En Transformar, desactivar "usar el ángulo de obturación de la composición" y subir el **ángulo de obturación** al máximo: desenfoque de movimiento.
7. Opcional: opacidad 0 → 100.
8. Clic derecho en Transformar → **Guardar ajuste preestablecido**. Tipo: **Anclar al punto de entrada** para una entrada; **Escala** si el preset tiene entrada y salida.

**B. Texto palabra por palabra** (CRE L11 00:57–04:29)

1. Pasar el texto del subtítulo de **párrafo a punto** (queda como título libre).
2. Tamaño o fuente por palabra seleccionada; colores y tipografías de tu marca.
3. Cortar el clip de texto donde entra cada palabra, subir los pedazos de pista y borrar en cada uno lo que todavía no se dijo.
4. Arrastrar el preset de entrada a cada pedazo.

**C. Emoji o PNG con rebote** (CRE L11 15:43–18:35): emojis estilo Apple de emojipedia.org ("/apple"); Transformar con **escala 0 → ~120 → 100** al entrar la palabra, desenfoque de movimiento; preset "pop" anclado a la entrada.

**D. Zoom** (CRE L11 20:01–22:50): Nuevo elemento → **Capa de ajuste** encima (afecta todo lo de abajo); Transformar con keyframes de escala (~130) y posición en **3 fotogramas**, cara centrada, curvas a la izquierda. Zoom inverso: copiar e invertir los keyframes (cómo lo invierte se ve en pantalla).

**E. Transiciones** (CRE L11 23:13; [[content-capital-cre-l10-premiere-composer-extension|CRE L10]]): Ventana → Extensiones → **Premiere Composer** (Mister Horse) → Starter Pack → Transiciones. Vienen **con sonido**. El curso no dice si el plugin es pago.

**F. Escena de fondo blanco estilo póster** (CRE L12)

1. **Mate de color** casi blanco, nunca blanco puro: #F8F8F8 (código dudoso por audio) o #F7F7FF (00:14–01:19).
2. Lumetri: **viñeta** muy ligera, cantidad ~-2, redondez casi al máximo (02:04).
3. Elegir **un solo estilo de imagen** para toda la animación: papel, logos 3D, dibujado a mano o íconos vectoriales (02:50).
4. Buscar una referencia en **Pinterest** y **armar el póster quieto** primero (03:27–07:37).
5. Sumar **texto chico de relleno** para el equilibrio visual, no para leer (07:54). Él lo toma de Wikipedia o de la web de la marca, en inglés (12:20).
6. **Sombras** que imiten la misma luz de la escena, con tamaño lógico para cada objeto (Sombra paralela; Voltear para cambiar el lado de la luz) (04:58, 11:45).
7. Recién ahí animar: posición y rotación con la misma curva a la izquierda; cortar el texto para que aparezca al decirse (09:04–09:53).

## Plantilla para llenar (ficha de animación)

```
FRASE DEL GUION: ______________________ (min ____)
TIPO: [texto por palabra | emoji pop | zoom | transición | escena póster]
ESTILO DE IMAGEN (uno solo): [papel | 3D | dibujado a mano | vectorial]
REFERENCIA (Pinterest): ______
PRESET: nombre ______ · efecto Transformar · propiedades ______ · fotogramas [3 | 5]
  interpolación: suavizar entrada+salida · curva toda a la izquierda · obturación máx. [sí/no]
  tipo: [anclar entrada | anclar salida | escala]
FONDO (si póster): mate #______ (no #FFFFFF) · viñeta ~-2
RELLENO: texto chico [sí/no] · fuente del texto ______
SOMBRAS: dirección de la luz ______ · tamaño por objeto ______
SUBTÍTULOS DEBAJO: [sí]
SONIDO asociado: ver sound-design (whoosh / pop / el de la transición)
```

## Ejemplos del curso desarmados

| Pieza (min) | Técnica | Detalle que importa |
|---|---|---|
| "Disculpa / me encanta / tu auto" (CRE L11 00:57–03:26) | Texto por palabra | Una palabra en Times New Roman Italic, "tu auto" en naranja, efecto de brillo (nombre dudoso) |
| Corazón y emoji de pregunta (CRE L11 15:43–18:35) | Preset "pop" | Escala 0 → ~120 → 100, inclinados un poco |
| B-roll de una chica que pregunta por autos (CRE L11 18:51–19:54) | B-roll oscuro | Saturación 0, exposición y sombras abajo: el blanco resalta |
| Dos zooms a la cara (CRE L11 21:16) | Capa de ajuste | Escala ~130 en 3 fotogramas |
| Porsche desde arriba + "Si vos querés manejar un auto como este" (CRE L12 04:06–13:49) | Escena póster | Texto detrás, "auto" grande, pasteles, llaves con sombra chica, párrafo en inglés de relleno |
| Logo 3D de Instagram en "lo peor que podés hacer en Instagram" (CRE L12 14:24–19:46) | Corte seco + 3D básico | Sombra de ventana en Multiplicar, emojis con Trazos de pincel |

## Errores comunes

- Dejar la interpolación lineal: "muy robótico" (CRE L11 07:48, 21:50).
- Aplicar el preset a un bloque que ya contiene una palabra animada: aparece dos veces. Apagar el relleno de la palabra, no borrarla (CRE L11 13:22).
- Guardar un preset de entrada + salida anclado a la entrada: en subtítulos largos desaparece a la mitad (CRE L11 12:05).
- Fondo blanco 100%: quema la imagen y lo blanco no resalta (CRE L12 00:28).
- Texto largo para leer dentro del video: no da tiempo (CRE L12 07:54).
- Mezclar estilos de imagen en una misma animación (CRE L12 02:50).
- No poder tocar un texto porque una capa de arriba lo tapa: apretar T o seleccionarlo antes (CRE L12 10:09).
- El curso baja B-roll de TikTok e imágenes de Google/Pinterest sin hablar de derechos de uso (nota de las páginas de lección, no del instructor).

## Checklist para agentes

```
[ ] ¿Cada animación usa Transformar (no la capa) con 3-5 fotogramas?
[ ] ¿Las curvas están suavizadas y tiradas a la izquierda (nada lineal)?
[ ] ¿El tipo de preset coincide con el uso (entrada = anclar entrada; entrada+salida = escala)?
[ ] ¿Las palabras aparecen cuando se dicen, no antes?
[ ] ¿Hay un solo estilo de imagen en toda la animación?
[ ] ¿El fondo es casi blanco (no #FFFFFF) con viñeta ligera?
[ ] ¿Se armó primero el póster quieto y después se animó?
[ ] ¿El texto de relleno es chico y no pretende leerse?
[ ] ¿Las sombras siguen la misma dirección de luz?
[ ] ¿Los subtítulos quedaron debajo, para poder quitar la animación?
[ ] ¿Pocos zooms si el video ya es cámara en mano?
```

## Fuentes

- Base: [[content-capital-cre-l11-animaciones-en-general]] 00:00–24:17 (keyframes, presets, emojis, zooms, transiciones).
- [[content-capital-cre-l12-edicion-practica]] 00:00–19:46 (fondo blanco, póster, estilo único, relleno, sombras).
- [[content-capital-cre-l10-premiere-composer-extension]] 00:00–01:09 (instalar Premiere Composer).
- Relacionadas: [[edicion-simple-premiere-look-profesional]] (flujo base y modos de fusión); [[sound-design-del-reel-musica-whooshes-sfx]] (un whoosh o pop por movimiento); [[broll-con-ia-en-el-reel]] (otra forma de llenar un tramo vacío); [[hook-cuatro-variables]] (el visual que rompe la lógica en el primer frame: la escena póster es una vía, inferencia mía).
- Inferencia mía: la división en seis técnicas (A-F) y la ficha ordenan lo que el curso muestra de corrido.

## Tensiones internas del curso

- **Enseñar vs. recomendar.** Enseña a animar subtítulos y el preset de entrada + salida, pero no recomienda ninguno de los dos por ahora (CRE L11 11:14, 12:05).
- **Una sola curva para todo.** "Siempre" la curva a la izquierda (CRE L12 15:57). No discute cuándo otra curva sirve mejor.
- **Animaciones libres vs. estilo único.** Dice que adentro las animaciones "son libres", pero pide un solo estilo de imagen coherente con la marca (CRE L12 02:50). Se leen como: libertad de técnica, no de lenguaje visual.
- **Rapidez.** El bloque promete no dedicarle horas por día (CRE L8 00:15), pero cada escena lleva ~30 min ya con práctica (CRE L12 19:46).
- Muchos ajustes finos (curvas, posiciones, el zoom inverso) se ven en pantalla y no se narran: no hay valores para copiar.
