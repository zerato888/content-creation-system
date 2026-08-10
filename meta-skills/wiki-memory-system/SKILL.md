---
name: wiki-memory-system
description: Build and query a personal knowledge base — create entities/concepts, ingest sources, run queries, and lint for broken links. Use when the user wants to save knowledge for later or ask what they already know about a topic.
---

# Wiki & Memory System

No API keys required — this skill operates entirely on local files.

## Routes

| Route | When to use |
|---|---|
| `init` | First-time wiki setup in the current project |
| `ingest` | Add a new source/entity/concept to the wiki |
| `query` | Answer a question from existing wiki pages |
| `lint` | Check for broken links, orphan pages, stale content |
| `remember` | Append a lesson to the project's `lessons.md` |

## Dispatch logic

1. **`init`**: create `wiki/{index.md,log.md,entities/,concepts/,sources/,analyses/}`
   if absent. Copy templates from `../../shared/wiki-engine/templates/`
   as a starting reference (do not auto-populate — the user fills these
   in).
2. **`ingest`**: given a source (article, conversation, document),
   follow the INGEST workflow in `../../shared/wiki-engine/SCHEMA.md`:
   create the right page type, synthesize (don't transcribe), link
   related pages, append to `log.md`, update `index.md` if new.
3. **`query`**: read `wiki/index.md` first, then only the matching
   pages — never read the whole wiki. If synthesis was non-trivial,
   offer to save the answer as a new `analyses/` page.
4. **`lint`**: scan `wiki/` for `[[links]]` with no matching page,
   pages not referenced anywhere, and pages whose `updated` frontmatter
   is old relative to the rest of the wiki. Report findings; don't
   auto-delete anything.
5. **`remember`**: call `framework.append_lesson()`
   (`../../shared/memory-system/framework.py`) with the pattern, rule,
   why, and today's date.

## Error handling

- `ingest`/`query`/`lint` called before `init` → run `init` first
  automatically, then proceed (this is safe/idempotent, unlike
  publishing actions).
- `query` with no matching pages found → say so plainly; never fabricate
  an answer from outside the wiki.
- Broken `[[link]]` found during `ingest` → warn but don't block; report
  it as a `lint`-style note.
