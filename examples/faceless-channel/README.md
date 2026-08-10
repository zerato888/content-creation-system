# Example: Faceless Channel Video

A fully worked walkthrough producing one faceless video (voiceover +
generated visuals, no on-camera talent), using the exact brief in
`config.json`.

## Run it

```bash
cd ../../meta-skills/content-video
cp ../../examples/faceless-channel/.env.example .env
# add MAGNIFIC_KEY and OMNIVOICE_API_KEY to .env
../../setup-env.sh .env MAGNIFIC_KEY
../../setup-env.sh .env OMNIVOICE_API_KEY
```

In Claude Code, from `meta-skills/content-video/`:

```
/content-video
```

When prompted, use the brief from
`examples/faceless-channel/config.json`:
- Topic: "the psychology behind why we procrastinate on easy tasks"
- Audience: "productivity-interested adults"
- Duration: 90 seconds
- Route: faceless (voiceover + generated visuals, no talent)

## What you'll get

A 90-second faceless video with a stock-voice voiceover and generated
visuals, cut on voiceover sentence boundaries, in
`meta-skills/content-video/outputs/`.

See `docs/case-studies/faceless-channel.md` for a narrated walkthrough of
this exact brief, including the lesson learned about pacing cuts to
voiceover boundaries.
