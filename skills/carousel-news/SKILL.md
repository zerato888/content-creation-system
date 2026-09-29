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
2. **Estructura.** Elegí un módulo por slide de `.kit/presets/carousel/ESTRUCTURAS.md` (de 4 a 8 slides, `cover` primero, `cta` al final). Hay tres ejemplos completos para copiar: `ejemplo-servicios.json`, `ejemplo-marca-personal.json` y `ejemplo-producto.json`, cada uno con su marca en `.kit/presets/brands/`. El motor avisa si la estructura no sigue las reglas.
3. **Copy.** Delegá al copywriter con el tema, la voz de la marca (`voice` en tu brand.json) y los tipos de slide disponibles. Pedí textos cortos: portada que diga el tema de entrada, una idea por slide, fuente y cierre.
4. **Imágenes (opcional).** Solo imágenes tuyas o con licencia, en `.jpg`, `.png` o `.webp`, dentro de la carpeta del proyecto. Nunca se descargan de internet. Si una slide no tiene imagen, se usa un panel con los colores de la marca. Con `"image_position": "top"` o `"bottom"` la foto va en una franja y el texto sobre fondo limpio; `"full"` (por defecto) la pone de fondo.
5. **Escribí el spec** (JSON). Tomá como modelo `.kit/presets/carousel/demo-spec.json`. Tipos de slide:
   - `cover`: `title`, `subtitle`, `highlight` (palabra resaltada), `image`
   - `headline`: `title`, `text`, `label`, `highlight`, `image`
   - `body`: `text`, `label`, `highlight`
   - `quote`: `quote`, `author`
   - `stat`: `value`, `text`, `label`
   - `source`: `text` (se antepone `source_label` de la marca)
   - `cta`: `text`, `follow` (si falta, se usa el `handle` de la marca), `image`
   Todos aceptan `kicker`. Los campos son texto; máximo 600 caracteres por campo y 20 slides.
6. **Render HTML** (revisión rápida en el navegador):
   `python .kit/launch.py carousel mi-carrusel.json --brand .kit-personal/brands/<marca>.json --html-only`
7. **PNG:** mismo comando sin `--html-only`. Antes de guardar cada PNG se corre un control de calidad: si una fuente no cargó, una palabra no entra, un texto se sale o se encima con otro, o una tilde choca con la línea de arriba, ese slide no se guarda y el comando dice qué corregir (sale con código 3). Necesita Playwright y Chromium en la caché compartida del kit; si faltan, el script dice cómo instalarlos. Usá `--out CARPETA` para elegir dónde quedan y `--project CARPETA` si tus imágenes viven en otra carpeta del proyecto.
8. **Revisión.** Delegá al creative-director con los PNG: legibilidad, jerarquía, colores de marca, texto cortado. Corregí el spec y volvé a renderizar.

## Reglas

- Todo el texto se escapa: lo que escribas se muestra tal cual, nunca se ejecuta.
- Las imágenes fuera de la carpeta del proyecto, URLs o formatos distintos a jpg/png/webp se rechazan.
- Las tipografías salen de tu brand.json y tienen que estar en la carpeta de fuentes del kit (el instalador descarga las libres). Si una fuente usada no está, el PNG no se genera: así nunca sale un carrusel con otra letra sin que lo sepas. No hay fuentes web.
- Chequeo sin conexión: `python .kit/launch.py carousel --selftest`.

## Módulos, objetivo y controles extra (opcional, para carruseles más fuertes)
- **`module` por slide** (ver la lista en `presets/carousel/modules.json` y la guía en `presets/carousel/ESTRUCTURAS.md`): si algún slide lo declara, el motor avisa cuando falta tensión (un slide que choque), cuando el cierre no sirve al objetivo o cuando hay demasiados slides sin foto.
- **`goal`** en el spec: `comments` (el cierre es un módulo de cierre y termina en `?`) o `sales` (el cierre es `oferta`).
- **Portada:** puede llevar un `circle` (círculo de contexto de 250 px con borde de acento). El titular nunca es una cita entre comillas. Si el titular toca el círculo, el control frena la portada.
- **Fotos:** cada foto lleva su `<nombre>.source.json` con `origin: own|ai|press|stock|other` (con `source_url` salvo en `own` y `ai`). `focus: "30% 20%"` fija el recorte a mano. En Mac, si está instalado `pyobjc-framework-Vision`, el motor detecta caras y frena si una queda cortada; sin detector solo deja una nota.
- **`--strict`** (o `"strict": true` en el spec): convierte los avisos en errores y exige las fuentes y la revisión de marca de agua (`python .kit/engines/carousel/check_watermark.py spec.json --project carpeta`).
- **`--brand nombre`** busca `.kit-personal/brands/nombre.json`.
