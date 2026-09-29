---
title: "Secuencia pre-call: confirmación y recordatorios (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-pag-l09, cc-pag-l07, cc-pag-l15, cc-ven-l10, cc-ven-l06, cc-ven-l07]
source_count: 6
created: 2026-09-25
updated: 2026-09-26
tags: [content-capital, cc-pag, framework, checklist, plantilla, automatizacion, gohighlevel, llamada-de-venta, metricas]
status: developing
---

## En una línea

Un workflow que corre solo apenas alguien agenda: aviso al closer, WhatsApp de confirmación, seguimiento si no responde, recordatorio el día anterior y 2-3 h antes, y link de la llamada cuando confirma. Existe para **subir la asistencia sin trabajo manual**.

## Qué es y por qué funciona (según el curso)

- Lógica de GHL: un trigger + acciones ([[content-capital-pag-l09-proceso-pre-call-automatizaciones|PAG L9]] 03:40). Trigger: "Cita reservada por el cliente", filtrado por calendario (L9 12:10).
- Por qué: si alguien agenda para el viernes y nadie le habla, se olvida. Hacerlo a mano obliga a responder al instante, y cuanto más tardás, menos asistencia (L9 34:10, 48:00).
- **Versión manual (Arquitectura de Ventas).** [[content-capital-ven-l10-proceso-pre-call|VEN L10]] (Mati Molina) enseña la misma secuencia hecha a mano por cada closer desde WhatsApp Business. El principio es igual: contactar "con el lead lo más caliente posible", apenas agenda; algunos equipos tienen gente full time esperando agendas (01:00). Meta: show up 75-85% (01:00, 05:03; cifra hablada).
- **Por qué agendó**: sin un dolor claro, no se presenta; hay que preguntarlo ([[content-capital-ven-l06-armado-de-tuberia|VEN L6]] 11:00).
- WhatsApp: GHL solo trae la API oficial, que cierra el WhatsApp del celular y tiene ventana de 24 h (si no responde, solo plantillas). Nico Bartolomé usa un conector externo por QR (~USD 39-49/mes según el curso), hasta 5 números (uno por closer), configurado como proveedor de SMS: la acción "SMS" pasa a mandar WhatsApp y ya no se pueden mandar SMS reales (L9 05:50-11:50). La API oficial, solo con volumen muy alto.

## Cuándo usarlo / cuándo no

- **Siempre** que haya calendario de llamadas, venga de anuncio, de VSL, de DM o de webinar.
- **Sin WhatsApp**: usar la acción Email (no la notificación interna), con subdominio propio tipo `info.dominio` y registros TXT/CNAME/MX (L9 58:00).
- **Manual (VEN L10)**: cuando no hay GHL o el closer quiere llevar la conversación él mismo; exige responder apenas entra la agenda.
- **Webinar**: la secuencia del día del evento es otra (mañana, 2 h, 30 min, "arrancamos"), ver [[embudo-de-webinar-a-llamada]].

## Pasos

1. **Trigger**: cita reservada en el calendario ___ (L9 12:10).
2. **Aviso interno** por email al usuario asignado (closer) o a uno mismo: asunto "Nueva llamada" + respuestas del formulario (L9 14:45).
3. **Evento a Meta** solo si califica (if/else sobre el campo del formulario). El detalle vive en la página de píxel y API de conversiones del curso (L9 17:40-28:30).
4. **WhatsApp de confirmación**: dos mensajes cortos; se puede adjuntar un video o audio del closer (L9 29:50-32:46).
5. **Esperar respuesta** con timeout de 15 h; si no responde → seguimiento (L9 33:25-33:51).
6. **Recordatorio 1 día antes**, relativo a la cita, con video de preparación o testimonios (L9 35:00-36:01).
7. **Recordatorio 2-3 h antes** (L9 37:34).
8. **Pedir "sí o no"**; condicional *reply intent* = positivo → mandar el link (Google Meet/Zoom) y avisar al closer "{nombre} va a asistir" (L9 39:03-41:32). Avanzado: IA para detectar si reprograma o cancela (L9 37:50).
9. **No activar "detener en respuesta"**: los recordatorios tienen que seguir aunque el lead responda (L9 43:39).
10. **Página de gracias** con video de preparación, y repetir el link en los recordatorios (L9 45:20; [[landing-page-de-agendamiento]]).
11. **Nutrición por email** en un workflow paralelo con el mismo trigger, con ventana horaria (lun-sáb 9-20 h) para no escribir de madrugada (L9 54:30-57:00).

