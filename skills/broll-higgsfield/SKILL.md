---
name: broll-higgsfield
description: Genera los clips de b-roll de un reel con Higgsfield (video con IA) usando la cuenta de la persona, a partir del plan del dp-cinematographer, y deja el broll.json listo para la skill reel. Usar cuando falte b-roll propio y la persona tenga Higgsfield. Gasta créditos de su cuenta.
role: dp-cinematographer
files: []
---

# B-roll con Higgsfield

## Delegación
- Los prompts de cada toma los escribe el rol dp-cinematographer. En Claude Code: use the Agent tool with subagent_type `dp-cinematographer`. En Codex: adopt the `dp-cinematographer` role from AGENTS.md.
- La revisión contra la marca la hace creative-director. En Claude Code: use the Agent tool with subagent_type `creative-director`. En Codex: adopt the `creative-director` role from AGENTS.md.

## Antes de empezar
- Hace falta la cuenta de Higgsfield de la persona conectada a su asistente:
  - **Claude:** conector de Higgsfield en la configuración de claude.ai.
  - **Codex:** servidor MCP de Higgsfield en `~/.codex/config.toml` (ver la guía oficial de Higgsfield).
  - Sin conector: el kit te da los prompts listos para pegar en la web de Higgsfield y descargás los clips a mano.
- Avisá el costo antes de generar: cada clip gasta créditos de **su** cuenta. Un reel típico usa de 3 a 5 clips de 3 a 5 segundos.

## Flujo
1. **Plan.** Con el guion transcripto (tiempos incluidos), el dp-cinematographer marca de 3 a 5 momentos para b-roll: qué se ve, por qué ahí (ilustra lo que se dice, no dónde se grabó) y cuántos segundos. Usa `.kit/knowledge/broll-planning.md` y `.kit/knowledge/visual-language.md`.
2. **Prompts.** Uno por toma, en inglés, vertical 9:16, con la luz y la paleta de la ficha de marca. Sin texto en la imagen, sin logos ajenos, sin caras de personas reales.
3. **OK de la persona** con la lista de tomas y el costo estimado.
4. **Generar** cada clip con Higgsfield y descargarlo a `assets/broll/` con un nombre claro (`01-cafe.mp4`).
5. **Revisar** cada clip: que se vea bien, sin cosas deformes. Si uno sale mal, se regenera ese.
6. **Escribir `broll.json`** con `start`, `end` y `file` de cada clip, y seguir con la skill `reel`.
