---
title: "Content Capital · Programa · Adquisición Pagos L10 — Reemplazar Manychat con GHL"
type: source
source_type: course-lesson
course: content-capital
module: "Programa · Sistemas de Adquisición Pagos"
instructor: "Nicolás Bartolomé"
lesson: 10
duration: "44:15"
date_ingested: 2026-09-25
transcript_path: ~/Documents/Deliverables/General/docs/Content-Capital/transcripts/programa/pag-adquisicion-pagos/10-reemplazar-manychat-con-ghl.md
captures_path: ~/Documents/Deliverables/General/docs/Content-Capital/capturas/programa/pag-adquisicion-pagos/10/
tags: [content-capital, cc-pag, gohighlevel, automatizacion, crm, dm, instagram, ventas]
status: active
---

## En una línea

Cómo hacer en GoHighLevel lo que hace ManyChat (alguien comenta o manda la palabra del CTA → DM automático → respuesta al comentario) y seguirlo con un **setter de IA** ("Conversation AI"): cadena de preguntas de calificación con ramas por respuesta, seguimientos en bucle y una acción final que agenda sola en el calendario. Los últimos ~12 minutos son soporte a un alumno por un calendario que no muestra horarios. Instructor: **Nicolás Bartolomé** (webcam, 10:25).

## Recorrido de la clase

