---
name: carousel-news
description: Arma un carrusel explicativo de noticias o temas (1080×1350) con los colores y tipografías de tu marca, usando solo tus propias imágenes, y lo exporta a HTML y PNG en tu máquina. Usalo cuando quieras convertir una historia o tema en un carrusel para redes.
role: creative-director
files: []
---

# Carrusel de noticias

Convierte una historia en un carrusel de 3 a 10 slides con la identidad de tu marca.
Todo corre en tu máquina: no se sube nada ni se descarga nada. Publicar queda fuera de este skill (llega como módulo aparte).

## Delegación

- El copy lo escribe el rol copywriter. En Claude Code: use the Agent tool with subagent_type `copywriter`. En Codex: adopt the `copywriter` role from AGENTS.md.
- La revisión de marca la hace el rol creative-director. En Claude Code: use the Agent tool with subagent_type `creative-director`. En Codex: adopt the `creative-director` role from AGENTS.md.

## Flujo

1. **Elegí la historia o el tema.** Una idea por carrusel. Si hay cifras, anotá de dónde salen.
2. **Copy.** Delegá al copywriter con el tema, la voz de la marca (`voice` en tu brand.json) y los tipos de slide disponibles. Pedí textos cortos: portada que diga el tema de entrada, una idea por slide, fuente y cierre.
3. **Imágenes (opcional).** Solo imágenes tuyas o con licencia, en `.jpg`, `.png` o `.webp`, dentro de la carpeta del proyecto. Nunca se descargan de internet. Si una slide no tiene imagen, se usa un panel con los colores de la marca.
4. **Escribí el spec** (JSON). Tomá como modelo `.kit/presets/carousel/demo-spec.json`. Tipos de slide:
   - `cover`: `title`, `subtitle`, `highlight` (palabra resaltada), `image`
   - `headline`: `title`, `text`, `label`, `highlight`, `image`
   - `body`: `text`, `label`, `highlight`
   - `quote`: `quote`, `author`
   - `stat`: `value`, `text`, `label`
   - `source`: `text` (se antepone `source_label` de la marca)
   - `cta`: `text`, `follow` (si falta, se usa el `handle` de la marca), `image`
   Todos aceptan `kicker`. Los campos son texto; máximo 600 caracteres por campo y 20 slides.
5. **Render HTML** (revisión rápida en el navegador):
   `python .kit/launch.py carousel mi-carrusel.json --brand .kit-personal/brands/<marca>.json --html-only`
6. **PNG:** mismo comando sin `--html-only`. Necesita Playwright y Chromium en la caché compartida del kit; si faltan, el script dice cómo instalarlos. Usá `--out CARPETA` para elegir dónde quedan y `--project CARPETA` si tus imágenes viven en otra carpeta del proyecto.
7. **Revisión.** Delegá al creative-director con los PNG: legibilidad, jerarquía, colores de marca, texto cortado. Corregí el spec y volvé a renderizar.

## Reglas

- Todo el texto se escapa: lo que escribas se muestra tal cual, nunca se ejecuta.
- Las imágenes fuera de la carpeta del proyecto, URLs o formatos distintos a jpg/png/webp se rechazan.
- Las tipografías salen de tu brand.json. Si el archivo de la fuente está en la carpeta de fuentes del kit se usa; si no, el sistema usa una fuente parecida. No hay fuentes web.
- Chequeo sin conexión: `python .kit/launch.py carousel --selftest`.
