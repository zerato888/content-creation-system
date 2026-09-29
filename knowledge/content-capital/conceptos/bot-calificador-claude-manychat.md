---
title: "Bot calificador ManyChat + Claude: la IA clasifica, no redacta (Content Capital)"
type: concept
course: content-capital
source_lessons: [cc-mc-l14]
source_count: 1
created: 2026-09-25
updated: 2026-09-25
tags: [content-capital, cc-mc, manychat, ia, framework, checklist, plantilla, automatizacion, dm, ventas, conversion]
status: developing
---

## En una línea

Cada etapa del setting es un flujo de ManyChat: el lead responde, la respuesta se guarda en un campo, Claude la **clasifica** y devuelve un JSON con una palabra clave (`resultado`) y un `motivo`, y ese campo cambiado dispara el flujo siguiente. Claude nunca escribe mensajes: solo elige cuál de los mensajes ya guardados mandar.

## Qué es y por qué funciona (según el curso)

- Lo muestra Paolo en una consultoría en vivo, con un nicho de ejemplo: mentoría de reparación de crédito ([[content-capital-mc-l14-manychat-claude|MC L14]] 00:00, 03:43). Aclara que ese nicho no es su especialidad (MC L14 04:03).
- **Clasificador, no redactor**: el bot solo dispara automatizaciones guardadas (textos y audios propios). "Es un bot determinista como un bot de banco" y "nunca va a alucinar" (MC L14 30:47, 42:03, 42:28).
- **Ante la duda, descalifica**: si el lead contesta algo fuera de guion, el bot no responde y lo deja descalificado; el setter puede rescatarlo. "No calificar" no es "no atender" (MC L14 21:17, 41:58).
- **El motivo sirve para auditar**: cada JSON trae el porqué en pocas palabras; con eso corrigió el bot "máximo dos veces" (MC L14 05:54).
- **Flujos independientes**: el setter puede lanzar el bot desde cualquier pregunta, no solo desde el principio (MC L14 03:00, 40:02).
- Según él, el bot agenda solo unas 4-5 llamadas por día y el resto lo sigue un setter; cuesta "no más de 10 dólares al mes" (MC L14 02:41, 14:23; anécdotas).

## Cuándo usarlo / cuándo no

- **Sí**: cuando ya tenés una estructura de prospección que convierte; si no, primero ir a arquitectura de ventas (MC L14 01:08).
- **Empezá chico**: calificar y mandar el calendario. No armes el bot entero de una (MC L14 01:44).
- **Ramificar a rants** solo cuando ya tenés 4-5 rants específicos grabados (MC L14 26:10).
- **No**: para conversar libremente ni para responder dudas abiertas: el bot no improvisa (MC L14 41:58).
- **No** en ticket alto como reemplazo del setter (ver [[manychat-setting-automatizado]]; inferencia a partir de MC L1 06:22).

## Pasos

1. **Escribí la estructura de prospección** (preguntas, rants, casos de éxito, pitch, calendario) y grabá los audios (MC L14 06:30, 30:47).
2. **Pedile a Claude el prompt calificador** de cada pregunta ("armame un prompt calificador") y sumale reglas propias (MC L14 04:55).
3. **Conectá la API de Claude** en la configuración de ManyChat (dice que carga desde USD 5). No compartas la clave en ningún documento (MC L14 13:53).
4. **Flujo 1 (arranque)**: disparador palabra clave con condición **"es"**, no "contiene", para que un texto largo no lo dispare (MC L14 10:21). En su sistema, la palabra la genera la pregunta de los reels o carruseles ("digital") (MC L14 07:28).
5. **Anti doble disparo**: acción que agrega la etiqueta "flow Claude" + condición "si no tiene la etiqueta flow Claude" (MC L14 12:28).
6. **Pregunta como recopilación de datos**, con retrasos (MC L14 11:04).
7. **Guardá la respuesta**: establecer un campo = última entrada de texto (MC L14 13:19).
8. **"Realizar solicitud" a Claude**: modelo Sonnet 4.6, prompt calificador, último mensaje = ese campo, temperatura 0,3, máximo 500 tokens, resultado a otro campo (MC L14 14:23-16:19).
9. **Flujo siguiente**: disparador "campo personalizado cambiado" **contiene** la palabra positiva ("contiene" porque el campo también trae el motivo) (MC L14 17:19).
10. **Repetí por etapa**: pregunta 2 → pregunta 3 → rant elegido por Claude → caso de éxito (sin Claude, pausa de 10 s) → Claude decide si está listo para el pitch → pitch → Claude decide si aceptó → flujo de calendario (MC L14 18:32-51:18).
11. **Probalo en vivo** desde tu cuenta (borrando tu contacto para reiniciar) y revisá los motivos en la bandeja (MC L14 37:26, 42:30).

