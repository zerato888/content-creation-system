---
name: humanizer
description: Revisa y reescribe texto en español o inglés para sacarle las marcas típicas de escritura automática (relleno, frases infladas, tríadas, muletillas de IA) sin cambiar lo que dice. Usar antes de publicar cualquier copy, guion o caption.
role: copywriter
files: [references/checklist.md]
---

# humanizer — que suene escrito por una persona

Pasa el texto por la lista de `references/checklist.md` y lo reescribe. Cambia la forma, nunca el
contenido: no agrega datos, no borra afirmaciones.

## Pasos

1. Leer el texto entero y detectar el idioma.
2. Recorrer la lista de chequeo sección por sección y marcar cada problema con la frase exacta.
3. Reescribir solo las frases marcadas. Mantener el registro de la marca
   (`.kit-personal/brands/<nombre>.json` → `voice`).
4. Entregar: el texto nuevo y una lista corta de "antes → después" con las 3-5 correcciones más importantes.

## Reglas

- Si una frase ya suena natural, no se toca.
- No reemplazar una muletilla por otra.
- En español, tildes y ñ siempre correctas: un texto largo sin ninguna tilde es síntoma de error.

## Opcional

Existe una skill externa de la comunidad con el mismo fin. Si la querés, instalala desde su
repositorio; el kit no la copia porque parte de su texto viene de una fuente con otra licencia.

## Delegación

- Claude Code: use the Agent tool with subagent_type `copywriter`.
- Codex: adopt the `copywriter` role from AGENTS.md.
