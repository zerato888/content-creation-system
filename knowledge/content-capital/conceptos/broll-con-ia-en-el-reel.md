---
title: "Planos con IA para el reel: frame del timeline, cámara → acción, iterar barato (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-cre-l13]
source_count: 1
created: 2026-09-26
updated: 2026-09-26
tags: [content-capital, cc-cre, framework, checklist, plantilla, ia, edicion, premiere, produccion, retention]
status: developing
---

## En una línea

Para meter un plano generado con IA en el reel: sacá **un fotograma del propio video** como imagen de partida, escribí el prompt **primero con la cámara y después con la acción**, generá **todo al mínimo** mientras iterás, y en Premiere **arrancá el clip antes de la frase y aceleralo** para que la acción ya esté pasando cuando se dice.

## Qué es y por qué funciona (según el curso)

- El plano con IA sirve para el hook o para el cuerpo; depende de lo grabado y del guion ([[content-capital-cre-l13-generacion-con-ia|CRE L13]] 00:00).
- La IA **depende de iterar**: al principio no genera lo que querés y cada intento cuesta créditos. "Es un juego de iteración esto" (CRE L13 01:21, 12:52).
- Partir de un frame del propio video hace que el primer frame generado **coincida** con el momento del corte (CRE L13 05:33, 13:03).
- La IA genera acciones lentas: por eso se adelanta y se acelera (CRE L13 06:00, 13:34).
- "La inteligencia artificial no entiende el no" (CRE L13 09:10).
- La lección no tiene presentación del instructor; se atribuye a Bernabé Verón por inferencia (mismo video del auto que L12 y L14).

## Cuándo usarlo / cuándo no

- **Sí**: en un tramo "demasiado vacío" donde la frase pide una imagen que no grabaste (CRE L13 05:33).
- **Sí, con plan pago**: sin plan no hay uso. El instructor recomienda Freepik **Premium+**; el Premium básico alcanza poco; quien meta IA en todos los videos necesita **Pro** (CRE L13 00:39).
- **Con extrema cautela**: modelos caros como Veo 3 (~12.000 créditos según él) (CRE L13 03:13).
- **No** generes en alta calidad mientras el prompt todavía no está probado (CRE L13 04:57).

## Pasos

1. **Elegir el tramo** en el timeline y decidir la acción (en el ejemplo: el protagonista baja del auto y explica en una pizarra) (CRE L13 05:33).
2. **Ubicar el plano 1-2 s antes de la frase** (CRE L13 06:00).
3. **Sacar el frame**: apagar con el ojo las capas de texto y sombra, y exportar el fotograma con el ícono de cámara como PNG (CRE L13 06:23). **Marcar ese frame** en el timeline (CRE L13 13:03).
4. **En la herramienta** (él usa Freepik → AI Suite → generador de video, que ofrece modelos de otras empresas) → **Start with image** (CRE L13 02:01, 06:44).
5. **Borrar el prompt de cámara por defecto** que aparece al cargar la imagen (un zoom in) (CRE L13 06:44).
6. **Todo al mínimo**: vertical (se ajusta a la imagen), 720p, 5 s. Costos que dice: 5 s a 720p = 300 créditos; 1080p = 500; 10 s ≈ el doble (CRE L13 07:14). Algunos modelos permiten 360p o 240p para probar el prompt (CRE L13 11:51).
7. **Prompt**: primero el movimiento de cámara (en mano, sujeto centrado, leve *camera shake*), después la acción y cómo cierra el plano (CRE L13 10:16).
8. **Opcionales** (Advanced settings): **seed** para repetir "el mismo caminito" con resultados parecidos; **negative prompt** con el objeto a evitar escrito en positivo ("payaso", no "no generes un payaso") (CRE L13 08:07, 09:10).
9. **Iterar**: la primera sale con fallas y se corrige en la segunda; cada prompt nuevo, a la calidad más baja (CRE L13 11:51).
10. **En Premiere**: alinear el primer frame con el frame marcado, acelerar el clip (probó 200% y 180%, quedó en ~160%) para que llene justo el tramo, y subir las capas de texto y animación por encima (CRE L13 13:34–14:22).

**Mapa de modelos según el instructor** (CRE L13 03:13–04:52; grafías por reconocimiento automático, algunas dudosas; precios y lista de la fecha de grabación, no verificados):

| Necesidad | Modelo que nombra |
|---|---|
| Lo más profesional | Kling ("cling"); 2.1 con multitoma para escenas movidas |
| Versátil y barato | Kling 1.6 Standard |
| Muy cinematográfico | Seedance ("SIDAN"), Kling 2.1 Master, uno que se oye "1, 2.2" (¿Wan 2.2?, dudoso) |
| Lo delirante | PixVerse ("PixBers") |
| Elegir el control de cámara | MiniMax Director |
| Movimientos físicos grandes | Hailuo (MiniMax) |
| Tipo stock profesional | Google Veo 2 (se rompe con ideas locas); Veo 3 Fast zafa; Veo 3 caro |
| No recomendado | uno que se oye "rango" (¿Runway?, dudoso): flojo y con límite corto de caracteres |

## Plantilla para llenar (ficha de plano con IA)

