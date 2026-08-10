# content-video

Generate short-form video: reels, podcast shorts, explainers, or
faceless videos.

## Setup

```bash
cp .env.example .env
# add MAGNIFIC_KEY or HIGGSFIELD_KEY; add OMNIVOICE_API_KEY for
# explainer/faceless routes
../../setup-env.sh .env MAGNIFIC_KEY
```

## Optional: persistent project

```bash
./init-project.sh
```

## Usage

```
/content-video
```

See `SKILL.md` for dispatch logic, `templates/` for the four available
formats.
