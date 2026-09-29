# hooks — avisos automáticos (opcionales)

Nueve programas chicos en Python (solo la librería estándar, funcionan en Mac y Windows). Se
instalan en `.kit/hooks/` y **están apagados** hasta que los pedís en el onboarding (`"hooks": [...]`).
Si alguno falla por cualquier motivo, no frena nada: sale sin hacer ruido.

| Aviso | Cuándo corre | Qué hace | Ofrecido por defecto |
|---|---|---|---|
| `block_sudo` | antes de un comando de terminal | frena comandos con permisos de administrador | sí |
| `session_start_summary` | al empezar la sesión | muestra `.kit-personal/hot.md` (dónde quedaste) | sí |
| `knowledge_router` | cuando escribís un pedido | sugiere la skill, el rol y tus lecciones (`.kit-personal/lessons.md`, o su índice `lessons-index.json` si lo generaste con `python .kit/launch.py lessons`) que coinciden | no |
| `post_compact_reminder` | después de compactar el contexto (solo Claude Code) | recuerda releer `hot.md` y el último punto de control | no |

| `simple_mode` | cuando escribís un pedido | agrega el contrato de lenguaje simple a cada mensaje (prendido por defecto; `/simple off` lo apaga en la sesión, `/simple on` lo vuelve a prender) | no |
| `plan_plain_language` | al salir del modo plan (solo Claude Code) | avisa si el plan no abre con `## En simple` o si esa sección trae jerga; avisa, nunca frena | no |
| `grounding_track` | después de leer un archivo (solo Claude Code) | anota que leíste la ficha de una marca (`.kit-personal/brands/*.json`) | no |
| `brand_gate` | antes de un comando de terminal | sin ficha de marca no hay pieza: frena `launch.py carousel`, `reel` y `logo` si no existe ninguna ficha (y, con `grounding_track` activo, si no la leíste en los últimos 45 min). Salida de emergencia: `KIT_NO_GATE=1` | no |
| `no_open_headless` | antes de un comando de terminal | en corridas desatendidas (`KIT_HEADLESS=1`) frena `open`/`start`/`xdg-open`, que dejan ventanas sin cerrar | no |

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

## Solo Claude Code, y qué pasa en Codex

`plan_plain_language` y `grounding_track` necesitan eventos que Codex no tiene (salir del modo plan,
leer un archivo): no se escriben en `.codex/hooks.json`. `brand_gate` sí corre en Codex, pero ahí solo
comprueba que exista la ficha. **En Codex los avisos pueden no dispararse solos** (hay que aprobarlos
con `/hooks`, y según la versión algunos eventos no llegan): la regla sigue valiendo por obediencia
del agente, no por bloqueo. Si algo debe frenarse sí o sí, no confíes solo en un aviso.

## Barra de estado con tokens reales (solo Claude Code)

`.kit/engines/statusline.py` dibuja una barra con el uso REAL de contexto de la sesión (lo lee del
historial, no lo estima). Funciona en Mac, Linux y Windows. No se activa sola: pegá esto en
`.claude/settings.json` (o en el global):

```json
"statusLine": {"type": "command", "command": "python .kit/engines/statusline.py"}
```

Para una ventana distinta de 200.000 tokens, definí `KIT_CTX_WINDOW` (por ejemplo `1000000`).

## Otras herramientas de este paquete

- `python .kit/launch.py doctor`: revisa Python, ffmpeg con subtítulos, Playwright, Whisper, fuentes,
  claves (sin mostrarlas) y skills, y dice en simple qué falta.
- `python .kit/launch.py docsizes`: presupuesto de lectura; avisa si un documento que se lee al
  arrancar es demasiado grande. Las rutas salen de `.kit-personal/read-budget.txt` (una por línea).
  `--rotate ARCHIVO.md` mueve lo viejo a `ARCHIVO-archive.md`.
- `python .kit/launch.py lessons`: arma el índice de `.kit-personal/lessons.md`.
