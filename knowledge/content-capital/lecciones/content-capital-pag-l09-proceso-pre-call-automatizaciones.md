---
title: "Content Capital · Programa · Adquisición Pagos L9 — Proceso Pre-Call + Automatizaciones"
type: source
source_type: course-lesson
course: content-capital
module: "Programa · Sistemas de Adquisición Pagos"
instructor: "Nicolás Bartolomé"
lesson: 9
duration: "1:18:07"
date_ingested: 2026-09-25
transcript_path: ~/Documents/Deliverables/General/docs/Content-Capital/transcripts/programa/pag-adquisicion-pagos/09-proceso-pre-call-automatizaciones.md
captures_path: ~/Documents/Deliverables/General/docs/Content-Capital/capturas/programa/pag-adquisicion-pagos/09/
tags: [content-capital, cc-pag, gohighlevel, automatizacion, crm, anuncios, vsl, ventas]
status: active
---

## En una línea

Clase en vivo (grabación de Zoom) donde se arma en GoHighLevel el **workflow que corre cuando alguien agenda**: aviso interno al closer → envío del agendamiento a Meta por la API de Conversiones, solo si el lead califica → WhatsApp de confirmación → espera de respuesta → recordatorios 1 día y 2-3 horas antes → pedido de "sí/no" y envío del link. La segunda mitad es consultoría a alumnos (subdominio de email, secuencia de nutrición, formulario que miente, estructura de campañas). Instructor: **Nicolás "Nico" Bartolomé** (así lo llaman los alumnos, 42:45).

## Recorrido de la clase

