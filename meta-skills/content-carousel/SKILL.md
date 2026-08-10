---
name: content-carousel
description: Generate multi-slide carousels (generic, educational, or news format) from a topic, audience, and optional CTA. Use when the user asks for a carousel, slideshow, or multi-slide social post.
---

# Content Carousel

Dispatches to one of three carousel routes based on the user's intent,
then hands off to `creative-director` for a composition audit and
`copywriter` for slide copy.

## Routes

| Route | When to use | Template |
|---|---|---|
| `generic` | No specific structure requested | `templates/generic/` |
| `educational` | Teaching a concept, how-to, listicle | `templates/educational/` |
| `news` | Reporting an event or update | `templates/news/` |

## Required keys

`MAGNIFIC_KEY` (primary image generation). `HIGGSFIELD_KEY` (fallback if
Magnific fails or is unavailable).

Before running anything, validate keys:

```bash
../../setup-env.sh .env MAGNIFIC_KEY
```

If this fails, stop and tell the user exactly which key is missing and
to add it to `.env` — do not attempt generation without it.

## Dispatch logic

1. **Detect route** from the user's request:
   - Mentions "how to", "steps", "guide", "tips" → `educational`
   - Mentions "news", "update", "announcement", "report" → `news`
   - Otherwise → `generic`
2. **Gather inputs** (ask if not provided):
   - `topic` (required) — what the carousel is about
   - `audience` (required) — who it's for
   - `cta` (optional) — the one action the last slide should drive
   - `slide_count` (optional, default 5-7 depending on route)
3. **Load the template** from `templates/<route>/README.md` — it
   describes the slide structure for that route (see below).
4. **Invoke `copywriter`** (`../../shared/agents/copywriter.md`) to
   write slide-by-slide copy following the template's structure.
5. **Invoke `creative-director`** (`../../shared/agents/creative-director.md`)
   to audit the copy + planned composition before generation — catch any
   slide trying to say two things at once.
6. **Generate images** per slide via Magnific (or Higgsfield if
   `MAGNIFIC_KEY` is absent but `HIGGSFIELD_KEY` is present).
7. **Output**: assembled carousel (image sequence or video) to
   `outputs/carousel_<route>_<YYYY-MM-DD>.mp4` (or `.zip` of stills if no
   video assembly tool is configured), plus a `.json` sidecar with the
   slide copy and template used.

## Slide structure per route

**generic** — see `templates/generic/README.md`: cover, 3-5 body slides,
CTA slide.

**educational** — see `templates/educational/README.md`: hook slide
(the promise), numbered steps/tips, recap slide, CTA slide.

**news** — see `templates/news/README.md`: headline slide, context
slide, 2-3 detail slides, "what this means" slide.

## Error handling

- **Missing key** → `[content-carousel] Missing required key(s):
  MAGNIFIC_KEY. Add it to .env (see .env.example), then re-run this
  skill.` Do not proceed.
- **Missing topic/audience** → ask the user directly; do not guess or
  generate a placeholder carousel.
- **Ambiguous route** → default to `generic` and tell the user which
  route was chosen and why, so they can redirect if wrong.
- **Generation API failure** → if `MAGNIFIC_KEY` fails and
  `HIGGSFIELD_KEY` is present, retry once via Higgsfield. If both fail,
  report the error verbatim and stop — never return a broken/partial
  carousel silently.