### Variante manual por WhatsApp Business ([[content-capital-ven-l10-proceso-pre-call|VEN L10]])

1. **Primer mensaje apenas agenda**, con copy fijo (captura 02:24) y la hora **siempre en el huso del lead** (03:01).
2. **Si responde**: "estoy armando un plan de acción personalizado… ¿qué te gustaría llevarte de la reunión?" y reflejarle el problema.
3. **Si no responde**: 2.º mensaje de escasez, "confirmá o libero el espacio para otra persona" (04:02); 3.º, aviso de cancelación con opción de reagendar (05:03). "Si no contesta, no se presenta"; revisar en Instagram por qué.
4. **Mantener la conversación** hasta 1-2 h antes y mandar casos de éxito del mismo nicho (06:01).
5. Copys cortos y ya validados; no sobrepensarlos.
6. Del lado del calendario: el formulario pide el compromiso de confirmar por WhatsApp y el calendario manda recordatorios por mail (24 h, 2 h, 30 min) y SMS (12 h, 2 h, 30 min) ([[content-capital-ven-l07-configuracion-de-calendario|VEN L7]] 13:03, 14:00; ver [[calendario-de-agendamiento-calificado]]).

## Plantilla para llenar

```
WORKFLOW PRE-CALL — calendario: ___
TRIGGER: Cita reservada por el cliente (filtro: calendario ___)

T+0      EMAIL INTERNO → {usuario asignado}
         Asunto: "Nueva llamada: {contact.name}"   Cuerpo: respuestas del formulario
T+0      [si califica: evento de agenda a Meta]
T+0      WHATSAPP 1: "Hola {first_name}, mi nombre es {usuario asignado} y recibí la solicitud
                     de tu llamada para {start date time}."
T+0      WHATSAPP 2: "Por favor confirmá tu asistencia respondiendo este mensaje."
         [opcional: video/audio del closer ___]
WAIT     hasta respuesta · timeout 15 h
  sin respuesta → WHATSAPP: "Recordá que si no podemos confirmar tu llamada, ___
                             (ej. vamos a liberar el horario)."
WAIT     hasta 1 día antes de la cita
T-1 día  WHATSAPP: "¡Hola {first_name}! Nos vemos mañana a las {start time}. Mientras tanto
                    mirá esto: ___ (video de preparación | testimonios)"
WAIT     hasta 2-3 h antes
T-2/3 h  WHATSAPP: "Nos vemos hoy a las {start time}. ¿Podrías confirmarme con un sí o no?"
IF reply intent = positivo
         → WHATSAPP: "¡Genial! Este es el link: {meeting location}"
         → aviso al closer: "{nombre} va a asistir"
ELSE     → ___ (reprograma / cancela → etapa ___)
CONFIG   "detener en respuesta": OFF

WORKFLOW PARALELO (mismo trigger): emails de nutrición ___ / ___ · ventana lun-sáb 9-20 h
SIN WHATSAPP: acción Email desde info.___ (TXT / CNAME / MX configurados)
```

Variante manual (VEN L10, copy de la captura 02:24):

```
AL AGENDAR  "{Nombre}, ¿cómo va? Te habla ______, del equipo de ______. Me pasó tu número
             porque agendaste una consultoría con nosotros. Tendríamos la reunión el {DÍA}
             a las {HORA EN EL HUSO DEL LEAD}. ¿Me confirmás?"
SI RESPONDE "Estoy armando un plan de acción personalizado… ¿qué te gustaría llevarte
             de la reunión?"  → reflejar el problema: ______
SIN RESP. 2 escasez: confirmá o libero el espacio para otra persona
SIN RESP. 3 aviso de cancelación + opción de reagendar
HASTA 1-2 h ANTES  conversación + casos de éxito del nicho ______
META SHOW UP 75-85%
```

## Ejemplos del curso desarmados

