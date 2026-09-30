---
name: imagen
description: Genera una imagen suelta (portada, miniatura, ilustración, foto editada) con la herramienta de imágenes que la persona ya tenga: ChatGPT/Codex primero, Gemini después, y Magnific o Higgsfield como alternativas. Usa imágenes de referencia por ruta, nunca las agranda y reintenta si sale en blanco o con el fondo equivocado. Usar cuando digan "generá una imagen", "hacé la portada", "una miniatura de...", "editá esta foto con este estilo" o "bajá esta imagen de internet".
role: dp-cinematographer
files: []
---

# imagen — una imagen, con lo que tengas

Motor: `.kit/engines/imagegen/imagegen.py`. Funciona aunque la persona solo tenga Codex.

## Delegación
- La composición y el prompt los diseña el rol dp-cinematographer; la revisión de marca, el creative-director.
- Claude Code: use the Agent tool with subagent_type `dp-cinematographer`.
- Codex: adopt the `dp-cinematographer` role from AGENTS.md.

## Qué se necesita (elegir UNA vía; no hace falta más)
| Vía | Cómo se instala | Cuenta |
|---|---|---|
| **Codex (ChatGPT)** — la principal | `npm install -g @openai/codex` y luego `codex login` | ChatGPT (Plus o Pro) |
| **Gemini por `agy`** — gratis | programa aparte de Google; la persona lo instala y entra con su cuenta | cuenta Google |
| **Magnific / Higgsfield** | se conectan como conector MCP en Claude Code o Codex; no tienen comando local | su propia cuenta |

Si la persona no tiene ninguna, decírselo claro y recomendar Codex. Nunca instalar un programa global sin su OK.

## Flujo
1. Armar el prompt con el rol (qué se ve, luz, encuadre, texto exacto que debe aparecer, qué NO debe aparecer).
2. Si hay personas reales o un estilo a sostener, juntar las **imágenes de referencia** (`--ref`). El motor escribe cada ruta dentro del prompt y el agente las abre; no se pasan por otra vía.
3. Generar (elige solo el proveedor instalado, primero Codex, después `agy`):
   ```
   python3 .kit/launch.py imagegen "prompt" --dest out/imagenes --ref referencia.png --bg dark
   ```
   `--bg dark|light` pide fondo oscuro o claro; `--provider codex|agy` fuerza uno.
4. Mirar el resultado antes de entregarlo. Si el motor avisa `intento N: blank/extreme/dark/light`, la imagen salió mal y lo reintentó (hasta 2 veces); si el último intento sigue mal, decírselo a la persona.
5. Mostrar la pieza final con la skill `entrega`.

## Reglas
- **Nunca agrandar ni reescalar** una imagen ya generada (ni Lanczos ni nada): la ablanda. Si falta detalle, se regenera; en Magnific se pide más resolución explícita.
- El motor obliga al proveedor a usar SU herramienta nativa de imágenes (regla estricta): prohibido dibujar con código o copiar otra imagen.
- Con una imagen mala, arreglar el **prompt o las referencias**, no cambiar de motor ni inventar explicaciones.
- Una pieza única donde manda la calidad: Codex (tarda 4 a 10 minutos con referencias). Un lote de 5 o más piezas: Magnific o Higgsfield, porque la espera de Codex se acumula.
- Retrato de una persona real: usar SU foto como referencia y no cambiarle la edad ni los rasgos.
- Imagen de internet en vez de generarla: `python3 .kit/launch.py fetch-image <url> <destino> --min-side 720` (verifica que sea imagen real y no chica). Si trae marca de agua, descartarla.
- El chequeo de brillo usa Pillow si está instalado (`pip install pillow`); sin él, no reintenta por brillo pero todo lo demás funciona.

## Qué sale de tu máquina
El prompt y las referencias van al servicio elegido (OpenAI o Google) con la cuenta de la persona. Avisarlo antes de la primera vez.