```
TRAMO: min ____ a ____ · FRASE: "______" · ¿por qué hace falta? (tramo vacío / la frase pide imagen)
ACCIÓN buscada: ______________________
INICIO DEL PLANO: 1-2 s antes de la frase → min ____
FRAME DE ORIGEN: min ____ · capas apagadas: [texto, sombra, ______] · marcador puesto [sí]
MODELO: ______ (por necesidad, ver mapa) · créditos estimados ______
PRUEBA: resolución [240p | 360p | 720p] · duración 5 s · prompt de cámara por defecto borrado [sí]
PROMPT:
  CÁMARA: ______________________ (en mano / centrado / shake / sigue al sujeto / se abre)
  ACCIÓN: ______________________
  CIERRE DEL PLANO: ______________________
NEGATIVO (en positivo, solo el objeto): ______
SEED: [no | ______]
ITERACIONES: v1 falla → ______ · v2 → ______
PREMIERE: velocidad ____% (probar ~160%) · primer frame alineado [sí] · texto por encima [sí]
```

## Ejemplos del curso desarmados

| Paso (min) | Lo que hace | Lectura |
|---|---|---|
| Tramo vacío en el video del auto (CRE L13 05:33) | Decide que el protagonista baje y explique en una pizarra | La IA llena lo que no se grabó |
| Frame "pelado" exportado como PNG (CRE L13 06:23) | Apaga texto y sombra antes de exportar | La imagen de partida no lleva gráficos |
| Se queda sin créditos y pasa a Kling 2.1 (CRE L13 06:44) | Cambia de modelo por costo | El modelo se elige también por precio |
| Prompt: cámara en mano, centrado, shake → baja del auto, pizarra verde, la cámara lo sigue y abre (CRE L13 10:16) | Cámara primero, acción después | Estructura del prompt |
| Clip al ~160% (CRE L13 13:34) | Acelera hasta llenar el tramo | La acción lenta llega a tiempo |
| "Podcast de mono" de Rama con Veo 3 (CRE L13 03:13) | Ejemplo de modelo caro | Solo cuando lo vale |

## Errores comunes

- Escribir "no generes X" en el prompt: genera X (CRE L13 09:10).
- Dejar el zoom in por defecto que propone la herramienta (CRE L13 06:44).
- Probar prompts nuevos en 1080p o 10 s: se queman créditos (CRE L13 04:57, 11:51).
- Exportar el frame con texto o sombras encima (CRE L13 06:23).
- No marcar el frame de origen y perder dónde encaja el clip (CRE L13 13:03).
- Poner el clip a velocidad normal justo en la frase: la acción llega tarde (CRE L13 06:00, 13:34).
- Usar modelos caros sin cuidado (Veo 3) (CRE L13 03:13).

## Checklist para agentes

```
[ ] ¿El tramo necesita de verdad un plano con IA (vacío o la frase pide una imagen)?
[ ] ¿La imagen de partida es un frame del propio video, sin texto ni sombras?
[ ] ¿El frame de origen quedó marcado en el timeline?
[ ] ¿El plano arranca 1-2 s antes de la frase?
[ ] ¿Se borró el prompt de cámara por defecto?
[ ] ¿El prompt describe primero la cámara y después la acción?
[ ] ¿El negativo está escrito en positivo (solo el objeto)?
[ ] ¿Las pruebas se hicieron al mínimo (≤720p, 5 s)?
[ ] ¿El clip está acelerado y el primer frame coincide con el corte?
[ ] ¿Texto y animaciones quedaron por encima del clip?
[ ] ¿Los nombres de modelos y precios se trataron como dudosos o de la fecha de grabación?
```

## Fuentes

- Base: [[content-capital-cre-l13-generacion-con-ia]] 00:00–14:22 (todo el flujo y el mapa de modelos). Los modos de fusión de la misma lección (15:26–18:53) están en [[edicion-simple-premiere-look-profesional]].
- Relacionadas: [[guionado-iterativo-con-ia]] (mismo principio de iterar en idas y vueltas cortas, aplicado a video; inferencia mía); [[guion-hook-problema-solucion-prueba-cta]] y [[hook-cuatro-variables]] (el plano depende de lo que diga el guion y puede ir en el hook, CRE L13 00:00); [[animacion-basica-para-reels]] (la otra forma de llenar un tramo vacío); [[sound-design-del-reel-musica-whooshes-sfx]].
- Inferencia mía: la ficha y la tabla de modelos por necesidad ordenan lo que el instructor enumera de corrido.

## Tensiones internas del curso

- **Hook vs. acción lenta.** Dice que la IA sirve para el hook (CRE L13 00:00), pero también que genera acciones lentas y hay que acelerarlas (CRE L13 06:00). No lo discute para los primeros segundos.
- **720p "ni se nota" vs. calidad.** Recomienda iterar al mínimo y dice que 720p casi no se nota en Premiere (CRE L13 11:51), sin decir cuándo vale pagar 1080p.
- **Kling profesional vs. PixVerse delirante**: después dice que Kling 2.1 mejoró en lo delirante (CRE L13 03:13). El mapa es opinión del instructor y de la fecha de grabación.
- **Costo**: los créditos por clip los dice de memoria ("no estoy con suficiente crédito"); son aproximados.
