---
title: "Tablero de KPI del negocio: métricas, fórmulas y referencias (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-m4-l05, cc-m4-l04, cc-ent-l09, cc-ent-l13, cc-ent-l16, cc-sho-l07, cc-out-l03]
source_count: 7
created: 2026-09-26
updated: 2026-09-26
tags: [content-capital, framework, plantilla, metricas, kpi, ventas, conversion, adquisicion]
status: developing
---

> **Diagnóstico de la tubería:** [[metricas-de-la-tuberia-de-negocio]].

## Plantilla para llenar

Tablero mensual. Los huecos se llenan con tus datos. La columna KPI es la del curso, no un benchmark verificado.

```
PERÍODO: __________   TICKET (precio total del servicio): $______   TRÁFICO: [frío | tibio]

── 0. TRAMO PAGO (si hay anuncios; PAG) ──────────────────────────────
Gasto en anuncios/mes ....................... $____
CTR ......................................... ____%  KPI >3% (piso 2,5-3%)
Repro 3 s / impresiones ..................... ____%  KPI >27-30%
Costo por conversación / por agenda ......... $____  KPI ≤ tope fijado por ticket
ROAS (ventas / gasto) ....................... ____   KPI ≥3 (mínimo rentable, webinar)

── 1. CONVERSIÓN INICIAL ─────────────────────────────────────────────
Conversaciones/día (inbound+outbound) ....... ____   KPI ≥100/día
Calendarios enviados/día .................... ____   KPI 5-10/día
Tasa de agenda = agendadas / conversaciones . ____%  KPI 2,5% outbound · 4% inbound

── 2. LLAMADAS ───────────────────────────────────────────────────────
Llamadas agendadas/mes ...................... ____   KPI ≥30 (ideal 100)
% calificadas = calificadas / agendadas ..... ____%  KPI 70%
Show rate = presentadas / agendadas ......... ____%  KPI ≥60% (ideal 80%+)
Calificadas presentadas ..................... ____   (la que usa para pagar bonos a setters)

── 3. CIERRE ─────────────────────────────────────────────────────────
Tasa de cierre = ventas / calificadas presentadas ____%
      KPI frío: mín 10 · normal 20 · ideal 30   |   tibio: mín 20 · normal 40 · ideal 50
% cerradas en llamada = en llamada / total .. ____%  KPI ≥50%
% cerradas en seguimiento ................... ____%  KPI equilibrado, ≤50%
Unidades cerradas totales ................... ____   KPI = tu objetivo (al inicio 10-20)

── 4. FINANCIERAS DEL CIERRE ─────────────────────────────────────────
AOV día 1 = cobrado el día de la venta / ventas ...... $____  = ____% del ticket  KPI ≥10% (ideal 25%)
AOV trato cerrado = cobrado para iniciar / ventas .... $____  = ____% del ticket  KPI 33-50% (ideal 50-75%)
% cash collected por venta = cobrado / total del trato ____%  KPI 33%
AOV en cuota ......................................... $____  KPI según servicio
Cobro de cuotas en unidades = pagaron / con cuota .... ____%  KPI ≥50% (ideal 75%)
Cobro de cuotas en dinero = cobrado / a cobrar ....... ____%  KPI 75%
% ingresos de cuotas = cash de cuotas / cash del mes . ____%  KPI 10-20%

── 5. RECOMPRA ───────────────────────────────────────────────────────
Recompra en unidades = recompran / clientes . ____%  KPI 10%
Recompra en % del cash collected ............ ____%  KPI 10%

── 6. VALOR POR CLIENTE ──────────────────────────────────────────────
LTV 12 meses ................................ $____  KPI ≥ pago inicial × 1,3
LTV / AOV trato cerrado ..................... ____   KPI ≥1,3 (ideal 2)
CAC = (anuncios + comisiones setter/closer/confirmador/triager) / clientes nuevos  $____
LTV / CAC ................................... ____   KPI ≥3 (ideal 5-6)

PRIMERA VÁLVULA BAJO KPI: ______________________   ACCIÓN: ______________________
--- Ampliación ORG ---
PERFIL: visita→seguidor ___% (≥1%) · clics link ___ · agendas desde perfil ___
CALIFICACIÓN LLAMADAS ___% (≥60%)   CALIFICACIÓN CUENTA ___% (según volumen de leads)
TIME TO BOOK ___ días
OUTBOUND HISTORIAS: respuesta ___% (~24-25%) · % de agendas ___
BIENVENIDA: seguidores ___ → entregados ___ → respondieron ___ → calificados ___ → bookeados ___
PAUTA: costo/seguidor ___ · CTR ___ · frecuencia ___ · hook rate ___
```

