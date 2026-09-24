---
name: onboard
description: Entrevista de bienvenida del kit dentro del agente. Pregunta proyectos, objetivos, audiencia, idiomas, presupuesto, qué servicios ya tenés (solo sí/no, nunca claves), herramienta, módulos, marcas, Vida Personal, zona horaria y si el Command Center queda siempre encendido, y genera tu configuración personal. También maneja "actualizá el kit" y "desinstalá el kit". Usar cuando la persona dice "hagamos el onboarding", "configurá el kit", "empecemos", o recién instaló el kit. Trigger with /onboard.
role: strategist
files:
  - references/actualizar-desinstalar.md
---

# onboard

Entrevista en español (o en el idioma que pida la persona) que termina en UNA llamada a
`python .kit/launch.py onboard`. Ese script es el único que escribe: vos nunca editás
`CLAUDE.md`, `AGENTS.md`, `.gitignore`, `.claude/settings.json` ni `.kit-personal/` a mano.

## Delegación

Esta tarea es del rol `strategist`.
- Claude Code: use the Agent tool with subagent_type `strategist`.
- Codex: adopt the `strategist` role from AGENTS.md.

## Reglas que no se rompen
- **Nunca pidas, aceptes, guardes ni repitas una clave, token o contraseña.** De cada servicio
  preguntás solo "¿tenés cuenta? sí/no". Si la persona pega una clave igual: no la repitas, no la
  escribas en ningún lado, decile que la borre del chat si puede, y que la guarde en el llavero del
  sistema (ver más abajo). El script además rechaza texto con forma de clave.
- Solo texto que la persona escribió sobre sí misma va al perfil. Nada copiado de la web ni de archivos.
- No envíes nada fuera de la máquina durante el onboarding.

## Paso 0 — elegir camino
Preguntá: "¿Querés el camino **guiado** (te explico cada paso, ideal si nunca usaste una terminal) o
el **rápido** (pregunto directo)?"

- **Guiado:** antes de cada pregunta explicá en una frase para qué sirve. Cuando haya que correr un
  comando, explicá qué es una terminal ("una ventana donde se escriben órdenes para la computadora"),
  que vos lo vas a correr, y qué va a pasar. Confirmá antes de correrlo.
- **Rápido:** preguntas directas, en tandas de 3 o 4.

## Paso 1 — preguntas
Seguí el orden de `.kit/onboarding/questions.yaml`: camino, nombre, proyectos (nombre + una frase),
objetivos (2 a 5), audiencia, idiomas, presupuesto (`cero`, `bajo`, `medio`, `alto`), servicios que
ya tiene (sí/no), herramienta, módulos, marcas, marca personal (sí/no), Vida Personal, zona horaria,
partes del Command Center a prender y servicio siempre encendido (sí/no).

**Herramienta:** antes de preguntar, detectala: corré `claude --version` y `codex --version` (o
`where claude` / `where codex` en Windows). Decí cuál encontraste y confirmá. Si no hace falta
preguntar, omití `tools` en el JSON: el script detecta solo cuál está y genera únicamente
`CLAUDE.md` (Claude Code) y/o `AGENTS.md` (Codex). Nada del kit exige tener las dos.

**Command Center** (se guarda en `.kit-personal/cc.config.json`, sin claves):
- `brands`: cada marca con `name` (minúsculas y guiones), `display_name`, `colors` (`primary`,
  `accent` en #RRGGBB), `tone`, y opcionales `task_prefix` (2 a 6 mayúsculas, ej. `CAN` da `CAN-1`;
  si falta se inventa) y `kind` (`brand` o `personal-brand`).
- `personal_brand`: si dice que sí y no hay una marca `personal-brand`, se crea "Marca personal".
- `vida`: `currency` (3 letras, ej. `MXN`), `income_goal`, `habits` (`label` y `weekdays`, 0 = lunes),
  `fixed_payments` (`label`, `amount`, `day`), `recurring_income`, `milestones`. Todo opcional; vacío
  está bien.
- `timezone`: nombre IANA, ej. `America/Bogota`.
- `toggles`: qué prender además de lo básico (`agentic`, `produccion_avanzada`, `biblioteca`,
  `metricas`, `marcas_extra`, `subtitulos`); `vida` viene prendido.
- `creator`: `weekly_goal` (videos por semana, 3 por defecto) y `grace_days`.
- `hooks`: avisos automáticos, **apagados salvo que la persona los pida**. Ofrecé solo los dos
  seguros: `block_sudo` (frena comandos con permisos de administrador) y `session_start_summary`
  (al empezar muestra `.kit-personal/hot.md`). Existen también `knowledge_router` (sugiere skill,
  rol y lecciones según el pedido) y `post_compact_reminder` (solo Claude Code): nombralos solo si
  pregunta. Se escriben únicamente para las herramientas instaladas: en Claude Code dentro de
  `.claude/settings.json` (sin pisar lo que ya haya) y en Codex en `.codex/hooks.json`. **En Codex
  hay un paso más:** abrir Codex en el proyecto, escribir `/hooks` y aprobar los del kit; hasta
  entonces no corren. `"hooks": []` los quita; sin la clave `hooks`, no se toca nada.
