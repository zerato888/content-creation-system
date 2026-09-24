---
name: task
description: Anotar, listar, mover y cerrar tareas del tablero del Command Center desde el chat (las mismas tarjetas que ves en Tablero y en cada marca). Usar cuando la persona dice "anotá la tarea…", "qué tengo pendiente", "pasá X a la marca Y", "cerrá la tarea CAN-3" o pide revisar tareas viejas. Trigger with /task.
role: strategist
files: []
---

# task — el tablero desde el chat

Todas las tareas viven en un solo lugar: `.kit-personal/data/` (lo mismo que muestra el Command
Center). Esta skill no guarda nada por su cuenta: corre el programa de tareas del kit, desde la
carpeta del proyecto.

```
python .kit/launch.py task list [--ecosystem <marca>] [--status open]
python .kit/launch.py task add "Grabar intro del video" --ecosystem <marca> [--priority high] [--due-date 2026-10-01] [--area hito]
python .kit/launch.py task move CAN-3 <otra-marca>
python .kit/launch.py task close CAN-3            # --reopen para reabrir
python .kit/launch.py task stale --days 14        # tareas quietas hace mucho
```

(En Windows, `python`; en Mac puede ser `python3`.) La salida es JSON: resumila en lenguaje simple,
no la pegues entera.

## Cómo se usa

1. **Marca (`--ecosystem`)**: es el `id` de una marca de `.kit-personal/cc.config.json`, o `vida`
   para Vida Personal. Si la persona no la dice y hay más de una, preguntá cuál. Si no hay ninguna
   marca, ofrecé agregarla con la skill `onboard`.
2. **Anotar**: una tarea = una acción concreta que se puede terminar ("Grabar el video de X", no
   "Contenido"). Si la persona dicta varias, anotalas de a una y al final mostrá la lista con sus
   códigos (por ejemplo `CAN-4`).
3. **Hitos**: lo grande de una marca va con `--area hito`; se ve en la pantalla de esa marca.
4. **Cerrar o mover**: confirmá el código antes de cerrar. Mover a otra marca conserva el código.
5. **Revisar ("qué hago hoy")**: listá las abiertas, marcá las vencidas y las quietas (`stale`) y
   proponé como mucho 3 para hoy, con una razón corta cada una. La persona decide.

Nunca edites la base de datos a mano ni borres tareas sin que la persona lo pida.

## Delegación

La priorización es trabajo del rol `strategist`.
- Claude Code: use the Agent tool with subagent_type `strategist`.
- Codex: adopt the `strategist` role from AGENTS.md.
