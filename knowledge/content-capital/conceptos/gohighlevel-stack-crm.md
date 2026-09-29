---
title: "GoHighLevel como stack de CRM y adquisición (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-pag-l06, cc-pag-l07, cc-pag-l09, cc-pag-l10, cc-pag-l11, cc-mc-l14]
source_count: 6
created: 2026-09-25
updated: 2026-09-25
tags: [content-capital, cc-pag, framework, checklist, plantilla, gohighlevel, crm, automatizacion, utm, dm, adquisicion, cc-mc, manychat, ia]
status: developing
---

## En una línea

GoHighLevel (GHL) junta en un solo lugar CRM, embudos, formularios, calendario, mensajería y automatizaciones; se configura **en orden fijo** (usuarios → formulario → calendario rotativo → pipeline), después se le suma el setter de IA que reemplaza a ManyChat y el trackeo de UTMs para saber de dónde viene cada agenda.

## Qué es y por qué funciona (según el curso)

- Nico Bartolomé lo presenta como el reemplazo de HubSpot/Salesforce (CRM), ClickFunnels (embudos), Typeform (formularios), Calendly, Zapier, ManyChat, Skool, email/WhatsApp, rastreo de llamadas y firma de documentos ([[content-capital-pag-l06-principales-funcionalidades-de-ghl|PAG L6]] 02:00-05:00). La tabla del propio vendedor compara USD 1.612/mes contra 97 (según el curso).
- Planes (según el curso): ~USD 97/mes para uso propio; ~300/mes en modo agencia, con subcuentas ilimitadas y marca blanca con dominio propio (L6 06:10, 12:00). Prueba gratis de 14 días, extensible a 30: abrirla cuando ya vas a prospectar o pautar y pagarla con el primer cliente ([[content-capital-pag-l07-armado-de-landing-page|PAG L7]] 42:40).
- Por qué funciona: todo el recorrido del lead (anuncio o DM → formulario → agenda → recordatorios → etapa del pipeline) queda en una sola ficha, y **mover una etapa dispara automatizaciones** (ej.: "no asistió" → seguimiento de 5 días) (L6 09:00-11:00).

- **Ampliación ManyChat (cc-mc).** El curso de ManyChat (L1-L17) **no menciona GHL**. Lo más cercano es el bot calificador de [[content-capital-mc-l14-manychat-claude|MC L14]]: la misma función de setter con IA, pero dentro de ManyChat y con Claude como clasificador que solo elige mensajes guardados. Ver [[bot-calificador-claude-manychat]]. La relación entre las dos herramientas es inferencia mía, no del curso.


## Cuándo usarlo / cuándo no

- **Sí**: agencia o consultor que va a pautar, agendar llamadas con varios closers o revender el sistema a clientes (subcuentas).
- **No todavía**: si solo prospectás por chat, no hace falta (L7 43:40). Tampoco N8N: solo si vendés automatizaciones avanzadas (L7 48:50).
- **No** depender de la marca blanca de un tercero sin poder llevarte las subcuentas: pedir la transferencia (L6 64:00).

- **ManyChat + Claude en vez de GHL** (inferencia): si todo el setting pasa por el chat de Instagram y ya usás ManyChat, el bot calificador cubre la calificación y el envío del calendario sin cambiar de herramienta (MC L14 01:44).


## Pasos

1. **Subcuenta**: desde snapshot (plantilla por nicho) o en blanco (L6 07:20). Configurar país, zona horaria, idioma de la plataforma e idioma de comunicación saliente (L6 12:40).
2. **Usuarios** (L6 13:40): uno por setter o closer, con rol y permisos (el closer ve solo lo suyo, no las automatizaciones). **La disponibilidad real se carga en cada usuario**, no en el calendario.
3. **Formulario** (L6 27:10-38:00): "empiezo toda la configuración desde los formularios". Encuesta (quiz) o formulario lineal. Nombre completo, teléfono con selector de país, email; campos personalizados en carpeta ("Datos del lead"): botón de opción para rangos de facturación, desplegable, varias líneas, monetario. Sacar términos y privacidad; botón personalizado.
4. **Calendario rotativo** (L6 15:00-27:00): ver la ficha de configuración en la plantilla. Asociar el formulario en "Formularios y pago"; página de confirmación = página de preparación ([[landing-page-de-agendamiento]]). **No** poner el píxel en el calendario: va por automatización.
5. **Pipeline** (L6 09:00-11:00): uno o varios (por setter o closer). Etapas: agendada, concretada, no asistió, cotización, contrato, venta, descartado.
6. **Dominio** (L6 68:00-75:00): pedir acceso al proveedor del cliente → Configuración → Dominios → registro A manual → verificar → elegir el dominio en la configuración del embudo. Varios dominios sí; varios en un mismo embudo no. El email es otro tema (subdominio propio, ver [[secuencia-pre-call]]).
7. **Automatizaciones pre-call**: ver [[secuencia-pre-call]].
8. **Setter de IA / reemplazo de ManyChat** ([[content-capital-pag-l10-reemplazar-manychat-con-ghl|PAG L10]]): conectar Instagram y Facebook en Integraciones y activar los mensajes (L10 00:00). Trigger "El cliente respondió" (DM de Instagram que contiene la palabra del CTA) o "Instagram comments on a post" (un post o cualquiera + palabra clave) (L10 01:40-03:40). Con miles de comentarios, **drip mode** (L6 51:50). Secuencia en la plantilla.
9. **Trackeo de UTMs** ([[content-capital-pag-l11-como-trackear-utms-en-ghl|PAG L11]]): carpeta "UTM's" en campos personalizados con `utm_source`, `utm_medium`, `utm_content` (texto de una línea, nombres exactos), agregados **ocultos** al formulario del calendario (L11 03:10-05:10). En anuncios, en la automatización de agenda: *Update contact field* = atribución first → UTM source/medium/content (L11 06:00-08:40). Contar con filtros de contactos o mandando cada agenda a Google Sheets (L11 09:00-11:20).
10. **Integraciones propias**: webhooks para Discord, Sheets, etc. (L6 55:20).