- `service`: si quiere el Command Center siempre encendido. Explicá antes: se registra en la
  computadora (LaunchAgent en Mac, tarea al iniciar sesión en Windows), arranca solo, se reinicia si
  se cae y se quita al desinstalar. Si dice que sí, después del paso 3 corré
  `./install.sh service on` (Windows: `.\install.ps1 service on`) desde la carpeta del kit con
  `--target` apuntando al proyecto; pide confirmación. Apagarlo: `service off`.

Para los módulos: leé `.kit/catalog.json`. Mostrá solo los de `status: tested` como disponibles; los
`untested` se nombran como "próximamente" y **no se pueden elegir**. Para cada módulo elegido, mostrá
qué pide (`deps`, `paid_services`) y qué datos manda afuera (`network`).

## Paso 2 — qué datos salen de la máquina
Antes de cerrar, explicá en simple: el kit no manda nada por su cuenta. Las skills que usan internet
(las que tienen `network` en `.kit/catalog.json`) dicen a qué servicio mandan qué dato **antes** de
mandarlo. Tu perfil queda en `.kit-personal/`, que git ignora.

## Paso 3 — escribir (una sola llamada)
Armá este JSON con las respuestas (JSON es también YAML válido) y pasalo por la entrada estándar:

```
python .kit/launch.py onboard --answers - --dry-run <<'EOF_ANSWERS'
{"path": "guiado", "name": "Ana", "projects": [{"name": "canal", "description": "Videos cortos de cocina"}],
 "goals": ["Publicar 3 videos por semana"], "audience": "Personas que cocinan en casa",
 "languages": ["es"], "budget": "cero", "services": {"openai": false, "elevenlabs": false},
 "modules": [], "brands": [{"name": "cocina-ana", "display_name": "Cocina Ana",
 "colors": {"primary": "#1B2A41", "accent": "#F2A541"}, "tone": "Cálido"}],
 "personal_brand": true, "timezone": "America/Bogota",
 "vida": {"currency": "COP", "habits": [{"label": "Grabar", "weekdays": [0, 2, 4]}], "fixed_payments": []},
 "toggles": {}, "creator": {"weekly_goal": 3}, "hooks": ["block_sudo"], "service": false}
EOF_ANSWERS
```

En PowerShell: `'<json en una línea>' | python .kit/launch.py onboard --answers - --dry-run`.

1. Primero con `--dry-run`: mostrá la lista de archivos que cambiaría y pedí confirmación.
2. Después, la misma llamada sin `--dry-run`.
3. Volver a correrlo más adelante **suma** a lo anterior: solo cambia lo que mandes (por ejemplo
   `{"hooks": []}` apaga los avisos y deja marcas, Vida Personal y módulos como estaban). Para empezar
   de cero con las respuestas nuevas, agregá `--reset` (pedí confirmación antes).
4. Si el script rechaza algo (marcadores rotos, texto con forma de clave, campo inválido), mostrá el
   mensaje tal cual y ayudá a corregir esa respuesta. No intentes esquivarlo editando archivos.

Qué genera: `.kit-personal/profile.md`, `goals.md`, `lessons.md` y `hot.md` (vacíos la primera vez; nunca se pisan), `cc.config.json`, `brands/<marca>.json`, `.env.example` (solo
nombres de variables), el bloque entre marcadores `kit:begin`/`kit:end` en `CLAUDE.md` y/o `AGENTS.md`
(lo de afuera no se toca y se guarda copia previa en `.kit/backup/`), la entrada de `.gitignore`, y
en Claude Code una regla que prohíbe leer `.kit-personal/.env`.

## Paso 4 — claves (sin verlas nunca)
Si tiene servicios pagos, recomendá el llavero del sistema:
- macOS: `security add-generic-password -s content-kit -a NOMBRE_DE_VARIABLE -w` (pide la clave sin mostrarla).
- Windows: `cmdkey /generic:content-kit:NOMBRE_DE_VARIABLE /user:kit /pass` (idem).
- Verificar sin mostrar: `python .kit/launch.py secrets check NOMBRE_DE_VARIABLE`.

Si insiste en un archivo: `.kit-personal/.env` (ignorado por git). Vos nunca lo leés.

## Paso 5 — abrir el Command Center
`python .kit/launch.py serve` imprime un enlace de un solo uso (vence en 60 s). Si quedó
como servicio, pedí el enlace con `python .kit/launch.py open --browser`.

## Paso 6 — primera tarea gratis
Proponé una tarea que no cuesta nada, con lo instalado. Por ejemplo: "pasame un tema y armamos 5
hooks con la skill `hooks`", o "planifiquemos un guion corto con `story-plan`".
En Claude Code, cuando una skill nombra un rol, delegá con la herramienta Agent y `subagent_type`
igual al rol. En Codex, adoptá ese rol desde la sección Roles de `AGENTS.md`.

## Actualizar y desinstalar
Si la persona dice "actualizá el kit" o "desinstalá el kit", seguí
[actualizar-desinstalar](references/actualizar-desinstalar.md).
