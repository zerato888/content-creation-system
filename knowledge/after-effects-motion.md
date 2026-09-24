# Motion graphics en After Effects

> Solo aplica si instalaste el módulo de After Effects. Lo usa el rol `motion-designer`.

## Proceso para clonar una referencia
Cada paso deja un archivo, así se puede revisar y retomar:

1. **Brief.** El texto se transcribe cuadro por cuadro del original. Nunca se supone: suponer suele salir mal.
2. **Ficha de movimiento** medida con herramientas (ffmpeg, OpenCV): cortes, pausas, picos, curvas, colores.
3. **Cuadro clave estático.** Tres planos representativos, lado a lado original y clon, con diferencias medidas.
   Primera aprobación.
4. **Animación editable desde el primer lote.** Todo atado a marcadores, el texto se ajusta solo a su largo,
   colores en un panel de controles, capas con nombres claros.
5. **Prueba de edición en una copia antes de aprobar:** otro texto más largo, otros colores, un marcador movido.
   Casi siempre rompe algo que el original no mostraba.
6. **Comparación lado a lado con cifras** que salen de un script guardado, no de una impresión.
7. **Aprobación final → catálogo:** parámetros, README (cuándo sí y cuándo no usarlo), proyecto sin audio ajeno, ejemplos.
8. **Revisión independiente** que vuelve a medir todo.

## Técnicas que conviene conocer
- **Tipografía cinética:** entradas cortas con posición + opacidad y curva agresiva; desenfoque que se enfoca;
  tracking que se abre; texto que nace de una línea; selectores de texto para animar por letra o palabra.
- **Formas:** morph de trazados cuidando el vértice inicial; rebotes ajustados en el editor de curvas; líneas que
  se dibujan con Trim Paths; repetidores para patrones radiales o en grilla.
- **Transiciones:** barridos con formas y mates; barrido por luminancia; glitch con mapa de desplazamiento;
  transiciones "sin costura" con Motion Tile.
- **Expresiones:** loops de keyframes, `wiggle` con control, `posterizeTime` para un look "a saltos", contadores,
  retrasos en cascada con `valueAtTime`, límites con `clamp`, un texto maestro para plantillas.
- **Cámara 3D:** cámara guiada por un null; profundidad de campo; proyección de una foto plana para dar paralaje.
- **Luz y sombras:** sombras sobre un piso invisible, sombras largas, luz que barre una superficie.
- **Texturas:** borde que "hierve" con Turbulent Displace suave, grano, papel, aberración cromática nativa.
- **Tracking:** seguimiento de puntos a un null, tracker de cámara 3D, reemplazo de pantallas. Parte del análisis es manual.

## Reglas
- Construir en el formato final desde el principio (por ejemplo 1080×1920 a 30 fps para vertical). Si la
  referencia usa pocos cuadros por segundo como efecto, imitarlo con `posterizeTime`, no bajando la composición.
- **Nada es imposible sin una prueba que falle.** Probar en una composición descartable antes de declarar un límite.
- Una técnica entra al recetario solo después de una micro-prueba renderizada (~2 s) y comparada.
- Preferir efectos nativos; un plugin de terceros se justifica y lo aprueba el usuario.
- Validar un bloque piloto en movimiento antes de extender el estilo.
- Si After Effects parece colgado, revisar primero si hay un diálogo abierto esperando un clic.

*Crédito: estas técnicas son de conocimiento común en la comunidad de motion design (tutoriales públicos de
School of Motion, Ben Marriott, ECAbrams, Jake Bartlett y otros). Acá están resumidas con palabras propias.*
