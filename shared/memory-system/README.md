# Memory System

A lightweight, per-project way to persist lessons learned across
sessions — no cloud, no database, one markdown file plus a tiny Python
helper.

## How it works

Each project (or meta-skill install) keeps its own `lessons.md`. When you
correct an agent's output, or discover a gotcha, append a lesson. Next
session, read `lessons.md` before starting work so the same mistake
doesn't repeat.

## Format

Each lesson is:

```markdown
## [YYYY-MM-DD] <short pattern name>

**Rule:** <the rule to follow going forward>
**Why:** <what happened that taught you this>
```

## Using `framework.py`

```python
from framework import append_lesson, read_lessons

append_lesson(
    "lessons.md",
    pattern="caption-length",
    rule="Keep IG captions under 125 chars before the fold.",
    why="A 300-char caption got truncated and the CTA never showed.",
    date="2026-08-07",
)

for lesson in read_lessons("lessons.md"):
    print(lesson["pattern"], "->", lesson["rule"])
```

## When to append

- A user corrects an agent's output in a way that generalizes beyond this
  one instance.
- You discover a tool gotcha (an API quirk, a format requirement) that
  will bite the next run too.

## When NOT to append

- One-off, project-specific facts (those belong in your own project docs,
  not memory).
- Anything already obvious from reading the code/skill itself.
