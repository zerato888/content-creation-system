# Troubleshooting

## "Missing required key" error

The exact key name is always in the error message. Add it to the
`.env` file in the meta-skill's own folder (not the repo root — each
meta-skill has its own `.env`), then re-run `setup-env.sh` to confirm.

```bash
cd meta-skills/<skill-name>
cat .env.example   # see which keys this skill needs
cp .env.example .env
# edit .env, add the missing key
../../setup-env.sh .env <THE_KEY_NAME>
```

## "setup-env.sh: command not found" or permission denied

The script needs execute permission:

```bash
chmod +x setup-env.sh
chmod +x meta-skills/*/init-project.sh
```

## A skill picked the wrong route

Every `SKILL.md`'s dispatch logic explains its route-detection triggers
under "Dispatch logic" → "Detect route". If it picked wrong, just tell
Claude Code directly which route you meant ("actually, make this an
educational carousel") — the skill will use your explicit choice over
its own detection.

## Generation failed (Magnific/Higgsfield/OmniVoice error)

Check the error message returned — it's reported verbatim, not
swallowed. Common causes: expired/invalid key (regenerate it from the
provider's dashboard), rate limits (wait and retry), or malformed input
(check required fields for that route in the skill's `SKILL.md`).

## `init-project.sh` says files already exist

It's idempotent — re-running it won't overwrite `wiki/`, `config.json`,
or `lessons.md` if they already exist. If you want a clean slate,
manually remove those first.

## I don't know which meta-skill to use

Start with `docs/quickstart.md` for `content-carousel`, then check the
table in the root `README.md` — it lists all 11 skills with a one-line
description of what each does.
