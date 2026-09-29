---
title: "ManyChat: bases y flujos por disparador (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-mc-l01, cc-mc-l02, cc-mc-l03, cc-mc-l04, cc-mc-l05, cc-mc-l06, cc-mc-l07, cc-mc-l08, cc-mc-l09, cc-mc-l10, cc-mc-l11, cc-mc-l12, cc-mc-l13, cc-mc-l15, cc-mc-l16, cc-mc-l17]
source_count: 16
created: 2026-09-25
updated: 2026-09-25
tags: [content-capital, cc-mc, manychat, framework, checklist, plantilla, automatizacion, dm, cta, historias, lead-magnet, operaciones]
status: developing
---

## En una línea

Todo flujo de ManyChat se arma con las mismas piezas (**disparador → acciones → condiciones → aleatorizador → pausas → mensajes**) y cambia según por dónde entra el lead: comentario en reel o carrusel, respuesta a historia, DM con palabra clave o nuevo seguidor. Desde las nuevas reglas de Meta, el flujo tiene que variar mucho los mensajes y entregar siempre el recurso prometido.

## Qué es y por qué funciona (según el curso)

- ManyChat automatiza partes del chat de Instagram: es "un recepcionista 24/7" que abre conversaciones, responde rápido y ordena la bandeja ([[content-capital-mc-l01-introduccion-y-usos|MC L1]] 01:18, 01:46).
- Responder rápido convierte más: el pico de intención es cuando el lead escribe ("un multiplicador directo de agendas", MC L1 02:20-02:38).
- **Las piezas** (MC L2-L5):
  - **Disparadores**: comentario en publicación o reel; respuesta a historia; DM con palabra clave; saludo a nuevos seguidores ([[content-capital-mc-l02-disparadores|MC L2]] 00:34-02:38).
  - **Bloques de mensaje**: texto, imagen, retraso, audio (.m4a, llega como nota de voz), video, botón y **recopilación de datos**, la única que permite ramificar según responda o no ([[content-capital-mc-l03-bloques-de-contenido|MC L3]] 00:14-01:33).
  - **Acciones**: etiquetas (qué contestó), campos de usuario (en qué estado está) y asignar conversación ([[content-capital-mc-l04-acciones|MC L4]] 00:17-03:00).
  - **Condiciones, aleatorizadores y pausas inteligentes**: ramificar por etiqueta o campo, variar abridores para testear y para no parecer robot, y esperar entre mensajes ([[content-capital-mc-l05-filtros-aleatorizadores-y-pausas-inteligentes|MC L5]] 00:14-02:42).
- **Regla de la ventana**: si el lead comentó un reel, solo se le puede mandar **un** mensaje (respuesta privada) hasta que toque un botón. En historias hay 24 h y se pueden mandar seguimientos libres (MC L3 01:42; [[content-capital-mc-l06-automatizaciones-para-reels-y-posteos|MC L6]] 07:32).
- **Versión 2026 ("nuevos flujos", Paolo)**: por las nuevas políticas de ManyChat y Meta, "lo menos robotizado posible": máximo de aleatorizadores (hasta 12, cree), pausas asimétricas y que "no le caiga la misma pregunta a dos personas al mismo tiempo" ([[content-capital-mc-l15-nuevo-flujo-para-bienvenidas|MC L15]] 01:17-02:08; [[content-capital-mc-l16-nuevo-flujo-de-reels-y-carruseles|MC L16]] 02:03). Además, **siempre hay que entregar el recurso prometido** (MC L16 02:27).

## Cuándo usarlo / cuándo no

- **Sí**: con volumen alto y un seteo que ya funciona; ManyChat multiplica lo que hay (MC L1 09:44).
- **No**: para arreglar un marketing malo ni con flujos complicados desde el día 1: "empezá simple, escalá después" (MC L1 08:08, slide 09:26).
- **Mega árbol**: solo con 10.000-20.000 leads por mes; "no te lo recomiendo para la gran mayoría" ([[content-capital-mc-l09-mega-arbol-de-manychat|MC L9]] 01:08, 04:41).
- **Abridor en historias**: la versión vieja lo usa solo con mucho volumen; la nueva, nunca (ver Tensiones).
- **Asignación avanzada** (por seguidores o tipo de lead): solo con más de 15.000-20.000 leads por mes ([[content-capital-mc-l12-asignacion-de-leads|MC L12]] 00:20).
- Siempre construir desde **"espacio en blanco"** en el constructor de flujos, no en la vista con el teléfono, que "está bastante limitada" (MC L2 00:00). El saludo a nuevos seguidores es la excepción: se activa la plantilla y se pasa al constructor (MC L2 02:38).

