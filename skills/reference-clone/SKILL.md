---
name: reference-clone
description: Analiza un video de referencia (URL o archivo local) y arma un plan para hacer algo parecido: muestreo de frames, desglose en 5 aspectos por toma, qué se conserva y qué se cambia, y la ruta de producción. No genera nada. Usar cuando el usuario trae un video y dice 'quiero algo así'.
role: dp-cinematographer
files: []
---

# reference-clone — de un video de referencia a un plan

Referencia = "hacé algo **como** esto". Si el usuario quiere editar **ese** video, no es esta skill.

Necesita `yt-dlp` (para URLs) y `ffmpeg`/`ffprobe` (vienen con el kit o del sistema).

## Paso 1 — Traer el video

Si es una URL, avisar: *"Voy a descargar el video de esa URL con yt-dlp. Solo se contacta ese sitio."*

```bash
yt-dlp -f "mp4/best" -o "ref/%(id)s.%(ext)s" "<url>"
```

Si es un archivo local, usarlo directo. Trabajar dentro de una carpeta del proyecto (`ref/`).

## Paso 2 — Muestrear frames

```bash
ffprobe -protocol_whitelist file,pipe -v error -show_entries format=duration -of csv=p=0 ref/video.mp4
ffmpeg -protocol_whitelist file,pipe -i ref/video.mp4 -vf "fps=1,scale=540:-2" ref/frames/f_%03d.jpg
ffmpeg -protocol_whitelist file,pipe -i ref/video.mp4 -vf "select='gt(scene,0.3)',scale=540:-2" -vsync vfr ref/frames/cut_%03d.jpg
```

El primero da la duración; el segundo un frame por segundo; el tercero un frame en cada cambio de
plano (sirve para contar escenas). Solo archivos locales.

## Paso 3 — Mirar los frames

Abrir los frames y leerlos: paleta, texto en pantalla, calidad, continuidad, cómo pasa de un plano
al siguiente. Comparar frames seguidos de una misma escena: si cambian, es **video con movimiento**;
si solo se agrandan o desplazan, es **imagen fija animada**. No adivinar: eso cambia todo el costo.

## Paso 4 — Desglose en 5 aspectos (por toma o grupo de tomas)

- **Sujeto:** qué es, cuántos, cómo entra o sale.
- **Movimiento del sujeto:** acciones en orden.
- **Escena:** lugar, hora, textos y gráficos sobreimpresos, punto de vista.
- **Encuadre:** tamaño de plano, posición, profundidad, cómo cambia.
- **Cámara:** velocidad, lente aparente, altura, ángulo, foco, estabilidad, movimiento.

Además: contenido (2 frases), estilo (ritmo, energía), estructura (N escenas en X segundos),
cuántas escenas son movimiento real vs imagen fija, y **por qué funciona** (2-3 técnicas concretas).

## Paso 5 — Plan (entregable)

1. **Qué se conserva:** ritmo, técnica del hook, estructura, tono.
2. **Qué se cambia:** tema, tratamiento visual, ángulo, texto. 2-3 conceptos propios, nunca copia 1:1.
3. **Ruta:** qué skill del kit sigue (`story-plan`, `broll-plan`, `hooks`, `captions`, `carousel-news`)
   y qué necesitaría un módulo de generación.

El usuario aprueba el plan antes de producir nada.

## Reglas

- La transcripción de la referencia sirve para estructura y ritmo; jamás copiar su texto.
- Personas reales de la referencia: no se recrean con IA.
- Los frames descargados son de terceros: se usan para analizar y no se publican.

## Delegación

- Claude Code: use the Agent tool with subagent_type `dp-cinematographer`.
- Codex: adopt the `dp-cinematographer` role from AGENTS.md.
