---
title: "Content Capital · Programa · ManyChat L14 — Manychat + Claude"
type: source
source_type: course-lesson
course: content-capital
module: "Programa · ManyChat"
instructor: "Paolo"
lesson: 14
duration: "58:49"
date_ingested: 2026-09-25
transcript_path: ~/Documents/Deliverables/General/docs/Content-Capital/transcripts/programa/mc-manychat/14-manychat-claude.md
captures_path: ~/Documents/Deliverables/General/docs/Content-Capital/capturas/programa/mc-manychat/14/
tags: [content-capital, cc-mc, manychat, automatizacion, dm, ia, ventas]
status: active
---

## En una línea

Consultoría en vivo: bot de setting en ManyChat que usa la API de Claude (Sonnet) como **clasificador**, no como redactor. Cada etapa de la estructura de prospección es un flow: recopila la respuesta en un campo, Claude devuelve un JSON con `resultado` (keyword) y `motivo` en otro campo, y ese campo cambiado dispara el flow siguiente (siguiente pregunta, rant según objetivo, caso de éxito, pitch, calendario). Nunca alucina: solo manda mensajes guardados. Ejemplo: mentoría de reparación de crédito. Instructor: **Paolo** (nombrado por un alumno en 30:47 y en la webcam).

## Recorrido de la clase

| Min | Idea |
|---|---|
| 00:00 | Segunda consultoría sobre Claude + ManyChat; esta vez arma un flow desde cero. |
| 01:08 | Requisito: una estructura de prospección que ya convierta (si no, ir a Arquitectura de Ventas). |
| 01:44 | No armar el bot entero de una: empezar por calificar y por el envío de calendario (el cuello de botella es cuánto tarda el setter en mandarlo). |
| 02:41 | Según él, el bot agenda solo ~4-5 llamadas/día; el resto se traba y lo sigue un setter (anécdota). |
| 03:00 | Flows independientes: el setter puede lanzar el bot desde cualquier pregunta. |
| 03:43 | Nicho de ejemplo: mentoría de reparación de crédito (califica solo en estados de EE. UU.). |
| 04:55 | Prompt calificador: se lo pide a Claude ("armame un prompt calificador") y le agrega reglas: "eres un clasificador de leads… ante cualquier duda responde descalificado"; reglas críticas (mexicano que vive en Texas califica). |
| 05:54 | Respuesta del bot en **JSON** en un campo personalizado: `resultado` (keyword) + `motivo`; el motivo sirve para auditar y mejorar. Corrigió el bot "máximo dos veces". |
| 07:28 | Inicio siempre por **keyword**: en el sistema de Ramiro las preguntas de reels/carruseles hacen que el lead responda "digital"; ese dato arranca el bot. |
| 09:04 | Usan el mismo flow para todos los reels; cambian solo la etiqueta. Dos ramas: leads nuevos y leads que ya recibieron una automatización. |
| 10:21 | Disparador palabra clave con "es", no "contiene" (un texto largo con la palabra lo dispararía): "quiero reparar mi crédito". |
| 11:04 | Primera pregunta ("¿de qué estado me escribís?") como recopilación de datos, con retrasos. |
| 12:28 | Anti doble disparo: acción que agrega etiqueta "flow Claude" + condición "si la etiqueta no es flow Claude". |
| 13:19 | Establecer campo "estado del lead" = última entrada de texto. |
| 13:53 | Antes usó ChatGPT; ahora Claude: pegar la API key en Configuración de ManyChat (dice que carga desde USD 5). |
| 14:23 | "Realizar solicitud" con Sonnet 4.6 ("no más de 10 dólares al mes"), prompt calificador, último mensaje = campo estado; resultado a un campo nuevo "califica abridor". |
| 16:19 | Guardar la keyword positiva ("EstadoCalificadoPositivo"); temperatura 0,3 (la mejor en sus pruebas), máx. 500 tokens. Si descalifica, el bot no sigue: no alucina. |
| 17:19 | Flow 2: disparador "evento de contacto: campo personalizado cambiado" = califica abridor **contiene** la keyword (porque también trae el motivo). |
| 18:32 | Pregunta 2: "perfecto, saludos por allá… comentame, ¿tu crédito cómo anda? ¿cuánto te está dando el score?" → campo "respuesta crédito" → Claude con prompt de rangos → campo "califica score" → "ScoreCalificadoPositivo". |
| 21:17 | No calificar ≠ no atender: el bot solo agenda solo leads muy calificados; el setter puede rescatar los descalificados. |
| 25:07 | Pregunta 3 (objetivo): "con la estrategia correcta hay mucha oportunidad de mejorar ese score. Arreglar tu crédito, ¿para qué lo necesitás exactamente? ¿casa, carro, o sacarte deudas de encima?". |
| 26:10 | Ramificación: el bot ya no califica, **elige qué rant enviar**. Extender a rants solo cuando ya tenés 4-5 rants específicos. |
| 27:05 | Campo "cuál ranteo crédito" → Claude devuelve CalificadoRanteoCasa / Auto / Deudas / Tarjetas; no son keywords literales, interpreta sinónimos; jerarquía si nombra dos objetivos (el más fácil de rantear). |
| 30:47 | Pregunta de un alumno: ¿usa mis audios ya grabados? Sí: el bot nunca redacta, solo dispara la automatización guardada (cada rant = un flow disparado por su keyword en el campo). |
| 34:22 | Crea el flow "ranteo auto": disparador campo "ranteo específico crédito" contiene "CalificadoRanteoAuto"; rant en varios mensajes (texto y audio). |
| 37:26 | Prueba en vivo desde su Instagram (borra su contacto para reiniciar): Texas → calificado; score 400 → calificado ("rango muy bajo, ideal para la reparación"). |
| 40:02 | Varios abridores: el bot no necesita arrancar desde el inicio; el setter lo lanza desde la pregunta que quiera. |
| 41:58 | Es un bot determinista "como un bot de banco": solo manda lo guardado; si el lead contesta otra cosa, no responde y lo deja descalificado. |
| 44:07 | Caso de éxito: no pasa por Claude tras el rant (siempre van conectados); pausa inteligente de 10 s. Termina en "¿te gustaría lograr algo similar?". |
| 46:45 | Claude decide si está listo para el pitch ("ListoParaPichearPositivoCredito"; ante duda, no). |
| 49:34 | Pitch: "si te parece, agendamos una llamada… armamos un plan detallado para mejorar tu crédito, te paso calendar". |
| 51:18 | Claude califica la respuesta al pitch ("ok, dale, sí, de una, mandame" = positivo; ante duda o evasivas, no) → "ListoCalendarPositivoCredito" → flow calendario ("acá te envío el calendario, avisame así le doy prioridad"). |
| 55:39 | Prueba completa: "de una" lo toma como positivo y manda el link. |

