---
name: agents-orchestration
description: Coordinate multiple agents and meta-skills for a full project brief (e.g. "launch a weekly content series"). Use for multi-step projects that span more than one meta-skill, not single-piece content requests.
---

# Agents Orchestration

No API keys of its own — this skill sequences other meta-skills and
agents. Each downstream skill's own key requirements still apply.

## When to use this vs. a single meta-skill

- Single piece of content ("make me a carousel about X") → use that
  meta-skill directly (`content-carousel`, `content-video`, etc).
- A brief spanning strategy + multiple content pieces + a publishing
  plan → use this skill to sequence the work.

## Dispatch logic (kickoff flow)

1. **Restate the brief** — confirm goal, audience, timeline, and which
   meta-skills are likely involved, before doing any work.
2. **Strategy pass** — if the brief involves positioning or a new content
   direction, invoke `head-estrategia`
   (`../../shared/agents/head-estrategia.md`) first to validate the
   approach and surface risks/tradeoffs.
3. **Plan the sequence** — list the concrete meta-skill calls needed
   (e.g., `content-carousel` x3, `content-video` x1,
   `publishing-distribution` for scheduling) and show this plan to the
   user before executing, for anything more than 2-3 steps.
4. **Execute in order**, one meta-skill at a time — do not fan out to
   all of them speculatively. Confirm each output before moving to the
   next when outputs feed into each other (e.g., a script feeding a
   video).
5. **Memory checkpoint** — at the end, if anything non-obvious was
   learned (a format that underperformed, a timing issue), invoke
   `wiki-memory-system`'s `remember` route to log it.

## Error handling

- Brief too vague to plan (missing goal/audience) → ask before planning
  any sequence.
- A downstream meta-skill fails mid-sequence (e.g., missing key) →
  stop the sequence, report which step failed and why, don't skip ahead
  to later steps that depend on it.
- User changes the brief mid-execution → re-confirm the updated plan
  before continuing, don't silently adapt.
