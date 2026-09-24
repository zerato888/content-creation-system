#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""UserPromptSubmit: suggest the installed skill, role and past lessons that match the prompt.

Reads only what is installed in this project: `.kit/catalog.json` (skills and roles), each
installed skill's SKILL.md description, and the person's `.kit-personal/lessons.md`. There is
no built-in keyword list: matching is plain word overlap. Prints at most a few short lines.
"""
import json
import re
import unicodedata

from _common import ROOT, event, read, run, say

SKILL_DIRS = (".claude/skills", ".agents/skills")
# ponytail: tiny generic stopword list (es/en); swap for TF-IDF if suggestions get noisy
STOP = set("""algo como cual cuando desde donde ella esas esos esta este esto estos hacer hace para pero
porque quiero sobre tambien tengo todo todos usar necesito puedo podes podés with this that from into your
what have will would should could please make want need about using them then than""".split())


def words(text: str) -> set:
    t = unicodedata.normalize("NFKD", str(text).lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return {w for w in re.findall(r"[a-z0-9]+", t) if len(w) >= 4 and w not in STOP}


def description(name: str) -> str:
    for d in SKILL_DIRS:
        m = re.search(r"^description:\s*(.+)$", read(f"{d}/{name}/SKILL.md"), re.M)
        if m:
            return m.group(1)
    return ""


def lessons() -> list:
    """Each bullet or heading of lessons.md is one lesson."""
    out = []
    for line in read(".kit-personal/lessons.md").splitlines():
        m = re.match(r"^\s*(?:[-*]|#{1,4})\s+(\S.*)$", line)
        if m:
            out.append(m.group(1)[:200])
    return out


def installed() -> set:
    names = set()
    for d in SKILL_DIRS:
        base = ROOT / d
        if base.is_dir():
            names |= {p.name for p in base.iterdir() if (p / "SKILL.md").is_file()}
    return names


def suggestions(prompt: str) -> list:
    asked = words(prompt)
    if not asked:
        return []
    try:
        cat = json.loads(read(".kit/catalog.json") or "{}")
    except ValueError:
        cat = {}
    have, scored = installed(), []
    for s in cat.get("skills", []):
        name = s.get("name", "")
        if name in have:
            vocab = words(" ".join([name.replace("-", " "), s.get("category", ""), description(name)]))
            if asked & vocab:
                scored.append((len(asked & vocab), name, s.get("role")))
    scored.sort(key=lambda x: (-x[0], x[1]))
    tips = [f"- skill `{n}`" + (f" (rol `{r}`)" if r else "") for _, n, r in scored[:2]]
    for text in lessons():
        if len(tips) >= 5:
            break
        if len(asked & words(text)) >= 2:
            tips.append(f"- lección tuya: {text}")
    return tips


def main():
    prompt = event().get("prompt")
    tips = suggestions(prompt if isinstance(prompt, str) else "")
    if tips:
        say("Sugerencias del kit para este pedido (usalas si aplican):\n" + "\n".join(tips))
    return 0


if __name__ == "__main__":
    run(main)
