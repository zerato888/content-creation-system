# Design Patterns Used Across This System

These are the recurring frameworks the shared agents apply. Understanding
them helps you predict what any agent will do, and helps you write
compatible prompts/briefs.

## Hook → Tension → Payoff (screenwriter)

Every narrative piece (video script, sometimes a carousel's slide
sequence) follows: an opening that's specific enough to earn attention
(hook), a body that builds a gap between expectation and reality
(tension), and a resolution that delivers on the hook's implicit promise
(payoff). A piece that's "flat" usually skipped the tension stage and
went hook-straight-to-payoff.

## Emotion-driven hooks + single CTA (copywriter)

Copy leads with curiosity, urgency, identity, or contrarian framing —
never a bare fact with no emotional angle — and asks for exactly one
action. Two CTAs in one caption reliably underperforms one.

## Composition & consistency audit (creative-director)

Before any visual output ships, check: does every element earn its
place (no pure decoration), is there one focal point per frame, is text
legible against its background, and is style applied consistently
start-to-finish. This audit happens *before* generation when possible
(auditing planned composition) and after when not.

## Shot-list discipline (dp-cinematographer)

Every visual beat gets an explicit shot type, angle, movement, lens
feel, duration, and lighting mood — never left implicit. When converting
to an AI-generation prompt, these five slots map directly to prompt
structure: subject+action, environment, camera, lighting, style.

## Platform-native formatting before net-new (social-media-manager)

Before creating new content, check whether an existing piece can be
reformatted/re-captioned for another platform. Repurposing is cheaper
than net-new and this pattern surfaces that option before defaulting to
"make something new."

## 6/12/36-month projection (head-estrategia)

Any strategic recommendation gets evaluated at three time horizons, not
just "does this work now." Short-term wins that create long-term
constraints (audience mismatch, platform over-dependence, unsustainable
cadence) get named explicitly rather than discovered later.

## Structured prompt slots (prompt-engineer)

AI generation prompts get built from explicit slots (subject, action,
environment, camera/composition, lighting, style) rather than one
unstructured sentence — this is the same decomposition
dp-cinematographer uses for shot lists, applied to prompt-writing
directly.
