---
title: "Content Capital · Programa · ManyChat L10 — Automatización de Envío de Calendario"
type: source
source_type: course-lesson
course: content-capital
module: "Programa · ManyChat"
instructor: "Matías 'Mati' Molina"
lesson: 10
duration: "3:08"
date_ingested: 2026-09-25
transcript_path: ~/Documents/Deliverables/General/docs/Content-Capital/transcripts/programa/mc-manychat/10-automatizacion-de-envio-de-calendario.md
captures_path: ~/Documents/Deliverables/General/docs/Content-Capital/capturas/programa/mc-manychat/10/
tags: [content-capital, cc-mc, manychat, automatizacion, dm, ventas, metricas]
status: active
---

## En una línea

Secuencia que el setter dispara con un botón: manda disponibilidad + link + audio de horarios, etiqueta "calendario enviado" y encadena seguimientos (30 min, 1 h, 6 h, 12 h) mientras el lead no responda, solo entre 8 y 22 h. Sirve para contar calendarios enviados. Instructor: **Matías Molina** (inferencia).

## Recorrido de la clase

| Min | Idea |
|---|---|
| 00:00 | Permite trackear cuántos calendarios mandan los setters y seguir cada agenda. |
| 00:23 | Condición inicial: si tiene la etiqueta "respondió calendario", borrarla (para que no choque); si no, sigue. |
| 00:38 | Envío: "acá te comparto disponibilidad" + link de agenda + audio de horarios ("tengo horarios bastante limitados") + "avisame así le doy prioridad" (pitch de agenda). Etiquetas "respondió calendario" y "calendario enviado". |
| 01:10 | Si en 30 min no contesta (8-22 h): "contestá un horario que se te acomode, se están ocupando". |
| 01:31 | +1 h: "avisame"; +6 h: audio "che, avisame si querías agendarte… o paso el link a alguien nuevo"; +12 h: "¿todavía tenés ganas de resolver lo que hablamos o no te interesa? Avisame si no sigo el chat, gracias". |
| 02:19 | Queda apagada y el setter la dispara desde la conversación (Automatización → calendario). |

## Frameworks que aparecen

- [[secuencia-pre-call]] (seguimientos alrededor de la agenda)
- [[venta-privada-hand-raisers-y-triage]]
- Framework del curso: [[manychat-setting-automatizado]] (setter con botones) · [[manychat-bases-y-flujos]]

## Ejemplos mostrados en pantalla

- **00:53** — Condición #4 (587 contactos): "Etiqueta = respondio_calendario" → Acciones #4 "Eliminar etiqueta respondio_calendario"; si no → Send Message (587 enviados, 100% entregado, 88,8% abierto): "acá te comparto la disponibilidad" + link de la página de llamada de SYK + "Esperando 3 segundos…" + audio "horarios.m4a" + "avisame así le doy prioridad" + espera de texto; Acciones: añadir "Calendario Enviado" y "respondio_calendario"; Smart Delay (310).

## Tareas y herramientas

- Grabar el audio de horarios y armar la secuencia apagada (00:43, 02:19).

## Citas clave

- "Te va a permitir trackear cuántos calendarios se están mandando." (00:12)

## Lo que no se procesó

- Los porcentajes de apertura son del ejemplo en pantalla, no un benchmark.
