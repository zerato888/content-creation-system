# Post-Skill Hook Pattern

A post-skill hook runs after a meta-skill produces output. Use it to
keep output consistent and to feed the memory/wiki system.

## Standard post-skill actions

1. **Output naming convention** — `outputs/<content-type>_<route>_<YYYY-MM-DD>.<ext>`,
   consistent across every meta-skill, so a project's `outputs/` folder
   stays scannable regardless of which skill produced what.
2. **Sidecar metadata** — for any generated content, write a `.json`
   sidecar with the inputs used (topic, route, template, agents
   invoked) so the generation is reproducible/auditable later.
3. **Optional memory checkpoint** — if something non-obvious happened
   (a retry, a fallback API used, an unexpected user correction), offer
   to log it via `wiki-memory-system`'s `remember` route. Don't log
   routine successful runs — only what's worth remembering.

## Where this lives in a SKILL.md

Put post-skill actions under the `## Dispatch logic`'s final "Output"
step (see any meta-skill's `SKILL.md`) — this doc is the shared
reference so every skill's final step follows the same convention.
