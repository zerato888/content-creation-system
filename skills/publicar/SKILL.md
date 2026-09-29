---
name: publicar
description: Programa un reel o un carrusel terminado en Instagram, Facebook o TikTok a través de Zernio, con la cuenta y la clave de la persona, incluido el primer comentario. Siempre muestra antes qué, dónde y cuándo, y no envía nada sin un OK. Usar cuando digan "publicalo", "programalo", "subilo a Instagram" o "agendá el post".
role: social-media-manager
files: []
---

# Publicar con Zernio

Motor: `.kit/engines/publish/zernio.py`. La clave nunca se muestra ni se guarda en archivos del proyecto.

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
3. Comprobar: `python .kit/launch.py publish accounts` lista sus cuentas.

## Flujo
1. **Pieza final.** Un reel (`.mp4` de la skill `reel`) o las imágenes del carrusel (2 a 10 PNG).
2. **Caption** en un archivo de texto: hook en la primera línea, cuerpo corto, CTA. El primer comentario invita a comentar (una pregunta concreta).
3. **Prueba** (no envía nada):
   ```
   python .kit/launch.py publish post --handle @su_cuenta --video reel.mp4 --caption caption.txt --at 2026-10-01T18:00 --platforms instagram,facebook --first-comment "¿Qué harías vos?"
   ```
   Carrusel: `--images out/slide-01.png out/slide-02.png ...` en vez de `--video`.
4. **Mostrar a la persona** el resumen que imprime (cuenta, redes, fecha, caption, comentario) y esperar su OK explícito.
5. **Programar:** el mismo comando con `--confirm`. Decir el id y que lo revise en zernio.com.

## Reglas
- Nunca `--confirm` sin el OK de la persona para ESA pieza.
- Nunca leer, imprimir ni copiar la clave.
- La hora va en su zona (`--tz`, por defecto America/Costa_Rica).
- Chequeo sin conexión: `python .kit/launch.py publish --selftest`.