### El tablero completo, métrica por métrica

| Métrica | Qué significa | Por qué importa | KPI según el curso | Cómo detectar el problema |
|---|---|---|---|---|
| **1 · Conversión inicial** | | | | |
| Conversaciones/día | Personas con las que hablás por día, inbound + outbound (M4 L5 13:27) | Es el flujo de agua; "lo más importante" (13:52) | ≥100/día. 100 DMs en frío se hacen "en cuatro horas o menos" (14:03), o con CTAs en contenido o anuncios a DM | Bajo = problema de marketing, comunicación o anuncios (14:44) |
| Calendarios enviados | Veces que compartís el link de agenda (M4 L5 ~14:50) | Mide si ven valor en avanzar | 5-10/día | Bajo = setting o prospección sin motivo real para agendar; o leads muy fríos (15:32) |
| Tasa de agenda | % de conversaciones que agendan | Conexión, urgencia y relevancia (15:54). Según el curso, la etapa que más agua pierde | 2,5% outbound · 4% inbound (16:00–16:16) | 3 lugares: marketing trae gente sin interés, setting no encuentra el dolor, Calendly/formulario con fricción (16:17) |
| **2 · Llamadas** | | | | |
| Llamadas agendadas | Reuniones pautadas por mes | Volumen de entrada a la venta | ≥30/mes (1 por día hábil); ideal 100/mes para USD 10k+/mes (17:10–17:45) | Bajo = volumen (marketing) o ejecución (setting) |
| Calificadas agendadas | Llamadas con gente que cumple criterios mínimos (18:00) | Calidad de los leads | Se mide como %, no cantidad | Marketing que trae a quien no debe, o prospección que no filtra red flags. Ver [[venta-privada-hand-raisers-y-triage]] |
| % calificadas | Calificadas / agendadas (19:08) | Segmentación | 70%: 3 de cada 10 no calificadas "es lógico" (19:20) | Marketing mal segmentado o setting que prioriza cantidad |
| Calificadas presentadas | Calificadas que efectivamente se presentaron (20:02) | "La más importante" del grupo; con ella paga bonos a setters (19:50) | La slide dice "ideal 60%+"; el audio la liga al show rate (ver Tensiones) | Pre-call sin contacto, sin info, sin seguimiento (20:20) |
| Show rate | % de agendadas que asisten | Si no vienen, no hay venta posible | ≥60%, ideal 80%+; más de 80% es "utópico" (21:07) | Mala experiencia pre-llamada, thank you page débil, sin contacto humano, o la prospección no mostró el dolor ni el gap (21:33–21:39). Bajo 60% = fallas graves (21:49) |
| **3 · Cierre** | | | | |
| Tasa de cierre | Ventas / **calificadas presentadas**, no sobre el total (22:34) | "La más importante de todas" del grupo: si está sana, el resto sigue (25:55) | Frío 10/20/30%, tibio ("templado") 20/40/50% = mínimo/normal/ideal (23:04–23:38) | Closer que no presenta bien, no resuelve objeciones o no genera urgencia |
| Cerradas en llamada | Ventas en la misma llamada | Menos seguimiento = proceso más eficiente (24:15) | ≥50% de las ventas (24:24) | Si todo cierra en seguimiento: falta urgencia, autoridad o claridad (24:29) |
| Cerradas en seguimiento | Ventas después de la llamada | Mide el poder del seguimiento (24:47) | Equilibradas, ≤50% (25:01) | Oferta sin acción inmediata → trabajar pitch, gatillos y un bono por decidir en la llamada (25:12) |
| Unidades cerradas totales | Resultado final | Objetivo del mes | Variable; al inicio 10, 15 o 20 (25:31) | Baja sostenida = falla en volumen, calificación, cierre o retención (25:42) |
| **4 · Financieras del cierre** | | | | |
| AOV día 1 | Promedio cobrado el mismo día de la venta | Caja inmediata | ≥10% del ticket; ideal 25% (26:44–27:42) | Compromisos sin pago real; fee cobrado "por vergüenza" de pedir la venta. Alerta: se separa mucho del AOV trato cerrado |
| AOV trato cerrado | Promedio que paga el cliente para iniciar (incluye día 1) | Qué tan accesible y convincente es la entrada | 33-50% del total; ideal 50-75% (28:49–29:27). Programa de 2.500 → ~900 (28:59) | <33% = ventas o precio alto; >80% = precio bajo |
| % cash collected por venta | % cobrado sobre el total del trato (30:01) | Flujo de caja | 33% | >80% barato, <33% caro (30:28) |
| AOV en cuota | Promedio de cada cuota o retainer | Caja diferida "que no tenés que volver a cerrar" | Según servicio | Cuotas bajas + AOV día 1 bajo = financiás sin retorno. "No saquen planes de pago así como sin nada" |
| Cobro de cuotas en unidades | % de clientes con cuota que pagan | Salud del cobro | ≥50%, ideal 75% (32:01) | Servicio sin valor o cobro desorganizado |
| Cobro de cuotas en dinero | Lo mismo en plata | Los deudores grandes pesan más | 75%. Ejemplo: pagan 8 de 10 pero se pierden 5.000 (33:08) | Falta seguimiento extra a quien debe montos altos (33:58) |
| % ingresos de cuotas | Parte del cash mensual que viene de cuotas | Residual de ventas pasadas | 10-20% (34:24) | Si baja, dependés solo de ventas nuevas |
| **5 · Recompra** | | | | |
| Recompra en unidades | % de clientes que vuelven a comprar (35:22) | Si el servicio resolvió y hay próximo paso | 10% (35:32) | Servicio que no resolvió el problema inicial o no ofrece el siguiente |
| Recompra en % del cash | % de ingresos de clientes antiguos (36:07) | Backend | 10% | Sin backend ni upsells, o el cliente no vio valor |
| **6 · Valor por cliente** | | | | |
| LTV 12 meses | Valor promedio que deja un cliente en un año | "Poco medida" en servicios digitales | ≥30% más que el pago inicial (37:40) | Baja entrega de valor o falta de recompra: "100% en el servicio" |
| LTV / AOV trato cerrado | Lo pagado en la vida del cliente vs. al inicio | Monetización de largo plazo | ≥1,3, ideal 2 (38:31) | Sin upsell, sin continuidad, sin seguimiento (39:04): modelo "de una sola venta" |
| **LTV / CAC** | Valor de vida del cliente / costo de conseguirlo (39:34) | "La métrica más importante para cualquier negocio en la historia de los negocios" (39:27) | ≥3, ideal 5-6 (39:45) | Adquisición cara o poca monetización por cliente |

