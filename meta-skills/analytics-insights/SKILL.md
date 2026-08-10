---
name: analytics-insights
description: Predict virality, analyze engagement, and track content performance over time. Use when the user wants to evaluate a piece of content before/after publishing, or spot performance trends.
---

# Analytics & Insights

## Routes

| Route | When to use |
|---|---|
| `virality-prediction` | Estimate a piece's likely performance before publishing |
| `engagement-analysis` | Analyze why a published piece performed as it did |
| `performance-tracking` | Track a metric (views, saves, engagement rate) over time |

## Required keys

`METRICOOL_TOKEN` for `engagement-analysis`/`performance-tracking` (pulls
real published-post data). `virality-prediction` works on unpublished
drafts and needs no publishing-platform key, but may use
`BRIGHTDATA_API_KEY` to pull comparable public examples.

```bash
../../setup-env.sh .env METRICOOL_TOKEN
```

## Dispatch logic

1. **Detect route** ("will this do well" / "predict" → `virality-prediction`;
   "why did this perform" / "analyze this post" → `engagement-analysis`;
   "track over time" / "how's this trending" → `performance-tracking`).
2. **Gather inputs**:
   - `virality-prediction`: `content_path_or_script` (required)
   - `engagement-analysis`/`performance-tracking`: `post_url_or_id`
     (required)
3. **Execute**:
   - `virality-prediction`: evaluate hook strength (first 3s), pacing,
     and clarity of the single core idea — reason explicitly about each,
     don't return a bare score with no rationale.
   - `engagement-analysis`: pull metrics via `METRICOOL_TOKEN`, then
     reason about which specific element (hook, length, CTA, timing)
     likely drove the result — again, rationale required, not just
     numbers restated.
   - `performance-tracking`: pull the metric series and report the
     trend plainly (up/down/flat) with the actual numbers, not just a
     qualitative label.
4. **Output**: a findings doc with the metric(s), the reasoning, and one
   concrete recommendation for next time.

## Error handling

- Missing `METRICOOL_TOKEN` for routes that need real data → name it,
  note that `virality-prediction` can still proceed without it.
- `post_url_or_id` not found in the connected account → say so plainly;
  never estimate metrics for a post that couldn't be found.
- Insufficient data for `performance-tracking` (e.g., posted <24h ago) →
  say the trend isn't established yet rather than reporting noise as
  signal.