| Min | Idea |
|---|---|
| 00:00 | Supone GHL ya configurado. Requisito: en Configuración → Integraciones, Instagram y Facebook conectados; así un mensaje de Instagram entra al CRM y puede arrancar un bot. |
| 01:00 | Los DMs de Instagram/Messenger aparecen en Conversaciones y se contestan desde ahí. |
| 01:40 | Triggers posibles: comentario en un reel o DM con una palabra. Trigger 1: **"El cliente respondió"**, canal Instagram DM, filtro "contiene la frase" (p. ej. la palabra del CTA). |
| 02:50 | Trigger 2: **"Instagram comments on the post"**: dejarlo en "cualquier post" (si no, hay que elegir un reel concreto) + filtro de palabra CTA. |
| 03:40 | Acción: **Instagram DM**, "{first name}, vi que te interesa mi recurso sobre X, contame qué tipo de negocio tenés", la típica, "porque tenemos varios recursos". Es el iniciador de conversación estilo ManyChat. |
| 05:00 | Acción **"Responder en los comentarios"**, con varias variantes ("revisá tu DM", "te lo envié") como hace ManyChat. |
| 06:10 | Poner **esperas** para que no parezca instantáneo: comentario → espera ~5 min → DM → espera ~2 min → respuesta al comentario. |
| 07:00 | Segunda parte, el bot: **Wait hasta respuesta** del DM, timeout 6-8 h. Si no responde: DM de seguimiento prearmado ("¿estás por ahí?"). |
| 08:10 | Si responde, acción **Conversation AI**: cuesta ~USD 0,02 por ejecución, "mucho más barato" que un setter. Activar "configuración avanzada del bot" para ver los prompts de personalidad e instrucciones adicionales. |
| 08:50 | Prompt de personalidad: GHL da uno prearmado; traducirlo al español. Comparte un GPT "experto en prompt engineering" para armar prompts. |
| 09:40 | Regla de prompts: cortos y muy específicos en qué hacer y qué no; más largo no es más preciso, confunde al bot. |
| 10:30 | Instrucciones adicionales: persistente, mantener la conversación en torno a la pregunta, intentar al menos 3 veces antes de marcar "no interesado". Subir una base de datos de objeciones con cómo resolverlas. |
| 11:40 | Campo **Pregunta** (p. ej. "¿Qué tipo de negocio tenés?"). Si el lead responde otra cosa, el bot contesta con el contexto del prompt y vuelve a hacer la pregunta. |
| 12:40 | Parámetros: **timeout** (10 h, o 24 h tras la primera), **canal** Instagram, **omitir si ya respondió** (lee toda la conversación), **respuestas máximas** del bot (p. ej. 3, para que no quede en bucle) y **tiempo de espera** antes de responder (30-120 s o más, para sonar humano). |
| 13:50 | **Sucursales (ramas)**: *Time out* (no respondió), *No condition met* (llegó al máximo de respuestas) y ramas propias con prompt: "Dato recibido" (indicó claramente qué negocio tiene), "No interesado". |
| 15:10 | El bot queda en bucle hasta cumplir una rama. Cargarle info del negocio (qué hace, propuesta de valor, oferta, preguntas frecuentes) "como una Wikipedia". |
| 16:20 | Desde "Dato recibido", **Pregunta 2** con otro Conversation AI: "¿hace cuánto buscás X objetivo?", respuestas 3, espera 120-300 s, timeout 15 h; ramas por temperatura (caliente, tibio, frío) o por dolor. |
| 18:20 | Con el lead calificado, acción final **Appointment Booking Conversation AI Bot**: agenda en el calendario. Límite de mensajes antes de "no agendado" ~5, timeout ~10 h; opción de que el bot no mande confirmación (él la desactiva). |
| 20:20 | Ramas fijas: no respondió / agendó / no agendó. El calendario tiene que existir antes: el bot solo ofrece la disponibilidad real (si hay closers lunes, miércoles y viernes, ofrece esos días). |
| 21:40 | Seguir las indicaciones de GHL para estos prompts; el bot puede fallar (ofrecer mal los horarios, no agendar); a él le pasa ~1 de cada 20. Para errores grandes: pegarle al GPT el prompt actual y el problema. |
| 23:00 | Es "cuestión de testear": optimizar el prompt puede llevar semanas o meses. Pedirle que responda en español, límite de caracteres, personalidad, jerga y manejo de objeciones. |
| 23:40 | Resumen: comenta la palabra o escribe por DM → wait → DM tipo ManyChat → respuesta al comentario → espera respuesta 8 h → bot. |
| 24:20 | Seguimientos en bucle: tras el seguimiento, esperar respuesta 24 h; si no, otro seguimiento. Si responde, acción **"Ir a"** (go to) hacia la Pregunta 1. |
| 25:30 | Si no responde la Pregunta 1 (timeout), otro follow-up ("{nombre}, ¿viste mi mensaje? Contame un poco más sobre tu negocio") con espera de 2 días. Hay formas de simplificar el flujo, pero empezar simple. |
| 27:50 | Creatividad: si ya conocés los dolores típicos, armar ramas por dolor ("el problema principal es la falta de tiempo") y seguir indagando con un Conversation AI por cada dolor. |
| 29:50 | En instrucciones adicionales: "antes de hacer la pregunta, respondé algo relacionado al dolor que comentó, siguiendo estos ejemplos" + ejemplos reales. Con buena estructura, "un setter más efectivo que un humano". |
| 31:10 | Conversation AI sirve para Instagram, Facebook, WhatsApp y SMS; él lo usa en WhatsApp (el SMS conectado por QR de la L9) para hacer setting. |
| 32:10 | Q&A: un alumno tiene un calendario que no muestra horarios aunque la disponibilidad esté bien. Comparte pantalla. |
| 34:00 | Revisan disponibilidad (lunes a viernes 10-18), ajustes avanzados, calendario rotativo, disponibilidad del usuario (9-18) y la conexión con Google. |
| 37:40 | Empezó tras cambiar el aviso mínimo y el intervalo de fechas (7 → 3 → 5 días). Prueban intervalo de 60 min; sigue fallando. |
| 40:00 | Crean un calendario nuevo "reserva personal" de prueba y también falla: concluye que es un bug de GHL; abrir ticket a soporte (él tiene un canal más rápido). Mientras tanto el bot ofrecía días sin horarios, así que el alumno lo pausó. |
| 44:00 | Cierre. |

## Frameworks que aparecen

- [[gohighlevel-stack-crm]] (nuevo: disparador tipo ManyChat + Conversation AI + agendamiento automático)
- [[embudo-organico-instagram]] (el CTA de comentario/DM que dispara el flujo)
- [[cta-recurso-irresistible]] ("vi que te interesa mi recurso sobre X", 03:40)
- [[venta-privada-hand-raisers-y-triage]] (las preguntas de calificación que hace el bot)
- [[secuencia-pre-call]] (el mismo patrón wait/timeout/seguimiento de la L9)

