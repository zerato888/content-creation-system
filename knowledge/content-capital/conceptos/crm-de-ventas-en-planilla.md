---
title: "CRM de ventas en planilla: cada rol carga poco, el resto se calcula (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-ven-l13, cc-ven-l06, cc-out-l03]
source_count: 3
created: 2026-09-25
updated: 2026-09-26
tags: [content-capital, cc-ven, framework, checklist, plantilla, crm, setter, closer]
status: developing
---

## En una línea

Un CRM en Google Sheets donde **el closer carga cada llamada**, **el setter carga su reporte de fin de día** y todo lo demás (métricas mensuales, CRM de agendas, leaderboards) **se calcula solo**; más un calendario de cuotas para cobrar lo pendiente.

## Qué es y por qué funciona (según el curso)

- Lo muestra en un Loom un integrante del equipo de SYK que no se presenta ([[content-capital-ven-l13-crm-de-ventas|VEN L13]] 00:00, 11:00).
- Es el tablero de la tubería de ventas: las mismas métricas que [[tablero-de-kpis-del-negocio]] (tasa de agenda, show up, cierre sobre calificadas, AOV, % de cash collected) (L13 03:11; [[content-capital-ven-l06-armado-de-tuberia|VEN L06]] 13:00–17:01).
- La carga es mínima y es más rápida que un formulario; las celdas grises son fórmulas (L13 09:01).
- Pensado para hasta 5 closers y 5 setters, ampliable; las hojas extra quedan ocultas hasta que se usan (L13 04:01–05:00).
- Alternativa en planilla al CRM de GoHighLevel: [[gohighlevel-stack-crm]].

## Cuándo usarlo / cuándo no

- **Sí**: equipo de ventas con setters y closers que necesita métricas mensuales sin herramienta paga.
- **Sí, para bonos**: los leaderboards muestran al mejor del mes (por ejemplo, por cash collected) y el esquema de bonos con condiciones mínimas (L13 01:00–02:01). Roles y SOPs: [[operaciones-roles-sops-finanzas]].
- **Outbound: tracker aparte.** Para el DM en frío el curso usa otra planilla: una copia por plataforma, una lista de leads antiduplicados (nombre, link, "¿usado?", repetidos en rojo) y la casilla "traqueado" como puerta de toda métrica ([[content-capital-out-l03-metricas|OUT L3]] 00:35–09:19). Es el tramo anterior a este CRM. Ver [[metricas-y-testeo-del-outbound]].
- **Con GHL**: si ya usás su pipeline, esta planilla duplica datos (inferencia).

## Pasos

1. **Copiá la planilla** y completá la hoja "Guía de uso" con los Looms y los SOPs de closers y setters (L13 00:00, 11:00).
2. **Definí los nombres**: cada persona con el **mismo nombre exacto** en todas las hojas, o se rompen las fórmulas (L13 05:00). Cargá las listas desplegables (setter, closer, fuente).
3. **El closer carga por llamada** (L13 06:00–08:00): lead, fecha de agenda, fecha de llamada, setter, closer, fuente (Instagram, YouTube, TikTok, landing), estrategia, medio de agenda, calificado sí/no, contexto del setter, se presentó, situación, programa ofrecido ("producto · plan · cuotas · total"), contexto del closer, **cash collected día 1** (lo cobrado en la llamada o ese día), **cash collected trato cerrado** (lo que da acceso al servicio; una reserva no cuenta), fecha de pago.
4. **El setter carga su EOD** (L13 08:00–09:01): mensajes respondidos, calendarios enviados, agendas.
5. **No toques** las hojas de solo lectura: Métricas (mensual) y CRM de agendas (junta todas las hojas de closer) (L13 03:04).
6. **Armá el calendario de cuotas** a principio de mes: programa, nombre, teléfono, fecha de cobro, monto, cobrado, closer responsable, estado (L13 10:02–11:00).
7. **Leé la hoja Métricas** con la lógica de la tubería: aguas arriba para ver consecuencias, aguas abajo para buscar causas (L06 24:02; ver [[metricas-de-la-tuberia-de-negocio]]).

## Plantilla para llenar

