---
title: "Estructura de campañas en Meta: campaña → conjunto → anuncio (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-pag-l04, cc-pag-l01, cc-pag-l05, cc-pag-l12, cc-pag-l13, cc-pag-l15, cc-pag-l09]
source_count: 7
created: 2026-09-25
updated: 2026-09-25
tags: [content-capital, cc-pag, framework, checklist, plantilla, anuncios, meta-ads, pauta, embudo]
status: developing
---

## En una línea

Toda cuenta se lee en tres niveles: la **campaña** fija UN objetivo, el **conjunto** fija presupuesto, público y ubicaciones, y el **anuncio** es el creativo con su copy. Se crea todo a mano, con nomenclatura que deja ver qué corre sin abrir nada, y cambiando una sola variable por vez.

## Qué es y por qué funciona (según el curso)

- **Campaña = objetivo.** Reconocimiento, tráfico, interacción, clientes potenciales, promoción de la app o ventas ([[content-capital-pag-l04-jerarquia-de-campanas|PAG L4]] 00:31, 01:16). Uno solo por campaña ([[content-capital-pag-l01-introduccion-publicidad-paga|PAG L1]] 58:43).
- **Conjunto = presupuesto diario, públicos y plataformas** (PAG L4 01:56).
- **Anuncio = lo que ve el usuario** (foto, video, carrusel), "la parte creativa" (PAG L4 02:30, 10:54).
- **Todo manual.** "Nosotros queremos correr las campañas de manera manual" (PAG L4 01:06): siempre "Crear" → "Campaña manual de X", nunca Promocionar ni la configuración recomendada Advantage (PAG L4 00:53, 04:17; [[content-capital-pag-l05-audiencias|PAG L5]] 26:40). "Tenemos que saber que tenemos todo bajo nuestro control" (PAG L4 04:51).
- **La nomenclatura es control.** Con 10-15 clientes, el orden visual sirve para reportar y para controlar al *trafficker* (PAG L5 29:05).
- **1-1-1 es la "estructura primitiva".** Hay estrategias con una campaña y 20-25 conjuntos (PAG L4 14:58). Este video enseña la jerarquía, no una estrategia (PAG L4 16:07).

## Cuándo usarlo / cuándo no

Qué objetivo elegir según el embudo (según el curso):

| Embudo | Objetivo de campaña | Objetivo de rendimiento | Fuente |
|---|---|---|---|
| Likes, comentarios, seguidores | Interacción | Maximizar la interacción con la publicación | PAG L4 06:32–06:54 |
| DM / WhatsApp | Interacción | App de mensajes → **maximizar conversaciones** (no clics) | [[content-capital-pag-l12-embudo-a-dm\|PAG L12]] 03:05, 23:47 |
| Landing con VSL que agenda | Clientes potenciales, conversión en sitio web | **Maximizar conversiones** (evento Cliente potencial) | [[content-capital-pag-l13-embudo-a-vsl\|PAG L13]] 01:22, 10:16 |
| Landing con checkout | Ventas | — | PAG L13 01:22 |
| Registro a webinar | Conversión por registro (Complete Registration o Lead) | — | [[content-capital-pag-l15-masterclass-de-webinars\|PAG L15]] 32:53 |
| Anuncios a registrados (hammer) | Interacción | ThruPlay | PAG L15 36:57, ver [[hammer-them-ads]] |

- **Cuándo dividir en varias campañas**: cuando cambia la temperatura. En VSL, el remarketing va en una campaña aparte "por orden" (PAG L13 33:52). En webinar, una campaña por hook/ángulo; los ángulos nuevos se prueban aparte (PAG L15 33:37).
- **No usar** esta estructura para decidir públicos o presupuestos de escala: eso está en [[audiencias-meta-por-temperatura]] y [[testeo-y-escalado-de-creativos-meta-ads]].

## Pasos