## Pasos

**A. Flujo de reels y carruseles (versión 2026, MC L16).**
1. Disparador: comentario en un reel específico, cualquier comentario (la versión vieja recomendaba "la siguiente publicación" y subir el reel enseguida, MC L2 00:47).
2. Respuestas públicas al comentario, muchas y variadas ("te envié un mensaje", "fijate los DMs"), adaptadas a tu forma de hablar (MC L16 05:16).
3. Acciones: etiquetas de formato + mes, de lead + mes y de pieza "FORMATO – ÁNGULO – FECHA"; campo ÁNGULO; marcar conversación abierta (MC L16 07:53-09:45). Ver [[deteccion-de-angulos-ganadores-trazabilidad]].
4. Condición "no tiene etiqueta ASIGNADO" → asignar a un grupo de setters + etiqueta ASIGNADO (MC L16 09:45).
5. Ramificar por ángulo (o "cualquier valor" para lo genérico) y, en cada rama, un aleatorizador de recursos de ese ángulo (MC L16 10:33-12:37).
6. Mensaje único con botón que entrega el recurso **dentro del chat**; etiqueta por botón y condición para que llegue una sola vez aunque lo toquen muchas veces (MC L16 14:24-15:59). Ver [[cta-recurso-irresistible]].
7. Bifurcar a dos flujos centrales: **general** (no seteados: pregunta A/B de arranque) y **seteando** (ya seteados: preguntas de seguimiento) (MC L16 18:08-23:22). Ver [[manychat-setting-automatizado]].
8. Para cada pieza nueva: duplicar el flujo y cambiar pieza y etiquetas (MC L16 06:51).

**B. Flujo de reels versión vieja (MC L6), por si no hay recurso por ángulo.** Etiquetas → abrir → asignar → si hubo interacción en las últimas 12 h, pausar y reintentar entre 8 y 22 h → pausa de ~2 min → condición por campos (digital, físico, no calificado; si ya tiene uno, no repetir la pregunta) → aleatorizador de 4-5 abridores con botones que setean un campo → recopilación de datos + seguimiento a 1 h (MC L6 00:34-06:54).

**C. Historias (MC L17).** Disparador: respuesta a todas las historias, cualquier palabra → marcar abierta → etiquetas "leads | mes", "historias | mes", "HISTORIA" y la de la pieza → asignar. Sin abridor: el setter entrega el recurso y sigue la estructura ([[content-capital-mc-l17-nuevo-flujo-de-historias|MC L17]] 01:06-03:39). Ver [[secuencias-de-historias]].

**D. Bienvenida a nuevos seguidores (MC L15).** Activar la plantilla y pasar al constructor → etiqueta nuevo seguidor + mes, marcar abierta, asignar → aleatorizador con todas las variantes → pausas asimétricas (2 min, 96 s, 189 s, 364 s) → un solo mensaje: agradecimiento + "contame así te guío" + pregunta A/B fácil (MC L15 00:49-03:41). KPI de la versión vieja: tasa de respuesta de al menos 65% ([[content-capital-mc-l08-outbound-a-seguidores|MC L8]] 00:14).

**E. DM con palabra clave (MC L2 02:14).** CTA "mandame la palabra INFO", con variantes mal escritas.

**F. Envío de calendario (MC L10).** Queda apagado y lo dispara el setter: borrar la etiqueta "respondio_calendario" si la tiene → "acá te comparto la disponibilidad" + link + audio de horarios + "avisame así le doy prioridad" → etiquetas "calendario enviado" y "respondio_calendario" → seguimientos a 30 min, 1 h, 6 h (audio) y 12 h, solo entre 8 y 22 h ([[content-capital-mc-l10-automatizacion-de-envio-de-calendario|MC L10]] 00:23-02:19).

**G. Automatizaciones útiles para el setter (MC L11, L13).** Secuencias prearmadas en carpetas (abridores, rants, casos de éxito, pitch, calendarios, seguimientos) que el setter lanza, pausa o reanuda desde el chat en vivo ([[content-capital-mc-l11-automatizaciones-utiles|MC L11]] 00:13-04:33; [[content-capital-mc-l13-gestion-de-chats|MC L13]] 00:37-01:11). Se crean con cualquier disparador, se publican y se apagan (MC L11 03:51).

