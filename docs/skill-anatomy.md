# Skill Anatomy: Building Your Own Meta-Skill

Every meta-skill in this repo follows the same shape. Use
`meta-skills/content-carousel/SKILL.md` as your reference while reading
this.

## The required sections

### 1. Frontmatter

```markdown
---
name: your-skill-name
description: One sentence — what it does and when to use it. This is
  what Claude Code matches against user requests, so be specific about
  triggers.
---
```

### 2. Routes table

A markdown table: route name, when to use it, which template it loads.
Keep routes mutually exclusive where possible — if two routes could both
apply, the dispatch logic (next section) needs an explicit tiebreaker.

### 3. Required keys

Name every `.env` key the skill needs, which are required vs. optional
fallbacks, and the exact `setup-env.sh` invocation to validate them.

### 4. Dispatch logic

A numbered list:
1. How to detect the route from user language (concrete trigger phrases,
   not vague "if it seems like X").
2. What inputs to gather, and which are required vs. optional.
3. Which `shared/agents/*.md` to invoke, in what order, and why.
4. How to execute (which tool/API, with fallback order if any).
5. Exact output path convention and any sidecar metadata to write.

### 5. Error handling

For each failure mode (missing key, missing input, ambiguous route, API
failure): the exact message/behavior. Never write "handle errors
appropriately" — name the literal message the user should see.

## Building a new meta-skill: checklist

1. Copy the shape of `content-carousel/SKILL.md` — same section headers.
2. Decide your routes (2-5 is typical — more than that suggests the
   skill should split into two).
3. List required keys, write `.env.example`.
4. Write template `README.md` files per route under `templates/<route>/`.
5. Decide which `shared/agents/*.md` your skill invokes and in what
   order — most skills need 1-2 agents, not all 7.
6. Write the error-handling section — literally list every way this
   skill can fail and what happens.
7. Add an `init-project.sh` only if your skill benefits from persistent
   local state (wiki, config, outputs) — some skills (like
   `wiki-memory-system`, `brand-strategy`) don't need one.
8. Write the skill's `README.md` (setup + usage, short).

## Common mistake: too many routes

If your skill needs more than ~5 routes to cover its domain, it's
probably two skills. `content-video` (4 routes: reel, podcast-shorts,
explainer, faceless) is close to the ceiling — anything past that,
consider whether a route deserves its own meta-skill.
