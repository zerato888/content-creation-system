# Contributing

This repo is intentionally brand-agnostic. Contributions should keep it
that way.

## What's welcome

- Bug fixes in `SKILL.md` dispatch logic or `shared/utils/` scripts.
- New templates within an existing meta-skill's route set.
- New meta-skills, if they fill a genuine gap (open an issue to discuss
  scope before a large PR).
- Documentation improvements, additional case studies (using invented,
  generic briefs — not real personal/brand content).

## What's not

- Any brand names, client names, or personal project references in
  code, docs, or examples.
- New required paid dependencies for the base flow (fallback/optional
  integrations are fine, gated behind their own `.env` key).
- Removing the confirmation gate in `publishing-distribution` or any
  other safety check named in a skill's `## Error handling` section.

## How to add a new meta-skill

1. Read `docs/skill-anatomy.md`.
2. Follow the exact section structure of an existing `SKILL.md` (routes
   table, required keys, dispatch logic, error handling).
3. Add it to the table in the root `README.md` and to
   `docs/api-reference.md`.
4. Open a PR describing the gap it fills.

## How to report a bug

Open an issue with: which meta-skill, which route, what you expected,
what happened instead (include the exact error message if one appeared
— every failure in this repo should produce one).