## Plantilla para llenar

```
OFERTA: ______________   PALABRA DE ARRANQUE: "______" (condición: ES)
ETIQUETA ANTI-DOBLE: "flow Claude"  (condición: no tiene la etiqueta)

POR ETAPA (copiar una vez por pregunta):
  FLOW N — disparador: [palabra clave ES "____" | campo "______" cambiado CONTIENE "______Positivo"]
  PREGUNTA (recopilación de datos, con retraso): "______________"
  CAMPO RESPUESTA: ______ = última entrada de texto
  SOLICITUD CLAUDE: modelo Sonnet · temperatura 0,3 · máx. 500 tokens
    último mensaje del usuario = CAMPO RESPUESTA
    guardar resultado en = CAMPO RESULTADO ______
  KEYWORD POSITIVA: "______Positivo"   → dispara FLOW N+1

PROMPT CALIFICADOR:
  Eres un clasificador de leads para [OFERTA]. Analizas la respuesta a "[PREGUNTA]"
  y decides si califica. Ante cualquier duda responde descalificado.
  CALIFICA SI: ______________
  DESCALIFICADO AUTOMÁTICO: ______________ (incluir evasivas: "no sé", "ni idea", "luego te digo")
  RESPUESTAS FUERA DE CONTEXTO: si responde algo que no es [tipo de dato], descalificar.
  RESPUESTA: Responde ÚNICAMENTE en formato JSON sin texto adicional:
  {"resultado": "______Positivo", "motivo": "[máximo 10 palabras]"}
  {"resultado": "descalificado", "motivo": "[máximo 10 palabras]"}

PROMPT DE ELECCIÓN (rants):
  Devolvé una sola: ____RanteoA / ____RanteoB / ____RanteoC / descalificado
  Interpretá sinónimos. Si nombra dos, elegí ______ (jerarquía).
  → cada keyword dispara el flow del rant guardado

CASO DE ÉXITO (sin Claude): pausa 10 s → [caso] → "¿te gustaría lograr algo similar?"
PROMPT "LISTO PARA PITCH" / "LISTO CALENDARIO":
  CALIFICA SI: cualquier respuesta positiva (ok, dale, sí, de una, mandame)
  SI HAY DUDA O "SÍ, PERO…": no califica
PITCH: "si te parece, agendamos una llamada… ______ te paso calendar"
CALENDARIO: "acá te envío el calendario, avisame así le doy prioridad" + [link]
```

## Ejemplos del curso desarmados

