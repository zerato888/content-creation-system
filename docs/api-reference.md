# API Reference

One entry per meta-skill: routes, required keys, agents invoked, and
output convention. Full detail lives in each skill's own `SKILL.md` —
this is the scannable index.

## content-carousel

- **Routes:** generic, educational, news
- **Required keys:** MAGNIFIC_KEY (HIGGSFIELD_KEY fallback)
- **Agents invoked:** creative-director, copywriter
- **Output:** `outputs/carousel_<route>_<date>.mp4` + `.json` sidecar

## content-video

- **Routes:** short-form-reel, podcast-shorts, explainer, faceless
- **Required keys:** MAGNIFIC_KEY or HIGGSFIELD_KEY; OMNIVOICE_API_KEY (explainer/faceless)
- **Agents invoked:** screenwriter, dp-cinematographer
- **Output:** `outputs/video_<route>_<date>.mp4` + `.json` sidecar

## content-graphics

- **Routes:** thumbnail, quote-card, tweet-post, motion-graphic
- **Required keys:** MAGNIFIC_KEY (HIGGSFIELD_KEY fallback)
- **Agents invoked:** creative-director, prompt-engineer
- **Output:** `outputs/graphic_<route>_<date>.png`

## image-generation

- **Routes:** generate, upscale, outpaint, remove-bg, variations
- **Required keys:** MAGNIFIC_KEY (HIGGSFIELD_KEY fallback for generate/variations)
- **Agents invoked:** prompt-engineer (generate route, if prompt underspecified)
- **Output:** `outputs/image_<route>_<date>.png`

## voice-synthesis

- **Routes:** voice-cloning, multi-lang-tts, dubbing
- **Required keys:** OMNIVOICE_API_KEY (ELEVENLABS_API_KEY fallback for multi-lang-tts)
- **Agents invoked:** none
- **Output:** `outputs/voice_<route>_<date>.mp3` (or `.mp4` for dubbing)

## publishing-distribution

- **Routes:** schedule, batch-schedule, publish-now
- **Required keys:** METRICOOL_TOKEN + METRICOOL_BLOG_ID, or ZERNIO_API_KEY
- **Agents invoked:** social-media-manager
- **Output:** publish confirmation with platform post ID/URL
- **Note:** always requires explicit confirmation before publishing, every time

## wiki-memory-system

- **Routes:** init, ingest, query, lint, remember
- **Required keys:** none
- **Agents invoked:** none
- **Output:** wiki pages under `wiki/`, or lesson entries in `lessons.md`

## agents-orchestration

- **Routes:** none (single kickoff flow)
- **Required keys:** none of its own (downstream skills' keys apply)
- **Agents invoked:** head-estrategia, plus whichever agents the sequenced meta-skills invoke
- **Output:** a project plan, then sequenced meta-skill outputs

## research

- **Routes:** web, youtube, competitor, audience
- **Required keys:** none for web/youtube; BRIGHTDATA_API_KEY or APIFY_API_KEY for gated competitor research
- **Agents invoked:** none
- **Output:** synthesized findings doc (markdown)

## analytics-insights

- **Routes:** virality-prediction, engagement-analysis, performance-tracking
- **Required keys:** METRICOOL_TOKEN (engagement-analysis, performance-tracking)
- **Agents invoked:** none
- **Output:** findings doc with metrics, reasoning, and one recommendation

## brand-strategy

- **Routes:** positioning, content-strategy, hook-analysis
- **Required keys:** none
- **Agents invoked:** head-estrategia (positioning, content-strategy), copywriter (hook-analysis)
- **Output:** strategy doc or hook evaluation with rewrites
