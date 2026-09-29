# Herramientas de terceros que conviene conocer

El kit no las copia: son de sus autores, con sus propias licencias. Se instalan desde su fuente y cada uno
mantiene lo suyo. Todas son opcionales.

| Herramienta | Para qué sirve | Dónde bajarla |
|---|---|---|
| **defuddle** | Deja una página web como texto limpio (sin menús ni publicidad). Ya la usa la skill `web-research`. | https://github.com/kepano/defuddle |
| **obsidian-skills** | Cómo escribir notas de Obsidian (enlaces, callouts, propiedades) si la persona lleva su base de notas ahí. | https://github.com/kepano/obsidian-skills |
| **frontend-design**, **theme-factory**, **canvas-design** | Diseño de páginas y piezas visuales con más criterio; temas de color y tipografía listos; carteles en imagen. Son skills de Anthropic. | https://github.com/anthropics/skills |

Reglas para sumar cualquiera de estas:
1. Bajarla del autor (no de una copia) y leer su licencia antes de usarla en un proyecto comercial.
2. Instalarla en la carpeta de skills de la herramienta que use la persona, no dentro de `.kit/`.
3. Si un rol la necesita, decirlo en la conversación: el kit no depende de ella para funcionar.

Búsqueda semántica de B-roll propio (indexar los videos de la persona y buscarlos por descripción): hoy exige
un modelo de imágenes de varios cientos de MB y librerías pesadas; queda fuera del kit base. Si la persona lo
quiere, se propone como módulo aparte con la dependencia opcional.
