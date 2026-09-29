---
name: reel
description: Convierte una grabación a cámara (talking head vertical) en un reel terminado sin abrir un editor. Quita los silencios, pone subtítulos de la marca quemados en el video, mete b-roll encima de la voz donde lo marque el plan y una música de fondo a volumen fijo. Usar cuando la persona diga "me grabé", "armá el reel", "editá este video" o pase un video suyo hablando.
role: editor-video
files: []
---

# Reel desde una grabación

Motor: `.kit/engines/video/reel.py` (usa el motor de subtítulos del kit). Todo local; el original nunca se toca.

## Delegación
- La edición y la revisión final las hace el rol editor-video. En Claude Code: use the Agent tool with subagent_type `editor-video`. En Codex: adopt the `editor-video` role from AGENTS.md.
- El plan de b-roll lo arma el rol dp-cinematographer con la skill `broll-plan`. En Claude Code: use the Agent tool with subagent_type `dp-cinematographer`. En Codex: adopt the `dp-cinematographer` role from AGENTS.md.

## Flujo
1. **Grabación.** Video vertical (9:16) de la persona hablando, en la carpeta del proyecto. Una sola toma buena por frase ayuda: el corte quita silencios, no tomas repetidas.
2. **Cortar silencios.**
   ```
   python .kit/launch.py reel cut "<video>"
   ```
   Sale `<video>.cut.mp4` y `<video>.cut_plan.json` (qué partes quedaron). Si corta de más, subir `--noise` (ej. `-40`); si deja pausas, bajar `--min-silence` (ej. `0.3`).
3. **Transcribir y revisar el texto (obligatorio).**
   ```
   python .kit/launch.py captions transcribe "<video>.cut.mp4" --lang es
   ```
   Mostrá el texto a la persona y corregí nombres o jerga en el JSON antes de seguir.
4. **B-roll (opcional).** El dp-cinematographer lee el guion con los tiempos y propone dónde va cada imagen. Los clips salen de la persona (sus grabaciones), de su banco o de la skill `broll-higgsfield`. Se escribe `broll.json`:
   ```json
   [{"start": 2.0, "end": 4.5, "file": "assets/broll/cafe.mp4"}]
   ```
   Tiempos sobre el video ya cortado. El b-roll tapa la imagen, la voz sigue.
5. **Armar el reel.** Preguntar siempre la altura de los subtítulos (abajo 0.12, medio 0.5, arriba 0.7).
   ```
   python .kit/launch.py reel build "<video>.cut.mp4" --brand .kit-personal/brands/<marca>.json --base-preset base-bold-left --margin-v-frac 0.2 [--hook-preset hook-serif-escalation] [--broll broll.json] [--music musica.mp3 --music-db -22]
   ```
   Sale `<video>.reel.mp4` en 1080×1920, listo para publicar.
6. **Revisar antes de entregar.** Mirar 3 cuadros (inicio, un b-roll, el final) y escuchar el audio: voz clara, música baja y pareja, subtítulos en sincronía y nada tapado. Entregar solo el reel final.

## Reglas
- La música va a un volumen fijo debajo de la voz, sin subidas ni bajadas.
- Nunca agrandar un clip de IA para que "entre": el motor ya lo recorta para cubrir 9:16.
- Chequeo sin conexión: `python .kit/launch.py reel --selftest`.
