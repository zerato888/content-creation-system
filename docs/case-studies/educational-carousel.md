# Case Study: Educational Carousel

**Skill used:** `content-carousel`, `educational` route

## Brief

Topic: "3 mistakes people make when starting a home workout routine."
Audience: adults starting fitness for the first time. CTA: save this
post for reference.

## What happened

1. Route detection: "mistakes people make" + implied tips-format →
   `educational` route selected automatically.
2. `copywriter` drafted: a hook slide naming the promise ("3 mistakes —
   and the fix for each"), 3 numbered mistake+fix slides, a recap slide,
   and a save-focused CTA slide.
3. `creative-director` flagged that mistake #2's slide tried to cover
   both "what the mistake is" and "why it happens" — too much for one
   slide. Split into two slides (mistake #2a, #2b), adjusting the total
   count from 6 to 7.
4. Images generated via Magnific, one per slide, consistent style
   (same lighting mood, same layout template) across all 7.
5. Output: `outputs/carousel_educational_2026-XX-XX.mp4` +
   `.json` sidecar with the final 7-slide copy.

## Lesson learned (logged via `remember`)

**Pattern:** educational-slide-overload
**Rule:** if a numbered tip needs both a "what" and a "why", default to
two slides, not one — don't force-fit both into a single slide's word
budget.
**Why:** creative-director's audit caught a 2-idea slide the copywriter
draft produced initially; codifying the split avoids relitigating it.
