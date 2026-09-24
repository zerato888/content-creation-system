---
name: trend-research
description: Investiga qué se está diciendo de un tema en los últimos 30 días (Reddit, X, YouTube, web) usando la herramienta externa last30days. Usar cuando haga falta saber qué es tendencia ahora antes de elegir un tema o un ángulo.
role: strategist
files: []
---

# trend-research — qué se habla ahora

El motor es **last30days**, una herramienta de terceros. El kit no la incluye: se instala desde su
repositorio oficial. Por eso esta capacidad figura como módulo sin probar.

## Instalación (una vez)

Seguir las instrucciones del repositorio upstream de last30days y fijar la versión:

```bash
pipx install last30days==<pin>
```

TODO: el nombre exacto del paquete y la versión `<pin>` se confirman en la fase D
(`third_party.lock.json`). Si upstream se distribuye como skill y no como paquete, instalarla con
su propio instalador y no copiar su texto dentro del kit.

## Uso

1. Pedir al usuario el tema y, si importa, el idioma o el país.
2. Avisar: *"Voy a enviar el tema como consulta a Reddit, X, YouTube y buscadores web a través de
   last30days. No se envía nada más."* Algunas fuentes piden claves propias del usuario; el kit nunca las pide ni las guarda.
3. Correr la herramienta según su documentación y leer el resultado.
4. Devolver: los 3 a 5 ángulos que más se repiten, qué está creciendo, qué ya está gastado, y las
   fuentes con fecha.

## Si no está instalada

Usar la skill `web-research` con búsquedas acotadas por fecha y decir que el resultado es una
aproximación, no un barrido de 30 días.

## Delegación

- Claude Code: use the Agent tool with subagent_type `strategist`.
- Codex: adopt the `strategist` role from AGENTS.md.
