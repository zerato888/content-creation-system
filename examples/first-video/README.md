# Example: First Video

A fully worked walkthrough producing one short-form reel, using the
exact brief in `config.json`.

## Run it

```bash
cd ../../meta-skills/content-video
cp ../../examples/first-video/.env.example .env
# add your MAGNIFIC_KEY to .env
../../setup-env.sh .env MAGNIFIC_KEY
```

In Claude Code, from `meta-skills/content-video/`:

```
/content-video
```

When prompted, use the brief from `examples/first-video/config.json`:
- Topic: "why most morning routines fail by 10am"
- Audience: "people who've tried and abandoned a morning routine before"
- Duration: 40 seconds

## What you'll get

A 40-second short-form reel (hook, 3 body beats, payoff) in
`meta-skills/content-video/outputs/`, plus a `.json` sidecar with the
script and shot list used.

See `docs/case-studies/short-form-reel.md` for a narrated walkthrough of
this exact brief.
