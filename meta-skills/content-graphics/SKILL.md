---
name: content-graphics
description: Generate single-image graphics — thumbnails, quote cards, tweet-style posts, or motion graphics. Use when the user needs one still image or short motion piece, not a multi-slide carousel or full video.
---

# Content Graphics

## Routes

| Route | When to use | Template |
|---|---|---|
| `thumbnail` | Video thumbnail (YouTube-style) | `templates/thumbnail/` |
| `quote-card` | A single quote/statement as an image | `templates/quote-card/` |
| `tweet-post` | Text post styled as an image (screenshot-style) | `templates/tweet-post/` |
| `motion-graphic` | Short animated graphic (title card, lower-third) | `templates/motion-graphic/` |

## Required keys

`MAGNIFIC_KEY` (primary), `HIGGSFIELD_KEY` (fallback).

```bash
../../setup-env.sh .env MAGNIFIC_KEY
```

## Dispatch logic

1. **Detect route** from context (thumbnail mentions a video title;
   quote-card mentions a quote/statement; tweet-post mentions
   text/screenshot style; motion-graphic mentions animation/title card).
2. **Gather inputs**: `subject` (required — the text or focal content),
   `style_reference` (optional — an existing style to match, never
   invented by the skill itself).
3. **Invoke `prompt-engineer`** (`../../shared/agents/prompt-engineer.md`)
   to build the generation prompt for the route.
4. **Invoke `creative-director`** (`../../shared/agents/creative-director.md`)
   to audit legibility and composition before finalizing.
5. **Generate** via Magnific (fallback Higgsfield).
6. **Output**: `outputs/graphic_<route>_<YYYY-MM-DD>.png`.

## Error handling

- Missing key → name it, point at `.env.example`, stop.
- Missing `subject` → ask; never generate a graphic with placeholder text.
- Generation failure → report verbatim, fallback to Higgsfield once if
  Magnific fails, then stop if both fail.