**Cómo mide el CAC el curso**: no solo anuncios. Suma las comisiones del equipo de venta: setter, closer, confirmadores y triager (M4 L5 40:18; M4 L4 12:36). Con LTV/CAC = 3, la rentabilidad es de 66% contando solo marketing y ventas (M4 L5 40:49). Con servicio, plataformas y software puede quedar en 50% o menos (41:02).

- **Ampliación del Programa.** Métricas nuevas por tramo:
  - **Perfil**: visita → seguidor ≥1%, clics en el link, agendas desde el perfil ([[content-capital-org-l07-optimizacion-de-perfil|ORG L7]] 12:49).
  - **Tasa de calificación de llamadas**: ≥ ~60% de las agendas ([[content-capital-org-l10-angulos-de-comunicacion|ORG L10]] 42:05).
  - **Tasa de calificación de la cuenta** según leads por mes (ORG L10 42:16–45:49): ~1.000 → 30% · 1.000-5.000 → ~20% · >5.000 → 10-20% · >10.000 → ~10%. Normalizá a la gente sin plata y filtrá rápido.
  - **Time to Book**: días desde el primer contacto hasta agendar (117 en su caso) (ORG L10 08:17–08:26).
  - **Outbound desde historias**: tasa de respuesta ~24-25% como KPI; el outbound aporta 30-50% de las agendas ([[content-capital-org-l11-detecta-tus-angulos-ganadores-trazabilidad|ORG L11]] 26:25).
  - **Pauta**: costo por seguidor, CTR, frecuencia, hook rate; rentabilidad estimada con la conversión histórica de seguidores, ~10 USD por seguidor en su caso ([[content-capital-org-l12-follow-me-ads|ORG L12]] 17:14, 51:22). Ver [[follow-me-ads-trafico-al-perfil]].

