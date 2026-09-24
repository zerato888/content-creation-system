# Componentes, presets y marcas

El kit no se organiza por marca. Se organiza por **componentes reutilizables**: un estilo de subtítulos,
un preset de B-roll, un formato de carrusel. Tu marca *usa* esos componentes.

## Cinco reglas

1. **Un motor por tipo de preset.** Cada familia de presets la lee un solo programa. Si dos programas leen el
   mismo preset de forma distinta (por ejemplo, la vista previa y el render), el preset deja de ser confiable.
   Se aprueba siempre sobre el render del motor real.
2. **Los presets están separados de las marcas.** Un preset dice *cómo se ve o se mueve* algo. No dice de quién es.
3. **Tokens de marca.** Tu identidad (colores, fuentes, logo, qué componentes podés usar) vive en un archivo
   cerrado: `.kit-personal/brands/<marca>.json`. Lo crea la skill `brand-onboarding`. Una clave que el motor
   no conoce se ignora; una que falta toma su valor por defecto.
4. **Recetas.** Una pieza concreta = componente con versión + tokens de marca + receta de la pieza
   (contenido, tiempos, variante). Nombrar el preset tiene que alcanzar para reproducirlo igual.
5. **Disciplina de estado.** Todo preset tiene estado:
   - `stable`: aprobado sobre un render real.
   - `pilot`: funciona, pero no está aprobado para producción.
   - sin registrar: el archivo existe pero no está en el registro. No se usa hasta registrarlo.

   Un `pilot` nunca se presenta como producción, aunque el render se vea bien.

## Producir desde la plantilla, no desde la última pieza

Copiar el último video terminado como base copia también sus errores. La base es siempre la plantilla del
componente; los datos de la pieza van aparte.

## Un dueño por dato

Cada dato vive en un solo lugar (una cifra en su fuente, la marca en su archivo, un preset en su registro).
Los demás documentos lo citan, no lo copian.
