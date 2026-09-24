---
name: broll-plan
description: Decide qué mostrar en cada tramo de un guion narrado: una tabla por beat con frase, función del visual, concepto concreto, direcciones posibles y tipo de montaje (presets de B-roll). No genera imágenes. Usar cuando hay un guion o transcripción y falta decidir el B-roll, o cuando el B-roll sale genérico.
role: dp-cinematographer
files: []
---

# broll-plan — qué se ve en cada beat

El error típico no es el estilo sino **elegir el concepto** mirando la línea suelta, sin contexto:
sale una plantilla repetida. Esta skill produce la decisión; generar las imágenes es otro módulo.

Criterios de fondo: `.kit/knowledge/visual-language.md` y `.kit/knowledge/broll-planning.md`.
Tipos de montaje: `.kit/presets/broll/` (`full_screen`, `split_screen`, `subject_gradient`).

## Paso 1 — Contexto (no saltear)

1. La transcripción **completa** con tiempos, no la línea suelta.
2. De qué trata la pieza y cada bloque.
3. La marca (`.kit-personal/brands/<nombre>.json`) y cualquier estilo fijado para la pieza.

## Paso 2 — Beats

Cortar por cambio de idea en el relato, no por tiempo fijo. Si ya hay beats aprobados, respetarlos.
Nunca repartir B-roll de forma pareja cada N segundos ni como relleno.

## Paso 3 — Tabla por beat

| Campo | Qué va |
|---|---|
| `frase` | la frase literal que cubre |
| `funcion` | qué trabajo hace el visual (explicar, probar, ubicar, emocionar, dar ritmo) |
| `concepto` | el objeto o situación concreta, no "algo que transmita tensión" |
| `direcciones` | 2-3 formas de mostrarlo, con su razón; marcar la elegida |
| `montaje` | `full_screen`, `split_screen`, `subject_gradient` o `sin B-roll` |
| `origen` | `real` (material propio o de banco) o `generado` |
| `duracion` | en frames, contra el fps real |

Reglas:

- Buscar **el objeto único** que comunica la línea, no una ilustración de la emoción.
- Si la línea es abstracta y no tiene nada fotografiable, un plano ambiente sostenido es válido.
- Dos beats vecinos no comparten composición.
- Nunca una imagen generada que imite a una persona real identificable: material real o resolverlo sin mostrarla.
- Un lugar va a un mapa; una emoción nunca a un gráfico; una cifra de sufrimiento va a una imagen a escala humana, no a un contador.
- Dejar respiro de persona a cámara entre bloques de B-roll. Guía: un bloque cada ~15 s de pieza, de hasta ~7 s.

## Paso 4 — Entregar

La tabla se aprueba **antes** de escribir un solo prompt. Después, si está instalado un módulo de
generación, se escriben los prompts desde la tabla y el estilo fijado.

## Delegación

- Claude Code: use the Agent tool with subagent_type `dp-cinematographer`.
- Codex: adopt the `dp-cinematographer` role from AGENTS.md.
