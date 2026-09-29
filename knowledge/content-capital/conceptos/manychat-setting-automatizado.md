---
title: "Setting automatizado con ManyChat: iniciar, filtrar, ordenar y agendar (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-mc-l01, cc-mc-l05, cc-mc-l06, cc-mc-l09, cc-mc-l10, cc-mc-l11, cc-mc-l12, cc-mc-l13, cc-mc-l14, cc-mc-l15, cc-mc-l16, cc-mc-l17]
source_count: 12
created: 2026-09-25
updated: 2026-09-25
tags: [content-capital, cc-mc, manychat, framework, checklist, plantilla, automatizacion, dm, ventas, conversion, operaciones]
status: developing
---

## En una línea

ManyChat hace la parte repetible del setting (primer mensaje, pregunta de filtro, clasificación, seguimientos y envío del calendario) y el setter humano entra donde hace falta criterio; la automatización es "para iniciar, filtrar y ordenar", no para cerrar solo.

## Qué es y por qué funciona (según el curso)

- El setting es la conversación que califica al lead y lo lleva a una llamada. ManyChat es "el mejor amigo del setter": entra cuando el lead ya contestó un CTA ([[content-capital-mc-l01-introduccion-y-usos|MC L1]] 03:23).
- Recorrido ideal: respuesta inmediata → bienvenida → primera pregunta de filtro → filtrado automático → derivación → el setter agenda (MC L1 10:16).
- **Qué sí automatizar**: respuestas rápidas, entrega de recursos, filtrado simple, derivación al setter con aviso, seguimientos básicos, etiquetas, Sheets o CRM (MC L1 05:56).
- **Qué no**: entender contexto, respuestas ambiguas, señales emocionales, distinguir dolor de curiosidad, preguntas estratégicas, generar confianza (MC L1 04:59).
- Se puede automatizar el 100%, pero no lo recomienda (MC L1 05:45). En ticket alto, reemplazar al setter con un bot "vas a perder mucha plata"; en ticket bajo o para agendar un triage, se puede vender por chat (MC L1 06:22).
- **"Setting con botones"**: el setter tiene secuencias prearmadas (abridores, rants, casos de éxito, pitch, calendario) y las dispara con un clic; así el chat "se ve súper natural" y "ya tenés el 90% del trabajo hecho" ([[content-capital-mc-l11-automatizaciones-utiles|MC L11]] 00:13-05:35).
- **Filtro por campos**: cada respuesta guarda un dato (negocio digital, físico, sin negocio, no calificado). Con eso el bot no repite preguntas y el setter ve el estado en el chat ([[content-capital-mc-l06-automatizaciones-para-reels-y-posteos|MC L6]] 03:54; [[content-capital-mc-l13-gestion-de-chats|MC L13]] 00:14).
- **Versión 2026 (Paolo)**: dos flujos centrales. **General** para quien todavía no está siendo seteado (pregunta A/B de arranque) y **seteando** para quien ya está en la estructura (preguntas de seguimiento que no chocan). La etiqueta SETEANDO va en todas las preguntas y pasos, incluido el pitch del calendario ([[content-capital-mc-l16-nuevo-flujo-de-reels-y-carruseles|MC L16]] 18:08-23:22).
- **Paso siguiente**: que Claude clasifique las respuestas y dispare cada etapa sola. Ver [[bot-calificador-claude-manychat]].

## Cuándo usarlo / cuándo no

- **Sí**: cuando ya tenés una estructura de prospección que convierte y volumen de conversaciones (MC L1 09:44; [[content-capital-mc-l14-manychat-claude|MC L14]] 01:08).
- **Sí, primero**: el filtro de arranque y el envío de calendario; el cuello de botella suele ser cuánto tarda el setter en mandarlo (MC L14 01:44).
- **No**: para reemplazar al setter en ticket alto (MC L1 06:22).
- **No**: si el seteo manual no funciona: "funciona peor" (MC L1 09:44).
- **Historias**: el que responde una historia es "bastante caliente": lo toma el setter sin abridor automático ([[content-capital-mc-l17-nuevo-flujo-de-historias|MC L17]] 00:39-01:59).

## Pasos

