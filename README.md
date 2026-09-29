# content-creation-system

Tu sistema de contenido con IA, listo para instalar. Lo pegás una vez en tu proyecto y tu asistente (ChatGPT/Codex o Claude Code) queda con:

- **11 roles expertos** que trabajan juntos: estrategia, guiones, copy, dirección de arte, edición, motion, redes, ingresos, interfaz y revisión de hechos.
- **Reglas de trabajo probadas**: plan antes de actuar, lenguaje simple, marca antes que creatividad, verificar antes de decir "listo", memoria de errores.
- **Skills** para cada paso: entrevista de marca, logo con IA, ideas, hooks, guiones, plan de b-roll, carruseles, subtítulos, investigación, wiki y tareas.
- **Command Center**: un tablero local con tus tareas, ideas y producción.

Todo corre en tu máquina. Tus datos quedan en `.kit-personal/` y nunca se suben.

## Lista de compras

| Qué | Para qué | Costo |
|---|---|---|
| **ChatGPT Plus o Pro** (recomendado) | Codex + imágenes (logos, portadas) | USD 20 o 100 al mes |
| Claude Pro o Max (alternativa) | Claude Code | desde USD 20 al mes |
| Higgsfield o Magnific (opcional) | Video e imágenes con IA si usás Claude | según plan |
| Zernio (opcional) | Programar publicaciones | según plan |

## Instalación en Mac (unos 20 minutos)

1. Instalá Homebrew (si no lo tenés) desde <https://brew.sh> y después, en la Terminal:

```bash
brew install python@3.12 ffmpeg-full git
```

2. Bajá el kit en la carpeta de tu proyecto e instalalo:

```bash
git clone https://github.com/zerato888/content-creation-system.git ~/content-creation-system
```

```bash
mkdir -p ~/MiMarca && ~/content-creation-system/install.sh install --target ~/MiMarca --tool codex --all
```

El instalador pregunta antes de cada descarga (dependencias de Python, tipografías libres, el navegador para exportar carruseles y el modelo de subtítulos).

3. Abrí Codex (o Claude Code) dentro de `~/MiMarca` y escribí: **"hagamos el onboarding"**.

## Cómo saber que todo funciona

```bash
python3 .kit/launch.py doctor
```

Te dice en lenguaje simple qué funciona y qué falta (Python, ffmpeg con subtítulos, navegador, modelo de transcripción, fuentes, claves, skills). Nunca muestra tus claves.

## Qué puedes pedirle

- **Marca:** "armemos mi marca" (entrevista, logo con 5 propuestas, dirección visual, ficha).
- **Contenido:** ideas, hooks, guiones, plan de b-roll, carruseles, subtítulos y **reel desde tu grabación** ("armá el reel de este video").
- **Imágenes:** "generá una imagen" (ChatGPT/Codex o Gemini) y galería para aprobar o rechazar.
- **Publicar:** "programá este reel para mañana a las 6" en Zernio o Metricool, con tu cuenta y tu clave (siempre te muestra qué, dónde y cuándo antes de enviar).
- **Conocimiento:** wiki propia, ingestar cursos y que tus agentes los usen; Content Capital ya viene cargado.
- **Tablero:** `python3 .kit/launch.py serve` abre el Command Center (tareas, ideas, producción y Vida Personal).

## Actualizar, revisar, volver atrás

```bash
~/content-creation-system/install.sh update --target ~/MiMarca
```

`status` muestra qué hay instalado y `rollback` vuelve a la versión anterior. Tu marca, tus lecciones y tu memoria no se tocan nunca.

## Windows

Instalá Python 3.11+ desde <https://www.python.org/downloads/> y ffmpeg, y usá `install.ps1` con los mismos pasos.

## Licencia

Código bajo PolyForm Noncommercial 1.0.0, contenido bajo CC BY-NC 4.0 (ver `LICENSE` y `NOTICE`). Uso personal y no comercial libre; el uso comercial requiere permiso escrito.
