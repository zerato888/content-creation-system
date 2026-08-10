# content-carousel

Generate multi-slide carousels: generic, educational, or news format.

## Setup

```bash
cp .env.example .env
# add MAGNIFIC_KEY (required), HIGGSFIELD_KEY (optional fallback)
../../setup-env.sh .env MAGNIFIC_KEY
```

## Optional: persistent project

```bash
./init-project.sh
```

Creates `wiki/`, `outputs/`, `config.json`, and `lessons.md` for this
project.

## Usage

In Claude Code, from this folder:

```
/content-carousel
```

Then answer: topic, audience, optional CTA. See `SKILL.md` for the full
dispatch logic and `templates/` for the three available slide structures.
