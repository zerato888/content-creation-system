# Subtítulos

## Cómo funcionan en el kit
- Subtítulos palabra por palabra, renderizados como capa con transparencia para poner encima del video.
- Cada pieza combina **un preset de hook** (un titular grande, un solo bloque) y **un preset de base** (el diálogo corrido).
- La **posición vertical no va en el preset**: se pregunta cada vez, porque depende del encuadre.
- Transcripción local (whisper) y render con ffmpeg compilado con libass. Las fuentes del kit son de licencia libre
  (OFL) y el motor las usa desde la carpeta del kit; no hace falta instalarlas en el sistema.

## Antes de renderizar
1. Transcribí y revisá el texto: nombres propios, cifras, muletillas.
2. Elegí hook y base por nombre. Nombrar el preset alcanza.
3. Elegí la posición mirando un frame real.

## Reglas
- **Se aprueba sobre el render real**, no sobre una vista previa que cambia fuentes.
- **Si falta la fuente exacta, el motor falla a propósito** en vez de reemplazarla en silencio.
- Nunca tapar una cara ni el texto importante del video.
- `stable` quiere decir que el preset pasó una prueba dura (palabras largas y ritmo rápido) y un render revisado.

## Agregar un preset
1. Un JSON con nombre, versión, tipo (`hook` o `base`), estado, tokens tipográficos, layout y forma de aparición.
   Un hook no limita la cantidad de líneas.
2. Registrarlo en el registro de presets con su huella (sha256).
3. Arranca como `pilot`. Pasa a `stable` solo después de la prueba dura y un render aprobado.
