---
name: wiki-lint
description: Revisa la salud de la wiki en markdown - enlaces rotos, páginas huérfanas, páginas fuera del índice, frontmatter incompleto y páginas viejas. Solo reporta; los arreglos se proponen. Usar cuando la persona dice "revisá la wiki", "lint de la wiki", "qué está roto en mis notas", o cada 10-15 ingestas.
role: strategist
files: []
---

# wiki-lint — revisar la wiki

1. Correr `python3 .kit/launch.py wiki-lint` (opciones: `--wiki <carpeta>`, `--stale-days 180`).
2. Leer el resultado. Cada línea dice qué página y qué pasa:
   - `ENLACE ROTO`: un `[[slug]]` apunta a una página que no existe. Crear la página o quitar el enlace.
   - `HUÉRFANA`: nadie la enlaza. Enlazarla desde una página relacionada.
   - `FUERA DEL ÍNDICE`: falta la línea en `wiki/index.md`.
   - `FRONTMATTER`: faltan `title`, `type`, `created` o `updated`.
   - `aviso ... sin tocar`: página vieja; revisar si sigue siendo cierta (no falla el control).
3. Proponer los arreglos en una lista corta. Aplicarlos solo con el OK de la persona.
4. Anotar la revisión arriba de `wiki/log.md`.

El motor solo lee. Las contradicciones entre páginas y las afirmaciones desactualizadas no las detecta un
script: se buscan leyendo, con la skill `wiki`.

## Delegación

- Claude Code: use the Agent tool with subagent_type `strategist`.
- Codex: adopt the `strategist` role from AGENTS.md.