## Plantilla para llenar

```
FICHA DE CONFIGURACIÓN GHL — [NEGOCIO]

1. SUBCUENTA: [snapshot ___ | en blanco]  país ___  zona horaria ___  idioma saliente ___
2. USUARIOS
   - ___ (rol: setter|closer)  disponibilidad: días ___ horas ___
   - ___ (rol: setter|closer)  disponibilidad: días ___ horas ___
3. FORMULARIO [quiz | lineal]
   - Nombre completo · Teléfono (selector de país) · Email
   - Carpeta "Datos del lead":
     ¿A qué te dedicás? (desplegable): ___
     Facturación mensual (botón de opción, RANGOS sin mostrar el mínimo): ___ / ___ / ___
     ¿Podés invertir en ___? (sí/no)
     ¿Qué te frena hoy? (varias líneas)
   - Ocultos: utm_source · utm_medium · utm_content
4. CALENDARIO ROTATIVO
   miembros: ___   modo: [por disponibilidad | distribución equitativa]  prioridad: ___
   disponibilidad general: 8-22 h, lun-dom (la real vive en el usuario)
   slot: 1 h  |  reunión: 45 min  |  aviso mínimo: 1 día  |  rango: 48 h a 3 días
   tope diario: ___  |  reservas por franja: 1
   formulario asociado: ___  |  confirmación → página de preparación: ___
   confirmación automática: [sí | no si hay triage]
   notificaciones: solo dentro de la app  |  invitación Google Calendar: sí
   asignar contacto al closer: sí  |  píxel: NO (va por automatización)
   link: [permanente | un solo uso para prospección]
5. PIPELINE: agendada → concretada → no asistió → cotización → contrato → venta → descartado
   automatización por etapa: no asistió → seguimiento ___ días
6. DOMINIO: ___  (registro A)  |  subdominio email: info.___
7. SETTER IA (ver plantilla de secuencia abajo)
8. UTMs manuales (Sheet): URL | Fuente | Medio | Contenido
   ___?utm_source=[instagram]&utm_medium=[setter1]&utm_content=[___]

SECUENCIA SETTER IA (reemplazo de ManyChat) — L10
trigger: [comentario con "___" en post ___ | DM que contiene "___"]
wait ~5 min → DM: "{first_name}, vi que te interesa mi recurso sobre ___, contame qué tipo de negocio tenés"
wait ~2 min → responder el comentario (variantes): "revisá tu DM" / "¡te escribí!" / ___
wait hasta respuesta 6-8 h → sin respuesta: "¿estás por ahí?" → bucle cada 24 h / 2 días
si responde → Pregunta 1 (Conversation AI): "___"
   ramas: Dato recibido | No interesado | Time out | No condition met
Pregunta 2: "¿hace cuánto buscás ___?" / "¿qué te limita para llegar a ___?"
   antes de preguntar: responder algo relacionado a su dolor (ejemplos: ___)
Cierre: Appointment Booking bot → calendario ___ (máx. ~5 mensajes, timeout 10-24 h)
Parámetros IA: timeout 10-24 h · respuestas máx. 3 · espera 30-300 s · omitir si ya respondió
Prompt: personalidad ___ + instrucciones (persistente, 3 intentos, objeción → permiso → volver a la pregunta, <20 palabras, imitar al prospecto) + objeciones ___ + info del negocio ___
```

## Ejemplos del curso desarmados

