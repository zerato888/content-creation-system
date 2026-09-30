---
name: publicar
description: Programa un reel o un carrusel terminado en Instagram, Facebook o TikTok a través de Zernio o de Metricool (a elección), con la cuenta y la clave de la persona, incluido el primer comentario. Siempre muestra antes qué, dónde y cuándo, y no envía nada sin un OK. Usar cuando digan "publicalo", "programalo", "subilo a Instagram" o "agendá el post".
role: social-media-manager
files: []
---

# Publicar con Zernio o con Metricool

Motores: `.kit/engines/publish/zernio.py` y `.kit/engines/publish/metricool.py`. La clave nunca se muestra ni se guarda en archivos del proyecto.
Se elige con `--via zernio` (por defecto) o `--via metricool`, en el mismo comando `python3 .kit/launch.py publish`.
Los dos hacen lo mismo: prueba sin enviar, `--confirm` para enviar, fecha futura en la zona de la persona y primer comentario.

## Delegación
- El caption, el primer comentario y la hora los decide el rol social-media-manager. En Claude Code: use the Agent tool with subagent_type `social-media-manager`. En Codex: adopt the `social-media-manager` role from AGENTS.md.
- El texto lo pule el rol copywriter. En Claude Code: use the Agent tool with subagent_type `copywriter`. En Codex: adopt the `copywriter` role from AGENTS.md.

## Una sola vez
1. La persona crea su cuenta en zernio.com y conecta sus redes ahí.
2. Copia su clave (API key) de Zernio y la guarda en el llavero de su Mac. La Terminal la pide sin mostrarla:
   ```
   security add-generic-password -s content-kit -a ZERNIO_API_KEY -w
   ```
   (Windows: `cmdkey /generic:content-kit:ZERNIO_API_KEY /user:kit /pass`)
3. Comprobar: `python3 .kit/launch.py publish accounts` lista sus cuentas.

## Una sola vez, si usa Metricool
1. Consigue su clave en Metricool (Cuenta > API) y anota su número de usuario y el de la marca (blog) donde publica.
2. Guarda los tres valores en el llavero (cada comando los pide sin mostrarlos):
   ```
   security add-generic-password -s content-kit -a METRICOOL_API_KEY -w
   security add-generic-password -s content-kit -a METRICOOL_USER_ID -w
   security add-generic-password -s content-kit -a METRICOOL_BLOG_ID -w
   ```
   (Windows: `cmdkey /generic:content-kit:METRICOOL_API_KEY /user:kit /pass`, y lo mismo con los otros dos nombres.)
3. Comprobar: `python3 .kit/launch.py publish --via metricool accounts` lista sus marcas con su número. Para otra marca en una corrida: `--blog-id`.

## Flujo
1. **Pieza final.** Un reel (`.mp4` de la skill `reel`) o las imágenes del carrusel (2 a 10 PNG).
2. **Caption** en un archivo de texto: hook en la primera línea, cuerpo corto, CTA. El primer comentario invita a comentar (una pregunta concreta).
3. **Prueba** (no envía nada):
   ```
   python3 .kit/launch.py publish post --handle @su_cuenta --video reel.mp4 --caption caption.txt --at 2026-10-01T18:00 --platforms instagram,facebook --first-comment "¿Qué harías vos?"
   ```
   Carrusel: `--images out/slide-01.png out/slide-02.png ...` en vez de `--video`.
   Con Metricool es igual, sin `--handle` (publica en la marca configurada): `python3 .kit/launch.py publish --via metricool post --images out/slide-01.png out/slide-02.png --caption caption.txt --at 2026-10-01T18:00 --platforms instagram,facebook --first-comment "¿Qué harías vos?"`. En Facebook el carrusel usa la primera imagen. Guarda un recibo (`caption.metricool.json`) y no repite la misma pieza salvo `--again`.
4. **Mostrar a la persona** el resumen que imprime (cuenta, redes, fecha, caption, comentario) y esperar su OK explícito.
5. **Programar:** el mismo comando con `--confirm`. Decir el id y que lo revise en zernio.com o en Metricool. Si una red falla y otra salió, no repetir la que salió.

## Reglas
- Nunca `--confirm` sin el OK de la persona para ESA pieza.
- Nunca leer, imprimir ni copiar la clave.
- La hora va en su zona (`--tz`, por defecto America/Costa_Rica).
- Chequeo sin conexión: `python3 .kit/launch.py publish --selftest` (o `--via metricool --selftest`).