| Pieza (min) | Qué hace | Por qué |
|---|---|---|
| Confirmación con nombre del closer (L9 29:50) | "Mi nombre es {usuario asignado}…" | El lead sabe con quién habla; parece humano |
| Timeout de 15 h (L9 33:25) | Si no responde, un seguimiento con consecuencia | Empuja a confirmar sin llamar a mano |
| Recordatorio del día anterior con video (L9 35:00) | Suma preparación o testimonios | Nutre y recuerda a la vez |
| "Sí o no" + reply intent (L9 39:03) | El link solo llega si confirma | Separa confirmados de dudosos y avisa al closer |
| "Detener en respuesta" apagado (L9 43:39) | Los recordatorios siguen | Un "gracias" del lead no debe cortar la secuencia |

## Errores comunes

- Dejar pasar horas entre la agenda y el primer contacto (L9 34:10).
- Usar la API oficial de WhatsApp sin volumen: ventana de 24 h y solo plantillas (L9 05:50).
- Activar "detener en respuesta" (L9 43:39).
- Mandar el link solo en la página de gracias: no todos la ven (L9 45:20).
- Mandar emails de madrugada por no poner ventana horaria (L9 55:50).
- Poner la hora de la reunión en tu huso y no en el del lead (VEN L10 03:01).
- Dejar que agende sin saber por qué: sin dolor claro, no viene (VEN L6 11:00).
- Configurar el email como notificación interna en vez de acción Email, o sin subdominio propio (L9 58:00).

## Checklist para agentes

```
[ ] ¿El trigger está filtrado por el calendario correcto?
[ ] ¿El closer recibe aviso con las respuestas del formulario?
[ ] ¿El WhatsApp de confirmación sale en el minuto 0 y nombra al closer y la fecha?
[ ] ¿Hay timeout (~15 h) con seguimiento si no responde?
[ ] ¿Hay recordatorio 1 día antes y 2-3 h antes, relativos a la cita?
[ ] ¿El link se manda al confirmar y también está en la página de gracias?
[ ] ¿"Detener en respuesta" está apagado?
[ ] ¿Los emails tienen ventana horaria y subdominio propio?
[ ] ¿Se mide la asistencia (show rate) para saber si la secuencia funciona?
[ ] Manual: ¿el primer mensaje sale apenas agenda, con la hora en el huso del lead? (VEN L10)
[ ] Manual: ¿hay 2.º mensaje de escasez y 3.º de cancelación con opción de reagendar? (VEN L10)
[ ] ¿Se sabe por qué agendó (dolor claro)? (VEN L6)
```

## Fuentes

- Base: [[content-capital-pag-l09-proceso-pre-call-automatizaciones]] 03:40-58:00.
- [[content-capital-pag-l07-armado-de-landing-page]] 05:00 (página de preparación).
- [[content-capital-pag-l15-masterclass-de-webinars]] (secuencia del día del webinar, para contraste).
- [[content-capital-pag-l10-reemplazar-manychat-con-ghl]] 07:00, 24:20 (mismo patrón de wait/timeout en DM).
- [[content-capital-ven-l10-proceso-pre-call]] 00:00-07:00 (versión manual por WhatsApp Business; copy en captura 02:24).
- [[content-capital-ven-l06-armado-de-tuberia]] 11:00-12:01 (por qué agendó) · [[content-capital-ven-l07-configuracion-de-calendario]] 13:03, 14:00 (compromiso de confirmar, recordatorios del calendario).
- Relacionados: [[gohighlevel-stack-crm]], [[metricas-de-la-tuberia-de-negocio]], [[venta-privada-hand-raisers-y-triage]].
- Inferencia mía: el texto del seguimiento y el del link completan frases que en la clase quedan a medias ("blah, blah, blah").

## Tensiones internas del curso

- **Automatizar vs. contacto humano**: la secuencia reemplaza el trabajo manual, pero la misma clase dice que la mejor asistencia viene de responder al instante; el curso no compara asistencia automatizada contra manual con datos. VEN L10 enseña la versión manual con meta de 75-85% de show up; el tablero de M4 L5 llama "utópico" a más de 80%. Tampoco hay datos que comparen.
- **Triage**: si hay confirmación manual de citas (L6 24:00), la confirmación automática se apaga; no se explica cómo convive con esta secuencia (pregunta abierta).