| Min | Idea |
|---|---|
| 00:00 | Tema: el proceso pre-call, qué pasa cuando el lead agenda. GoHighLevel (GHL) reemplaza Calendly, Zapier, ClickFunnels, Typeform: todo integrado, "10 veces más fácil" disparar automatizaciones. |
| 02:00 | Recomienda ver las clases previas de GHL (calendario, landing). Plan: lógica de automatizaciones, acciones más usadas y dos automatizaciones de cero: subir el % de asistencia y mejorar la campaña de anuncios. |
| 03:00 | GHL trae plantillas (appointment confirmation, reminder, survey, booking); él las hace de cero para personalizarlas. |
| 03:40 | Lógica: **trigger** (lo que tiene que pasar: se agenda una llamada, entra un lead, se completa un formulario, o algo externo) + **acciones** (mandar WhatsApp, email, notificación interna al closer). Hay "10.000 acciones": probarlas todas. |
| 05:20 | Objetivo del caso: al agendarse, mandar mensajes automáticos por WhatsApp para que setter o closer no tengan que hacerlo. |
| 05:50 | GHL no tiene WhatsApp directo salvo por la API oficial de Meta, con muchas limitaciones. Recomienda integraciones pagas que simulan el SMS. |
| 06:45 | Opciones: AppLevel (USD 49/mes; él tiene 6-7 cuentas activas con clientes), Wazzap (de un equipo mexicano, ~USD 39, 5 días gratis, algo más difícil de conectar) y una tercera de USD 29 que no recomienda. |
| 08:20 | Por qué no la API oficial: hay que cerrar el WhatsApp del celular y operarlo desde GHL; y funciona con **ventana de 24 h**: si el lead no responde, solo podés mandar plantillas, no mensajes libres. Él usa la API en una cuenta y es "mucho más viaje"; cuesta USD 10 en GHL. Solo conviene con volumen muy alto. |
| 10:00 | Estas integraciones se conectan por QR y admiten hasta 5 WhatsApp (uno por closer). En Configuración → Números de teléfono → avanzado se elige el proveedor de SMS = WhatsApp. Consecuencia: con WhatsApp conectado no se pueden mandar SMS reales. |
| 11:50 | Con ese setup hizo una reactivación automática de ~100 leads por WhatsApp. |
| 12:10 | Trigger: **"Cita reservada por el cliente"** (*customer booked appointment*), con filtro "en el calendario" = el calendario creado antes en GHL. |
| 14:10 | Muestra su propio workflow real y lo va rearmando de cero. |
| 14:45 | Acción 1: **notificación interna** por email (SMS no funciona con WhatsApp). Destinatario: *assigned user* (el closer asignado) o *custom email* (uno mismo). Asunto "Nueva llamada" + campos del contacto y campos personalizados del formulario (p. ej. "¿puede invertir?"). |
| 15:50 | Para emails hay que configurar un subdominio dedicado (se ve más adelante). |
| 17:40 | Acción 2: **Facebook Conversion API**, para quienes corren anuncios. Mandar a Meta solo los datos de leads que califican, así optimiza la campaña del VSL hacia ese perfil: llamadas "más calificadas y más baratas". |
| 19:00 | Anécdota: con VSL llegó a llamadas agendadas a USD 3-5, y ~90% calificadas. |
| 19:40 | En Meta: Administrador de eventos → el píxel → Configuración → "Generar identificador de acceso" (token). Guardar el token y el ID del píxel. No recomienda conversiones personalizadas; la API registra mejor. |
| 21:10 | En el conjunto de anuncios, evento de conversión = agendamiento ("programar"). |
| 21:40 | En GHL, acción FB Conversion API: tipo *Funnel event* (landing → VSL → agenda) o *Lead event* (formulario sin calendario). Pegar token e ID del conjunto de datos; nombre del evento = **Schedule**. El valor es opcional. |
| 23:30 | Filtro previo con la acción **condicional (if/else)**, "Build your own": rama "Sí" si el campo "¿puede invertir?" es "sí"; rama "No" (ninguna condición) no se envía. |
| 26:00 | Muestra el formulario del calendario con la pregunta de presupuesto. |
| 27:00 | Se pueden encadenar condicionales (tiene presupuesto → es dueño de la empresa → recién ahí API). Pero no poner "87 filtros": con pocos datos Meta no optimiza; buscar balance calidad-volumen. |
| 29:00 | Acción 3: **WhatsApp de confirmación** (la acción se llama SMS). Sirve también para setters que prospectan por Instagram y mandan el link del calendario de GHL. |
| 29:50 | Texto armado con variables: "Hola {first name}, mi nombre es {nombre del usuario asignado} y recibí la solicitud de tu llamada para {start date time}". Se puede adjuntar video del closer, audio o imagen. Mejor partir en dos mensajes cortos. |
| 31:50 | Su versión real: no filtra antes de la API porque en su embudo "los que agendan son calificados"; manda mail a él, mail al lead y WhatsApp: "recibí tu llamada para [fecha], por favor confirmá tu asistencia respondiendo este mensaje". |
| 33:00 | Acción **Wait → hasta que el contacto responda** (al WhatsApp de confirmación), con timeout de 15 horas. Dos ramas: *Contact reply* / *Time out*. Si no responde: follow-up "recordá que si no podemos confirmar tu llamada...". |
| 34:10 | Recordatorios: si un lead agenda para el viernes y no le hablás en días, se olvida. Confirmación + recordatorios son clave para el % de asistencia. |
| 35:00 | Wait basado en la cita: **1 día antes** → WhatsApp "Hola {nombre}, nos vemos mañana a las {start time}". Puede sumar un video de preparación o de testimonios. |
| 37:00 | Copiar la acción y ajustar: **2-3 horas antes** → "nos vemos hoy...". |
| 37:50 | Más avanzado: usar IA (GPT) para saber si el lead confirma, reprograma o cancela; queda para otro día. |
| 39:00 | Versión simple: pedir "confirmá con sí o no" y condicional **"Contact reply intent type = positivo"**. Si es positivo, mandar el link de la reunión (*appointment meeting location*, con Google Calendar, Outlook, Apple o Zoom conectado) y notificar al closer "{nombre} va a asistir". |
| 42:40 | Q&A: un alumno pregunta si siguen los mensajes cuando el lead responde. Sí; si se quiere cortar, Configuración → "detener en respuesta", que no recomienda en este flujo. |
| 44:00 | Las dos acciones de WhatsApp son "SMS". Sin WhatsApp, usar la acción **Email** (no la notificación interna), que requiere el subdominio. |
| 45:20 | Él manda al lead a una **página de gracias** con video de preparación ("tu llamada fue agendada con éxito, pero es necesario que sigas estos pasos..."). No todos la ven, así que el recordatorio repite "mirá este video antes de la llamada". |
| 48:00 | Sin automatización, todo es manual: estar pendiente de responder al toque; cuanto más tarde, menos asistencia. Paga los USD 40 de la integración. |
| 49:00 | Consultoría a un alumno: tiene landing + VSL en GHL con avisos a Discord por webhook; quiere una secuencia de emails. Recomienda la página de gracias como extra (nutrir con testimonios, el servicio por dentro) y WhatsApp "100%". |
| 52:00 | Emails recurrentes o secuencias: desde Automatizaciones, no desde campañas de Marketing (esas son de un envío). No se puede importar un flujo de ActiveCampaign; se rehace. |
| 54:30 | Nutrición en paralelo: un workflow aparte con el mismo trigger, así el lead entra a recordatorios y a nutrición a la vez. |
| 55:50 | Wait inicial (~30 min) con **ventana avanzada**: enviar solo lunes a sábado de 9 a 20 h; si es fuera de horario, espera al día siguiente. Útil para seguimientos (no mandar a las 4 de la mañana). Luego email → espera 1-3 días → email. |
| 58:00 | Subdominio: Configuración → Servicio de correo electrónico → dominios dedicados. GHL da uno por defecto, pero conviene uno propio: un subdominio tipo "info." del dominio de la empresa (no el dominio principal), cargar los registros que da GHL en el proveedor y mandar desde nombre@info.dominio. |
| 62:00 | Otro alumno: no toma llamadas el fin de semana. Opciones: dos calendarios, o bajar presupuesto o pausar campañas el fin de semana (automatizable en Meta). |
| 63:00 | "La gente miente en el formulario" (dice no tener la inversión y sí la tiene). Solución: preguntar por **rangos** sin revelar el mínimo, y calificar según el rango. |
| 65:40 | Informes: Reporting → Appointment report (agendadas, confirmadas, canceladas, asistidas, no asistidas). |
| 66:30 | El alumno filtra con if = "no incluye 'no cuento con ese capital'". ~18 llamadas a < USD 5 c/u. Alternativa: mandar la API cuando el lead se mueve a la etapa "calificado" del pipeline tras la llamada; pero con 15-30 datos al mes no alcanza (con USD 1.000 serían ~200). |
| 68:40 | Métrica principal en campañas de agendamiento: **costo por llamada**; antes miran CTR, frecuencia y % de visualización, pero él se fija "únicamente" en el costo por llamada. |
| 69:40 | Revisión de la campaña del alumno: un conjunto a ~3.000 pesos por llamada y otro a ~15.000 (5 veces más): apagar el caro. Escalar ~20% cada 2 días, no de golpe. |
| 72:00 | Un anuncio por conjunto (6 conjuntos) no hace falta: Meta ya concentra el presupuesto en 1-2 anuncios. Propuesta: dejar los que funcionan, apagar el resto y crear un conjunto **Advantage+** con los 3 mejores creativos; empezar con ~5.000 pesos/día y subir. |
| 76:30 | Otro alumno segmenta por intereses; Nico dice que ~8 de cada 10 veces le rindió más Advantage+, aunque tiene un conjunto por puestos laborales (dueños) que funciona. Cierre. |