- **Ampliación del tramo pago: métricas antes de la llamada.** En el Administrador de anuncios: alcance (personas únicas) contra impresiones (veces mostrado; 10 de alcance pueden ser 30 impresiones), costo por resultado (gasto / resultados: USD 10 / 2 ventas = 5), CTR ("la métrica de la persuasión"), ROAS (ventas / gasto), CPC y conversiones (en un embudo a VSL, agendar) ([[content-capital-pag-l01-introduccion-publicidad-paga|PAG L1]] 51:26–58:05, 60:17). Detalle y umbrales en [[testeo-y-escalado-de-creativos-meta-ads]].
- **Costo por llamada: métrica principal de las campañas de agenda, pero no es ROAS.** Bartolomé la marca como la métrica principal del embudo pago ([[content-capital-pag-l09-proceso-pre-call-automatizaciones|PAG L9]] 68:40, según el resumen de la lección). Hay que fijar el costo por llamada ideal antes de optimizar: no todas las llamadas agendadas califican, se presentan ni cierran, y si se paga mucho por agenda el ROAS final baja ([[content-capital-pag-l14-escalado-y-optimizacion-de-vsl|PAG L14]] 04:21–04:32).
- **Show rate en el embudo pago**: lo protegen la página de preparación ([[content-capital-pag-l07-armado-de-landing-page|PAG L7]] 06:00) y la [[secuencia-pre-call]] (PAG L9 34:10). En webinar, agendar dentro de 72-96 h ([[content-capital-pag-l15-masterclass-de-webinars|PAG L15]] 49:17).
- **Anuncios a DM** ([[content-capital-pag-l12-embudo-a-dm|PAG L12]] 11:42–16:09): CTR > 3 %, repro 3 s > 27-30 %, repro 50 % > 20 % en videos cortos, costo por resultado contra el ticket (según el curso). Ver [[embudo-pago-a-dm]].


## Tensiones internas del curso

- **Calificadas presentadas.** La slide dice "Ideal: 60%+". El audio dice que es la más importante y la liga al show rate, sin darle un porcentaje propio (M4 L5 19:50–20:49). No queda claro si es cantidad o %.
- **Qué es "lo más importante".** Las conversaciones son "lo más importante" (13:52), la tasa de cierre es "la más importante de todos" en su grupo (25:55), las calificadas presentadas son "la más importante" (19:50), y LTV/CAC es "la más importante en la historia de los negocios" (39:27). Cada una lo es dentro de su grupo; LTV/CAC queda como métrica madre (inferencia).
- **Tasa de agenda: "la etapa que más agua pierde"** según la tasa (2,5-4%), pero en la tubería dice que "la mayoría" pierde en las objeciones (~08:15). Son dos pérdidas distintas: volumen arriba, venta abajo (inferencia).
- **Transcripción dudosa**: en 00:43 el audio dice "de 50 a 5 conversaciones"; lo lógico es 50 → 100 (inferencia de la página de lección).
- **Todos los KPI y montos** son reglas del instructor sacadas de sus negocios, sin datos que los respalden.
- **Calificación: 70% (M4) vs. ≥60% (ORG L10 42:05)** para las llamadas; y 10-30% para la cuenta según volumen. Son tramos distintos (inferencia), pero los números no coinciden entre clases.

