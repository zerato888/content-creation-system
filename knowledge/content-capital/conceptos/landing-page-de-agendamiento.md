---
title: "Landing page de agendamiento + página de preparación (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-pag-l07, cc-pag-l06, cc-pag-l09, cc-pag-l15]
source_count: 4
created: 2026-09-25
updated: 2026-09-25
tags: [content-capital, cc-pag, framework, checklist, plantilla, landing-page, vsl, conversion, cta, gohighlevel]
status: developing
---

## En una línea

Un embudo de dos páginas: una **landing con el VSL arriba y el calendario abajo**, armada como "panel, botón, panel, botón", y una **página de preparación** que se ve al agendar y sube la asistencia.

## Qué es y por qué funciona (según el curso)

- Antes de diseñar, elegir el tipo de embudo: captación, agendamiento o webinar. El estándar del curso es landing con VSL → agendamiento ([[content-capital-pag-l07-armado-de-landing-page|PAG L7]] 01:20).
- La landing es "un VSL desglosado en texto" ([[content-capital-pag-l06-principales-funcionalidades-de-ghl|PAG L6]] 78:00): repite por escrito la lógica del video ([[estructura-del-vsl]]) para quien no lo mira entero.
- Primero que funcione, después que sea linda (L7 07:30). La oferta distinta pesa más que el diseño (L6 61:00-63:30).
- La página de preparación existe para nutrir y subir la asistencia a la llamada (L7 05:00-06:00). Se repite el link en los recordatorios porque no todos la ven ([[content-capital-pag-l09-proceso-pre-call-automatizaciones|PAG L9]] 45:20).

## Cuándo usarlo / cuándo no

- **Sí**: cuando el destino del anuncio o del link del perfil es agendar una llamada ([[embudo-pago-a-vsl]]).
- **No todavía**: si recién arrancás y agendás por chat, no gastes semanas en VSL y landing (L7 44:40).
- **Variantes** (L7 38:40): pre-landing de captación (nombre, email, teléfono) antes del VSL, o solo VSL + calendario. Si la llamada sale cara (ej. USD 50, según el curso), testear otra variante.
- Webinar: la landing de registro sigue una lógica parecida (hero, proceso, quién sos, casos, FAQ, botón tras cada sección) ([[content-capital-pag-l15-masterclass-de-webinars|PAG L15]]); ver [[embudo-de-webinar-a-llamada]].

## Pasos

1. Elegir tipo de embudo y plantilla del constructor (sección → fila → columna → elemento; L7 10:00).
2. Diseñar **celular primero**, con tamaños propios para mobile (L7 17:10).
3. Armar las secciones en el orden de la plantilla (L7 12:50-39:10). El orden exacto de los paneles "es cuestión de probar" (L6 80:00).
4. Subir el VSL a un reproductor que mida el % visto (Wistia en el curso) y ponerlo **visible sin scrollear**.
5. Poner un botón "Agendar llamada" después de cada panel: baja al calendario, abre un pop-up o lleva a otra página.
6. Embeber el calendario rotativo ([[gohighlevel-stack-crm]]) con el formulario de calificación.
7. Configurar la confirmación del calendario para que lleve a la página de preparación.
8. Conectar dominio propio y medir.

## Plantilla para llenar

```
LANDING DE AGENDAMIENTO — [NEGOCIO]

S1 · CABECERA
   logo + FILTRO DE NICHO: "Solo para ___ con ___"   (quien no es del nicho se va)
S2 · TÍTULO (promesa corta): "___"
     SUBTÍTULO (mecanismo o prueba): "___ en automático / sin ___"
S3 · VSL (visible sin scrollear, reproductor con % visto)
     [BOTÓN] Agendar llamada
S4 · RESULTADOS / TESTIMONIOS (tarjetas video + texto, justo después del VSL)
     "___ pasó de ___ a ___ en ___"  x3
     [BOTÓN]
S5 · ¿PARA QUIÉN ES?  dolores: ___ / ___ / ___   deseos: ___ / ___
     ¿QUÉ VAS A CONSEGUIR?  3 beneficios con ícono: ___ / ___ / ___
     [BOTÓN]
S6 · CÓMO FUNCIONA / ENTREGABLES: paso 1 ___ · paso 2 ___ · paso 3 ___
S7 · SOBRE NOSOTROS (autoridad): ___
     GARANTÍA: ___
     PREGUNTAS FRECUENTES: ___? / ___? / ___?
     [BOTÓN]
S8 · PANEL DE AGENDAMIENTO
     "Estás a un paso de ___"
     Para qué es la llamada de valoración gratuita: ___
     Urgencia: "___ (ej. solo esta semana)"
     Escasez: "___ (ej. cupos para ___ clientes por mes)"
     [CALENDARIO EMBEBIDO + formulario de calificación]

DISEÑO: tipografía [Poppins | Montserrat] · títulos 50-55 · subtítulos 25-30 (siempre iguales)
        margin vs padding · cambiar solo el ancho de imágenes · color picker de la marca · guardar seguido

PÁGINA 2 · PREPARACIÓN (confirmación del calendario)
   Título: "Tu llamada fue agendada con éxito, pero es necesario que sigas estos pasos"
   Video de preparación (closer o fundador): ___
   Qué va a pasar en la llamada: ___
   Testimonios: ___
   Próximos pasos: vas a recibir un WhatsApp de ___ · confirmá respondiendo · horario ___ · ten a mano ___
```

