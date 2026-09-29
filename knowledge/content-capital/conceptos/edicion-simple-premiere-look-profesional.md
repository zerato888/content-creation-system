---
title: "Flujo de edición de un reel en Premiere: lo mínimo con look profesional (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-cre-l08, cc-cre-l09, cc-cre-l12, cc-cre-l13, cc-cre-l15]
source_count: 5
created: 2026-09-26
updated: 2026-09-26
tags: [content-capital, cc-cre, framework, checklist, plantilla, edicion, premiere, produccion, retention]
status: developing
---

## En una línea

Un reel prolijo en Premiere sale de un flujo fijo y de **tres presets guardados una sola vez**: proyecto con fecha → secuencia propia 1080×1920 a 25 fps → cortes rápidos con Q/W → subtítulos con estilo de marca → color básico en Lumetri → degradé oscuro abajo → export en Match Source sin tocar nada más.

## Qué es y por qué funciona (según el curso)

- El bloque enseña **lo mínimo** para una edición básica pero vistosa, prolija y con aspecto profesional. Para un nivel experto, la recomendación es **delegar en un editor** ([[content-capital-cre-l08-introduccion|CRE L8]] 00:38–00:53).
- Al principio es lento; cuantas más horas le dedicás al arranque, más rápido salís después (CRE L8 00:26).
- La velocidad sale de los **presets**: secuencia, estilo de subtítulo y corrección de color se configuran una vez y después se arrastran ([[content-capital-cre-l09-primeros-pasos-en-adobe-premiere|CRE L9]] 09:51, 42:04, 48:18).
- Menos carga visual, más cómodo de ver: por eso el degradé abajo, donde la app pone perfil, descripción y likes (CRE L9 49:29–49:38).
- Techo del método: es "lo más simple" que da un look profesional. Más capas cuestan más tiempo; para algo complejo, editor o más horas ([[content-capital-cre-l13-generacion-con-ia|CRE L13]] 18:56).
- El instructor es Bernabé Verón, editor de Ramiro Cubría (apellido por reconocimiento automático; CRE L8 00:13). Desde L13 no se presenta: se le atribuye por inferencia.

## Cuándo usarlo / cuándo no

- **Sí**: cada reel vertical de talking head que editás vos mismo.
- **Sí, antes de animar**: es la base sobre la que se montan [[animacion-basica-para-reels]], [[sound-design-del-reel-musica-whooshes-sfx]] y [[broll-con-ia-en-el-reel]].
- **No**: si buscás un nivel de edición experto. Ahí el curso dice delegar (CRE L8 00:53).
- **No uses** el preset vertical de fábrica de Premiere: trae "ciertas configuraciones" que no ayudan (CRE L9 08:49). No dice cuáles.

## Pasos

1. **Proyecto**: nombre con la fecha; carpeta predeterminada de Premiere con una subcarpeta por fecha (CRE L9 00:30).
2. **Espacio de trabajo**: Ventana → Espacios de trabajo → **Vertical**. Paneles a gusto; él deja Propiedades a la derecha y Controles de efectos lo más largo posible (CRE L9 02:05, 04:21). Etiquetas en estilo clásico: Edición → Preferencias → Etiquetas (CRE L9 28:56).
3. **Secuencia** (Proyecto → clic derecho → Nuevo elemento → Secuencia): partir de cualquiera, invertir a **1080×1920**, fotogramas **25 o 30**, nunca 29,97. **Guardar ajuste preestablecido** ("1080 25 fps") antes de aceptar (CRE L9 09:04–09:51). Profundidad de bits y calidad máxima: opcionales, consumen recursos (CRE L9 09:32).
4. **Timeline**: arriba todo lo visual, abajo todo el audio; pistas comprimidas al máximo para ver más capas (CRE L9 11:20, 12:04).
5. **Importar**: arrastrar a la timeline, o por el panel Proyecto si el arrastre trae solo el audio. Ante el aviso de discrepancia del clip: **Mantener la configuración existente** (CRE L9 26:20, 27:22).
6. **Cortar**: sacar silencios y pausas que "se sienten muy separadas". Lo más rápido es **Q** (borra hasta el corte anterior) y **W** (hasta el siguiente), que cierran el hueco solos. Solo cuentan las pistas marcadas "con importancia" (CRE L9 31:48–35:58). Qué botones de pista deja encendidos se ve en pantalla, no se entiende por audio (CRE L9 13:31).
7. **Subtítulos** (CRE L9 36:11–47:08):
   - Texto → Transcripción → **Generar transcripción estática**, desde la **pista de voz** (nunca "Mezcla" si hay otro audio), en español.
   - Corregir: con la lupa → **Reemplazar todo**, sacar puntos, comas y signos de apertura; después palabra por palabra.
   - Crear un texto propio con tu tipografía y colores y guardarlo en **Estilos vinculados → Crear estilo** ("estilo subs").
   - Botón **CC**: ~15 caracteres (13-17), duración mínima al mínimo, **una línea**, estilo "subs".
   - Alinear a mano los que aparecen antes de la palabra o fuera del corte; agrupar por sentido.
   - **Gráficos → Actualizar pista de subtítulos a gráfico**, subirlos desde Movimiento y copiar ese Movimiento a todos.
