---
name: curso-ingest
description: Ingiere un curso completo (videos locales, YouTube, PDF o texto) a la wiki de la persona y lo conecta a sus agentes. Transcribe cada lección, frena las que salieron rotas, arma páginas de lección y de frameworks, índice, ficha y registro de cursos. Usar cuando la persona compra o trae un curso y quiere que sus agentes lo usen, o dice "ingerí este curso", "metele este curso a mis agentes".
role: strategist
files: []
---

# curso-ingest — un curso, en la wiki, usado por los agentes

El conocimiento vive solo en la wiki; los agentes lo citan. Para artículos o videos sueltos, usar `wiki`.
Trabajo pesado (audio, texto completo): fuera del proyecto, en una carpeta `cursos/<Curso>/transcripts/<modulo>/NN-slug.md`.

## Pasos

1. **Mapa.** Lista de módulos y lecciones con duración. Si el curso ya está en `.kit-personal/cursos.md`,
   marcar lo que ya existe y no repetirlo.
2. **Texto de cada lección**, en el formato `# Título` + líneas `[mm:ss] texto`:
   - Video local: `python .kit/launch.py course transcribe <video> <salida.md> "<título>" --lang es`
     (usa la transcripción local de `transcribe`; si falta el modelo, `python .kit/launch.py models small`).
   - YouTube o web: `web-research` para bajar los subtítulos y dejarlos en el mismo formato.
   - PDF o documento: leerlo; una "lección" por capítulo.
   Descargar o exportar los videos de una plataforma es cosa de la persona y de sus permisos: esta skill no lo hace.
3. **Control de calidad (puerta obligatoria):** `python .kit/launch.py course qc <transcripts>`.
   Frena: texto idéntico entre lecciones, bucles (líneas repetidas), huecos de más de 90 s, exceso de
   "[Música]", casi vacías, y cortes (la transcripción termina mucho antes que el video, si el video está
   al lado con el mismo nombre). Avisa: el arranque no menciona el título. Lo pendiente no se usa:
   se vuelve a transcribir o queda anotado como pendiente.
4. **Páginas de lección** (`wiki/sources/<curso>-<modulo>-lNN-slug.md`): resumen, ideas clave, lección y minuto
   de cada cosa. En tandas de 3-4 lecciones por vez; cada tanda deja candidatos a framework.
5. **Frameworks** (`wiki/concepts/`): una página por idea reutilizable, con `source_lessons` y la cita
   `[[fuente]] MM:SS` en cada afirmación. Máximo ~25 KB por página. Separar "el curso dice" de "inferencia".
   Nunca mezclar dos cursos en un framework sin marcar de cuál sale cada parte.
6. **Índice + ficha + registro:** `python .kit/launch.py course index <transcripts> --course "<Nombre>"`
   (crea el índice, la ficha y la fila en `.kit-personal/cursos.md`; solo cuenta lo que pasó el control).
   Completar la ficha; sumar todo a `wiki/index.md` y `wiki/log.md`; correr `wiki-lint`.
7. **Conectar a los agentes (la persona aprueba).** Armar un `connect.json` con las páginas por rol:
   `{"course","folder","cap":12,"pages":[{"path","tags":["copy"],"when":"...","consult":false}]}`
   y correr `python .kit/launch.py course connect connect.json`. Imprime el bloque
   `## Conocimiento: <Curso>` para pegar en el rol. Reglas:
   - Etiqueta por tipo de tarea (`[copy]`, `[guion]`, `[hook]`...), y `cuando:` dice la tarea concreta.
   - Tope de 10-15 páginas por rol; el resto queda fuera. El `creative-director` recibe solo el índice.
   - `[curso-consulta]` para lo que solo se abre si la tarea toca ese tema.
   - Si el curso contradice la marca o las lecciones de la persona, ganan ellas.
   Mostrar la tabla (rol, páginas, etiqueta) y esperar el OK antes de editar `agents/*.md`.

## Delegación

- Claude Code: use the Agent tool with subagent_type `strategist`.
- Codex: adopt the `strategist` role from AGENTS.md.