| Etapa (min) | Pregunta | Regla de Claude | Keyword |
|---|---|---|---|
| Estado (MC L14 11:04, 06:30) | "¿de qué estado me escribís?" | Califica solo estados de EE. UU. (un mexicano que vive en Texas califica); fuera de contexto ("tengo deudas") → descalificado | EstadoCalificadoPositivo |
| Score (MC L14 18:32, 21:30) | "¿tu crédito cómo anda? ¿cuánto te está dando el score?" | 300-670 ideal; 671-720 con margen; 721+, sin archivo de crédito o evasivas → no | ScoreCalificadoPositivo |
| Objetivo (MC L14 25:07-27:05) | "¿para qué lo necesitás exactamente? ¿casa, carro, o sacarte deudas de encima?" | Ya no califica: elige el rant; interpreta sinónimos; si nombra dos, el más fácil de rantear; "timeline no importa" | CalificadoRanteoCasa / Auto / Deudas / Tarjetas |
| Caso de éxito (MC L14 44:07) | Caso ficticio de un cliente de Houston + "¿te gustaría lograr algo similar?" | Sin Claude: va siempre después del rant | — |
| Pitch (MC L14 46:45, 49:34) | "agendamos una llamada… te paso calendar" | Positivo claro = sí; duda = no | ListoParaPichearPositivoCredito |
| Calendario (MC L14 51:18, 55:39) | Respuesta al pitch | "ok, dale, sí, de una" = sí; "sí, pero…" = no | ListoCalendarPositivoCredito |
| Prueba en vivo (MC L14 42:30) | "400" | El campo muestra: "score 400, rango muy bajo, ideal para reparar" | — |

## Errores comunes

- Armar el bot completo desde el día 1 (MC L14 01:44).
- Usar "contiene" en la palabra de arranque: un mensaje largo lo dispara sin querer (MC L14 10:21).
- Usar "es" en los flujos siguientes: el campo trae también el motivo, entonces nunca coincide (MC L14 17:19).
- No poner la etiqueta anti-doble disparo (MC L14 12:28).
- Dejar que la IA redacte las respuestas: se pierde el control y aparece la alucinación (inferencia a partir de MC L14 30:47, 42:28).
- Prompt sin "ante cualquier duda, descalificá" ni reglas para respuestas fuera de contexto (MC L14 04:55, 06:30).
- No leer los motivos para corregir el prompt (MC L14 05:54).
- Olvidar que el setter tiene que rescatar a los descalificados (MC L14 21:17).

## Checklist para agentes

```
[ ] ¿La estructura de prospección ya convierte sin el bot?
[ ] ¿El bot empieza solo por calificar + calendario?
[ ] ¿La palabra de arranque usa "es" y los flujos siguientes "contiene"?
[ ] ¿Hay etiqueta "flow Claude" contra el doble disparo?
[ ] ¿Cada prompt dice "ante cualquier duda, descalificado" y trata respuestas fuera de contexto?
[ ] ¿La salida es SOLO JSON con resultado + motivo (≤10 palabras)?
[ ] ¿Temperatura 0,3 y tope de tokens definidos?
[ ] ¿Claude solo elige mensajes guardados, nunca los redacta?
[ ] ¿Los rants existen (4-5 específicos) antes de ramificar a ellos?
[ ] ¿Un setter revisa y rescata a los descalificados?
[ ] ¿La clave de la API quedó fuera de todo documento?
```

## Fuentes

- Base: [[content-capital-mc-l14-manychat-claude]] (00:00-58:49).
- Relacionadas: [[manychat-setting-automatizado]] · [[manychat-bases-y-flujos]] · [[guionado-iterativo-con-ia]] (Claude redacta el prompt) · [[venta-privada-hand-raisers-y-triage]] · [[arsenal-de-ventas-diez-armas]] · [[gohighlevel-stack-crm]] (setter de IA en otra herramienta).
- Inferencia mía: la plantilla generaliza los prompts del ejemplo de crédito; los prompts completos se leen solo en parte en pantalla.

## Tensiones internas del curso

- **Bot que agenda solo vs. "no automatices el 100%".** MC L1 05:45 desaconseja automatizar todo; MC L14 muestra un bot que agenda sin setter. Se concilia porque el bot solo pasa a los muy calificados y el resto vuelve al setter (MC L14 21:17; inferencia).
- **Clasificador vs. conversador.** En [[gohighlevel-stack-crm]] el setter de IA de GHL (Conversation AI) sí redacta respuestas con un prompt de personalidad; acá la IA nunca redacta. Son dos diseños distintos dentro del mismo curso (inferencia).
- **Cifras** (4-5 llamadas por día, USD 5 de carga, ≤USD 10 al mes, "máximo dos correcciones") son del instructor.
