# Esquema de la wiki

## Carpetas

```
raw/                 fuentes originales (solo lectura para el agente)
wiki/
  index.md           catálogo de todas las páginas
  log.md             registro de operaciones, lo más nuevo arriba
  sources/           una página por fuente ingerida
  entities/          personas, organizaciones, productos, proyectos, lugares
  concepts/          ideas, marcos, términos
  analyses/          respuestas a consultas que se guardaron
```

## Nombres

- Archivos en minúsculas con guiones: `wiki/concepts/escalera-de-investigacion.md`.
- El slug es el nombre del archivo sin `.md`. Los links internos son `[[slug]]`.

## Frontmatter de cada página

```yaml
---
title: Escalera de investigación
type: concept          # source | entity | concept | analysis
created: 2026-01-15
updated: 2026-01-20
sources: [slug-de-fuente]   # de qué fuentes sale lo que dice
tags: [investigacion]
---
```

Las páginas `source` agregan `origin:` (URL o ruta dentro de `raw/`) y `ingested:` (fecha).

## Cuerpo

- **source:** resumen (3-6 líneas), ideas clave en viñetas, citas cortas entre comillas si hacen falta, páginas que actualizó.
- **entity / concept:** qué es, lo que se sabe (cada afirmación con su `[[fuente]]`), relaciones, contradicciones abiertas.
- **analysis:** la pregunta, la respuesta, las páginas en las que se apoya.

## index.md

Una sección por tipo, una línea por página: `- [[slug]] — resumen de una línea`.

## log.md

Lo más nuevo **arriba**. Una entrada por operación:

```
## 2026-01-20 — ingest — nombre de la fuente
- creó: [[slug-fuente]]
- actualizó: [[concepto-a]], [[entidad-b]]
```

Para ver lo último, leer solo las primeras ~40 líneas.

## Reglas

- Nada de texto copiado largo: se destila con palabras propias.
- Todo lo que se afirma tiene fuente o se marca como supuesto.
- No se borra: lo viejo que quedó mal se marca como superado y se enlaza lo nuevo.
