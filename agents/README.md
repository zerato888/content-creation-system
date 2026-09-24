# agents — los roles del kit

Cada archivo de esta carpeta describe **un rol**: qué hace, qué no hace, cómo trabaja y a quién le pasa el trabajo.
Es la **única fuente**. Nadie edita las copias instaladas: se regeneran desde acá.

| Rol | Para qué |
|---|---|
| [strategist](strategist.md) | Qué hacer y por qué: ángulos, temas, evaluar ideas |
| [screenwriter](screenwriter.md) | Guiones y estructura narrativa |
| [copywriter](copywriter.md) | Hooks, títulos, captions, copy corto |
| [creative-director](creative-director.md) | Cuidar la marca del usuario y aprobar piezas |
| [dp-cinematographer](dp-cinematographer.md) | Diseñar la imagen: planos, B-roll, prompts visuales |
| [editor-video](editor-video.md) | Armar la pieza: cortes, audio, subtítulos, export |
| [fact-checker](fact-checker.md) | Revisar cifras, nombres y fuentes antes de publicar |
| [social-media-manager](social-media-manager.md) | Calendario, adaptación por red, lectura de métricas |
| [motion-designer](motion-designer.md) | Motion graphics en After Effects (solo con ese módulo) |

## Una fuente, dos herramientas

El instalador lee estos archivos y los convierte según la herramienta que el usuario eligió:

- **Claude Code:** copia cada rol a `.claude/agents/<rol>.md`. Claude Code los carga como subagentes.
- **Codex:** junta todos los roles en una sección `## Roles` dentro de `AGENTS.md` (entre los marcadores del kit).
  Se probó que Codex sigue esas instrucciones. Diferencia aceptada: en Codex el rol es una instrucción dentro
  del mismo agente, no un subagente aislado.

`motion-designer` solo se instala si el usuario activa el módulo de After Effects.

## Formato de cada archivo

Encabezado (frontmatter) obligatorio:

- `name` — el nombre del rol, igual al nombre del archivo.
- `description` — cuándo usarlo, en una o dos frases. Es lo que la herramienta lee para decidir.
- `skills` — las capacidades del catálogo que este rol atiende. Lo completa y valida `catalog.json`
  (cada skill nombra un rol y ese rol la lista de vuelta).

No hay campo de herramientas: los roles no dependen de una herramienta concreta.

Las rutas a `knowledge/` se escriben como texto (`knowledge/archivo.md`), relativas a la carpeta del kit
instalado, para que sigan valiendo en cualquier lugar donde se copie el rol.

## Cómo se delega

Las skills nunca dicen "usá la herramienta X". Dicen, siempre con esta forma:

> **Delegá al rol `copywriter`:** escribí 3 hooks para este guion.

- Claude Code lo resuelve lanzando el subagente con ese nombre.
- Codex lo resuelve aplicando las reglas de ese rol en `AGENTS.md` (o lanzando un subagente con ellas).

Un pedido puede pasar por varios roles en orden (por ejemplo: `screenwriter` → `copywriter` → `creative-director`).
Pedir dos roles para una sola pieza no es exceso: es el proceso.