**H. Asignación y chats (MC L12, L13).** Asignación automática básica entre los setters disponibles, límite ilimitado; reasignar es un clic desde la pestaña del chat (MC L12 00:49, 01:22). En cada chat, el setter ve lo que contestó el lead y sus campos (MC L13 00:14).

## Plantilla para llenar

```
FLUJO: [reel/carrusel | historia | bienvenida | DM palabra clave | calendario | secuencia setter]
DISPARADOR: ______________ (reel específico ____ / todas las historias / palabra "____" + variantes ____, ____)
RESPUESTAS PÚBLICAS (si es comentario, 6+ variantes): 1 ____ 2 ____ 3 ____ 4 ____ 5 ____ 6 ____
ACCIONES:
  etiqueta formato|mes: "____ | ____"   etiqueta lead|mes: "Leads | ____"
  etiqueta pieza: "FORMATO – ÁNGULO – FECHA" = ______________
  campo ÁNGULO = ______   marcar abierta: sí
CONDICIÓN "no tiene ASIGNADO" → asignar a ______ + etiqueta ASIGNADO
[reels vieja] CONDICIÓN última interacción >12 h? no → pausa, reintento 8-22 h
RAMAS POR ÁNGULO: A ______ | B ______ | cualquier valor → genérico
  cada rama: aleatorizador de recursos: ____ / ____ / ____
MENSAJE CON BOTÓN (único): "______________ tocá el botón" [BOTÓN: ____]
  etiqueta "botón recurso ____ N" + condición "llega una sola vez"
BIFURCACIÓN: tiene SETEANDO? no → flow GENERAL · sí → flow SETEANDO
PAUSAS (asimétricas): ___ s / ___ s / ___ s   ventana: 8:00-22:00
BIENVENIDA: "[saludo + gracias por seguir]" + "[contame así te guío]" + "[pregunta A/B: ____ o ____?]"
KPI: tasa de respuesta ___% (bienvenida ≥65%) · CTR botón ___% (≥30-35%)
```

## Ejemplos del curso desarmados

| Flujo (min) | Qué hace | Qué copiar |
|---|---|---|
| Respuesta pública múltiple: "¡Mensaje entregado! Revisá tus DMs" / "Revisá los DMs – la información está ahí" / "¡Hecho! Está en tus DMs" (MC L6 00:30) | Varía la respuesta al comentario | Nunca una sola respuesta pública |
| "reel leads podridos" con 6+ respuestas públicas (MC L16 06:30) | Variantes "mega orgánicas" | Adaptar el tono al nicho, no copiar el voseo |
| Aleatorizador A/B/C/D al 25%: "contame en q situación estás apretando el botón q más se adapte a tu caso" + 3 botones que setean NEGOCIO DIGITAL (MC L6 06:30) | Abridor con botones que clasifican | El botón abre la ventana y guarda el dato |
| Flujo "HR – 23/12": respuesta a historia → etiquetas HR, conversación y historias del mes → condición ASIGNADO (MC L7 00:30) | Historias versión vieja | Lo central son las etiquetas |
| "TEMPLATE HISTORIAS JUNIO": abrir + 4 etiquetas + asignar (MC L17 03:30) | Historias versión nueva, sin abridor | Mínimo y sin mensaje masivo |
| Bienvenida: "buenas, gracias por seguir 💪 / contame así te guío mejor / tu negocio es físico, digital o arrancás de 0?" (MC L15 03:30) | Un mensaje con pregunta A/B | La pregunta tiene que ser casi un "no-brainer" |
| Calendario: 587 envíos, "acá te comparto la disponibilidad" + audio "horarios.m4a" (MC L10 00:53) | Secuencia que dispara el setter | Cuenta calendarios enviados |
| "My Automations" con carpetas AUDIOS, CALENDARIOS SETTER, CASOS DE ÉXITO, FOLLOW UPS, PITCHS, RANTEOS, TRAZABILIDAD (MC L11 04:29) | Biblioteca del setter | Las más usadas a la vista, el resto en carpetas |

## Errores comunes

