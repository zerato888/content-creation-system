# Architecture

## The three layers

1. **`meta-skills/`** — user-facing entry points. Each is a self-contained
   Claude Code skill (`SKILL.md`) with its own routes, required keys, and
   templates. A user only needs the meta-skill folder(s) they care about.
2. **`shared/`** — agents, memory, wiki engine, and utils that every
   meta-skill references by relative path (`../../shared/...`). Nothing
   in `shared/` calls out to `meta-skills/` — dependencies flow one
   direction only.
3. **Local project state** (`.env`, `wiki/`, `outputs/`, `config.json`,
   `lessons.md`) — created per-project via each meta-skill's optional
   `init-project.sh`, never committed to this repo, always git-ignored
   in the user's own project.

## How a skill call resolves

```
User: "/content-carousel, make me an educational carousel about X"
  │
  ▼
SKILL.md detects route: educational
  │
  ▼
Pre-skill checks (shared/hooks/pre-skill-hook.md pattern):
  - setup-env.sh validates MAGNIFIC_KEY
  - required inputs present? (topic, audience)
  │
  ▼
Loads templates/educational/README.md (slide structure)
  │
  ▼
Invokes shared/agents/copywriter.md → slide copy
  │
  ▼
Invokes shared/agents/creative-director.md → composition audit
  │
  ▼
Generates images (Magnific, fallback Higgsfield)
  │
  ▼
Post-skill actions (shared/hooks/post-skill-hook.md pattern):
  - writes outputs/carousel_educational_<date>.mp4
  - writes .json sidecar
  - optionally logs a memory lesson
```

Every meta-skill in this repo follows this exact shape. See
`meta-skills/content-carousel/SKILL.md` as the canonical reference.

## Why agents are separate from skills

Agents (`shared/agents/`) carry **frameworks** (hook structure,
composition rules, strategic reasoning patterns) — they're reusable
across every meta-skill. Skills (`meta-skills/*/SKILL.md`) carry
**dispatch logic** (which route, which template, which keys, what order
to call agents in) specific to one content type. This separation means
improving `copywriter.md` once improves every skill that invokes it.

## Why no central orchestrator process

There's no long-running server or central router. Each `SKILL.md` is
read and interpreted by Claude Code directly when invoked — the "routing"
is markdown instructions a capable model follows, not compiled code. This
keeps every skill inspectable and editable as plain text.

## Error handling philosophy

No skill in this repo fails silently. Every `SKILL.md` has an
`## Error handling` section naming: what happens on a missing key
(exact key name + where to add it), what happens on missing required
input (ask, never guess), and what happens on an API failure (report
verbatim, fallback once if one exists, then stop). See
`shared/hooks/pre-skill-hook.md` and `post-skill-hook.md` for the shared
patterns behind this.