## Ejemplos del curso desarmados

| Pieza (min) | Qué hace | Por qué, según el curso |
|---|---|---|
| Landing de nicho solar (L7 12:50) | "Solo para empresas solares con trayectoria" arriba del título | El filtro echa al que no es del nicho antes de que agende |
| Subtítulo "Generando prospectos y citas de venta en automático" (L7 12:50-17:00) | Mecanismo debajo de la promesa | La promesa sola no alcanza: el subtítulo dice cómo |
| Landing de SYK (L6 77:00-79:00) | Testimonios justo después del VSL; luego autoridad, garantía y FAQ | La prueba va donde aparece la duda |
| Panel de agendamiento (L7 35:50) | "Estás a un paso de…" + urgencia + escasez + calendario | Cierra la página con un motivo para agendar hoy |
| Página de preparación (L7 05:00; L9 45:20) | Video + próximos pasos | Sube la asistencia; el lead llega preparado |

## Errores comunes

- VSL abajo de la línea de scroll o sin medición de % visto (L7 12:50-17:00).
- Diseñar en escritorio y dejar que el celular se acomode solo (L7 17:10).
- Tipografías y tamaños distintos en cada panel (L7 17:10).
- Casos de estudio largos en la landing: van mejor en el VSL (L7 39:50).
- Frenarse por no tener testimonios: se puede cerrar sin ellos al principio (L7 39:50).
- Olvidarse de la página de preparación: el lead agenda y se enfría (L7 05:00).

## Checklist para agentes

```
[ ] ¿Hay un filtro de nicho visible arriba del título?
[ ] ¿El título es una promesa corta y el subtítulo dice el mecanismo o la prueba?
[ ] ¿El VSL se ve sin scrollear y se mide el % visto?
[ ] ¿Hay un botón de agendar después de cada panel?
[ ] ¿Los testimonios están cerca del VSL?
[ ] ¿El panel final tiene deseo + para qué es la llamada + urgencia + escasez + calendario?
[ ] ¿La confirmación del calendario lleva a una página de preparación con video y próximos pasos?
[ ] ¿Se diseñó primero para celular, con tipografía y tamaños fijos?
[ ] ¿La oferta es distinta, y no solo el diseño lindo?
```

## Fuentes

- Base: [[content-capital-pag-l07-armado-de-landing-page]] 01:20-39:50 (estructura completa y diseño).
- [[content-capital-pag-l06-principales-funcionalidades-de-ghl]] 61:00-80:00 (landing como VSL desglosado, landing de SYK, orden de paneles).
- [[content-capital-pag-l09-proceso-pre-call-automatizaciones]] 45:20 (página de gracias con video).
- [[content-capital-pag-l15-masterclass-de-webinars]] (landing de registro de webinar).
- Inferencia mía: la numeración S1-S8 ordena la demo de L7 con la landing de SYK de L6; el curso no fija un orden único.

## Tensiones internas del curso

- **Orden de los paneles**: L7 pone "para quién es" antes de los testimonios; la landing de SYK pone los testimonios justo después del VSL (L6 77:00). El propio instructor dice que el orden es cuestión de probar (L6 80:00).
- **Invertir en la landing vs. no hacerlo**: L7 enseña a armarla con detalle y en 44:40 dice que si recién arrancás no gastes semanas en eso.
- **Urgencia y escasez**: el curso las pide en el panel, pero no dice cómo evitar que sean inventadas (ver [[palancas-psicologicas-de-cierre]], que pide que el contraste no sea rebuscado).
