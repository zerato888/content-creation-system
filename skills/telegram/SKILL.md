---
name: telegram
description: Manda una pieza terminada (video, audio, imagen o archivo) o un aviso corto al celular de la persona con su propio bot de Telegram. Los videos y audios llegan reproducibles. Usar cuando digan "mandámelo al celular", "avisame por Telegram", "envialo a mi Telegram" o al terminar un trabajo largo que se quiere ver desde el teléfono.
role: social-media-manager
files: []
---

# telegram — la pieza en tu celular

Motor: `.kit/engines/telegram/tg_send.py`. Usa el bot de la persona; el token y el chat viven en el llavero, nunca en archivos del proyecto.

## Delegación
- El texto del aviso lo pule el copywriter; qué se manda y cuándo lo decide el social-media-manager.
- Claude Code: use the Agent tool with subagent_type `social-media-manager`.
- Codex: adopt the `social-media-manager` role from AGENTS.md.

## Una sola vez (lo hace la persona)
1. En Telegram, hablar con **@BotFather**, crear un bot y copiar el token.
2. Escribirle cualquier mensaje al bot nuevo. Luego abrir `https://api.telegram.org/bot<TOKEN>/getUpdates` en el navegador y copiar el número `id` del chat.
3. Guardar los dos en el llavero (la Terminal pide cada valor sin mostrarlo):
   ```
   security add-generic-password -s content-kit -a TELEGRAM_BOT_TOKEN -w
   security add-generic-password -s content-kit -a TELEGRAM_CHAT_ID -w
   ```
   Windows: `cmdkey /generic:content-kit:TELEGRAM_BOT_TOKEN /user:kit /pass` y lo mismo con `TELEGRAM_CHAT_ID`.
4. Comprobar (solo dice si están, nunca los muestra): `python .kit/launch.py telegram check`

## Flujo
1. Prueba, no envía nada: `python .kit/launch.py telegram file out/reel.mp4 "Reel de prueba"`
2. Mostrar a la persona qué se va a mandar y esperar su OK.
3. Enviar: el mismo comando con `--confirm`. Un aviso de texto: `python .kit/launch.py telegram text "Listo el lote"`.

## Reglas
- Nunca `--confirm` sin el OK de la persona para esa pieza.
- Nunca leer, imprimir ni copiar el token; si un error lo menciona, no repetirlo.
- Tope de Telegram para bots: **50 MB**. Un video más pesado se manda como una copia más liviana que se arma aparte; el original no se toca.
- Video y audio llegan reproducibles; imágenes hasta 10 MB llegan como foto; lo demás, como archivo. Si Telegram rechaza el formato, cae solo a archivo.
- Cada envío lleva una línea de pie que diga qué es la pieza.
- No sirve para publicar en redes: eso es la skill `publicar`.
