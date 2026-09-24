# Principios de trabajo

Cómo trabajar con el kit (y con un agente de IA en general) sin gastar de más ni adivinar.

## 1. Economía de tokens
Cada cosa que el agente lee cuesta contexto. Cuanto más lleno, peor razona.
- **Leer por partes:** la sección que hace falta, no el archivo entero.
- **Delegar las búsquedas grandes** a un subagente o rol; que vuelva con la conclusión, no con los archivos.
- **No volver a derivar** lo que ya está escrito: si hay una regla o una página, se cita.
- **Un dueño por dato:** cada dato vive en un lugar; los demás lo enlazan.

## 2. Escalera de investigación
Subir un escalón solo si el anterior no alcanza:

1. **agent-reach** — web, RSS, YouTube y GitHub desde la terminal, sin claves para lo básico.
   <https://github.com/Panniantong/Agent-Reach>
2. **defuddle** — saca el texto limpio de una página (sin menús ni publicidad), ideal para leer artículos.
   <https://github.com/kepano/defuddle>
3. **last30days** — qué se dijo de un tema en los últimos 30 días (Reddit, YouTube, web).
   <https://github.com/mvanhorn/last30days-skill>
4. **deep-research** (skill del kit) — investigación larga con varias fuentes, citas y conclusiones.

## 3. Plugins y repos recomendados
Se instalan **desde su repo oficial**, no vienen copiados en el kit. Revisá su licencia y su README antes.

| Qué | Para qué | Dónde |
|---|---|---|
| ponytail | Escribir el mínimo código que funciona | <https://github.com/DietrichGebert/ponytail> |
| andrej-karpathy-skills | Pautas para programar con IA: pensar antes, simple primero, cambios chicos | <https://github.com/multica-ai/andrej-karpathy-skills> |
| superpowers | Brainstorming, planes, TDD, revisión de código | <https://github.com/obra/superpowers> |
| hyperframes | Videos y motion graphics con HTML (Apache 2.0) | https://github.com/heygen-com/hyperframes |

Ninguno es obligatorio. El kit detecta si están y los usa como mejora.

## 4. kickoff-lite: el hábito de arranque
Antes de una tarea real (no una pregunta):
1. **¿Ya hay una skill que lo haga?** Mirá el catálogo. Usarla gana a improvisar.
2. **¿Hay una marca en juego?** Si sí, que exista su archivo de marca y que `creative-director` la mire.
3. **Plan corto:** qué se hace, qué rol o skill lo hace, qué pasa si sale mal. El usuario aprueba.
4. **Ejecutar** y verificar sobre el resultado real.

Si la tarea es de alto riesgo (datos que no se pueden recuperar, seguridad, pagos, arquitectura nueva),
el plan corto se vuelve más completo: pedir una segunda opinión (otro rol, o Codex si está instalado) antes de aprobar, y dejar escrito cómo se vuelve atrás.

## 5. El hábito de la wiki
Lo que aprendés se guarda una vez y se consulta siempre (skill `wiki`):
- **Ingerir:** una fuente nueva (artículo, video, notas) se destila en una página con su crédito.
- **Consultar:** antes de investigar de nuevo, preguntale a la wiki.
- **Revisar:** cada tanto, buscar páginas viejas, contradicciones y enlaces rotos.

## 6. Verificar antes de decir "listo"
- Mirar el resultado real: frames, audio, el archivo final.
- Toda entrega de texto creativo abre con `Grounding:` y la lista de archivos que se leyeron.
- Si algo se desvía del plan, parar y re-planear.