1. **Crear** desde el botón "Crear" del Administrador de anuncios → objetivo → **campaña manual** (PAG L4 00:53, 04:17).
2. **Nombrar la campaña**: OBJETIVO en mayúscula + fecha ("INTERACCIÓN – 21/10", "TRÁFICO – 30/10", "VSL funnel – fecha") (PAG L4 04:53; PAG L5 26:19; PAG L13 02:17).
3. **Presupuesto**: por defecto, desactivar "Presupuesto de la campaña Advantage+" (el presupuesto va en el conjunto) y la prueba A/B nativa (PAG L4 05:41–05:57). La excepción CBO está en Tensiones.
4. **Conjunto**:
   - objetivo de rendimiento y evento de conversión (ver tabla);
   - presupuesto diario (mínimo para testear; ver [[testeo-y-escalado-de-creativos-meta-ads]]);
   - Controles de público → "Usar público original" → demografía + personalizados/similares + segmentación detallada (PAG L4 07:16–07:35);
   - **ubicaciones manuales**: sacar Audience Network ("está lleno de bots") (PAG L1 59:40; PAG L5 29:50).
5. **Nombrar el conjunto** con el público + fecha: "BROAD AUTOMATIC – 30/10", "LAA 1% WV 180D", "DETAILED TARGETING (fecha)" (PAG L5 27:10, 32:54, 41:43).
6. **Anuncio**: verificar página e Instagram (PAG L4 11:10); subir el archivo o usar una publicación existente (PAG L4 11:27); formato correcto para que Meta no agregue márgenes (PAG L4 12:20); **texto principal** obligatorio (PAG L4 13:57). Con destino web: URL de la landing y seguimiento del conjunto de datos activado (PAG L13 17:17–17:56).
7. **Nombrar el anuncio** sin fecha: "AD01 – [hook]" (PAG L4 10:35; PAG L12 25:30; PAG L13 18:23).
8. **Duplicar para testear**, cambiando una sola variable: mismo anuncio en BROAD AUTOMATIC / BROAD IG / BROAD FB para hallar la plataforma ganadora; mismo público con AD01…AD05 para aislar el creativo (PAG L5 31:13–32:12; PAG L12 26:22–27:44).
9. **Publicar** y no tocar hasta la ventana de evaluación.

## Plantilla para llenar

```
CAMPAÑA ─────────────────────────────────────────────────────────
Nombre: [OBJETIVO] – [DD/MM]            ej.: CLIENTES POTENCIALES – 30/10
Objetivo: [interacción | tráfico | clientes potenciales | ventas | registro]
Configuración: MANUAL (no recomendada / no Promocionar)
Presupuesto Advantage+ (CBO): [OFF por defecto | ON solo si ______]
Prueba A/B nativa: OFF

CONJUNTO (uno por público o por creativo a testear) ─────────────
Nombre: [PÚBLICO] – [DD/MM]              ej.: BROAD IG – 30/10 · LAA 1% WV 180D
Rendimiento: [max. conversaciones | max. conversiones | max. interacción | ThruPlay]
Evento de conversión: ______ (Cliente potencial / Schedule / registro)
Presupuesto diario: USD ____
Público: [original] · país ____ · edad ____ · sexo ____ · idioma ____
Advantage de público: OFF
Ubicaciones manuales: [IG] [FB] [Messenger] — Audience Network: OFF
Exclusiones: ______

ANUNCIO ─────────────────────────────────────────────────────────
Nombre: AD0_ – [hook]
Identidad: página ____ · Instagram ____
Formato/medida del creativo: ______
Texto principal: ______
CTA: ______   Destino: ______   Seguimiento del conjunto de datos: ON
```

## Ejemplos del curso desarmados

| Ejemplo (min) | Campaña | Conjunto | Anuncio | Qué enseña |
|---|---|---|---|---|
| Práctica de interacción (PAG L4 04:17–13:57) | "INTERACCIÓN – 21/10", manual, Advantage+ OFF | "CONJUNTO 1 – 21/10", Argentina, ~1 USD/día | "ANUNCIO 1", sin CTA ni destino | La jerarquía mínima; en interacción no hay CTA |
| Test de plataforma (PAG L5 24:31–32:12) | "TRÁFICO – 30/10" | BROAD AUTOMATIC / BROAD FACEBOOK / BROAD INSTAGRAM | El mismo en los tres | Duplicar cambiando solo la ubicación |
| Embudo a DM (PAG L12 21:07–27:44) | "mensajes" + fecha | "broad IG" + fecha, solo Instagram | AD01…AD05, uno por conjunto, con el hook como nombre | Aislar la variable creativo en un público broad |
| Embudo a VSL (PAG L13 02:17–33:20) | "VSL funnel" + fecha, clientes potenciales | 7 conjuntos fríos (broad, LAA, intereses, video) | AD01 + hook, máx. 4-5 por conjunto | Un "mini funnel de públicos fríos" |
| Remarketing VSL (PAG L13 33:52) | "VSL funnel remarketing" + fecha | Web visitors 90 / 120, IG engagement por ventana | Creativos distintos | Temperatura distinta = campaña aparte |

