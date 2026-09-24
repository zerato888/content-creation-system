---
name: brand-onboarding
description: Entrevista guiada para crear la ficha de una marca: preguntas de fundamento, identidad visual, voz, contenido y posicionamiento, y como salida un brand.json válido para el kit. Usar cuando una marca no tiene ficha, al sumar un cliente nuevo o antes de cualquier pieza creativa sin marca definida.
role: creative-director
files: [references/questionnaire.md, references/output_templates.md]
---

# brand-onboarding — la ficha de la marca

Todo el kit lee la marca desde un solo archivo de tokens. Sin ficha, ninguna pieza tiene de dónde
sacar colores, tipografías ni voz.

## Pasos

1. **Identificar:** nombre de la marca y un nombre corto en minúsculas con guiones (`mi-marca`).
   Revisar si ya existe `.kit-personal/brands/<nombre>.json`; si existe, preguntar antes de reescribir.
2. **Cuestionario:** hacer las preguntas de `references/questionnaire.md` en orden. Anotar las
   respuestas textuales. Si una respuesta es vaga, pedir un ejemplo concreto.
3. **Visual:** colores en hex (`#RRGGBB`), tipografías (preferir familias libres OFL como Inter,
   Montserrat, Bebas Neue, Instrument Serif, Anton, JetBrains Mono), estilo de imagen y lo que nunca se usa.
4. **Voz:** 3 adjetivos, registro, palabras que siempre y nunca se usan.
5. **Contenido y posicionamiento:** pilares, formatos, plataformas, referentes y diferencias.
6. **Salida:** armar el `brand.json` (abajo) y mostrarlo al usuario. El usuario lo guarda en
   `.kit-personal/brands/<nombre>.json` (carpeta personal, fuera de git). Opcional: un documento
   de marca en texto con `references/output_templates.md`.

## Campos del brand.json

El archivo tiene que validar contra `.kit/presets/brand.schema.json`. Los campos que falten toman
los valores por defecto del kit; los desconocidos se ignoran.

```json
{
  "schema_version": 1,
  "name": "Mi Marca",
  "handle": "@mimarca",
  "language": "es",
  "voice": {"tone": "cercano y preciso", "person": "second", "avoid": ["increíble", "revolucionario"]},
  "colors": {"background": "#101418", "surface": "#1B222A", "text": "#F4F1EA",
             "muted": "#8E99A6", "accent": "#E4572E", "accent_2": "#2E86AB"},
  "fonts": {"display": "Bebas Neue", "body": "Inter", "serif": "Instrument Serif",
            "mono": "JetBrains Mono", "condensed": "Anton"},
  "logo_text": "MI MARCA",
  "cta": "Seguinos para más",
  "source_label": "Fuente:"
}
```

- `schema_version` y `name` son obligatorios.
- `language`: código como `es` o `es-AR`.
- `voice.person`: `first`, `second` o `third`.
- Colores: siempre `#` + 6 dígitos hex.
- El kit no guarda logos en imagen: `logo_text` es la marca escrita.

## Criterio de éxito

Con la ficha, cualquier rol puede revisar una pieza y responder sí o no a "¿esto respeta la marca?".
Nada ambiguo.

## Delegación

- Claude Code: use the Agent tool with subagent_type `creative-director`.
- Codex: adopt the `creative-director` role from AGENTS.md.
