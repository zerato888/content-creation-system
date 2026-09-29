---
title: "Content Capital · Programa · Sistemas de Adquisición Outbound L3 — Métricas"
type: source
source_type: course-lesson
course: content-capital
module: "Programa · Sistemas de Adquisición Outbound"
instructor: "Santiago (mismo instructor de L1-L2, inferencia: no se presenta)"
lesson: 3
duration: "16:30"
date_ingested: 2026-09-26
transcript_path: ~/Documents/Deliverables/General/docs/Content-Capital/transcripts/programa/out-adquisicion-outbound/03-metricas.md
tags: [content-capital, cc-out, outbound, metricas, kpi, prospeccion, setter]
status: active
---

## En una línea

Cómo usar el **tracker de outbound** en Google Sheets: una copia por plataforma, una **lista de leads** antiduplicados antes del tracker, y una fila por prospecto que se mueve de estado (A iniciado → B interesado → C Calendly enviado → D agendado) marcando "traqueado" y la **fecha** de cada seguimiento, para que el dashboard calcule solo las tasas.

Instructor: no se presenta. Por la voz de la clase, el sistema de 4 estados y la referencia al "SIC"/"CDN", es el mismo de L1-L2 (inferencia). La clase es un recorrido de pantalla que la transcripción no describe.

## Recorrido de la clase

| Min | Idea |
|---|---|
| 00:00 | Primera pestaña (dashboard): no se llena nada a mano, "parece un bodrio pero tranquilo". |
| 00:35 | Pestañas por mes. Siempre **hacer una copia** y poner la plataforma en el título: un tracker por plataforma, si no las métricas no son certeras. Zoom al 85% para verlo entero. |
| 01:16 | **Pestaña de conexiones** (LinkedIn o solicitudes de amistad de Facebook): nombre, link, fecha de conexión, si es tomador de decisión, país, si está activo, estado (enviada/aceptada) y notas. |
| 01:48 | País y actividad son opcionales pero útiles. Ejemplo: 5 a Argentina y 5 a Chile; si Argentina responde más, exprimir Argentina (con datos más grandes). Buscar perfiles activos, más fáciles al principio. |
| 02:40 | La **tasa de conexión** (aceptación) dice si el perfil está bien optimizado. |
| 02:59 | **Métricas arriba de la hoja**: estado A, vio el video, estado B, C y D. Son fórmulas; no se rellenan. |
| 03:33 | **Estado A** = a quien se le mandó el pedido de permiso (el "pre-pitch" o caballo de Troya). Solo esa gente entra al tracker, si no se ensucia. |
| 03:56 | **Lista de leads** aparte: nombre, link y "¿usado?". Evita pisarse al escalar volumen o al sumar un setter: sin ella, podés pasar una hora scrapeando leads repetidos. |
| 05:17 | **Prompt de ChatGPT**: organizar las URL en columna A (nombre del perfil) y B (link), listas para pegar en Sheets. |
| 05:43 | Flujo: perfil ideal → similares → Cmd/Ctrl + clic en los que califican (una pestaña cada uno) → cerrar los que no → extensión de Chrome **Copy URL** para copiar todas las URL → ChatGPT → lista. Sirve para buscar por países. |
| 07:42 | Un lead repetido **se marca en rojo** solo. Permite una lista enorme sin duplicados antes de pasar al tracker. |
| 08:10 | **Cómo traquear en A**: nombre, link, plataforma, fecha de contacto y la casilla **"traqueado"**. Sin esa casilla la fila no cuenta en ninguna métrica. |
| 09:19 | Un error de atención con esa casilla "te arruina todas las métricas de tu negocio". |
| 09:32 | Columna de FU1 del caballo de Troya y notas (con "insertar nota"). Columna **"vio el video"**: la tasa de vista importa si mandás video, porque la entrega de Instagram "juega en contra". Con audio o texto cuesta medirla. |
| 10:31 | El que dice que no **no se borra**: se tacha y se pinta de rojo. |
| 10:55 | En los seguimientos se anota **la fecha**, no "sí/no": con la fecha sabés cuándo toca el siguiente. |
| 11:27 | Respuesta positiva: se copia la fila al estado siguiente y en el anterior se tacha (sin rojo), así se sabe que ya no está ahí. |
| 12:01 | **Estado B**: se marca "traqueado" cuando le mandás el VSL evergreen, el audio, la propuesta o un Loom personalizado, lo que haya pedido. Siete columnas de seguimiento con fecha. |
| 12:55 | **Ritmo**: FU1 a las 12-24 h, FU2 a las 24 h siguientes y, desde el FU3, cada 48 h (ej.: días 15 → 17 → 19 → 21). En nichos de gente muy ocupada se puede alargar un poco, "no más de 48 horas". |
| 14:08 | Las columnas muestran **dónde se queda la gente**: si todos pasan después del FU5, es una prueba de concepto de que el FU5 agenda. |
| 14:27 | **Estado C** (Calendly enviado) igual: traqueado + 7 seguimientos. **Estado D** (agendado): se tacha en C, se pasa a D y se marca traqueado. |
| 15:15 | El dashboard cuenta todo y calcula las métricas solo. Tracker + lista de leads + ChatGPT = prospección ordenada y constante. |
| 15:34 | **Traquear bien vale más que el volumen**: mejor 30 mensajes diarios traqueados que 100 sin traquear. Un sistema sin traqueo "crea caos". |
| 16:00 | Duda común: gente en B al cambiar de mes. Se pega en la pestaña nueva pintada de un color (amarillo pastel) para saber que viene del mes anterior. |

