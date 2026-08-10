# Setting Up Your Wiki

The wiki engine (`shared/wiki-engine/`) is architecture and templates,
not a pre-built database — you build your own.

## Quick setup

```bash
cd meta-skills/wiki-memory-system
```

In Claude Code:
```
/wiki-memory-system
```
Choose the `init` route. This creates:

```
wiki/
├── index.md
├── log.md
├── entities/
├── concepts/
├── sources/
└── analyses/
```

## Populate it

Use the `ingest` route whenever you learn something worth keeping:
- Read an article relevant to your content strategy → `ingest` as a
  `sources/` page.
- Track an ongoing project → `ingest` as an `entities/` page (copy
  `shared/wiki-engine/templates/entity-template.md`).
- Notice a recurring pattern in what performs well → `ingest` as a
  `concepts/` page.

See the worked examples in `shared/wiki-engine/examples/` for what a
filled-in entity and analysis page look like.

## Query it later

```
/wiki-memory-system
```
Choose `query`, ask your question. The skill reads `index.md` first,
then only the matching pages — not the whole wiki every time.

## Keep it healthy

Run the `lint` route periodically to catch broken `[[links]]` and orphan
pages. Full schema and workflow details: `shared/wiki-engine/SCHEMA.md`.
