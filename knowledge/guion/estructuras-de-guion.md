# Estructuras de guion

Las estructuras con sus beats y plantillas viven en `presets/scripts/script-formats.json` (dueño único; esta página
no las copia). Sirve para elegir y aplicar.

## Cómo se usa el archivo
- `structures`: 13 estructuras nombradas, cada una con `when` (cuándo) y `beats` (pasos con plantilla).
  Historias de transformación (viaje del héroe, de X a Y), recuperación (hombre en un pozo), descubrimiento
  (el quiebre), error y arreglo, una sola decisión, lección de otro, y expectativa y reversión.
- `hook_styles`: siete estilos de arranque (confesión, contraste, dolor reconocible, afirmación provocadora,
  "si yo fuera vos", desmentir un mito, resultado en un tiempo).
- `storytelling_wheel`: capa obligatoria sobre cualquier estructura, ver [rueda-de-historias.md](rueda-de-historias.md).
- `cold_open_cinematic`: alternativa sin fórmulas de hook, cuatro actos.
- `voice`: la voz. **`voice.default`** es el valor neutro; cada marca lo pisa con el campo `voice` de su ficha
  (`.kit-personal/brands/<nombre>.json`). Sin voz definida, se usa el valor neutro.
- `process`: los siete pasos de escritura.

## Proceso resumido
1. Elegir la estructura que calza con el tema.
2. Escribir la **última línea primero**: qué querés que sientan al final.
3. Encontrar el hook: lo más honesto, incómodo o sorprendente enterrado en el tema.
4. Rellenar beats con PERO / POR LO TANTO, no con Y DESPUÉS.
5. Variar el largo de las frases.
6. Leerlo en voz alta: si suena escrito, se reescribe.
7. Cortar lo que no mueve la historia.

## Formatos por pieza
- **Reel o corto (30 a 90 s):** hook (0 a 3 s) que ya da tema y curiosidad, cuerpo con pequeños conflictos cada
  dos o tres frases, cierre que aterriza un sentimiento (no un resumen). CTA solo si cae natural.
- **Video largo (5 a 15 min):** apertura en frío, planteo del problema, re-gancho cada dos o tres minutos,
  dos a cuatro secciones de una idea cada una, cierre que vuelve a la tensión inicial.
- **Carrusel:** la portada es el hook; cada lámina termina con un bucle abierto (idea incompleta, pregunta,
  número, mini suspenso); máximo dos o tres líneas por lámina; la última paga la promesa y trae un solo CTA.

## Título y subtítulo del hook
- El **título** lleva tensión (subida y caída, contradicción, algo en juego o un error) y dice de qué trata
  desde la primera línea. Un logro plano ("llegó con poco y ganó mucho") no tiene fricción: no es un hook.
- El **subtítulo** es obligatorio: promete el cierre o suma contexto, genera una emoción (curiosidad, indignación,
  miedo, asombro, identificación), nunca repite el título ni es una frase fija.
- La **primera frase de la voz** dice esa misma tensión con otras palabras; el cierre paga la promesa.
- La primera línea hablada es la plantilla del banco con los huecos llenos, en 14 palabras o menos. No abre con
  cargos, instituciones, credenciales, fechas ni una descripción del sujeto: abre con una escena, una pérdida o
  una pregunta que le importe a quien mira.
- En una prueba se presentan tres opciones de categorías distintas; cada una cita la categoría y la plantilla.

## Cierre
Todo guion termina completo, también un episodio de serie: conclusión, lección o idea propia. La continuidad
entre episodios la llevan las portadas, los textos y la función nativa de series, no la voz.
