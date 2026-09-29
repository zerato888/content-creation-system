---
title: "Content Capital · Programa · Adquisición Pagos L11 — Cómo trackear UTM´s en GHL"
type: source
source_type: course-lesson
course: content-capital
module: "Programa · Sistemas de Adquisición Pagos"
instructor: "Nicolás Bartolomé (inferencia: misma voz y cuenta que L9-L10; no aparece en cámara)"
lesson: 11
duration: "11:59"
date_ingested: 2026-09-25
transcript_path: ~/Documents/Deliverables/General/docs/Content-Capital/transcripts/programa/pag-adquisicion-pagos/11-como-trackear-utm-s-en-ghl.md
captures_path: ~/Documents/Deliverables/General/docs/Content-Capital/capturas/programa/pag-adquisicion-pagos/11/
tags: [content-capital, cc-pag, utm, gohighlevel, crm, automatizacion, anuncios, metricas]
status: active
---

## En una línea

Dos formas de saber de dónde viene cada lead en GoHighLevel: **orgánico/manual** (un Sheet que arma links con utm_source/medium/content + tres campos personalizados ocultos en el formulario del calendario) y **anuncios** (GHL ya trae la atribución; una automatización la copia a esos campos) y, en ambos casos, mandar todo a un Google Sheet para contar leads por fuente con fórmulas. Instructor: probablemente **Nicolás Bartolomé** (inferencia).

## Recorrido de la clase

| Min | Idea |
|---|---|
| 00:00 | Dos escenarios: contenido orgánico (saber si las agendas vienen de Instagram, TikTok o de qué setter) y anuncios (a VSL, a formulario, generación de leads en Facebook). |
| 00:40 | Se comparte un Sheet simple para crear links con UTMs, para contenido o cuando el setter manda el link del calendario a mano. |
| 01:00 | Columnas: URL (calendario o landing), Fuente, Medio, Contenido = *source, medium, content*. No hay regla fija: fuente = Instagram, medio = setter 1 (o su nombre), contenido = reel X. |
| 02:00 | Trackear cada reel exige un link nuevo por reel: "no es tan sostenible". Lo usual es trackear la fuente y, como mucho, el medio. |
| 02:40 | Una fórmula concatena link + parámetros: "...?utm_source=instagram&utm_medium=setter&utm_content=reelx". Ese es el link que se manda en el setting. |
| 03:10 | En GHL: Configuración → Campos personalizados → carpeta nueva "UTM's" → tres campos de texto de una línea llamados exactamente **utm_content, utm_medium, utm_source**. |
| 04:10 | Sitios → Formularios → el formulario del calendario: agregar los tres campos y **marcarlos ocultos**; se completan solos desde el link. |
| 05:10 | Al agendar, en la carpeta UTM del contacto aparece "instagram", "setter 1", "reel x". |
| 06:00 | Anuncios: si el lead entró por formulario instantáneo, landing o calendario, en el contacto (abajo a la derecha) ya está la **atribución** (fuente Facebook, campaña, utm_content = ID del anuncio). En Meta se puede configurar que el utm_content muestre una palabra clave del anuncio en vez del ID. |
| 07:40 | Para unificar: en la automatización de "llamada agendada", acción **Update contact field**: utm_source = *Attribution first → UTM source*; igual con medium y content. |
| 09:00 | Contar: filtrar contactos por campo (p. ej. utm_medium = setter 1), o mejor mandar los datos a Google Sheets desde la misma automatización (conectar cuenta, archivo y hoja; el Sheet con columnas creadas antes: nombre, teléfono, fecha de llamada, UTM). |
| 10:40 | No muestra un Sheet real "para no mostrar ningún dato". En el Sheet, fórmulas del tipo "contar leads con utm_content X". Airtable o webhook también sirven; Sheets es lo más simple. |
| 11:20 | Resumen: orgánico = links con UTM + campos personalizados ocultos en el formulario; anuncios = la atribución de Facebook → campos → Sheet. |

## Frameworks que aparecen

- [[gohighlevel-stack-crm]] (nuevo)
- [[tablero-de-kpis-del-negocio]] (medir de qué fuente o setter vienen las agendas)
- [[metodos-y-tuberia-de-adquisicion]] (orgánico, setting y anuncios como fuentes separadas)

## Ejemplos mostrados en pantalla

- **00:00** — Sheet "UTM's" con columnas URL CALENDARIO, Fuente, Medios, Contenido y UTM; dos filas de ejemplo (fuentes "instagram" y "tiktok") y la columna UTM con el link concatenado "...?utm_source=instagram&utm_medium=&utm_content=".
- **03:45** — Modal "Nueva carpeta de campos personalizados" con el nombre "UTM's", objeto Contacto.
- **05:44 / 09:45** — Lista de contactos de GHL (nombres, emails y teléfonos no se transcriben).

## Tareas y herramientas

- Crear los tres campos personalizados con los nombres exactos y agregarlos ocultos al formulario (03:10-05:10).
- Agregar "Update contact field" con la atribución en la automatización de agendamiento (07:40).
- Mandar los leads a un Google Sheet y contar con fórmulas (09:00).
- Herramientas: Google Sheets, GoHighLevel, Meta Ads (parámetros de URL), Airtable o webhook como alternativas.

## Citas clave

- Trackear cada reel "no es algo tan sostenible en el tiempo". (02:10)
- Mandarlo a Sheets es lo más simple y lo que "la mayoría usa". (11:05)

## Lo que no se procesó

- No se muestra cómo configurar en Meta los parámetros de URL para que utm_content lleve una palabra clave (se menciona y se saltea, 06:50).
- La conexión GHL → Google Sheets se remite a "otros módulos".
- El instructor no aparece en cámara; su nombre es inferencia.