8. **Color básico** en Lumetri → Corrección básica: bajar un poco la exposición, bajar sombras, subir contraste, desaturar. Un look frío se ve "más serio". Guardar como preset "corrección básica" y arrastrarlo a cada clip (CRE L9 47:10–48:18). Hay un valor que el audio deja dudoso ("resultados").
9. **Degradé abajo**: forma con relleno degradado lineal negro, opacidad 0 arriba, a todo el ancho y durante todo el video (CRE L9 49:23).
10. **Look extra opcional — modos de fusión** (en Opacidad; CRE L13 15:26–18:53):
    - **Multiplicar**: lo blanco desaparece, lo oscuro queda (en L12 se usa para una sombra de ventana).
    - **Pantalla**: lo oscuro desaparece, lo claro queda. Ahí van las transiciones de luz (*light leaks*) bajadas de YouTube.
    - **Superponer** y **Luz suave**: actúan sobre claros y oscuros; Luz suave es más sutil.
    - **Diferencia**: cada color busca su opuesto; sobre texto es un efecto conocido, casi no se nota sobre gris.
11. **Exportar** ([[content-capital-cre-l15-exportando-nuestro-proyecto-premiere|CRE L15]]):
    - borrar todo lo que sobra en el timeline;
    - tocar solo **nombre** y **ubicación**; "tocar más" puede arruinar el video;
    - preset **Match Source – Adaptive High Bitrate** (MP4);
    - rango: toda la secuencia solo si no queda nada después; si no, **I / O**, retrocediendo un fotograma antes de marcar la salida para no llevarte un frame negro (clave en loops);
    - Media Encoder solo si aparece y el video es largo; un reel tarda 1-2 min.

## Plantilla para llenar (ficha de presets del reel)

```
PROYECTO: nombre = AAAA-MM-DD_<tema> · carpeta = <Premiere>/<fecha>
PRESET SECUENCIA: nombre ______ · 1080×1920 · fps [25 | 30] (nunca 29,97)
PRESET SUBTÍTULO ("estilo subs"):
  tipografía ______ · peso ______ · tamaño ______ · interlineado ______
  color/relleno ______ (de la paleta de marca) · alineación: centrado
  CC: máx. ___ caracteres (13-17) · 1 línea · duración mínima al mínimo
  posición vertical: ______ (arriba del degradé y del texto de la app)
PRESET COLOR ("corrección básica"): exposición ↓ · sombras ↓ · contraste ↑ · saturación ↓ · temperatura ______
DEGRADÉ INFERIOR: negro → opacidad 0 · alto ______ · todo el video [sí/no]
MODO DE FUSIÓN extra (si hay): capa ______ en [Multiplicar | Pantalla | Superponer | Luz suave | Diferencia]
EXPORT: Match Source – Adaptive High Bitrate · MP4 · rango [secuencia | I/O -1 frame] · nombre ______
```

Los valores numéricos de color, degradé y tamaño **no se dicen en el curso**: se ajustan mirando. No inventarlos.

## Ejemplos del curso desarmados

| Paso (min) | Lo que hace | Por qué |
|---|---|---|
| Secuencia 1080×1920 a 25 fps guardada (CRE L9 09:04–09:51) | Parte de un preset de YouTube e invierte medidas | Evita el preset de fábrica y 29,97 por compatibilidad |
| ~20 s cortados con Q/W (CRE L9 34:01) | Reel de Rama con la escena del auto | Sacar pausas que se sienten separadas |
| Subtítulo Helvetica Bold, degradé blanco-azul a 90° (CRE L9 39:40–40:22) | Estilo propio; al final lo pasa a blanco sólido (46:34) | Mostrar que el color se aplica a todas las letras |
| "Corrección básica" de Lumetri (CRE L9 47:10) | Exposición y sombras abajo, contraste arriba, desaturado | "Mil veces más profundidad" que por defecto |
| Degradé negro abajo (CRE L9 49:23) | Forma con opacidad 0 arriba | Suaviza la zona de perfil y likes |
| Transición de luz en Pantalla (CRE L13 15:01, 18:19) | Light leak de YouTube con clic sonoro, girado para cubrir | Lo oscuro desaparece y queda la luz |
| Export con I/O (CRE L15 03:59) | Retrocede un frame antes de O | No llevarse un frame negro al final |

