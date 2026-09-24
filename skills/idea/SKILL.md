---
name: idea
description: Convierte una idea cruda en 5 guiones editables en los formatos que mejor le quedan, con insight central, ángulo y emoción. Usar con /idea o cuando hay un concepto desordenado y falta decidir qué pieza hacer.
role: copywriter
files: []
---

# idea — de idea cruda a 5 guiones

Es una herramienta para decidir **qué** hacer antes de elegir el formato. No guarda archivos: el
resultado vive en la conversación hasta que el usuario elige.

## Antes de empezar

- Preguntar "¿Para qué marca?" (o tomarla de `--brand <nombre>`). Cargar
  `.kit-personal/brands/<nombre>.json`; si no existe, correr `brand-onboarding` primero y volver.
- Todo en el idioma de la marca (por defecto, español).

## Entradas posibles

1. Texto suelto (frases, viñetas, un párrafo desordenado).
2. Una URL: leerla con `web-research` y usar sus ideas, nunca su texto literal.
3. Una referencia de otro creador: analizar la estructura y proponer una versión propia.

## Paso 1 — Analizar

- **Insight central:** la verdad no obvia de la idea, en una línea.
- **Ángulo:** por qué alguien frenaría el scroll (curiosidad, controversia, identidad, miedo, aspiración).
- **Emoción:** qué debería sentir (bronca, asombro, alivio, miedo, pertenencia).

## Paso 2 — Elegir 5 formatos

Solo valen capacidades instaladas (revisar `.kit/catalog.json`):

| Destino | Cuándo encaja |
|---|---|
| `story-plan` | historia con personajes o escenas, corta o larga |
| `carousel-news` | explicación en 4-7 slides, datos, lista, mito vs realidad |
| `captions` | la idea ya está grabada y hay que subtitularla |
| Command Center: Ideas y Content Lab | hay una referencia viral que adaptar o un guion a mejorar |
| `hooks` | la idea está, falta el arranque de los primeros 3 segundos |
| `broll-plan` | hay un guion narrado y falta decidir qué se ve |

Siempre mostrar 5 propuestas ordenadas de mejor a peor ajuste (dos pueden compartir destino con
ángulos distintos).

## Paso 3 — Escribir los 5 guiones

- **Video narrado:** texto con marcas de tiempo, notas visuales por tramo, hook de arranque.
- **Carrusel:** texto por slide, tipo (historia, educativo, dato, mito, pasos), portada y cierre.
- **Historia:** arco con inicio, cambio y resolución.

Marcos cortos útiles: la lección (tropiezo → dolor → salida → aprendizaje), mito derribado,
paso a paso, error común, antes y después.

## Paso 4 — Presentar y derivar

Mostrar análisis + 5 guiones numerados. El usuario puede: elegir uno, editar y elegir, elegir
varios (se hacen en orden) o pedir "refiná el 2". Al elegir, pasar a la skill destino el guion
aprobado, la marca y el análisis.

## Delegación

- Claude Code: use the Agent tool with subagent_type `copywriter`.
- Codex: adopt the `copywriter` role from AGENTS.md.
