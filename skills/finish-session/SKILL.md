---
name: finish-session
description: Cierre de sesión en 4 pasos cortos. Actualiza la nota de "dónde estamos" (.kit-personal/hot.md), agrega una entrada al registro del día (.kit-personal/logs/), guarda las lecciones nuevas en .kit-personal/lessons.md y ofrece pasar lo aprendido a la wiki. Usar cuando la persona dice "cerremos", "terminamos por hoy", "cierre de sesión" o "wrap up". Trigger with /finish-session.
role: strategist
files: []
---

# finish-session — cerrar sin perder nada

Todo lo que escribe esta skill es de la persona y vive en `.kit-personal/` (git lo ignora). No toca
archivos del kit ni de otras personas. Mostrá cada cambio antes de escribirlo y pedí un OK al final
(uno solo para todo).

## 1. Tareas y trabajo a medias

- Si quedó una tarea a medias, ofrecé guardar un punto de control con la skill `task-checkpoint`.
- Si se terminaron o surgieron tareas del tablero, ofrecé cerrarlas o anotarlas con la skill `task`.

## 2. `.kit-personal/hot.md` — dónde estamos (se reemplaza)

Máximo 30 líneas, en simple. Es lo primero que se lee al empezar la próxima sesión.

```
# Dónde estamos (<fecha>)
## En qué estamos
- ...
## Decisiones pendientes
- ...
## Próximo paso
1. ...
```

Reemplazá la nota vieja: lo que ya no sirve, se va. Lo importante del pasado queda en el registro.

## 3. `.kit-personal/logs/<AAAA-MM-DD>.md` — registro del día (solo se agrega)

Si el archivo del día ya existe, agregá una sección nueva al final; nunca borres ni reescribas lo que
había (puede venir de otra sesión del mismo día).

```
## Sesión <hora>
- Qué se hizo: ...
- Qué se decidió y por qué: ...
- Archivos que cambiaron: ...
- Qué quedó pendiente: ...
```

## 4. Lecciones — `.kit-personal/lessons.md`

Si en la sesión la persona corrigió algo ("así no", "otra vez esto", "te dije que…"), agregá una línea
por lección, arriba de todo:

```
- <fecha> · <regla en una frase> — <cuándo aplica>
```

Una lección es una regla que se puede seguir la próxima vez, no un resumen. Si no hubo correcciones,
no inventes ninguna. El aviso de ruteo del kit (si está prendido) usa este archivo para recordarlas.

## 5. Wiki (opcional)

Si en la sesión apareció conocimiento que vale para siempre (una fuente leída, un método que
funcionó), preguntá: "¿Lo paso a la wiki?". Si dice que sí, usá la skill `wiki` (ingesta). Si no,
listo.

## Cierre

Terminá con 3 líneas: qué se hizo, qué quedó pendiente y cuál es el próximo paso.

## Delegación

Resumir decisiones y ordenar lo pendiente es trabajo del rol `strategist`.
- Claude Code: use the Agent tool with subagent_type `strategist`.
- Codex: adopt the `strategist` role from AGENTS.md.
