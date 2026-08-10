# Pre-Skill Hook Pattern

A pre-skill hook runs before a meta-skill's main dispatch logic. Use it
for checks that should block execution if they fail.

## Standard pre-skill checks

1. **Key validation** — run `setup-env.sh` (or `key_manager.check_keys`)
   for every key the detected route needs. Fail loud with the exact
   missing key name.
2. **Required input presence** — confirm every required field for the
   detected route is present before proceeding (never substitute a
   guess for a missing required field).
3. **Destructive-action gate** (only for skills that publish/schedule/
   delete) — require explicit confirmation restating exactly what will
   happen, every time, regardless of earlier approvals in the
   conversation.

## Where this lives in a SKILL.md

Put pre-skill checks under a `## Required keys` and `## Error handling`
section (see any meta-skill's `SKILL.md` for the pattern) — not as
separate hook files per skill. This doc exists so every skill author
applies the same checks consistently.