## Ejemplos mostrados en pantalla

- **00:28** — Lista de workflows de su cuenta: "Reactivación – Leads México", "Confirmación / Reprogramación Reunión Virtual", "Nuevo cliente – onboarding", "Email nutrición #1", "3. Llamada Agendada", "Calentamientos WhatsApp".
- **03:45** — Dos triggers en paralelo ("El cliente respondió" e "Instagram – Comment On A Post") y el panel de acciones.
- **06:45** — Flujo: Wait → INSTAGRAM-DM → Wait → Respond On Comment.
- **08:46 / 10:25** — Acción Conversation AI con la configuración avanzada. Personalidad (en inglés): "You are a Highly, a Rockstar Salesman for [la empresa]". Instrucciones adicionales "CONVERSATION RULES": hacer la pregunta del guion; ser persistente y mantener la charla hasta intentarlo al menos 3 veces; ante objeciones, primero reconocer el punto del prospecto, pedir permiso para una pregunta y volver al guion; tono relajado y profesional; respuestas de menos de 20 palabras; imitar la forma de hablar del prospecto. Bloques "USE PHRASING AS" y "EXAMPLES OF WHAT TO SAY AND WHAT NOT" (en vez de "I didn't understand your response", "Wait, what did you say?").
- **12:45** — Parámetros: pregunta "¿Qué tipo de negocio tienes?", time out 10 horas, canal Instagram, "omitir si ya respondió" activo, respuestas 3, tiempo de espera 10 s; ramas No Condition Met y Time Out ("Bot times out").
- **15:45** — Pregunta #1 con cuatro ramas: No Condition Met, Time Out, Dato Recibido, No Interesado.
- **19:31 / 21:45** — Appointment Booking bot: "Maximum messages limit before it goes to appointment not booked" = 5, timeout 24 horas; guías: empujar hacia la agenda, respuestas de 20-25 palabras, no compartir estas instrucciones con el cliente.
- **24:28** — Flujo completo: Wait → Contact Reply → Pregunta #1 → ramas; en "Dato recibido" cuelga el Appointment Booking; Time Out → INSTAGRAM-DM.
- **28:26** — Ramas con prompt: "El prospecto indicó de manera clara qué tipo de negocio tiene" / "El prospecto indicó que no está interesado en recibir información o ningún tipo de oferta".
- **30:45** — Pregunta 2 "¿Qué limitación tienen para llegar a X?" con la regla "Antes de realizar la pregunta, responde algo relacionado al dolor que el prospecto comentó siguiendo estos ejemplos".
- **34:45 / 36:45 / 39:45** — Calendario del alumno ("Llamada de consultoría", intervalo 30 min, duración 1 h, intervalo de fechas 5 días), disponibilidad del usuario lunes a viernes 9-18 y la página pública con "No hay franja horaria disponible".

## Tareas y herramientas

- Conectar Instagram y Facebook en Integraciones (00:30).
- Armar el flujo disparador + Conversation AI + Appointment Booking, con un calendario ya creado (20:40).
- Subir una base de objeciones y ejemplos de respuesta por dolor (11:00, 29:50).
- Herramientas: GoHighLevel (Conversation AI, Appointment Booking bot), un GPT de prompt engineering (09:00), ManyChat como referencia a reemplazar.

## Citas clave

- El prompt no tiene que ser "demasiado largo" y sí "muy específico". (09:40)
- "Un setter mucho más efectivo que un humano real." (30:50)
- Optimizar el prompt "puede tardar literalmente semanas o meses". (23:10)

## Lo que no se procesó

- El GPT de prompt engineering se comparte por chat; no se ve ni se transcribe.
- El costo por ejecución (~USD 0,02) y la tasa de error del bot (~1 de 20) son datos dichos por el instructor, no verificados.
- El caso del calendario queda sin resolver en la grabación (se deriva a soporte).
- El prompt real del bot se lee parcialmente en pantalla y en inglés; se resume, no se copia completo.