- **Tasa de agenda: 2,5-4% (M4 L5) vs. 5% (10% en oportunidad de negocio) en VEN L8 41:00**, que además dice que 20% no es sostenible. Cifras habladas de instructores distintos.
- **KPI de calificación dentro de VEN L6**: 35% en 01:02 y 65-75% en 26:00. Inconsistencia del instructor.

- **Show rate.** El tablero de M4 pide ≥60 % (ideal 80 %+); en webinar, Mati Molina trabaja con ~70 % de show para dimensionar closers (PAG L15 51:15) y un show al evento de ~20 % (PAG L15 57:00). Son dos métricas distintas (asistir a la llamada contra asistir al webinar), pero comparten nombre.
- **Otra "métrica principal".** El tramo pago suma el costo por llamada como métrica principal (PAG L9 68:40), mientras M4 reserva ese lugar para la tasa de cierre y LTV/CAC. Lectura posible: costo por llamada es la principal del lado de anuncios, LTV/CAC sigue siendo la madre (inferencia).

## Ejemplos y ampliaciones numéricas

Ampliación del Programa: embudo de bienvenida de SYK ([[content-capital-org-l11-detecta-tus-angulos-ganadores-trazabilidad|ORG L11]] 27:54) — 4.912 nuevos seguidores → 2.947 entregados (60% de entregabilidad) → 648 respuestas (22%; ideal 30%) → 89 → 14 bookeados (0,29%) (anécdota).

Ampliación del tramo pago (webinar, [[content-capital-pag-l15-masterclass-de-webinars|PAG L15]]):
- **Matemática de closers** (51:15): máximo 7-8 llamadas efectivas por día y por closer, 11-12 agendadas (asumiendo ~70 % de show), ideal sostenible 6-7. Ejemplo: 300 presentes al pitch × 30 % = 90 llamadas en 3 días → 4-5 closers.
- **Webinar real a llamada** (anécdota, 58:38): show ~27 %, retención ~88 %, agendas 16 % con filtro, cierre 15 %, CAC ~120, ROAS 9.
- **Números de referencia** (KPI según el curso, 57:00): show ~20 % (pico de viewers / registros), retención al pitch ~80 %, apertura WhatsApp ≥ 40 %, email ≥ 15 %, agendas/presentes 25-50 % sin filtro y 15-20 % con filtro, ROAS mínimo 3. Ver [[embudo-de-webinar-a-llamada]].


## Ampliaciones verificadas en otras lecciones

- **LTGP/CAC > 3:1:** ENT L9 distingue el valor facturado (LTV) de la ganancia bruta de por vida (LTGP = LTV × margen bruto). Propone LTGP/CAC mayor a 3:1, ideal 5:1 o más en servicios; no confundir con LTV/CAC. [[content-capital-ent-l09-como-hacer-que-tus-clientes-te-paguen-mas]] 05:26–06:50.
- **Calculadora inversa:** ENT L13 va de 800 conexiones/mes × 40% aceptación × 40% respuesta × 15% interés × 20% cierre ≈ 4 ventas. La clase advierte que las cifras habladas son aproximadas. [[content-capital-ent-l13-entrega-de-servicio-agencia]] 05:35–07:04.
- **Cash collected por fuente:** el tablero financiero de ENT L16 permite filtrar cobros por fuente, concepto, producto, mes y rango de fechas. [[content-capital-ent-l16-finanzas-y-contabilidad]] 01:18.
- **Subsistemas y estrella polar:** SHO L7 mide atención → interés → agenda → asistencia → preparación → cierre. Para un subsistema que busca reuniones, la estrella polar son las agendas; la tasa de agenda (ABR) es su indicador principal. Los KPI son metas del subsistema, no hechos universales. [[content-capital-sho-l07-introduccion-a-la-prospeccion]] 60:37–69:00.
- **Conexión y vista del video:** OUT L3 usa la tasa de aceptación para diagnosticar el perfil y la columna «vio el video» para evaluar el estímulo y su entrega. No da fórmulas ni umbrales exactos. [[content-capital-out-l03-metricas]] 02:40, 09:32–09:52.