## Errores comunes

- Crear con Promocionar o con la configuración recomendada (PAG L4 00:53; PAG L5 26:40).
- Dejar Audience Network prendido (PAG L1 59:40).
- Elegir "maximizar clics" en vez de conversaciones o conversiones: Meta busca gente que clickea pero no escribe ni agenda (PAG L12 23:47; PAG L13 10:16).
- Cambiar anuncio y público a la vez: no se sabe qué variable movió el resultado (PAG L12 18:57).
- Meter demasiados creativos en un conjunto: Meta "hoy no reparte bien" (PAG L13 18:23).
- Pedir el creativo sin la medida correcta (PAG L4 12:20).
- Nombres genéricos que obligan a abrir cada conjunto para saber qué corre (PAG L5 27:10).

## Checklist para agentes

```
[ ] ¿La campaña se creó en modo manual, con un solo objetivo?
[ ] ¿El objetivo de rendimiento es la acción real (conversación / conversión), no clics?
[ ] ¿El nombre de la campaña lleva OBJETIVO + fecha?
[ ] ¿El nombre del conjunto lleva PÚBLICO + fecha?
[ ] ¿El anuncio lleva AD0X + hook, sin fecha?
[ ] ¿Audience Network está apagado y las ubicaciones son manuales?
[ ] ¿Está definida la elección de presupuesto (conjunto por defecto; CBO solo con motivo)?
[ ] ¿Cada duplicado cambia una sola variable?
[ ] ¿El creativo tiene la medida correcta y texto principal?
[ ] Si el destino es web: ¿seguimiento del conjunto de datos activado?
```

## Fuentes

- Base: [[content-capital-pag-l04-jerarquia-de-campanas]] (jerarquía, creación manual, nomenclatura).
- [[content-capital-pag-l01-introduccion-publicidad-paga]] 58:43–60:17 (glosario de niveles y ubicaciones).
- [[content-capital-pag-l05-audiencias]] 24:31–46:36 (nomenclatura de conjuntos, duplicación).
- [[content-capital-pag-l12-embudo-a-dm]] 03:05, 21:07–27:44 (objetivos del embudo a DM).
- [[content-capital-pag-l13-embudo-a-vsl]] 01:22–33:52 (objetivos y estructura del embudo a VSL).
- [[content-capital-pag-l15-masterclass-de-webinars]] 32:03–37:50 (CBO, Advantage+, campañas por ángulo).
- [[content-capital-pag-l09-proceso-pre-call-automatizaciones]] 69:40–77:00 (Advantage+ con los mejores creativos, según el resumen de la lección).
- Inferencia mía: la tabla de objetivo por embudo junta lo que el curso dice en clases distintas.
- Conexiones: la estructura aplicada por embudo en [[embudo-pago-a-dm]] y [[embudo-pago-a-vsl]].

## Tensiones internas del curso

- **ABO contra CBO.** Nico Donovan apaga el presupuesto de campaña Advantage+ y controla todo desde el conjunto (PAG L4 05:41). Mati Molina, para webinars, usa CBO con gasto mínimo por anuncio y Advantage+ con muchos creativos (PAG L15 32:03–33:37). Nico Bartolomé propone Advantage+ con los 3 mejores creativos en vez de un anuncio por conjunto (PAG L9 69:40–77:00). Lectura posible (inferencia): ABO para testear y aislar variables; CBO/Advantage+ cuando ya hay creativos probados y volumen.
- **Un anuncio por conjunto contra 4-5.** En DM, un creativo por conjunto (PAG L12 03:05); en VSL, hasta 4-5 por conjunto (PAG L13 18:23).
- **Messenger.** En el glosario "Messenger sí" (PAG L1 59:40); en el broad Instagram del VSL se saca junto con Facebook (PAG L13 15:22). Depende de dónde esté el público.
