# Case Study: Short-Form Reel

**Skill used:** `content-video`, `short-form-reel` route

## Brief

Topic: "why most morning routines fail by 10am." Audience: people who've
tried and abandoned a morning routine before. Duration: 40 seconds.

## What happened

1. Route detection: no podcast source, no "explain how X works" framing,
   no explicit "faceless" request → defaulted to `short-form-reel`.
2. `screenwriter` produced a hook ("Your morning routine isn't failing
   because you're lazy — it's failing because of this one thing"),
   3 body beats building tension around a specific, concrete cause, and
   a payoff naming the fix in one sentence.
3. `dp-cinematographer` converted each beat into a shot: hook = extreme
   close-up, static, high-key lighting; body beats = medium shots with
   slow push-ins to sustain motion without being distracting; payoff =
   wide shot, warm lighting, giving the resolution room to land.
4. Visuals generated via Magnific per shot; voiceover skipped (route was
   `short-form-reel`, not `explainer`/`faceless`, on-camera-style
   narration assumed handled by the user or a separate pass).
5. Output: `outputs/video_short-form-reel_2026-XX-XX.mp4` + `.json`
   sidecar with script and shot list.

## Lesson learned (logged via `remember`)

**Pattern:** payoff-needs-room
**Rule:** always reserve the final 2-3 seconds purely for the payoff
line with no competing visual motion — a payoff landing during a push-in
transition reads as less confident than one on a settled, static frame.
**Why:** dp-cinematographer's shot list initially kept the push-in
motion through the payoff beat; separating it produced a stronger
ending on review.
