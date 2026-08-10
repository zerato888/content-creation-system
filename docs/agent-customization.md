# Customizing Agents for Your Context

The 7 agents in `shared/agents/` carry frameworks, not brand identity.
Here's how to adapt them without breaking the pattern other skills rely
on.

## What's safe to customize

- **Tone examples** inside an agent's framework (e.g., `copywriter`'s
  "Tone adaptation" section) — add tones relevant to your niche.
- **NEVER rules** — add project-specific hard constraints (e.g., "NEVER
  make medical claims" for a health-content project).
- **Output format** — adjust the exact markdown structure an agent
  returns, as long as downstream skills that parse it are updated too.

## What NOT to customize directly in `shared/agents/`

- Don't bake in your own brand colors, fonts, or voice into
  `creative-director.md` or `copywriter.md` — these files are shared
  across every meta-skill you use. Brand specifics belong in your own
  project-level style guide, referenced (not copied) by the agent when
  it runs.

## Recommended pattern: a project-level style guide

Create `wiki/entities/brand-style.md` (using the entity template from
`shared/wiki-engine/templates/entity-template.md`) with your actual
colors, fonts, and tone rules. When invoking `creative-director` or
`copywriter`, point them at this file instead of editing the shared
agent definitions:

```markdown
# When invoking creative-director for this project, also read:
wiki/entities/brand-style.md
```

This keeps `shared/agents/` reusable across every project you start,
while still getting brand-consistent output per project.

## Adding an 8th agent

If your niche needs a role none of the 7 covers (e.g., a
`community-manager` agent for a Discord-heavy project), follow the same
frontmatter + Role + Framework + NEVER pattern as the existing 7 (see
any file in `shared/agents/` as a template) and drop it in
`shared/agents/your-agent.md`. Reference it from your meta-skill's
`SKILL.md` the same way existing skills reference the built-in 7.
