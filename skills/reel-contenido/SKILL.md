---
name: reel-contenido
description: Arma un reel vertical de contenido desde un guion con voz e imágenes, con el estilo de tu marca (portada con título sin caja, un resaltado por video, tarjetas de a una, retrato citado y cierre con tu llamada a la acción), y lo revisa cuadro por cuadro antes de exportarlo. Usar cuando la persona ya tiene la voz grabada (o generada con la herramienta que use) y sus imágenes, y pide "armá un reel de contenido", "reel con guion y voz", "reel con tarjetas", "un reel como los de datos". Para "me grabé hablando y quiero el reel" usar la skill reel, no esta.
role: editor-video
files: []
---

# Reel de contenido (voz + imágenes + tu marca)

Motor: `.kit/engines/video/reel9.py`. Todo corre en tu computadora; solo se baja, con tu permiso, la librería de animación GSAP (una vez, con el hash verificado).

**Cuál skill usar.** `reel` = "me grabé hablando y sale el reel" (corta silencios, pone subtítulos). `reel-contenido` = "tengo un guion con su voz y sus imágenes y quiero un reel armado con tarjetas": el video no muestra a la persona hablando, muestra las imágenes con el texto encima.

## Delegación
- El armado, la mezcla y la revisión final las hace el rol editor-video. En Claude Code: use the Agent tool with subagent_type `editor-video`. En Codex: adopt the `editor-video` role from AGENTS.md.
- El título, el subtítulo y los textos de las tarjetas los escribe el rol copywriter con la skill `hooks`. En Claude Code: use the Agent tool with subagent_type `copywriter`. En Codex: adopt the `copywriter` role from AGENTS.md.

## Lo que la persona trae
1. **La voz**: un archivo de audio (su grabación o la que generó con la herramienta que use). El kit no genera voces.
2. **Las imágenes**: una para la portada del hook y las demás para el cuerpo, todas de al menos 720 px de lado menor. Nunca se estiran ni se repiten.
3. **La marca**: una ficha de marca del kit (`presets/brands/`) con colores, tipografías libres del kit, nombre, usuario y llamada a la acción. Hay tres ejemplos en `presets/reel/brands/` (servicios, marca personal, producto). Para afinar el reel, la ficha admite un bloque opcional `reel`: `tag`, `stat_kicker`, `display_weight` (100-900), `display_case` (`uppercase` o `none`), `display_leading`, `emphasis_weight`, `logo` (imagen junto a la ficha) y `logo_has_name`.
4. **El guion** (`vo.txt`): el texto exacto de la voz, entre 1,8 y 3,6 palabras por segundo.

## Flujo
1. **Carpeta del reel.** Crear una carpeta con `data.json`, `vo.txt`, el audio y las imágenes DENTRO (en `assets/`). Si una imagen está afuera, el armado la copia adentro.
2. **Mezclar la voz con la música (opcional).** La música va a un volumen fijo y bajo, sin subidas ni bajadas:
   ```
   python .kit/launch.py reel9 mix "<carpeta>" --voice voz.mp3 --music musica.mp3 --music-db -17
   ```
   Sale `audio_mix.m4a`; ponerlo en `audio.src` del `data.json` con la duración real. Sin música, usar la voz sola en `audio.src`.
3. **Control de datos** (no arma nada, dice qué falta):
   ```
   python .kit/launch.py reel9 check "<carpeta>"
   ```
4. **Armar** (control de datos, reglas de la plantilla y control de maqueta):
   ```
   python .kit/launch.py reel9 build "<carpeta>" --brand .kit-personal/brands/<marca>.json
   ```
   La primera vez pide la librería GSAP: `python .kit/launch.py reel9 fetch-gsap --yes` (baja unos 70 KB y verifica el hash). Si algo falla, no queda `index.html`: se arregla lo que dice y se repite.
5. **Exportar el video** (1080×1920, unos minutos, no mover el equipo):
   ```
   python .kit/launch.py reel9 render "<carpeta>" --out reel.mp4
   ```
6. **Revisar antes de entregar.** Mirar 3 cuadros (portada, una tarjeta, el cierre) y escuchar el audio completo. Entregar solo el reel final.

## El `data.json`
```json
{
  "kicker": "AHORRO · TEMA DEL VIDEO",
  "title": "Ahorrar sin <span class=\"hl\">culpa</span> sí se puede",
  "subtitle": "Lo que nadie te explica sobre el primer mes",
  "audio": {"src": "audio_mix.m4a", "duration": 45.0, "music": "musica.mp3"},
  "visual_slots": [
    {"id": 1, "start": 0.0, "end": 2.5, "asset": "hook.png", "role": "hook_image"},
    {"id": 2, "start": 2.5, "end": 3.7, "asset": "assets/b.png", "role": "image"},
    {"id": 3, "start": 3.7, "end": 5.0, "asset": "assets/c.png", "role": "image"},
    {"id": 4, "start": 5.0, "end": 7.5, "asset": "assets/d.png", "role": "image", "scale_start": 1.0, "scale_end": 1.05}
  ],
  "script_blocks": [{"start": 5.0, "end": 12.0}],
  "cards": [
    {"type": "intro", "start": 0.0, "end": 5.0},
    {"type": "lower-third", "start": 5.0, "end": 12.0, "html": "IDEA UNO<br><span class=\"b\">CON ÉNFASIS</span>"},
    {"type": "stat", "start": 12.0, "end": 18.0, "val": "3<span class=\"stat-sep\">/</span>5", "label": "DE CADA CINCO", "tag": "FUENTE"},
    {"type": "dossier", "start": 18.0, "end": 24.0, "asset": "assets/retrato.png", "caption": "Nombre o concepto", "subject": "person"},
    {"type": "outro", "start": 43.0, "end": 45.0}
  ]
}
```
- **Hook (0 a 5 s):** tres imágenes seguidas (portada 0–2,5 s, luego 2,5–3,7 s y 3,7–5 s), con el título encima de las tres. Ninguna imagen queda quieta más de 3 s.
- **Título:** con un solo resaltado por video: `<span class="hl">` (color de la marca) **o** `<span class="mk">` (marcador), nunca los dos. El título tiene tensión y se entiende desde la primera línea; el subtítulo promete el cierre o suma contexto (mínimo 4 palabras, sin repetir el título); `kicker` es la línea de tema de arriba.
- **Tarjetas:** una por idea del guion (`script_blocks`), de a una en pantalla, con tiempo para leerse. Tipos: `lower-third`, `stat`, `dossier` (retrato citado con pie; siempre sale acompañado de una tarjeta de texto o dato de su misma idea), `flash`, `outro`. No hay sello de abajo ni círculo de contexto.
- **Nada baja de la línea de tarjetas (1472 px de 1920):** el control de maqueta lo mide cuadro por cuadro. Si el título no entra, avisa `TITULO_LARGO`: acortarlo con el copywriter (máximo 2 intentos, mismo sentido).

## Reglas
- La voz siempre se revisa a oído entera antes de entregar; el kit no juzga la emoción del guion.
- Nunca agrandar una imagen para que "entre": pedir una más grande.
- Las reglas (duraciones, líneas, tiempos) están en `presets/reel/standard.json`; se pueden cambiar con `--standard`.
- Chequeo sin conexión: `python .kit/launch.py reel9 --selftest`.
