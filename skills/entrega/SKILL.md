---
name: entrega
description: Muestra las piezas terminadas en una galería de revisión local, en el navegador, donde la persona marca aprobar o rechazar y deja un comentario por pieza; las decisiones quedan en un archivo que el agente lee. Usar cuando haya 2 o más piezas para revisar, o cuando digan "mostrame las piezas", "quiero aprobar esto", "armá la galería" o "entrega".
role: creative-director
files: []
---

# entrega — revisar y decidir piezas

Motor: `.kit/engines/gallery/gallery.py`. Es una página local: no usa cuentas ni internet.

## Delegación
- Antes de mostrar, el creative-director revisa que cada pieza cumpla la marca.
- Claude Code: use the Agent tool with subagent_type `creative-director`.
- Codex: adopt the `creative-director` role from AGENTS.md.

## Flujo
1. Juntar solo las piezas **finales** en UNA carpeta (imágenes, videos `.mp4`, audios `.mp3`/`.m4a`). Pruebas y borradores no.
2. Abrir la galería:
   ```
   python .kit/launch.py gallery serve out/entrega --title "Entrega del lunes"
   ```
   Imprime una dirección `http://127.0.0.1:...` y abre el navegador. La dirección solo funciona en esta máquina y cambia cada vez. Si el navegador no abre, pasarle la dirección a la persona.
3. La persona marca **Aprobar** o **Rechazar** y escribe un comentario por pieza. Se guarda solo.
4. Cuando diga que terminó, leer las decisiones y actuar sobre ellas:
   ```
   python .kit/launch.py gallery read out/entrega
   ```
   Devuelve `{"pieza.png": {"status": "aprobado|rechazado|", "comment": "..."}}`. Lo rechazado se rehace con su comentario; lo aprobado sigue. Lo que quedó sin marcar se pregunta, no se supone.
5. Cerrar la galería (Ctrl+C) y anotar qué se aprobó.

## Reglas
- Una sola pieza: basta mostrarla directamente; la galería es para 2 o más.
- Video pesado: hacer una copia liviana solo para revisar; el original no se toca.
- Las decisiones viven en `decisiones.json` dentro de esa carpeta; no se editan a mano.
- Para mandar una pieza al celular: skill `telegram`.
- `python .kit/launch.py gallery list <carpeta>` muestra qué piezas detecta (formatos: png, jpg, webp, gif, mp4, mov, webm, mp3, m4a, wav).
