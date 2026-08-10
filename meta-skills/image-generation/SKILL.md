---
name: image-generation
description: Direct image operations — generate, upscale, outpaint/expand, remove background, or produce variations. Use when the user wants raw image manipulation, not a finished piece of content (see content-graphics for that).
---

# Image Generation

## Routes

| Route | Operation |
|---|---|
| `generate` | New image from a text prompt |
| `upscale` | Increase resolution of an existing image |
| `outpaint` | Expand an image's canvas beyond its original borders |
| `remove-bg` | Cut out the subject, transparent background |
| `variations` | Generate N variations of an existing image |

## Required keys

`MAGNIFIC_KEY` (primary for all routes). `HIGGSFIELD_KEY` (fallback for
`generate` and `variations` only — upscale/outpaint/remove-bg are
Magnific-specific in this skill).

```bash
../../setup-env.sh .env MAGNIFIC_KEY
```

## Dispatch logic

1. **Detect route** directly from the verb in the request ("generate",
   "upscale", "expand"/"outpaint", "remove the background",
   "give me variations").
2. **Gather inputs**:
   - `generate`: `prompt` (required), `aspect_ratio` (optional, default
     1:1). Route the prompt through `prompt-engineer`
     (`../../shared/agents/prompt-engineer.md`) first if it's under ~10
     words (likely under-specified).
   - `upscale`/`outpaint`/`remove-bg`/`variations`: `source_image_path`
     (required).
3. **Execute** the operation via Magnific (fallback Higgsfield only for
   `generate`/`variations`).
4. **Output**: `outputs/image_<route>_<YYYY-MM-DD>.png`.

## Error handling

- Missing key → name it, stop.
- Missing `source_image_path` for an edit route → ask for the file path;
  never operate on a guessed/placeholder image.
- Underspecified `generate` prompt → run it through `prompt-engineer`
  once before generating rather than generating on a thin prompt.
- Generation/edit failure → report verbatim, fallback once where
  applicable, then stop.
