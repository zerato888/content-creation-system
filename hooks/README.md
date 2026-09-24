# hooks — avisos automáticos (opcionales)

Cuatro programas chicos en Python (solo la librería estándar, funcionan en Mac y Windows). Se
instalan en `.kit/hooks/` y **están apagados** hasta que los pedís en el onboarding (`"hooks": [...]`).
Si alguno falla por cualquier motivo, no frena nada: sale sin hacer ruido.

| Aviso | Cuándo corre | Qué hace | Ofrecido por defecto |
|---|---|---|---|
| `block_sudo` | antes de un comando de terminal | frena comandos con permisos de administrador | sí |
| `session_start_summary` | al empezar la sesión | muestra `.kit-personal/hot.md` (dónde quedaste) | sí |
| `knowledge_router` | cuando escribís un pedido | sugiere la skill, el rol y tus lecciones (`.kit-personal/lessons.md`) que coinciden | no |
| `post_compact_reminder` | después de compactar el contexto (solo Claude Code) | recuerda releer `hot.md` y el último punto de control | no |

`knowledge_router` solo lee lo instalado en tu proyecto (`.kit/catalog.json`, las skills instaladas
y tu archivo de lecciones). No trae listas de palabras de nadie.

## Dónde se configuran

Solo para las herramientas que tenés:

- **Claude Code:** se agregan a `.claude/settings.json` (lo que ya tenías ahí se respeta). Corren
  solos desde la próxima sesión.
- **Codex:** se escriben en `.codex/hooks.json`. **Paso extra:** abrí Codex en el proyecto, escribí
  `/hooks` y aprobá los del kit. Hasta que los apruebes no corren (Codex pide permiso para cualquier
  aviso nuevo o cambiado).

Para apagarlos: volvé a correr el onboarding con `"hooks": []`. Al desinstalar el kit se quitan solos
de los dos archivos; tus propios avisos quedan como estaban.