## Frameworks que aparecen

- [[secuencia-pre-call]] (nuevo: el workflow completo desde el agendamiento hasta la llamada)
- [[configuracion-meta-business-y-pixel]] (nuevo: mandar a Meta solo agendamientos calificados)
- [[metricas-de-la-tuberia-de-negocio]] (show rate y costo por llamada; el pre-call es el tramo que protege la asistencia)
- [[venta-privada-hand-raisers-y-triage]] (filtro de calificación y preguntas de rango, 63:00)
- [[estructura-del-vsl]] (la página de gracias con video como extensión del VSL, 45:20)

## Ejemplos mostrados en pantalla

- **00:45** — Grilla de Zoom con alumnos (no se transcriben nombres).
- **06:45** — Web de AppLevel: "Fully replace SMS with WhatsApp & OpenAI, today", "Connect up to 5 devices per GHL subaccount".
- **09:45** — Lista de workflows de la cuenta de su agencia: "1. Facebook CAPI: Lead" (346 inscritos), "2. Nuevo Lead | No Agendó" (325), "3. Llamada Agendada" (58), "Accesos curso venta", "Calentamientos WhatsApp", "Confirmación / Reprogramación Reunión Virtual", "Contactos que no tienen wpp". Muestra que separa flujos por etapa del lead.
- **12:45** — Panel "Activador de flujo de trabajo" buscando "cita" → "Cita reservada por el cliente".
- **15:46** — Acción Internal Notification: tipo Email, nombre "Nueva llamada", tipo de usuario, asunto y plantilla.
- **21:45** — Acción "FB Conversion API": tipo de evento *Funnel Event / Lead Event*, ID del píxel, nombre del evento de Facebook, valor, moneda USD.
- **24:35 / 25:36 / 26:56** — Condición "¿Tiene presupuesto?": ramas "Sí" (campo "¿Puede invertir?" = "Sí") y "No"; la lista de campos muestra "¿Sos dueño de una empresa o negocio solo?". El árbol queda: trigger → condición → FB Conversion API → Internal Notification.
- **31:02** — Acción SMS "WhatsApp Confirmación": "{{contact.first_name}}, mi nombre es {{appointment...name}} y recibí la solicitud de tu llamada", con el menú de variables de *Appointment* (Start Date Time, Start Time, End Time, Day of the week).
- **33:45 / 42:45 / 45:45** — El flujo armado: WhatsApp Confirmación → Wait (Contact Reply / Time Out 15 hour) → rama sin respuesta: SMS y END; rama con respuesta: Wait → "Recordatorio – 1 día antes" → Wait → "WhatsApp – Recordatorio 2hs antes" → "¿Respondió positivamente?".
- **37:56** — SMS con "Hola {{contact.first_name}}! Nos vemos hoy para..." y botón "Añadir archivo adjunto".
- **39:45** — Condición "¿Yes?" con fórmula "Build your own".
- **50:28 / 54:45 / 57:45** — Cuenta de un alumno: Marketing por correo electrónico (campañas vacías) y un workflow nuevo en blanco en la carpeta "Email Marketing".
- **60:45** — "Configure el dominio manualmente añadiendo los siguientes registros": tabla con registros TXT, CNAME y MX para el subdominio (valores de Mailgun), y el aviso de usar un subdominio, no el dominio principal.
- **66:33** — Execution Logs de un workflow del alumno: por contacto se ve "Add to workflow → Califica → FB Conversion API → Removed by End Of Workflow".
- **70:02 / 72:45** — Ads Manager del alumno, columnas "VSL FUNNEL Métricas": 6 conjuntos "BROAD IG" con 1-5 resultados "Website schedule" y costos por resultado de ~3.000 a ~15.000 pesos; a nivel anuncio, 6 anuncios con hooks tipo "Es imposible crecer tu carrera como...".

