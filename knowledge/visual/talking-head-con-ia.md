# Talking-head editado con IA: flujo de seis pasos

*Crédito: flujo observado en un editor que publicó su método; resumido con palabras propias.*

**Tesis:** la IA sola no reemplaza a un editor, pero una IA entrenada con criterio de editor produce resultados muy
buenos en una fracción del tiempo. La ventaja es entrenar con material propio y con decisiones anotadas (por qué
ese hook, por qué ese corte).

1. **Transcripción con marcas de tiempo** a un archivo estructurado; una skill de recorte marca los tramos y
   ffmpeg corta.
2. **Subtítulos** ([captions.md](../captions.md)).
3. **Plan de edición línea por línea**, con `dp-cinematographer` y [visual-language.md](../visual-language.md). La
   pregunta única: **¿esta línea es crucial para entender?** Si sí, lleva una animación o visual que la explique,
   fundamentada en los disparadores; si no, es un **respiro** de subtítulos puros, un descanso deliberado para
   conectar con quien habla. Prohibido repartir bloques de forma mecánica por tiempo.
4. **Maquetas estáticas antes de animar.** Animar es lo caro: primero se aprueba la imagen fija.
5. **Animación de unos 5 s con efectos de sonido y sin música**, con la cámara descrita de forma explícita.
6. **Armado con una tabla de línea de tiempo** (recurso, entrada y salida exactas): arrastrar y soltar, sin decidir.

## Reglas que se desprenden
- El respiro es diseño, no falta de recursos, y baja del 40 al 50% el costo de gráficos por lote.
- A escala (30 clips o más), dos niveles: plan completo solo para las piezas de nivel A.
- El estilo de los gráficos se fija una vez por lote sobre la paleta de la marca.
- Personajes generados genéricos son una vía válida cuando la historia es de otra persona real y no se quiere
  usar su cara.