1. **Definí la pregunta de arranque** A/B, fácil de responder y ligada a tu oferta ("¿tu negocio es físico, digital o arrancás de 0?") ([[content-capital-mc-l15-nuevo-flujo-para-bienvenidas|MC L15]] 03:04-03:41; MC L16 22:05).
2. **Guardá la respuesta en un campo** (botón que setea el campo o recopilación de datos) (MC L6 05:41-06:54).
3. **Condición por campo**: si ya lo tiene, no repetir la pregunta; mandale otra cosa (MC L6 03:54; [[content-capital-mc-l09-mega-arbol-de-manychat|MC L9]] 04:04).
4. **Sin respuesta**: pausa y "todo bien, avisame" a los ~20 min, y seguimientos en cadena ([[content-capital-mc-l05-filtros-aleatorizadores-y-pausas-inteligentes|MC L5]] 02:42). Si ya se le preguntó y no contestó: marcarlo "sin categorizar" y mandar "creo que ya te pregunté antes pero no se me guardó" (MC L9 03:10).
5. **Asigná** la conversación a un setter (etiqueta ASIGNADO); reparto automático básico ([[content-capital-mc-l12-asignacion-de-leads|MC L12]] 00:49).
6. **Marcá SETEANDO** en cada paso de la estructura, para que un lead en curso no reciba la pregunta de arranque de nuevo (MC L16 19:08).
7. **Armá la biblioteca del setter** en carpetas: abridores, rants (texto o 3-4 audios con 10-11 s entre sí), casos de éxito por segmento, pitch de la llamada en audio, calendarios, seguimientos (MC L11 01:14-04:33).
8. **Envío de calendario** como secuencia que dispara el setter: disponibilidad + link + audio de horarios + "avisame así le doy prioridad"; seguimientos a 30 min, 1 h, 6 h y 12 h, solo entre 8 y 22 h; etiqueta "calendario enviado" para contar ([[content-capital-mc-l10-automatizacion-de-envio-de-calendario|MC L10]] 00:38-02:19).
9. **El setter opera desde el chat**: ve campos y respuestas, lanza, pausa (30 min o siempre) o reanuda automatizaciones (MC L11 00:13; MC L13 00:37-01:11).
10. **Variá todo**: aleatorizadores en abridores y pausas asimétricas, para no parecer robot y para que nadie reciba la misma pregunta al mismo tiempo (MC L5 01:38; MC L16 02:03).

## Plantilla para llenar

```
OFERTA: ______________  TICKET: [bajo → puede cerrar por chat | alto → setter humano]
PREGUNTA DE ARRANQUE (A/B, "no-brainer"): "¿______ o ______?"
  variantes (aleatorizador): 1 ____ 2 ____ 3 ____ 4 ____
CAMPOS: NEGOCIO_A = sí/no · NEGOCIO_B = sí/no · SIN_NEGOCIO · NO_CALIFICADO · SIN_CATEGORIZAR
  si ya tiene campo → mensaje alternativo: "______________"
SIN RESPUESTA: +20 min "______ avisame" → +___ h "______" → sin categorizar: "creo que ya te pregunté pero no se me guardó"
ASIGNACIÓN: grupo ______ · etiqueta ASIGNADO
ETIQUETA SETEANDO en: pregunta 1 ☐ pregunta 2 ☐ rant ☐ caso ☐ pitch ☐ calendario ☐
FLOW GENERAL (no seteados): pregunta de arranque
FLOW SETEANDO (seteados), 2-4 preguntas: 1 ____ 2 ____ 3 ____
BIBLIOTECA DEL SETTER:
  abridores: ____  rants (texto/audio): ____  casos de éxito por segmento: ____
  pitch (audio): ____  seguimientos: ____
CALENDARIO: "acá te comparto la disponibilidad" + [link] + [audio horarios] + "avisame así le doy prioridad"
  +30 min "______" · +1 h "avisame" · +6 h [audio] · +12 h "¿todavía tenés ganas de ______?"  (8-22 h)
```

## Ejemplos del curso desarmados

