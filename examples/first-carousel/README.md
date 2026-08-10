# Example: First Carousel

A fully worked walkthrough producing one educational carousel, using the
exact brief in `config.json`.

## Run it

```bash
cd ../../meta-skills/content-carousel
cp ../../examples/first-carousel/.env.example .env
# add your MAGNIFIC_KEY to .env
../../setup-env.sh .env MAGNIFIC_KEY
```

In Claude Code, from `meta-skills/content-carousel/`:

```
/content-carousel
```

When prompted, use the brief from `examples/first-carousel/config.json`:
- Topic: "how to batch-cook for the week"
- Audience: "busy professionals with little cooking experience"
- CTA: "save this for your next grocery run"

## What you'll get

A 6-7 slide educational carousel (hook, numbered tips, recap, CTA) in
`meta-skills/content-carousel/outputs/`, plus a `.json` sidecar showing
exactly what copy and template were used.

## Modify it

Change `config.json`'s topic/audience/cta and re-run — same process,
your own brief.
