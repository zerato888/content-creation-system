---
name: logo
description: Crea el logo de tu marca con IA (ChatGPT recomendado) a partir de tu ficha de marca — foto de perfil para Instagram y logotipo con fondo transparente — y revisa cada imagen antes de usarla. Úsalo después de armar tu brand.json, cuando necesites tu logo o tu foto de perfil.
role: creative-director
files: []
---

# Logo con IA

El logo siempre se hace con IA. El kit escribe el pedido desde tu ficha de marca, la IA dibuja,
y un control revisa la imagen antes de que la uses.

**Herramienta recomendada: ChatGPT** (Plus, USD 20/mes, o Pro, USD 100/mes). Genera imágenes y
logotipos con fondo transparente mejor que las demás, y con tu cuenta de ChatGPT también tienes
Codex. **Alternativa:** Claude + un generador de imágenes aparte (Higgsfield o Magnific, con su
propio costo), porque Claude no genera imágenes.

## Delegación

- Las direcciones de logo y los pedidos los arma el rol dp-cinematographer. En Claude Code: use the Agent tool with subagent_type `dp-cinematographer`. En Codex: adopt the `dp-cinematographer` role from AGENTS.md.
- La revisión de marca la hace el rol creative-director. En Claude Code: use the Agent tool with subagent_type `creative-director`. En Codex: adopt the `creative-director` role from AGENTS.md.

## Flujo

1. **Ficha de marca.** Tiene que existir `.kit-personal/brands/<marca>.json` (si no, primero `brand-onboarding`).
2. **Ronda 1: 5 propuestas.** El dp-cinematographer (o creative-director) escribe 5 pedidos, cada uno
   UNA lámina 1536x1024 con **isotipo + nombre juntos** sobre fondo liso. Los 5 tienen que ser
   ideas distintas de verdad: monograma, letras dibujadas, sello o emblema, marca geométrica,
   espacio negativo. Nunca "una hoja al lado del nombre" repetida con otro marco. Nada de
   clipart del rubro (gotas, burbujas, hojita genérica). El miembro elige **una**.
   **Ronda 2, solo con el ganador:** dos pedidos que copian ese diseño (adjuntá la lámina ganadora
   como referencia):
   - **perfil**: ícono cuadrado 1:1, 1024x1024, fondo sólido del color `background`, símbolo dentro
     del 70% central (Instagram lo recorta en círculo), que se lea a 110 px.
   - **logotipo**: el mismo isotipo + nombre, horizontal, **PNG con fondo transparente real** (canal
     alfa), nunca fondo blanco ni cuadriculado dibujado.
   - Siempre: plano, vectorial, sin mockups, sin sombras 3D, sin texto extra, sin marca de agua.
3. **Generar.** Empieza SIEMPRE el pedido con esta línea (sin ella, Codex a veces "resuelve" dibujando
   el logo con código, y eso no es un logo hecho con IA):
   `STRICT RULE: create this image ONLY with your built-in image generation tool. Do NOT write code, SVG, HTML, Pillow/PIL, ImageMagick or any script to draw it, and do not edit or resize the result. If the image tool is unavailable or fails, stop and say so.`
   - **Codex (con tu cuenta de ChatGPT):** escribe `$imagegen` seguido del pedido. Las imágenes
     quedan en tu carpeta de Codex (`generated_images`); cópialas a `assets/logo/` de tu proyecto.
   - **App de ChatGPT:** pega el pedido, descarga como PNG y guárdalo en `assets/logo/`.
   - **Higgsfield o Magnific:** mismo pedido, descarga en PNG.
4. **Control de calidad** (obligatorio, antes de usar la imagen):
   `python .kit/launch.py logo perfil assets/logo/perfil.png --brand .kit-personal/brands/<marca>.json`
   `python .kit/launch.py logo logotipo assets/logo/logotipo.png --brand .kit-personal/brands/<marca>.json`
   Revisa tamaño, cuadrado, fondo sólido, que el símbolo no toque el borde del círculo, fondo
   transparente real y que aparezcan los colores de la marca. Si falla, agrega el motivo que
   imprime al pedido y genera de nuevo.
5. **Revisión.** El creative-director mira los que pasaron: legible a 110 px, ortografía exacta,
   coherente con la ficha. Elige uno de cada tipo.

## Reglas

- Solo cuenta un logo que salió del generador de imágenes. Si ves que Codex escribió código, SVG o
  un script para dibujarlo, descarta ese archivo y pide de nuevo con la regla del paso 3.

- Nunca agrandes una imagen generada por IA: si sale chica o borrosa, pídela de nuevo a 1024x1024.
- Si el logotipo sale con fondo blanco, pide otra vez "transparent background PNG". Quitar el
  fondo con otra herramienta está permitido: no cambia el tamaño.
- Guarda el logo elegido en `assets/logo/` y úsalo en carruseles y videos.
- Control sin conexión: `python .kit/launch.py logo --selftest`.