| Pieza (min) | Etapa | Qué muestra |
|---|---|---|
| "negocio digital = verdadero → ¿cómo viene tu negocio digital?; si no → ¿qué tipo de negocio tenés?" (MC L5 00:40) | Filtro por campo | No repetir lo que ya sabés |
| Carrusel "Hago 300k": condición NEGOCIO DIGITAL / FÍSICO / SIN NEGOCIO / NO CALIFICADO (MC L9 00:30) | Mega árbol | Cuatro ramas según el campo |
| "creo que ya te pregunté antes pero no se me guardó" (MC L9 03:10) | Rescate | Pregunta de nuevo sin sonar robot |
| Chat con "antes q nada dame un poco de contexto" / "vos ya venís vendiendo por ig?" y panel AGENDADO, CALIFICADO, HOT LEAD (MC L13 00:30) | Operación del setter | El estado se lee en los campos |
| "ENVIAR A NEGOCIOS FÍSICOS": setea el campo → audio → link a video → "avisame qué pensás" (MC L11 03:21) | Secuencia de un clic | Caso de éxito por segmento |
| Flow general (1.595 envíos) y flow seteando (141 envíos) (MC L16 21:30) | 2026 | Métricas centralizadas en dos flujos |
| Seteando: "¿cómo vienen los leads que te están llegando?", "che, me parece que ya habíamos hablado" (MC L16 23:22) | 2026 | Preguntas que no chocan con la estructura |

## Errores comunes

- Automatizar todo, incluso donde hace falta criterio (MC L1 04:59, 08:08).
- Preguntar el presupuesto (MC L1 08:08).
- Reemplazar al setter en ticket alto (MC L1 06:22).
- Mandar la pregunta de arranque a quien ya está siendo seteado (MC L16 18:08).
- Repetir una pregunta ya contestada: "nota que es un robot" (MC L6 03:54).
- No contar los calendarios enviados (MC L10 00:12).
- Dejar leads sin asignar (MC L9 01:43).

## Checklist para agentes

```
[ ] ¿Hay una estructura de prospección que ya convierte antes de automatizarla?
[ ] ¿La pregunta de arranque es A/B y fácil de responder?
[ ] ¿Cada respuesta queda guardada en un campo?
[ ] ¿El flujo evita repetir preguntas ya contestadas?
[ ] ¿Hay seguimiento si no responde y un rescate para "sin categorizar"?
[ ] ¿Todo lead queda asignado (ASIGNADO)?
[ ] ¿SETEANDO está en todos los pasos de la estructura?
[ ] ¿El setter tiene la biblioteca en carpetas (abridores, rants, casos, pitch, calendario)?
[ ] ¿El calendario sale con audio, "avisame así le doy prioridad" y seguimientos 8-22 h?
[ ] ¿Se cuentan los calendarios enviados?
[ ] ¿En ticket alto el cierre queda en manos humanas?
```

## Fuentes

- Base: [[content-capital-mc-l01-introduccion-y-usos]] (qué automatizar y qué no), [[content-capital-mc-l11-automatizaciones-utiles]] (setting con botones), [[content-capital-mc-l16-nuevo-flujo-de-reels-y-carruseles]] 18:08-26:35 (general vs. seteando).
- [[content-capital-mc-l05-filtros-aleatorizadores-y-pausas-inteligentes]], [[content-capital-mc-l06-automatizaciones-para-reels-y-posteos]], [[content-capital-mc-l09-mega-arbol-de-manychat]], [[content-capital-mc-l10-automatizacion-de-envio-de-calendario]], [[content-capital-mc-l12-asignacion-de-leads]], [[content-capital-mc-l13-gestion-de-chats]], [[content-capital-mc-l15-nuevo-flujo-para-bienvenidas]], [[content-capital-mc-l17-nuevo-flujo-de-historias]].
- [[content-capital-mc-l14-manychat-claude]] 01:08-03:00 (requisitos y por dónde empezar).
- Relacionadas: [[manychat-bases-y-flujos]] · [[bot-calificador-claude-manychat]] · [[venta-privada-hand-raisers-y-triage]] · [[arsenal-de-ventas-diez-armas]] · [[secuencia-pre-call]].

## Tensiones internas del curso

- **Cuánto automatizar.** MC L1 dice que se puede todo pero no conviene; MC L14 muestra un bot que agenda solo (~4-5 llamadas por día, anécdota). Se concilian si el bot solo agenda a los muy calificados y el setter rescata al resto (MC L14 21:17; inferencia).
- **Quién clasifica.** En MC L9 00:13, sin filtro prefiere preguntas sin botón y que el setter clasifique; en MC L6 los botones setean campos solos.
- **Recurso antes o después del filtro.** Mati lo prefiere después de filtrar (MC L6 10:03); Paolo lo entrega primero porque Meta obliga (MC L16 02:27).
- **Cifras** (90% del trabajo, llamadas por día) son dichos de los instructores.