- Creer que "cuanto más automático, mejor" (MC L1 08:08).
- Mensajes largos y robóticos (MC L1 08:08).
- No testear los disparadores ni los abridores con aleatorizadores (MC L1 08:08; MC L5 01:38).
- Hacer la pregunta equivocada (presupuesto) (MC L1 08:08).
- Flujos complicados desde el día 1 (MC L1 09:26).
- Siempre el mismo abridor: "van a decir, esto es un robot" (MC L5 02:20). En 2026, además, es riesgo de baneo (MC L16 02:03).
- Repetir una pregunta que el lead ya contestó (MC L6 03:54).
- Meterse en una conversación en curso (sin la condición de 12 h) (MC L6 02:52).
- Olvidar la etiqueta ASIGNADO: los leads no llegan a la bandeja del setter (MC L7 00:53; MC L9 01:43).
- Olvidar las variantes mal escritas de la palabra clave (MC L2 01:05).
- No entregar el recurso prometido (regla de Meta) o mandarlo como link de salida (MC L16 02:27, 15:59).

## Checklist para agentes

```
[ ] ¿El flujo se armó desde "espacio en blanco" en el constructor?
[ ] ¿El disparador cubre la palabra clave y sus variantes mal escritas?
[ ] ¿Hay varias respuestas públicas al comentario?
[ ] ¿Tiene etiquetas de formato/mes, lead/mes y de pieza (FORMATO – ÁNGULO – FECHA)?
[ ] ¿Marca la conversación como abierta?
[ ] ¿Asigna con la condición "no tiene ASIGNADO"?
[ ] ¿Los abridores están en un aleatorizador y las pausas son asimétricas?
[ ] ¿En reels, el primer mensaje trae botón (si no, no se puede seguir)?
[ ] ¿El recurso prometido se entrega dentro del chat y una sola vez?
[ ] ¿Se evita repetir preguntas ya contestadas (condición por campo)?
[ ] ¿Los seguimientos corren solo entre 8 y 22 h?
[ ] ¿Historias van sin abridor (versión 2026)?
[ ] ¿Se mide tasa de respuesta y CTR del botón?
```

## Fuentes

- Base vieja (Mati Molina): [[content-capital-mc-l01-introduccion-y-usos]], [[content-capital-mc-l02-disparadores]], [[content-capital-mc-l03-bloques-de-contenido]], [[content-capital-mc-l04-acciones]], [[content-capital-mc-l05-filtros-aleatorizadores-y-pausas-inteligentes]], [[content-capital-mc-l06-automatizaciones-para-reels-y-posteos]], [[content-capital-mc-l07-automatizaciones-para-historias]], [[content-capital-mc-l08-outbound-a-seguidores]], [[content-capital-mc-l09-mega-arbol-de-manychat]], [[content-capital-mc-l10-automatizacion-de-envio-de-calendario]], [[content-capital-mc-l11-automatizaciones-utiles]], [[content-capital-mc-l12-asignacion-de-leads]], [[content-capital-mc-l13-gestion-de-chats]].
- Nuevos flujos (Paolo): [[content-capital-mc-l15-nuevo-flujo-para-bienvenidas]], [[content-capital-mc-l16-nuevo-flujo-de-reels-y-carruseles]], [[content-capital-mc-l17-nuevo-flujo-de-historias]].
- Relacionadas: [[manychat-setting-automatizado]] · [[bot-calificador-claude-manychat]] · [[deteccion-de-angulos-ganadores-trazabilidad]] · [[cta-recurso-irresistible]] · [[secuencias-de-historias]] · [[embudo-organico-instagram]].
- Inferencia mía: la plantilla junta en un solo bloque lo que el curso muestra en flujos separados.

## Tensiones internas del curso

- **Abridor en historias.** Mati: con mucho volumen, abridor; con pocas respuestas (ejemplo: 100), sin abridor ([[content-capital-mc-l07-automatizaciones-para-historias|MC L7]] 01:40-02:11). Paolo: nunca, ni con más de ~600 ejecuciones, porque el mismo mensaje a todos es "contraproducente y riesgoso" (MC L17 01:06). La versión nueva reemplaza a la vieja (inferencia).
- **Entregar el recurso.** La versión vieja prefería preguntas sin botón y no siempre entregar (MC L9 00:44; MC L16 02:27); la nueva lo obliga por Meta.
- **Botones.** Mati los usa para abrir la ventana; Paolo dice que bajan la tasa pero hay que usarlos y medir CTR (MC L16 03:24).
- **"Siguiente publicación" vs. reel específico** como disparador (MC L2 00:47 vs. MC L16 05:16).
- **Cifras** (65% de respuesta, CTR 30-35%, umbrales de leads/mes, "hasta 12 aleatorizadores", "recomendaciones de Meta") son dichos de los instructores, sin documento mostrado.
