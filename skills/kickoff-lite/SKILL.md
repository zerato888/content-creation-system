---
name: kickoff-lite
description: Hábito de arranque para cualquier tarea: revisar si ya hay una skill instalada que la cubre, escribir un plan corto, esperar el OK explícito y recién ahí ejecutar. Usar al empezar trabajo real (no para preguntas sueltas).
role: strategist
files: []
---

# kickoff-lite — antes de tocar nada

No aplica a preguntas, charlas ni lecturas de contexto. Aplica a todo trabajo que cambia archivos
o produce una pieza.

## 1. ¿Ya hay una skill?

Leer `.kit/catalog.json` (lo instalado: skills del núcleo + módulos agregados). Buscar por nombre,
categoría y descripción. Si una skill cubre la tarea, usarla en vez de improvisar. Si hay una
parecida pero no igual, decirlo y preguntar.

Si la pieza lleva marca, confirmar que existe `.kit-personal/brands/<nombre>.json`; si no, proponer
`brand-onboarding` primero.

## 2. Plan corto

```
## En simple
<2-4 líneas: qué se va a hacer, quién lo hace, qué pasa si sale mal>

## Pasos
1. ...
2. ...

Archivos que se tocan: <lista>
Qué sale de la máquina: <nada / qué dato y a qué servicio>
Costo: <gratis / estimado si hay servicio pago>
```

## 3. Esperar el OK

No ejecutar hasta un "sí", "dale" u OK explícito. Si el usuario cambia algo, rehacer el plan.

## 4. Ejecutar y verificar

Seguir los pasos. Al final mostrar la prueba de que funciona (salida de un comando, archivo
generado, test verde), no solo "listo".

## Tareas de alto riesgo

Si la tarea toca autenticación, datos que no se pueden recuperar, migraciones, pagos o borra cosas:

- Hacer el plan más completo: qué puede fallar en cada paso y cómo se nota.
- Pedir una segunda opinión antes de aprobar: otro rol del kit o, si está instalado, Codex.
- Escribir cómo se vuelve atrás (copia previa, comando de reversión) antes de ejecutar.

## Delegación

- Claude Code: use the Agent tool with subagent_type `strategist`.
- Codex: adopt the `strategist` role from AGENTS.md.
