---
name: hooks
description: Analiza un guion o transcripción para encontrar su idea más fuerte, elegir el mejor arranque literal y proponer 3 hooks de mecanismos distintos desde el banco genérico del kit. Usar cuando falta el arranque de los primeros 3 segundos o hay que comparar variantes de hook para grabar.
role: copywriter
files: []
---

# hooks — los primeros 3 segundos

Objetivo: que el espectador sienta algo fuerte apenas empieza, y que sepa de qué trata la pieza.
El hook **dice el tema** de entrada; no lo esconde detrás de un misterio.

Banco: `.kit/presets/hooks/hooks-bank.json` (categorías, plantillas y ejemplos inventados).
Criterios de fondo: `.kit/knowledge/hooks-storytelling.md`.

## Paso 1 — Entrada

- Si es un guion: leerlo tal cual.
- Si es una transcripción: sacar marcas de tiempo, nombres de hablante y muletillas.
- Si no hay nada: pedir el texto antes de seguir.
- Cargar la voz de la marca desde `.kit-personal/brands/<nombre>.json` (`voice`).

## Paso 2 — Valor principal

La idea más polémica, reveladora o vulnerable del texto, en 1-2 frases concretas (no el tema
general). Buscar: algo que contradiga lo que el público cree, un error que el público reconoce en
sí mismo, un dato que rompe lo esperado.

## Paso 3 — Arranque literal

Elegir **un fragmento textual** del guion con la mayor carga. Nunca inventarlo. Descartar frases
que necesitan contexto, que son de transición o que miden más de 2 oraciones. Si no hay ninguno
fuerte, decirlo y sugerir reescribir el comienzo.

## Paso 4 — 3 hooks de 3 categorías distintas

Del banco, elegir 3 categorías **distintas entre sí** (y distintas de la del hook original, si ya
hay uno). Para cada una:

```
HOOK N — <categoría>
Plantilla: "<plantilla del banco>"
Adaptado: "<versión para este guion>"
Emoción: <emoción>
Por qué: <1 línea que lo ata al valor principal>
```

El espectador es el sujeto ("vos", "la mayoría"), no el autor. Nada de palabras infladas
("increíble", "revolucionario").

## Paso 5 — Pulir

Pasar los hooks nuevos por la skill `humanizer`. Si ya existía un hook original, queda como
opción 1 sin tocar y los generados son las opciones 2 y 3 (para grabarlos seguidos y comparar).

## Chequeo final

- [ ] Valor principal concreto, no temático.
- [ ] Arranque textual, sin parafrasear.
- [ ] 3 categorías distintas.
- [ ] Cada hook se dice en 3-7 segundos.
- [ ] Capa triple: curiosidad + giro + promesa de valor.

## Delegación

- Claude Code: use the Agent tool with subagent_type `copywriter`.
- Codex: adopt the `copywriter` role from AGENTS.md.
