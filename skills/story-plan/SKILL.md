---
name: story-plan
description: Planifica una historia en video (corta o larga): brief, 3 conceptos, guion por capítulos o escenas, dirección de arte, storyboard y prompts de escena como texto. Generar imágenes o video es un módulo aparte. Usar con /story-plan o cuando una idea necesita estructura narrativa completa antes de producir.
role: screenwriter
files: [references/style-library.md]
---

# story-plan — de un tema a un plan de rodaje

Todo en texto. Cada etapa con compuerta: no se avanza sin aprobación.

## Antes de empezar

- "¿Para qué marca?" → `.kit-personal/brands/<nombre>.json`. Si no existe, `brand-onboarding` primero.
- "¿Corta (menos de 90 s) o larga (5-15 min)?"
- Entradas: un tema, una URL (leída con `web-research`), un guion aprobado que viene de `idea`
  (entra directo en la etapa 4) o una referencia (analizada con `reference-clone`).

## Etapa 1 — Brief

Objetivo, público, emoción, duración, plataforma, restricciones, qué no hacer, llamado a la
acción (si hay), criterio de éxito.

## Etapa 2 — Conceptos (compuerta 1)

Tres conceptos, cada uno con título, una frase de logline, mundo visual, enfoque narrativo, arco
emocional y 2-3 escenas clave. El usuario elige A, B, C o una mezcla.

## Etapa 3 — Guion (compuerta 2)

- **Corta:** hook → tensión → giro → cierre. Marcos: la lección, mito derribado, antes y después.
- **Larga:** capítulos (planteo, subida, clímax, resolución, cierre). Marcos: origen, gran objetivo,
  de X a Y, una decisión.

Mostrar palabras y duración estimada. El usuario aprueba o pide cambios.

## Etapa 4 — Dirección de arte y storyboard

- Dirección de arte: paleta (desde la marca), clima por escena, luz motivada, composición, textura,
  tipografía de placas, lo que nunca se hace. Estilos base en `references/style-library.md`.
- Storyboard: tabla `# | tiempo | duración | tipo | descripción | cámara | texto en pantalla`.
  Tipos: `movimiento`, `fija`, `solo-texto`, `transición`. Apuntar a mayoría de planos con movimiento.

## Etapa 5 — Prompts como texto

- Personajes: descripción consistente de cara, cuerpo y vestuario por escena.
- Escenas: 2 cuadros clave por escena (entorno, luz, composición).
- Movimiento: cámara y acción por plano, transiciones.

Nunca prompts de personas reales identificables.

## Salida

Todo se guarda en una carpeta de la pieza, por ejemplo `piezas/<slug>-<fecha>/`: `brief.md`,
`conceptos.md`, `guion.md`, `arte.md`, `storyboard.md`, `prompts.md`. Si hay un módulo de generación
instalado, se ofrece como paso siguiente, con su costo antes de gastar.

## Delegación

- Claude Code: use the Agent tool with subagent_type `screenwriter`.
- Codex: adopt the `screenwriter` role from AGENTS.md.
