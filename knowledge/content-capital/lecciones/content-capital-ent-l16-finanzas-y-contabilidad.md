---
title: "Content Capital · Programa · Entrega de Servicio y Operaciones L16 — Finanzas y Contabilidad"
type: source
source_type: course-lesson
course: content-capital
module: "Programa · Entrega de Servicio y Operaciones"
instructor: "no identificado (no se presenta; habla en pesos argentinos y de \"nuestra\" LLC)"
lesson: 16
duration: "12:00"
date_ingested: 2026-09-26
transcript_path: ~/Documents/Deliverables/General/docs/Content-Capital/transcripts/programa/ent-entrega-de-servicio/16-finanzas-y-contabilidad.md
tags: [content-capital, cc-ent, operaciones, finanzas, metricas]
status: active
---

> No es asesoría contable ni legal. La clase explica cómo usar una planilla del curso, no cómo declarar impuestos.

## En una línea

Tutorial de la **planilla financiera del negocio** que entrega el curso: dos hojas de solo lectura (**estado de resultados** con cash flow y profit mes a mes, y **dashboard** de ventas, comisiones y cash collected) que se alimentan solas de tres entradas que sí se cargan a mano: el **formulario de pagos** (con botón que corre un script), la **planilla de gastos** (software, anuncios, otros) y la hoja de **payroll** del equipo por mes. Regla operativa: la fecha bien puesta decide en qué mes cae cada número; una copia nueva por año.

Instructor: **no identificado**. No se presenta; habla de "nuestra" LLC y pone el ejemplo en pesos argentinos (03:47).

## Recorrido de la clase

| Min | Idea |
|---|---|
| 00:01 | Presenta el "modelo de planilla financiera de negocio". Dos hojas principales de representación. |
| 00:20 | Recomendación: **una copia nueva por año**. Se podría adaptar para llevar histórico, pero se vuelve incómoda. |
| 00:42 | **Estado de resultados**: no se toca nada, todas las celdas son fórmulas que se alimentan de otras hojas. Muestra la evolución de cash flow y profit mes a mes. |
| 01:18 | **Dashboard**: ventas con comisiones del equipo comercial, evolución del cash collected, cash collected por fuente y por concepto. Filtros por mes, por producto y por rango de fechas. Con datos de ejemplo "no son muy representativos". |
| 02:29 | Dos entradas alimentan todo: el formulario de pagos y la planilla de gastos. |
| 02:43 | **Formulario de pagos**: fecha de carga · programa o producto (los nombres se editan en una lista desplegable) · nombre del cliente · teléfono · efectivo recaudado en dólares · medio de pago · si cobraste en moneda local, se convierte al tipo de cambio del día (ejemplo hablado con pesos argentinos). |
| 04:00 | Más campos: **closer** y **setter** (alimentan las comisiones), **comprobante** (link a la imagen dentro de una carpeta de Drive ordenada por cliente), **concepto** (pago completo, cuota 1, 2, 3…; se agregan las que hagan falta) y **fuente** (YouTube, Instagram, etc.). |
| 05:07 | Botón **cargar**: corre un script que guarda el pago en el registro. La primera vez pide permiso ("permitir"/"allow"). Después, botón **limpiar** para cargar el siguiente. |
| 05:41 | **Comisión de pasarela**: si cobraste 1.000 y la pasarela se quedó con 40 (ejemplo hablado con PayPal), se carga acá. |
| 06:01 | Si te equivocaste, se corrige directo en el registro. Recomienda revisarlo siempre. |
| 06:36 | **Planilla de gastos**: categorías software, anuncios y otros. "Otros" es todo lo que no sea software ni anuncios (formaciones, un impuesto de la LLC, etc.). Carga manual: fecha, concepto, medio de pago, monto (ejemplo: 75 dólares de una herramienta de automatización), categoría y, opcional, departamento. |
| 08:03 | **La fecha es crítica**: cada mes toma lo que tiene esa fecha. Mal cargada, el número cae en otro mes y las cuentas no cierran. Vale igual para el registro de pagos. |
| 08:26 | **Payroll**: el equipo no va en gastos sino en una hoja propia con una tabla por mes (enero a diciembre). Por persona: medio de pago, dirección o cuenta, teléfono, puesto, **departamento** (ventas, marketing, operaciones, producto), base, comisiones y bonos, fecha de pago y casilla de pagado. |
| 09:30 | El departamento decide en qué línea del estado de resultados cae el sueldo. Ejemplo: base de 200 dólares a un closer aparece en ventas. |
| 10:17 | Resumen: la operatoria diaria no es compleja; lo largo fue explicar problemas que les pasaron a ellos. |
| 11:02 | Abajo del estado de resultados hay un resumen automático: lo recaudado, el beneficio y el porcentaje de beneficio. |
| 11:12 | Los gastos se pueden cargar repasando el resumen de la tarjeta de crédito. |
| 11:26 | Truco: **ocultar** las filas de meses pasados (clic derecho, "hide rows"). Ocultar no borra; **borrarlas sí rompe** los datos. |

## Frameworks que aparecen

- [[operaciones-roles-sops-finanzas]] (ampliar el paso 5 "Armá las finanzas": acá está la planilla concreta con P&L, dashboard de cash collected, pagos, gastos y payroll)
- [[crm-de-ventas-en-planilla]] (se toca: el formulario de pagos registra closer, setter, cuota y fuente, igual que el CRM de ventas; verificar si son la misma base o dos)
- [[tablero-de-kpis-del-negocio]] (mención posible: cash collected por fuente)
- Nuevo propuesto: `planilla-financiera-del-negocio` (o sección dentro de operaciones)

## Ejemplos mostrados en pantalla

- **00:42-02:26** — Estado de resultados con fórmulas y gráficos de cash flow y profit; dashboard con gráficos de comisiones, cash collected por fuente y por concepto, y filtros.
- **02:43-06:30** — Formulario de pagos completado con un cliente ficticio y sus listas desplegables.
- **06:36-08:26** — Planilla de gastos con una fila de ejemplo.
- **08:26-10:15** — Hoja de payroll con tablas mensuales. Todos los datos son de ejemplo.

## Tareas y herramientas

- Google Sheets con script propio (botones cargar y limpiar).
- Carpeta de Google Drive para comprobantes, ordenada por cliente (04:19).
- Resumen de tarjeta de crédito como fuente para cargar gastos (11:15).

## Citas clave

- "Acá no hay que tocar ningún dato." (01:07, sobre el estado de resultados)
- "Es importante que acá pongan bien la fecha." (08:12)

## Lo que no se procesó

- La transcripción automática rompe palabras al final de cada línea ("plat illa", "comerc iano"). Se reconstruyó por contexto.
- No se ve la planilla: nombres exactos de columnas y hojas son los que se oyen, no los que figuran en pantalla.
- La moneda y los montos son ejemplos hablados, no cifras del negocio.
- El script de carga no se explica por dentro.
- Tensión menor: M1 desaconseja PayPal y acá aparece como ejemplo de pasarela (05:47). Es solo un ejemplo.
