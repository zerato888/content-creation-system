---
name: brand-strategy
description: Positioning, content strategy, and hook-pattern analysis. Use for strategic questions about direction, not for producing a specific piece of content.
---

# Brand Strategy

No API keys required — this skill is reasoning-driven, invoking
`head-estrategia` and `copywriter`.

## Routes

| Route | When to use |
|---|---|
| `positioning` | Define or refine what a project/channel stands for and for whom |
| `content-strategy` | Decide content pillars, formats, and cadence |
| `hook-analysis` | Evaluate/improve a specific hook or opening line |

## Dispatch logic

1. **Detect route** from the request ("who is this for", "what do we
   stand for" → `positioning`; "what should we post about", "content
   pillars" → `content-strategy`; "is this hook strong", "improve this
   opening" → `hook-analysis`).
2. **Invoke `head-estrategia`** (`../../shared/agents/head-estrategia.md`)
   for `positioning` and `content-strategy` — these need the 6/12/36-month
   framing and tradeoff analysis.
3. **Invoke `copywriter`** (`../../shared/agents/copywriter.md`) for
   `hook-analysis` — evaluate against the emotion-driven-hook framework
   and propose 2-3 concrete rewrites, not just critique.
4. **Output**: a strategy doc (`positioning`/`content-strategy`) or a
   hook evaluation with rewrites (`hook-analysis`). Offer to save
   strategy docs to the wiki via `wiki-memory-system` if one exists.

## Error handling

- Vague brief with no audience/goal stated → ask before invoking
  `head-estrategia` — a strategy session on an unstated goal wastes the
  analysis.
- `hook-analysis` with no actual hook text provided → ask for it; don't
  evaluate a hypothetical.
