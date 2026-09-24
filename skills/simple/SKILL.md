---
name: simple
description: Modo de lenguaje simple. Reescribe una respuesta, un plan o un texto técnico en frases cortas y palabras de todos los días, sin perder precisión. Usar cuando la persona dice "no entiendo", "explicámelo más fácil", "en simple", pega un texto complicado, o pide que desde ahora todo sea en simple. Trigger with /simple.
role: copywriter
files: []
---

# simple — decirlo fácil sin decir menos

## Tres usos

- `/simple <texto>`: reescribí ese texto en simple.
- `/simple` solo: reescribí tu último mensaje en simple.
- "desde ahora, todo en simple": aplicá estas reglas al resto de la sesión, hasta que la persona
  diga "modo normal". (Si quiere que sea siempre, puede escribirlo fuera de los marcadores del kit
  en `CLAUDE.md` o `AGENTS.md`; eso es suyo y el kit no lo toca.)

## Reglas

1. **Primero qué pasa y qué cambia para la persona**; cómo está construido, después y solo si lo pide.
2. Frases cortas. Una idea por frase.
3. Palabras de todos los días. Si hace falta un término técnico, explicalo en la misma frase la
   primera vez ("un repositorio, o sea la carpeta con historial de cambios").
4. Describí con palabras en vez de nombrar archivos, funciones o siglas. Excepción: lo que la
   persona tiene que abrir, copiar o aprobar va tal cual, en un bloque de código, con una línea
   simple al lado.
5. Nada de relleno ("¡Excelente pregunta!") ni de validar por validar.
6. Precisión intacta: cifras, pasos y advertencias no se redondean ni se esconden. Si algo es
   riesgoso, se dice claro.

## Forma de los planes y cierres

Todo plan o cierre abre con:

```
## En simple
<3-6 líneas: qué vamos a hacer, quién lo hace, qué pasa si sale mal>
```

y abajo va el detalle completo, sin recortar.

## Ejemplo

Antes: "Se implementó un mecanismo de invalidación de caché basado en mtime para el config."
Después: "Ahora, cuando cambiás la configuración, el programa lo nota solo. No hace falta reiniciarlo."

## Delegación

Reescribir texto es trabajo del rol `copywriter`.
- Claude Code: use the Agent tool with subagent_type `copywriter`.
- Codex: adopt the `copywriter` role from AGENTS.md.