## Errores comunes

- Mover un texto fuera del borde de la capa de gráficos y después mover la capa: queda recortado. La capa es la pecera; los textos, los peces (CRE L9 19:05–20:14).
- Punto de anclaje corrido: la rotación y la escala salen de un lugar inesperado (CRE L9 22:26).
- Usar el recorte de Movimiento; hay un efecto que lo hace mejor (CRE L9 23:15). El audio no dice cuál.
- Transcribir desde "Mezcla" cuando hay música u otro audio (CRE L9 36:11).
- Dejar la puntuación en los subtítulos (CRE L9 37:26).
- Subtítulo que aparece antes de la palabra o que arranca fuera del corte (CRE L9 43:28, 45:36).
- Tocar configuraciones de export de más (CRE L15 00:48).
- Exportar "toda la secuencia" con clips sueltos o negros al final; marcar O parado en el último frame (CRE L15 02:43, 03:59).

## Checklist para agentes

```
[ ] ¿La secuencia es 1080×1920 a 25 o 30 fps, desde un preset propio (no el de fábrica, no 29,97)?
[ ] ¿Se mantuvo la configuración de la secuencia ante la discrepancia del clip?
[ ] ¿Se cortaron silencios y pausas largas?
[ ] ¿La transcripción salió de la pista de voz, en español, y fue corregida a mano?
[ ] ¿Los subtítulos no tienen puntuación, usan el estilo de marca guardado, 1 línea, ~15 caracteres?
[ ] ¿Ningún subtítulo aparece antes de la palabra ni cruza un corte?
[ ] ¿Se aplicó el preset de color a todos los clips?
[ ] ¿Hay degradé oscuro abajo durante todo el video?
[ ] ¿El export es Match Source – Adaptive High Bitrate, MP4, sin clips sueltos ni frame negro al final?
[ ] ¿Todo ajuste que el curso solo muestra en pantalla quedó marcado como "a ojo", sin valores inventados?
```

## Fuentes

- Base: [[content-capital-cre-l09-primeros-pasos-en-adobe-premiere]] 00:30–52:35 (todo el flujo).
- [[content-capital-cre-l08-introduccion]] 00:13–00:53 (alcance y cuándo delegar).
- [[content-capital-cre-l12-edicion-practica]] 01:36 (subtítulos siempre abajo) y 16:47 (Multiplicar en uso).
- [[content-capital-cre-l13-generacion-con-ia]] 15:01–20:05 (modos de fusión, light leaks, techo del método).
- [[content-capital-cre-l15-exportando-nuestro-proyecto-premiere]] 00:00–04:33 (export).
- Relacionadas: [[grabacion-celular-luz-encuadre-audio]] (el espacio abajo para subtítulos al grabar se completa acá con el degradé); [[hook-cuatro-variables]] (el texto en pantalla que se entiende sin audio sale de este mismo estilo de subtítulo, inferencia mía); [[formatos-rotacion-sin-quemar]].
- Inferencia mía: la ficha de presets y el orden en 11 pasos agrupan lo que el curso enseña de corrido.

## Tensiones internas del curso

- **Subtítulos animados.** Enseña un preset de entrada para subtítulos, pero dice que en subtítulos a él "personalmente no me gusta mucho" (CRE L11 11:14). La ficha no lo incluye por defecto.
- **Desaturar siempre vs. color.** La corrección básica desatura; en L11 el B-roll puede ir en color si se cuida la saturación (CRE L11 19:40). Es gusto, no regla.
- **Export de audio.** Para el video final, Match Source; para mandar la voz a limpiar, exporta MP3 porque es más rápido (CRE L14 05:49). No se contradicen: son dos exports distintos.
- **"Sin dedicarle horas" vs. "al principio es lento".** Los dos están en L8 (00:15, 00:26); el curso los concilia con la práctica y los presets.