## Frameworks que aparecen

- [[guionado-iterativo-con-ia]] (Claude arma el prompt calificador)
- [[venta-privada-hand-raisers-y-triage]] (preguntas de calificación)
- [[arsenal-de-ventas-diez-armas]] (rant, caso de éxito, pitch)
- [[gohighlevel-stack-crm]] (la misma idea de bot calificador en GHL)
- Framework del curso: [[bot-calificador-claude-manychat]] · [[manychat-setting-automatizado]]

## Ejemplos mostrados en pantalla

- **06:30 / 15:30** — Documento "Mentor de crédito Estructura" y modal "Editar Acciones de Claude": "5. RESPUESTAS FUERA DE CONTEXTO: si responde algo que no es una ubicación ('quiero mejorar mi crédito', 'tengo deudas', 'me urge'), descalificar"; "RESPUESTA: Responde ÚNICAMENTE en formato JSON sin texto adicional: {"resultado": "EstadoCalificadoPositivo", "motivo": "[máximo 10 palabras]"} / {"resultado": "descalificado", …}"; campos "Último mensaje del usuario: ESTADO DEL LEAD", "Guardar resultado en: Respuesta de Claude", tokens máximos 500.
- **18:30 / 21:30** — Prompt calificador del score: "Eres un clasificador de leads para una mentoría de reparación de crédito. Analizas la respuesta a '¿Tu crédito cómo anda? ¿Cuánto te está dando el score?'…"; CALIFICA SI: 300-670 directo (cliente ideal), 671-720 con margen; DESCALIFICADO AUTOMÁTICO: score alto (721+, "está excelente"), sin archivo de crédito ("no tengo crédito", "acabo de llegar a EE.UU.", "soy ITIN"), respuestas evasivas ("no sé", "ni idea", "luego te digo").
- **30:30 / 33:30** — Prompt de rants: "TIMELINE NO IMPORTA"; salida JSON con CalificadoRanteoCasa / Auto / Deudas / Tarjetas / descalificado; texto del "RANTEO CASA" (préstamo más caro por score bajo).
- **38:13 / 39:30** — Prueba en el DM: "Quiero reparar mi crédito" → "cómo vas? contame así te doy una mano, de qué estado me escribís?" → "comentame, tu crédito cómo anda?…" → "400" → "con la estrategia correcta hay mucha oportunidad…".
- **42:30** — Bandeja con el campo "CALIFICA SCORE" actualizado: "resultado ScoreCalificadoPositivo, motivo: score 400, rango muy bajo, ideal para reparar".
- **45:30** — Caso de éxito "CASO DE ÉXITO AUTO" (cliente ficticio de Houston, score de 530 a 710 en 4 meses) + "¿te gustaría lograr algo similar?".
- **48:30** — Prompt del calendario: "CALIFICA SI: cualquier tipo de respuesta positiva como Ok, dale, sí, de una…"; "SI HAY DUDA O RESPONDEN SI, PERO… NO LO CALIFIQUES"; resultado "ListoParaPichearPositivoCredito".

## Tareas y herramientas

- Conectar la API de Claude en ManyChat (13:53).
- Por etapa: recopilación → campo de respuesta → Claude (Sonnet, temp 0,3, 500 tokens, JSON) → campo de resultado → flow disparado por "campo cambiado contiene keyword".
- Herramientas: ManyChat, Claude API (Sonnet), Claude para redactar los prompts.

## Citas clave

- Es "un bot determinista como un bot de banco". (42:03)
- "Nunca va a alucinar." (42:28)

## Lo que no se procesó

- La API key y la configuración de cuenta no se muestran (correcto no registrarlas).
- Costos (USD 5, ≤USD 10/mes) y llamadas/día del bot son dichos del instructor.
- Los prompts completos se leen solo en parte; aquí se resumen.
- El caso de éxito es inventado para el ejemplo; el nicho de crédito no es su especialidad (lo aclara, 04:03).