## Tareas y herramientas

- Conectar WhatsApp a GHL con una integración (AppLevel o Wazzap), no con la API oficial salvo volumen alto (06:45-09:40).
- Armar el workflow "llamada agendada" (trigger → notificación → CAPI con filtro → confirmación → recordatorios → sí/no → link).
- Configurar un subdominio de envío propio (58:00).
- Crear una página de gracias con video de preparación (45:20).
- Herramientas: GoHighLevel, Meta Events Manager / Ads Manager, AppLevel, Wazzap, Google Calendar / Zoom, Discord por webhook, Mailgun (visto en los registros), ActiveCampaign (mencionado).

## Citas clave

- "La idea es buscar un balance entre que sean calificados, pero darle a Facebook cierto volumen." (28:30)
- Mientras más tardás en responder, "menos porcentaje de asistencia". (48:20)
- Se fija "únicamente en el costo por llamada". (69:10)

## Lo que no se procesó

- Las cifras (llamadas a USD 3-5, 90% calificadas, 6-7 cuentas de AppLevel, precios de las integraciones) son anécdotas y precios dichos en vivo, no verificados.
- La parte de IA para detectar reprogramaciones o cancelaciones se menciona y se deja para otra clase (37:50).
- El workflow de Discord por webhook del alumno no se explica (él no recuerda cómo lo armó).
- Nombres de alumnos y de contactos que aparecen en Zoom y en los logs se omiten a propósito.
- La transcripción dice "Goja Level", "lápí/API", "zamada" (llamada); se corrigió por contexto.
