# Estructuras narrativas para carruseles

Cada slide tiene dos capas: **qué cuenta** (el módulo) y **cómo se ve** (el tipo de slide del motor).
Pensado para negocios y marcas personales.

## Reglas (el motor avisa si no se cumplen)
- De 4 a 8 slides. La primera es `cover` y la última es `cta`.
- Una idea por slide. Si no tienes una idea nueva, no agregues un slide de relleno.
- Nunca dos slides del mismo tipo seguidos: cansa la vista.
- Un número se presenta como real solo si es tuyo o tiene fuente. Si es ilustrativo, escribe "(ejemplo)".

## Módulos
| módulo | qué hace | ejemplo | tipo de slide |
|---|---|---|---|
| problema | el dolor de tu cliente, en sus palabras | "Publicas todos los días y nadie reserva." | cover, headline |
| error_comun | lo que casi todos hacen mal | "Ahorrar lo que sobra a fin de mes." | headline |
| por_que_pasa | la causa real del problema | "Tus fotos muestran el plato, no el motivo para venir." | body |
| como_lo_resuelvo | tu método, en un paso claro | "Armo un mes de posts con tu menú real." | body, headline |
| pasos | 3 a 5 pasos concretos, uno por slide | "Paso 1: aparta primero, gasta después." | headline (×3) |
| antes_despues | el cambio en dos momentos | "Antes: 6 horas por video. Ahora: una idea." | stat, body |
| dato | una cifra que sorprende, con fuente o "(ejemplo)" | "40 barras por lote (ejemplo)." | stat |
| historia | cómo empezó, una escena real | "Empezó en una cocina, un lote a la vez." | headline, body |
| como_se_usa | el producto en la vida del cliente | "Haz espuma entre las manos y aplícala." | body |
| prueba | testimonio o resultado real | "«Por fin las redes hablan como nosotros.»" | quote, stat |
| frase | la idea que la gente guarda y comparte | "El orden no te quita libertad." | quote |
| mito_realidad | desarma una creencia | "Mito: necesitas más horas. Realidad: menos tareas." | body |
| oferta | qué ofreces y el siguiente paso | "Te reviso tus últimas 9 publicaciones gratis." | cta |
| pregunta | invita a comentar | "¿Qué tema explicamos después?" | cta |

## Tres estructuras listas (ver los ejemplos en esta carpeta)
- **Servicios** (`ejemplo-servicios.json`): problema → por qué pasa → cómo lo resuelvo → qué haces tú → prueba → testimonio → oferta.
- **Marca personal** (`ejemplo-marca-personal.json`): problema → error común → paso 1 → paso 2 → paso 3 → frase → pregunta u oferta.
- **Producto** (`ejemplo-producto.json`): gancho → historia → oficio → ingredientes → cómo se usa → dato → oferta.

## Imágenes (gratis)
El motor no descarga nada: cada imagen es un archivo dentro de la carpeta del proyecto.
- **Fotos propias** (celular): la mejor opción para producto y marca personal.
- **Bancos gratis**: Unsplash o Pexels, descargadas a mano.
- **IA**: la generas aparte (ChatGPT, Gemini) y guardas el archivo.
- `"image_position": "top"` o `"bottom"` pone la foto en una franja y el texto sobre fondo limpio. `"full"` (por defecto) la pone de fondo con sombra.
