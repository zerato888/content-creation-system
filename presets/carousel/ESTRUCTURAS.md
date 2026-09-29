# Estructuras narrativas para carruseles

Cada slide tiene dos capas: **qué cuenta** (el módulo) y **cómo se ve** (el tipo de slide del motor).
Pensado para negocios y marcas personales.

## Reglas (el motor avisa si no se cumplen)
- De 4 a 8 slides. La primera es `cover` y la última es `cta`.
- Una idea por slide. Si no tienes una idea nueva, no agregues un slide de relleno.
- Nunca dos slides del mismo tipo seguidos: cansa la vista.
- Un número se presenta como real solo si es tuyo o tiene fuente. Si es ilustrativo, escribe "(ejemplo)".
- El mismo texto no se repite en dos slides.

## Guía del copywriter (no la controla el motor, pero sube el alcance)
- **Tensión.** Al menos un slide que choque: un error común, un mito, dos posturas, un antes y después o un dato que no cuadra. Un carrusel sin tensión se desliza sin guardarse.
- **Cierre que invite.** Si el objetivo es comentarios, el último slide termina en una pregunta concreta de A o B, y el **primer comentario** repite esa pregunta. Si el objetivo es vender, termina en la oferta con un paso claro.
- **Imágenes.** Como máximo 1 slide sin imagen si el carrusel tiene 4 o 5, y 2 si tiene de 6 a 8. La portada no cuenta. La foto va en una franja (`image_position`) y el texto sobre fondo limpio, nunca encima de la foto.
- **Una foto por idea.** Cifra: el hecho detrás del número. Cita: la persona que la dijo. Pasos: la acción. Cierre: la persona o el lugar de la pregunta.

## Portada (estándar)
- Una sola portada: siempre el slide 1. Una cita, una cifra o un versus nunca van en la portada; van en el slide 2.
- El titular dice el tema de entrada y nunca es una cita entre comillas.
- Foto a pantalla completa que se funde al color de fondo en el tercio inferior. Si el tema nombra a una persona real, se usa una foto real de esa persona, nunca una cara inventada.
- Tildes en mayúsculas: el motor frena el slide si la tilde toca la línea de arriba.

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
| contradiccion | lo que se dice vs. lo que pasa | "Todos dicen 'publicá más'; los que crecen publican menos." | body |
| lo_que_nadie_dice | el dato incómodo | "Nadie te cuenta que el 80% no vuelve a comprar." | body |
| dato_que_no_cuadra | la cifra que rompe el relato | "3 posts por semana. 10 000 seguidores." | stat |
| traducido_a_tu_bolsillo | la cifra en plata o tiempo del lector | "Son 4 horas por semana que recuperás." | stat |
| la_escena | una persona real en el momento | "Ana abrió el local a las 6 y no entró nadie." | headline |
| ya_paso_antes | el precedente | "En 2020 pasó lo mismo con los reels." | body |
| voz_experta | cita con nombre y cargo | "«El precio sigue al problema» — nombre, cargo." | quote |
| linea_de_tiempo | 3 a 5 momentos en orden | "Mes 1: … · Mes 3: … · Mes 6: …" | headline (×3) |
| encuesta_ab | pone al lector a elegir | "¿Precio bajo o precio alto?" | cta |

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
