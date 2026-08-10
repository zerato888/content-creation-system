# Wiki Engine — Schema

A personal knowledge base is four page types plus an index and a log.
This is architecture, not software — you build your own wiki by copying
these templates into a `wiki/` folder in your project and filling them in.

## Structure

```
wiki/
├── index.md       # Master catalog — links to every page, grouped by type
├── log.md         # Append-only timeline: "2026-08-07 — ingested X"
├── entities/      # People, projects, companies, places
├── concepts/      # Ideas, frameworks, recurring terms
├── sources/       # One page per ingested source (article, video, doc)
└── analyses/      # Point-in-time query results worth preserving
```

## Page types

### Entity
A person, project, company, or place. See `templates/entity-template.md`.

### Concept
An idea, framework, or term you reference repeatedly. See
`templates/concept-template.md`.

### Analysis
A preserved answer to a specific question — a snapshot, not a living
page. See `templates/analysis-template.md`.

### Source
A page per ingested external source (article, video, book). Not
templated here since format varies by source type — start from
`entity-template.md`'s frontmatter pattern and adapt.

## Workflows

### INGEST
When you learn something from an external source (article, video,
conversation):
1. Create a page under the right type (`entities/`, `concepts/`, or
   `sources/`).
2. Fill in frontmatter (`type`, `title`, `updated`, `tags`, `related`).
3. Write a synthesis, not a transcript — condense to what you'll actually
   need later.
4. Link related pages with `[[page-name]]`.
5. Append one line to `log.md`.
6. Update `index.md` if this is a new top-level topic.

### QUERY
When you need to answer a question from your wiki:
1. Read `index.md` first to find relevant pages.
2. Read only the pages that match — not the whole wiki.
3. If the answer required synthesizing multiple pages, consider saving
   it as a new page under `analyses/` so you don't redo the work.

### LINT
Periodically check for:
- Broken `[[links]]` (referenced pages that don't exist).
- Stale pages (not updated in a long time, marked `status: stale` when
  found).
- Orphan pages (not linked from `index.md` or any other page).

## Rotation

`log.md` grows unbounded. Read only the last ~20-40 lines
(`tail -n 40 wiki/log.md`) in normal use — never read it in full unless
you're specifically auditing history.
