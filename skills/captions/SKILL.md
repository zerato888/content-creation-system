---
name: captions
description: Genera subtítulos palabra por palabra (karaoke, cada palabra entra con fade-in) como capa .mov con transparencia para poner encima del video en cualquier editor. Transcribe en local con Whisper, deja un JSON editable para corregir antes de renderizar y usa presets de tipografía libres (OFL). Usar cuando pidan subtítulos animados, captions word-by-word o re-renderizar unos subtítulos ya corregidos.
role: editor-video
files: []
---

# Subtítulos palabra por palabra

Transcripción local con Whisper → JSON editable → archivo `.ass` → `.mov` ProRes 4444 con canal alfa. La capa dura lo mismo que el video y va en una pista encima del clip, alineada al inicio.

Motor: `.kit/engines/video/captions.py` (usa `.kit/engines/video/transcribe.py`).
Presets: `.kit/presets/captions/presets/*.json` (catálogo en `.kit/presets/captions/LIBRARY.json`).

## Delegación

Esta tarea es del rol `editor-video`.
- Claude Code: use the Agent tool with subagent_type `editor-video`.
- Codex: adopt the `editor-video` role from AGENTS.md.

## Requisitos

- Python 3.11+ y el entorno del kit (`.kit/venv`).
- ffmpeg **con libass** (el filtro `subtitles`). Si el ffmpeg del sistema no lo trae, apuntar `KIT_FFMPEG` a uno que sí. El motor lo verifica y avisa antes de renderizar.
- Un motor de Whisper: `faster-whisper` en `.kit/venv` (recomendado) o `whisper.cpp` en el PATH.
- El modelo de Whisper (por defecto `small`, versión fijada con hash) se descarga **una sola vez**, con tu permiso, a la caché compartida del kit: `python .kit/launch.py models small` dice el tamaño y la carpeta antes de bajar nada. Si falta, transcribir avisa con ese comando; nunca descarga solo. Las fuentes OFL van a `.kit/fonts/` en la instalación. Nada de esto sale de tu máquina durante el uso: la transcripción y el render son 100% locales. Modelos más grandes que `small` solo con `--allow-large-model`.

## Flujo

1. **Transcribir.**
   ```
   python .kit/launch.py captions transcribe "<video>" --lang es
   ```
   Escribe `<video>.captions.json` y muestra el texto agrupado en bloques. Solo acepta archivos locales: rechaza URLs, playlists (`.m3u8`, `.m3u`) y listas de concat.

2. **Revisar el texto (obligatorio).** Mostrá la transcripción al usuario y esperá sus correcciones antes de renderizar. Whisper se equivoca con nombres propios y jerga. Las correcciones van en el JSON: cambiar el campo `text` de cada palabra (los tiempos `start`/`end` se conservan) o borrar la palabra entera. Las muletillas comunes (eh, em, este, o sea…) se quitan solas al renderizar.

3. **Elegir preset.** Listar con:
   ```
   python .kit/launch.py captions list
   ```
   - `base-*`: diálogo normal (una o dos líneas, con o sin caja de fondo, con palabra destacada).
   - `hook-*`: frase de apertura con tipografía más dramática; el bloque entero queda en pantalla junto.
   - Opcional: un texto anotado para marcar el gancho y los énfasis, con las mismas palabras del JSON ya corregido: `[hook]esto cambia[/hook] todo lo que *sabías*`. Si el texto no coincide con el JSON, el render se frena y muestra dónde (nunca adivina tiempos).
   - `base-serif-accent` toma el color de acento del `brand.json` activo (`--brand <archivo>`).

4. **Preguntar la posición vertical. Siempre, en cada render.** Nunca asumirla del preset. Opciones: abajo (≈0.12), medio (≈0.5), arriba (≈0.7), o una fracción exacta medida desde abajo. Se pasa con `--margin-v-frac` y vale igual para el gancho y el diálogo, para que no salten de lugar.

5. **Renderizar.**
   ```
   python .kit/launch.py captions render "<video>.captions.json" --base-preset base-bold-left [--hook-preset hook-serif-escalation] [--annotated-text texto.txt] --margin-v-frac 0.2
   ```
   Produce `<video>.captions.mov` (y el `.ass` al lado). Corregir el JSON y re-renderizar toma segundos; no hace falta transcribir de nuevo.

6. **Verificar antes de entregar.** Componer 2 o 3 frames de control sobre el video (uno en mitad de un fade) y mirarlos: posición correcta, palabras en sincronía, nada cortado en los bordes.
   ```
   ffmpeg -protocol_whitelist file,pipe -ss 3 -i "<video>" -ss 3 -i "<video>.captions.mov" -filter_complex overlay -frames:v 1 control.png
   ```

7. **Al editor.** Importar el `.mov` y ponerlo en una pista encima del clip, desde el frame 0. Funciona en cualquier editor que respete el canal alfa de ProRes 4444 (por ejemplo Premiere, DaVinci Resolve o Final Cut); ninguno es obligatorio.

## Notas

- Las fuentes se pasan a libass de forma explícita (`fontsdir=` + un `fonts.conf` generado), así que no hace falta instalarlas en el sistema. Si falta una fuente del kit, el motor usa la alternativa del sistema declarada en `.kit/presets/captions/font-map.default.json` y lo avisa; si tampoco está, se frena.
- Si una línea no entra en el ancho, se achica sola solo esa línea.
- Autoprueba sin ffmpeg ni Whisper: `python .kit/launch.py captions --selftest`.
- LUTs de color opcionales para el video base: `.kit/presets/luts/`.