| Pieza (min) | Qué muestra | Lección para replicar |
|---|---|---|
| Calendario rotativo de SYK (L6 15:00-27:00) | Disponibilidad abierta en el calendario y real en cada usuario; rango de 48 h a 3 días | El rango corto evita que el lead agende para dentro de una semana y se enfríe |
| Formulario con rangos de facturación (L6 27:10) | Botón de opción en vez de campo abierto | Filtra sin fricción; en L9 63:00 agrega: no mostrar el mínimo para que no mientan |
| Trigger de comentario (L6 51:50; L10 01:40) | Palabra clave en un post → DM automático | Reemplaza a ManyChat; con volumen alto, drip mode |
| Conversation AI (L10 08:10-11:00) | Prompt corto + base de objeciones + info del negocio "como una Wikipedia" | Prompts largos confunden al bot; cuesta ~USD 0,02 por ejecución (según el curso) |
| Sheet de UTMs (L11 01:00-02:40) | Fórmula que concatena la URL con fuente, medio y contenido | Trackear por reel no es sostenible: quedarse con fuente y medio |

## Errores comunes

- Configurar el calendario antes que los usuarios y el formulario (L6 27:10).
- Cargar la disponibilidad en el calendario y no en cada usuario (L6 13:40).
- Abrir el calendario a una semana o más (L6 15:00-27:00).
- Pixelar desde el calendario en vez de hacerlo por automatización (L6 15:00-27:00).
- Bot de agenda con un calendario sin horarios: ofrece días vacíos. Pausarlo (L10 40:00). El bot falla ~1 de cada 20 veces según el curso; iterar el prompt lleva semanas (L10 21:40-23:00).
- No poder saber de qué reel orgánico viene un lead: se resuelve con una etiqueta por palabra clave o a mano (L6 47:30).

## Checklist para agentes

```
[ ] ¿El orden fue usuarios → formulario → calendario → pipeline?
[ ] ¿La disponibilidad real está en cada usuario?
[ ] ¿El calendario tiene rango de 48 h a 3 días, aviso mínimo y tope diario?
[ ] ¿La confirmación del calendario lleva a la página de preparación?
[ ] ¿El píxel/evento se manda por automatización y NO desde el calendario?
[ ] ¿El formulario califica con rangos (sin mostrar el mínimo)?
[ ] ¿Los campos UTM existen con nombres exactos y están ocultos en el formulario?
[ ] ¿Hay automatización por etapa del pipeline (ej. no asistió → seguimiento)?
[ ] ¿El setter IA tiene prompt corto, ramas de timeout y un calendario con horarios reales?
[ ] ¿La subcuenta es transferible si la marca blanca es de un tercero?
[ ] Si el setting vive en ManyChat, ¿se evaluó el bot calificador con Claude antes de migrar a GHL? (inferencia, MC L14)
```

## Fuentes

- Base: [[content-capital-pag-l06-principales-funcionalidades-de-ghl]] (qué reemplaza, orden de configuración, calendario, formulario, pipeline, dominio, reemplazo de ManyChat).
- [[content-capital-pag-l07-armado-de-landing-page]] 10:00, 42:40-48:50 (constructor, prueba gratis, cuándo no hace falta).
- [[content-capital-pag-l10-reemplazar-manychat-con-ghl]] (setter de IA completo).
- [[content-capital-pag-l11-como-trackear-utms-en-ghl]] (UTMs).
- [[content-capital-pag-l09-proceso-pre-call-automatizaciones]] 63:00 (rangos sin mostrar el mínimo).
- Inferencia mía: la ficha de configuración unifica en un solo bloque lo que el curso muestra en demos separadas.

- [[content-capital-mc-l14-manychat-claude]] (setter con IA dentro de ManyChat; no menciona GHL). Relacionada: [[bot-calificador-claude-manychat]].


## Tensiones internas del curso

- **"Todo en uno" vs. "no lo necesitás todavía"**: L6 vende GHL como reemplazo de todo; L7 43:40 dice que si solo prospectás por chat no hace falta. Se resuelve por momento: GHL entra cuando hay pauta o varios closers (inferencia).
- **Setter de IA vs. setter humano**: L10 lo presenta como reemplazo de parte del setter, pero reconoce fallas (~1 de cada 20) y semanas de iteración. No hay una cifra de conversión del bot contra un humano.
- **Precios y ahorro**: los USD 1.612 vs. 97 salen de la tabla del vendedor, no de una medición del instructor.

- **IA que redacta vs. IA que clasifica.** El Conversation AI de GHL (PAG L10) redacta respuestas con prompt de personalidad y falla ~1 de cada 20 veces según el curso; en MC L14 Claude solo clasifica y manda mensajes guardados, "nunca va a alucinar" (MC L14 42:28). Son dos diseños distintos para el mismo problema; el curso no los compara (inferencia).
