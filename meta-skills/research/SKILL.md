---
name: research
description: Web, YouTube, and competitor research — gather and synthesize information before content creation or strategy work. Use when the user needs facts, competitor analysis, or audience insight before creating content.
---

# Research

## Routes

| Route | When to use |
|---|---|
| `web` | General web research on a topic |
| `youtube` | Research/transcript-analysis of YouTube content |
| `competitor` | Analyze a specific competitor's public content/social presence |
| `audience` | Research a target audience's pain points/interests |

## Required keys

None strictly required for `web`/`youtube` (uses standard web
fetch/search tools available in Claude Code). `BRIGHTDATA_API_KEY` or
`APIFY_API_KEY` needed for `competitor` route if it targets a platform
requiring authenticated scraping (e.g., Instagram).

```bash
../../setup-env.sh .env BRIGHTDATA_API_KEY   # only if using competitor route on a gated platform
```

## Dispatch logic

1. **Detect route** from the request (a URL/topic → `web`; a YouTube
   link/channel → `youtube`; "what is [competitor] doing" →
   `competitor`; "who is my audience" / "what does my audience want" →
   `audience`).
2. **Gather inputs**: `query_or_url` (required), `depth` (optional:
   "quick" for a single-source answer, "thorough" for multi-source
   synthesis).
3. **Execute**:
   - `web`/`youtube`: use available web/YouTube fetch tools directly —
     no paid API required.
   - `competitor`: use `BRIGHTDATA_API_KEY`/`APIFY_API_KEY` for gated
     platforms; fall back to public web fetch for open platforms.
   - `audience`: combine `web` research (forums, public discussions)
     with any first-party data the user provides (survey results, DMs,
     comments) — never fabricate audience insight from nothing.
4. **Output**: a synthesized findings doc (markdown), not a raw dump of
   sources. Offer to save it to the wiki via `wiki-memory-system`'s
   `ingest` route if a wiki exists in the project.

## Error handling

- Missing key for a gated `competitor` target → name the exact key
  needed and note that public-only research can proceed without it.
- No sources found → say so; never present a synthesized answer as
  confident when the underlying research came up empty.
- Ambiguous query → ask a clarifying question before researching broadly.
