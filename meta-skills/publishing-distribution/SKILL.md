---
name: publishing-distribution
description: Schedule or publish finished content to social platforms via Metricool or Zernio. Use when content is ready and the user wants to schedule/post it, not create it.
---

# Publishing & Distribution

## Routes

| Route | When to use |
|---|---|
| `schedule` | Queue a post for a future date/time |
| `batch-schedule` | Queue multiple posts across a date range |
| `publish-now` | Post immediately |

## Required keys

`METRICOOL_TOKEN` + `METRICOOL_BLOG_ID`, or `ZERNIO_API_KEY` — at least
one publishing backend must be configured.

```bash
../../setup-env.sh .env METRICOOL_TOKEN
# or, if using Zernio instead:
../../setup-env.sh .env ZERNIO_API_KEY
```

## Dispatch logic

1. **Detect route** from the request ("schedule for Tuesday" →
   `schedule`; "schedule these 5 posts" → `batch-schedule`; "post this
   now" → `publish-now`).
2. **Invoke `social-media-manager`**
   (`../../shared/agents/social-media-manager.md`) to confirm
   platform-native formatting and timing before queuing anything.
3. **Gather inputs**: `media_path` (required), `caption` (required),
   `platform` (required), `scheduled_time` (required for `schedule`/
   `batch-schedule`).
4. **CRITICAL — explicit confirmation gate**: before calling the
   publish/schedule API, restate exactly what will be posted, where, and
   when, and require an explicit "yes" from the user. Approving the
   content earlier in the conversation does NOT count as approval to
   publish — this gate is separate and mandatory every time.
5. **Execute** via the configured backend (Metricool or Zernio).
6. **Output**: confirmation with the platform's post ID/URL if returned.

## Error handling

- Missing key (both backends absent) → tell the user neither
  `METRICOOL_TOKEN` nor `ZERNIO_API_KEY` is configured, name both as
  options, stop.
- Missing `scheduled_time` for `schedule`/`batch-schedule` → ask; never
  default to "now" for a route explicitly about scheduling.
- No explicit "yes" at the confirmation gate → do not call the publish
  API. Ask again or wait.
- API failure → report verbatim; never retry a publish/schedule call
  silently (duplicate posts are worse than a failed one).
