---
name: voice-synthesis
description: Voice cloning, multi-language text-to-speech, and video dubbing. Use when the user needs a voiceover, a cloned voice, or a video dubbed into another language.
---

# Voice Synthesis

## Routes

| Route | When to use |
|---|---|
| `voice-cloning` | Create a reusable voice profile from sample audio |
| `multi-lang-tts` | Generate speech from text in a specified language |
| `dubbing` | Replace/add a spoken track in an existing video |

## Required keys

`OMNIVOICE_API_KEY` (primary, all routes). `ELEVENLABS_API_KEY`
(fallback for `multi-lang-tts` only).

```bash
../../setup-env.sh .env OMNIVOICE_API_KEY
```

## Dispatch logic

1. **Detect route**:
   - "clone my voice", "voice profile" → `voice-cloning`
   - "voiceover", "read this in [language]", "text to speech" →
     `multi-lang-tts`
   - "dub this video", "translate the audio" → `dubbing`
2. **Gather inputs**:
   - `voice-cloning`: `sample_audio_path` (required, clean single-speaker
     audio, minimum ~30s recommended)
   - `multi-lang-tts`: `script_text` (required), `language` (required),
     `voice_profile` (optional — uses a cloned voice if provided,
     otherwise a stock voice)
   - `dubbing`: `source_video_path` (required), `target_language`
     (required)
3. **Execute** via OmniVoice (fallback ElevenLabs for `multi-lang-tts`
   only).
4. **Output**: `outputs/voice_<route>_<YYYY-MM-DD>.mp3` (or `.mp4` for
   `dubbing`).

## Error handling

- Missing key → name it, stop.
- `voice-cloning` with short/noisy sample audio → warn the user before
  proceeding that clone quality may suffer; let them confirm or provide
  better source audio.
- Missing required input per route → ask directly, never substitute a
  default voice/language silently when the user specified one that
  wasn't found.
- API failure → report verbatim; fallback to ElevenLabs only for
  `multi-lang-tts`, otherwise stop.
