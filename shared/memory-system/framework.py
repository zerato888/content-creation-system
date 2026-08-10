"""Minimal file-backed lessons-learned log. One markdown file, no deps."""
from pathlib import Path


def append_lesson(lessons_path: str, pattern: str, rule: str, why: str, date: str) -> None:
    """Prepend a new lesson entry to `lessons_path` (creates the file if absent)."""
    path = Path(lessons_path)
    entry = f"## [{date}] {pattern}\n\n**Rule:** {rule}\n**Why:** {why}\n\n"

    if not path.exists():
        path.write_text(f"# Lessons Learned\n\n{entry}")
        return

    content = path.read_text()
    header, _, rest = content.partition("\n\n")
    if not header.startswith("# "):
        header, rest = "# Lessons Learned", content
    path.write_text(f"{header}\n\n{entry}{rest}")


def read_lessons(lessons_path: str) -> list[dict]:
    """Parse `lessons_path` into a list of {date, pattern, rule, why} dicts."""
    path = Path(lessons_path)
    if not path.exists():
        return []

    lessons = []
    blocks = path.read_text().split("\n## ")
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        header = lines[0]
        date = header.split("]")[0].lstrip("[")
        pattern = header.split("]", 1)[1].strip()
        rule = ""
        why = ""
        for line in lines[1:]:
            if line.startswith("**Rule:**"):
                rule = line.replace("**Rule:**", "").strip()
            elif line.startswith("**Why:**"):
                why = line.replace("**Why:**", "").strip()
        lessons.append({"date": date, "pattern": pattern, "rule": rule, "why": why})
    return lessons


def demo():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        lessons_path = f"{tmp}/lessons.md"

        append_lesson(
            lessons_path,
            pattern="caption-length",
            rule="Keep captions under 125 chars before the fold.",
            why="A long caption got truncated and hid the CTA.",
            date="2026-08-07",
        )
        append_lesson(
            lessons_path,
            pattern="key-naming",
            rule="Always name the exact .env key in error messages.",
            why="Vague 'missing key' errors wasted 10 minutes of debugging.",
            date="2026-08-08",
        )

        lessons = read_lessons(lessons_path)
        assert len(lessons) == 2
        assert lessons[0]["pattern"] == "key-naming"  # most recent first
        assert lessons[1]["pattern"] == "caption-length"
        assert lessons[0]["rule"] == "Always name the exact .env key in error messages."

    print("memory framework: all checks passed")


if __name__ == "__main__":
    demo()
