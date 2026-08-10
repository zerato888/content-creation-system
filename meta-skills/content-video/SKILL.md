---
name: content-video
description: Generate short-form video content — reels, podcast shorts, explainers, or faceless videos. Use when the user asks for a video, reel, short, or clip.
---

# Content Video

Dispatches to one of four video routes, then hands off to `screenwriter`
for the script and `dp-cinematographer` for the shot list before
generation.

## Routes

| Route | When to use | Template |
|---|---|---|
| `short-form-reel` | General social reel, no specific sub-type | `templates/short-form-reel/` |
| `podcast-shorts` | Clipping/repurposing long-form audio/video | `templates/podcast-shorts/` |
| `explainer` | Teaching a concept via narrated video | `templates/explainer/` |
| `faceless` | No on-camera talent, voiceover + b-roll/motion | `templates/faceless/` |

## Required keys

`MAGNIFIC_KEY` or `HIGGSFIELD_KEY` (visuals). `OMNIVOICE_API_KEY`
(voiceover, required only for `explainer` and `faceless` routes).

```bash
../../setup-env.sh .env MAGNIFIC_KEY
```

For `explainer`/`faceless` specifically, also validate `OMNIVOICE_API_KEY`
before starting voiceover generation.

## Dispatch logic

1. **Detect route**:
   - "clip from my podcast/stream" → `podcast-shorts`
   - "explain", "how X works", "tutorial" → `explainer`
   - "no face", "voiceover only", "faceless channel" → `faceless`
   - Otherwise → `short-form-reel`
2. **Gather inputs**:
   - `topic` (required)
   - `audience` (required)
   - `duration_seconds` (optional, default 30-60)
   - `source_material` (required for `podcast-shorts` — path to source
     audio/video)
3. **Invoke `screenwriter`** (`../../shared/agents/screenwriter.md`) to
   produce a hook → tension → payoff script for the chosen duration
   (skip for `podcast-shorts`, which extracts rather than writes).
4. **Invoke `dp-cinematographer`** (`../../shared/agents/dp-cinematographer.md`)
   to convert the script into a shot list and, for AI-generated visuals,
   generation prompts.
5. **Generate/assemble**:
   - `short-form-reel`/`explainer`/`faceless`: generate visuals per shot,
     generate voiceover (if applicable) via OmniVoice, assemble.
   - `podcast-shorts`: extract the specified time range from
     `source_material`, reframe to vertical, add captions.
6. **Output**: `outputs/video_<route>_<YYYY-MM-DD>.mp4` plus a `.json`
   sidecar with the script and shot list used.

## Error handling

- **Missing key** → name the exact missing key and route requiring it,
  point at `.env.example`, stop.
- **`podcast-shorts` with no `source_material`** → ask for the file path;
  never fabricate source content.
- **Duration conflicts with route norms** (e.g., 5-minute "short-form
  reel") → flag the mismatch and ask whether to proceed or switch route.
- **Generation failure** → report verbatim, do not output a partial
  video silently.
