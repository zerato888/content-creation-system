---
name: wiki
description: Mantiene una base de conocimiento en markdown dentro del proyecto: ingerir fuentes, responder preguntas desde lo ya destilado y revisar su salud (links rotos, páginas huérfanas, contradicciones). Usar cuando el usuario trae una fuente para guardar, pregunta algo que la wiki puede responder o pide revisar la wiki.
role: strategist
files: [references/schema.md]
---

# wiki — conocimiento que se acumula

Una wiki en markdown que el agente mantiene. Cada fuente se lee una vez y queda destilada; después
se consulta la wiki en vez de releer las fuentes. La estructura y los formatos están en
`references/schema.md`: leerlo antes de la primera operación.

## Ingerir

El usuario deja una fuente en `raw/` (o pega un texto o una URL, que se lee con `web-research`).

1. Leer la fuente completa. `raw/` nunca se modifica.
2. Crear `wiki/sources/<slug>.md` con el resumen, las ideas clave y la referencia.
3. Actualizar o crear las páginas de `wiki/entities/` y `wiki/concepts/` que toca. Enlazar con `[[slug]]`.
4. Si contradice algo existente, anotarlo en las dos páginas; no borrar lo anterior.
5. Sumar la página a `wiki/index.md` y una entrada **arriba** de `wiki/log.md`.

## Consultar

1. Leer `wiki/index.md` y abrir solo las páginas relevantes.
2. Responder citando las páginas usadas (`[[slug]]`).
3. Si la respuesta vale la pena guardarla, crear `wiki/analyses/<slug>.md` y registrarla en índice y log.
4. Si la wiki no alcanza, decirlo y proponer qué fuente ingerir.

## Revisar (lint)

Buscar y reportar: links `[[...]]` a páginas que no existen, páginas que nadie enlaza, páginas
fuera del índice, frontmatter incompleto, afirmaciones que se contradicen entre páginas, fuentes en
`raw/` sin página en `wiki/sources/`. Proponer arreglos; aplicar solo con OK.

## Delegación

- Claude Code: use the Agent tool with subagent_type `strategist`.
- Codex: adopt the `strategist` role from AGENTS.md.
