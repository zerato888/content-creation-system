# Content Creation System

A modular, AI-native content creation toolkit: carousels, videos, graphics,
voice, publishing, research, and strategy — as pick-and-choose Claude Code
skills, backed by 7 generic creative/strategy agents and a lightweight
memory system.

Built to lower the barrier to AI-driven content production. Clone one
module, add your API keys, and generate your first piece of content in
under 15 minutes.

## What's inside

11 independent **meta-skills** (`meta-skills/`), each installable on its own:

| Skill | What it does |
|---|---|
| `content-carousel` | Generate multi-slide carousels (generic, educational, news) |
| `content-video` | Short-form reels, podcast shorts, explainers, faceless videos |
| `content-graphics` | Thumbnails, quote cards, tweet posts, motion graphics |
| `image-generation` | Generate/upscale/outpaint images via Magnific or Higgsfield |
| `voice-synthesis` | Voice cloning, multi-language TTS, dubbing |
| `publishing-distribution` | Schedule posts via Metricool / Zernio |
| `wiki-memory-system` | Build a personal knowledge base (entities, concepts, ingest) |
| `agents-orchestration` | Coordinate agents + skills for a project brief |
| `research` | Web/YouTube/competitor research |
| `analytics-insights` | Virality prediction, engagement analysis |
| `brand-strategy` | Positioning, content strategy, hook analysis |

Plus `shared/` (7 generic agents, memory framework, wiki engine, utils)
that every meta-skill draws on.

## Quick start (5 minutes)

```bash
git clone https://github.com/[your-username]/content-creation-system.git
cd content-creation-system/meta-skills/content-carousel
cp .env.example .env
# edit .env: add MAGNIFIC_KEY (get one at magnific.ai) — see docs/quickstart.md
../../setup-env.sh .env MAGNIFIC_KEY
```

Then, in Claude Code, open this folder and invoke the skill:

```
/content-carousel
```

(Claude Code needs to discover the skill first — see docs/quickstart.md for the install step.)

Full walkthrough: [docs/quickstart.md](docs/quickstart.md).

## How it's organized

- **`meta-skills/`** — one folder per skill, each with its own `SKILL.md`
  (the dispatch logic), plus `.env.example` and `templates/` where the skill needs them.
  Clone only the ones you need.
- **`shared/`** — agents, memory system, wiki engine, and utility code
  every meta-skill imports.
- **`docs/`** — architecture, how to build your own skill, how to
  customize agents, API reference.
- **`examples/`** — three runnable end-to-end projects.

Read [ARCHITECTURE.md](ARCHITECTURE.md) for how the pieces fit together.

## Philosophy

- **No brand baked in.** Agents carry frameworks (hook structure,
  positioning, shot-list discipline) — not anyone's visual identity. You
  bring your own colors, fonts, and voice.
- **Fails loud, never silent.** Every skill validates its inputs and keys
  up front and tells you exactly what's missing.
- **Pick-and-choose.** No monolith to install. Take the one skill you
  need today.

## License

MIT — see [LICENSE](LICENSE).
