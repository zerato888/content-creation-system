# Quickstart: Your First Carousel in 15 Minutes

## 1. Clone the module you need (2 min)

```bash
git clone https://github.com/[your-username]/content-creation-system.git
cd content-creation-system/meta-skills/content-carousel
```

You don't need the whole repo — just this folder plus `shared/` and the
root `setup-env.sh` (all included in the clone; you're just choosing
which meta-skill to focus on first).

## 2. Add your API key (3 min)

```bash
cp .env.example .env
```

Open `.env` and add your Magnific key:
```
MAGNIFIC_KEY=your-key-here
```

Don't have one? Sign up at magnific.ai — the free tier is enough to try
this. (Higgsfield is a supported fallback if you'd rather start there —
see `.env.example` for the alternate key.)

## 3. Validate your setup (1 min)

```bash
../../setup-env.sh .env MAGNIFIC_KEY
```

You should see `✅ MAGNIFIC_KEY is set` and "All required keys present."
If you see a `❌`, fix the named issue and re-run.

## 4. Make the skill discoverable (1 min)

For Claude Code to find the `/content-carousel` command, either:
- **Option A (recommended):** Open this folder directly in Claude Code: `File > Open` → select `content-carousel/`
- **Option B:** Symlink to your project's `.claude/skills/` dir: `ln -s $(pwd) ~/your-project/.claude/skills/content-carousel`

Then Claude Code will detect the local `SKILL.md` and register the skill.

## 5. Generate your first carousel (5-10 min)

Open this folder in Claude Code and run:

```
/content-carousel
```

Answer the prompts:
- **Topic:** something you know well (e.g., "how to batch-cook for the
  week")
- **Audience:** who it's for (e.g., "busy professionals")
- **CTA (optional):** what you want viewers to do

The skill picks a route (educational, news, or generic), drafts slide
copy via the `copywriter` agent, audits it via `creative-director`, and
generates the images.

## 6. Find your output

```bash
ls outputs/
```

Your carousel and a `.json` sidecar (with the copy and template used)
will be there.

## What's next

- Try `./init-project.sh` to set up a persistent `wiki/` and
  `lessons.md` for this project (optional — useful once you're doing
  this regularly).
- Read [ARCHITECTURE.md](../ARCHITECTURE.md) to understand how agents
  and skills connect.
- Try another meta-skill — `content-video` follows the identical setup
  pattern.