## Métricas que nombra

| Métrica | Dónde sale | Para qué |
|---|---|---|
| Tasa de conexión / aceptación | Pestaña de conexiones | Diagnóstico del perfil (02:40) |
| Tasa de vista del video | Columna "vio el video" en A | Calidad del estímulo y de la entrega de Instagram (09:52) |
| Tasa de respuesta positiva | Paso de A a B | Eficacia del caballo de Troya (10:21) |
| Pasos A → B → C → D | Dashboard | Conversión por estado (02:59, 15:15) |
| Seguimiento donde se convierte | Columnas FU con fecha | Prueba de concepto de la cadena (14:08) |

Las fórmulas exactas y los benchmarks no se dicen (inferencia: la tabla ordena lo que la clase menciona).

## Frameworks que aparecen

- [[crm-de-ventas-en-planilla]] (mención: otra planilla de la tubería; esta es solo de outbound)
- [[seguimientos-y-reactivacion-de-leads]] (ampliar: cadena manual con fechas y ritmo 24/24/48 h)
- [[tablero-de-kpis-del-negocio]] (relacionada; ver propuesta)
- Nuevo propuesto: `metricas-del-outbound`: tracker por estados, lista antiduplicados, fecha por seguimiento y "traqueado" como puerta de toda métrica.

## Ejemplos mostrados en pantalla

- Todo es pantalla compartida del tracker, la lista de leads, el prompt y la extensión, pero la transcripción no lo describe. Sin capturas en esta ingesta.

## Tareas y herramientas

- Copiar el tracker, una copia por plataforma (00:46).
- Armar la lista de leads con la extensión Copy URL + el prompt de ChatGPT (05:17–07:42).
- Marcar "traqueado" en cada estado y anotar la fecha de cada seguimiento (08:10, 10:55).
- Tachar sin borrar (rojo = no interesado; sin color = pasó de estado) (10:31, 11:27).

## Citas clave

- "Si no traqueás esto, no te va a traquear ninguna de las métricas." (09:14, paráfrasis)
- "Mejor 30 mensajes diarios traqueados a la perfección que 100 sin traquear." (15:38, paráfrasis)
- "No estás creando un sistema." (15:53, sobre prospectar sin traquear)

## Lo que no se procesó

- Recorrido visual sin descripción: no se sabe el diseño exacto del dashboard ni las fórmulas.
- Nombres de leads de ejemplo omitidos a propósito.
- "SIC" (00:00) probablemente es el nombre del programa o comunidad; lectura dudosa.
