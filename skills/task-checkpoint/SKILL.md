---
name: task-checkpoint
description: Guardar un punto de control de una tarea larga (qué se hizo, qué falta, qué se decidió) y retomarla después sin perder el hilo, aunque sea en otra sesión o con otra herramienta. Usar cuando la persona dice "guardá hasta acá", "checkpoint", "hasta aquí llegamos", "continuá con CAN-12" o antes de cerrar una sesión con trabajo a medias. Trigger with /task-checkpoint.
role: strategist
files:
  - scripts/checkpoint.py
---

# task-checkpoint — guardar y retomar

Cada tarea tiene su carpeta en `.kit-personal/checkpoints/<código>/`:

- `CURRENT.md` — la foto vigente (se reemplaza en cada guardado).
- `history/<fecha-hora>.md` — cada foto anterior, sin tocar nunca.

El código es el de la tarjeta (`CAN-12`) o, si no hay tarjeta, un nombre corto en minúsculas
(`web-nueva`). El script hace la escritura segura; vos escribís el contenido. Corré el script desde
la carpeta del proyecto con la ruta de esta skill (`.claude/skills/task-checkpoint/` en Claude Code,
`.agents/skills/task-checkpoint/` en Codex):

```
python <carpeta de esta skill>/scripts/checkpoint.py save CAN-12 --file nota.md   # o por la entrada estándar con --file -
python <carpeta de esta skill>/scripts/checkpoint.py show CAN-12
python <carpeta de esta skill>/scripts/checkpoint.py list
```

## Guardar

Escribí la nota con esta forma (corta, en simple, sin copiar código entero):

```
# <código> — <qué es la tarea en una línea>
Actualizado: <fecha>

## Dónde quedamos
<2-5 líneas>

## Hecho
- ...

## Falta (en orden)
1. ...

## Decisiones tomadas (y por qué)
- ...

## Archivos que importan
- <ruta> — <para qué>
```

Mostrale la nota a la persona y guardala con `save`. No guardes claves ni datos privados que no
hagan falta para seguir.

## Retomar

1. `show <código>` y leé la nota entera.
2. Resumí en 3 líneas dónde quedó y cuál es el próximo paso.
3. Confirmá con la persona antes de seguir (el plan pudo cambiar).

Si no hay punto de control para ese código, decilo y ofrecé empezar uno.

## Delegación

Si hay que re-planificar lo que falta, es trabajo del rol `strategist`.
- Claude Code: use the Agent tool with subagent_type `strategist`.
- Codex: adopt the `strategist` role from AGENTS.md.