```
HOJAS: Guía de uso · Leaderboard closers · Leaderboard setters · Métricas (lectura) ·
       CRM de agendas (lectura) · Closer 1-5 · Setter 1-5 · Calendario de cuotas

FILA CLOSER:
lead | f. agenda | f. llamada | setter | closer | fuente | estrategia | medio agenda |
calificado [sí/no] | contexto setter | se presentó [sí/no] | situación |
programa "producto · plan · cuotas · total" | contexto closer | CC día 1 | CC trato cerrado | f. pago

FILA SETTER (EOD):
fecha | mensajes respondidos | calendarios enviados | agendas

FILA CUOTA:
programa | nombre | teléfono | fecha | monto | cobrado [sí/no] | closer | estado

MÉTRICAS (se calculan):
INBOUND: conversaciones · calendarios enviados · agendadas · tasa de agenda x calendario · x mensaje
VENTAS: agendadas · calificadas · % calificadas · calificadas presentadas · show up ·
        cierre s/ calificadas · cerradas en seguimiento / en llamada / total ·
        AOV día 1 · AOV trato cerrado · % CC por venta
```

## Ejemplos del curso desarmados

| Pantalla (min) | Qué se ve | Lectura |
|---|---|---|
| Hoja Métricas vacía (L13 03:04) | #DIV/0! en todas las celdas | Es normal: se llena sola al cargar |
| Hoja Métricas (L13 03:11) | Bloques INBOUND y VENTAS, enero a diciembre | Mismas métricas que la tubería |
| Calendario de cuotas (L13 10:02) | Una segunda cuota de ejemplo, con estado | Cada cuota pendiente tiene dueño |

## Errores comunes

- Escribir el nombre de una persona de dos formas distintas (L13 05:00).
- Editar las hojas de lectura (L13 03:04).
- Contar una reserva como cash collected de trato cerrado (L13 08:00).
- No armar el calendario de cuotas a principio de mes (L13 11:00).

## Checklist para agentes

```
[ ] ¿Cada persona tiene un nombre único y exacto en todas las hojas?
[ ] ¿El closer cargó todas las llamadas del día con calificado y se presentó?
[ ] ¿CC día 1 y CC trato cerrado están separados (sin contar reservas)?
[ ] ¿El programa ofrecido sigue el formato "producto · plan · cuotas · total"?
[ ] ¿El setter cargó su EOD (mensajes, calendarios, agendas)?
[ ] ¿El calendario de cuotas del mes está armado y con responsable?
[ ] ¿Nadie editó Métricas ni CRM de agendas?
```

## Fuentes

- Base: [[content-capital-ven-l13-crm-de-ventas]] 00:00–11:00 (estructura completa).
- [[content-capital-ven-l06-armado-de-tuberia]] 13:00–17:01, 24:02 (métricas de ventas y lectura direccional).
- Relacionadas: [[metricas-de-la-tuberia-de-negocio]], [[gohighlevel-stack-crm]], [[operaciones-roles-sops-finanzas]], [[calendario-de-agendamiento-calificado]], [[estructura-de-prospeccion-setting]], [[seguimientos-y-reactivacion-de-leads]], [[estructura-de-llamada-de-cierre]], [[manejo-de-objeciones-rap-tie-down]], [[secuencia-pre-call]], [[venta-privada-hand-raisers-y-triage]], [[modalidades-de-pago-y-escalera-de-precio]] (cuotas).
- [[content-capital-out-l03-metricas|OUT L3]] 00:35–09:19 (tracker de outbound).
- Nota: el slug coincide con el que propone la página de fuente de L13.
- Inferencia mía: la plantilla de filas y el paso 7.

- Mapa del hub de ventas (en orden de la tubería): [[estructura-de-prospeccion-setting]] · [[outbound-desde-historias-y-antibloqueo]] · [[seguimientos-y-reactivacion-de-leads]] · [[calendario-de-agendamiento-calificado]] · [[estructura-de-llamada-de-cierre]] · [[puertas-de-cualificacion]] · [[manejo-de-objeciones-rap-tie-down]] · [[venta-privada-hand-raisers-y-triage]] · [[secuencia-pre-call]] · [[estructura-de-venta-cinco-partes]] · [[arsenal-de-ventas-diez-armas]] · [[palancas-psicologicas-de-cierre]] · [[influencia-en-ventas-ethos-autoridad]] · [[metricas-de-la-tuberia-de-negocio]].

## Tensiones internas del curso

- **Quién la dicta**: sin verificar; el instructor no se presenta (L13).
- **Hoja del setter**: en la transcripción aparece un campo que no se entiende ("web 0"); quedó fuera.
