# Case Study: Faceless Channel

**Skill used:** `content-video`, `faceless` route (+ `voice-synthesis`,
`multi-lang-tts` route)

## Brief

Topic: "the psychology behind why we procrastinate on easy tasks."
Audience: productivity-interested adults. Duration: 90 seconds. No
on-camera talent — voiceover + generated visuals only.

## What happened

1. Route detection: "no on-camera talent" + "voiceover" → `faceless`
   route in `content-video`.
2. `screenwriter` wrote a 90-second hook→tension→payoff script framed
   around a specific psychological mechanism (not generic "just do it"
   advice).
3. `dp-cinematographer` built a shot list favoring visual variety since
   there's no face anchoring attention — alternating abstract
   generated visuals with simple on-screen text emphasis for key phrases,
   no single visual held longer than 5 seconds.
4. `voice-synthesis` (`multi-lang-tts` route) generated the voiceover
   from the script using a stock voice profile (no cloning requested for
   this piece).
5. Visuals generated via Magnific per shot; assembled with voiceover as
   the pacing backbone (visual cuts timed to voiceover sentence
   boundaries, not fixed intervals).
6. Output: `outputs/video_faceless_2026-XX-XX.mp4` + `.json` sidecar.

## Lesson learned (logged via `remember`)

**Pattern:** faceless-pacing-follows-voiceover
**Rule:** cut visuals on voiceover sentence boundaries, not fixed
time intervals — fixed intervals sometimes cut mid-sentence, breaking
the sense that visual and narration are one unit.
**Why:** an early assembly attempt using fixed 4-second cuts
occasionally split a visual change in the middle of a spoken clause,
which read as unintentional rather than stylistic.
