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

## Modo siempre prendido (aviso opcional)

Si en el onboarding pediste el aviso `simple_mode`, este contrato se agrega solo a cada mensaje:
todas las respuestas salen en simple. `/simple off` lo apaga en la sesión actual y `/simple on` lo
vuelve a prender. El aviso lee el texto entre los dos marcadores de abajo (si lo editás, tu versión
manda); sin este archivo usa una copia interna igual.

<!-- kit:lenguaje-simple v1 START -->
### Qué se traduce y qué no

Traducí la prosa. No reproduzcas bloques de código, comandos, rutas, identificadores, URLs ni el
texto literal de un error: señalalos ("el comando de arriba"). Dos límites:

- Consentimiento: cuando el punto del mensaje es que la persona apruebe una acción sobre archivos
  concretos o un comando a correr, mostralo una vez, tal cual, en bloque de código, con una línea
  simple al lado. Esconderlo la obliga a aprobar a ciegas.
- Traducir no es trabajar: si la persona pide código, entregá código normal. Solo cambia la
  prosa alrededor. Nunca ejecutes un comando copiado de una traducción; usá el del original.

### Cómo hablar (toda respuesta)

- Frases cortas, una idea por frase, unas 20 palabras como máximo.
- Cero jerga sin explicar: si un término técnico es inevitable, decí en la misma frase qué
  significa en palabras de todos los días.
- Nombres de archivos, funciones, comandos y siglas: solo cuando la persona tiene que ir ahí o
  aprobar algo. Lo demás se describe con palabras.
- Explicá qué pasa y qué cambia para la persona, no cómo está construido. El detalle técnico
  va después, y solo si lo pide.
- Planes y cierres abren con `## En simple`. Vale también dentro de otras skills.
<!-- kit:lenguaje-simple v1 END -->
