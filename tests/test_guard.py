# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""One seeded violation per guard rule class, plus boundary cases that must pass.
The private term list is an invented fixture passed via --terms / $GUARD_TERMS_FILE."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import guard  # noqa: E402

REAL_WHICH = shutil.which
TERMS = ["# fixture list", "acme corp", "zorblax*", "blorptown", "\u00a4"]


@pytest.fixture
def terms(tmp_path):
    p = tmp_path / "terms.txt"
    p.write_text("\n".join(TERMS) + "\n", encoding="utf-8")
    return str(p)


@pytest.fixture(autouse=True)
def no_gitleaks(monkeypatch):
    monkeypatch.setattr(guard.shutil, "which", lambda n: None if n == "gitleaks" else REAL_WHICH(n))


def make_repo(tmp_path, files: dict, catalog=None):
    root = tmp_path / "repo"
    (root / "tools").mkdir(parents=True)
    shutil.copy(REPO / "catalog.schema.json", root / "catalog.schema.json")
    shutil.copy(REPO / "tools" / "guard-allowlist.json", root / "tools" / "guard-allowlist.json")
    cat = catalog or {"version": "0.1.0", "skills": [], "roles": []}
    (root / "catalog.json").write_text(json.dumps(cat), encoding="utf-8")
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            p.write_bytes(content)
        else:
            p.write_text(content, encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    return root


def run(root, capsys, *extra):
    rc = guard.main(["--repo", "--root", str(root), *extra])
    return rc, capsys.readouterr().out


def fails(tmp_path, capsys, files, rule, catalog=None):
    rc, out = run(make_repo(tmp_path, files, catalog), capsys)
    assert rc == 1, out
    assert f"[{rule}]" in out, out
    return out


# --- clean baseline and boundaries ----------------------------------------
def test_clean_repo_passes(tmp_path, capsys):
    rc, out = run(make_repo(tmp_path, {"README.md": "# kit\nhello\n"}), capsys)
    assert rc == 0, out


def test_no_terms_means_no_deny_rule(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("GUARD_TERMS_FILE", raising=False)
    rc, out = run(make_repo(tmp_path, {"docs/a.md": "acme corp and zorblax\n"}), capsys)
    assert rc == 0, out


@pytest.mark.parametrize("text", [
    "An acme of design; the corp next door.",   # words far apart
    "acmecorporate",                             # non-* term needs whole token
    "blorptowns and blorp town",                 # non-* term, different tokens
    "zorbla x",                                  # split prefix
])
def test_ordinary_words_pass(tmp_path, capsys, terms, text):
    rc, out = run(make_repo(tmp_path, {"docs/a.md": text + "\n"}), capsys, "--terms", terms)
    assert rc == 0, out


def test_allowlist_is_exact_string_and_path_scoped(tmp_path, capsys, terms):
    root = make_repo(tmp_path / "a", {"LICENSE": "(c) Acme Corp\n", "docs/x.md": "(c) Acme Corp\n"})
    (root / "tools" / "guard-allowlist.json").write_text(json.dumps({"entries": [
        {"path": "LICENSE*", "string": "(c) Acme Corp", "reason": "fixture"}]}))
    rc, out = run(root, capsys, "--terms", terms)
    assert rc == 1 and "docs/x.md" in out and "LICENSE" not in out, out
    # Same file, but the term appears outside the exact allowed string.
    (root / "LICENSE").write_text("(c) Acme Corp\nby acme corp\n")
    rc, out = run(root, capsys, "--terms", terms)
    assert "LICENSE:2" in out, out


def test_shipped_allowlist_is_valid(tmp_path, capsys):
    root = make_repo(tmp_path, {})
    assert "[allowlist]" not in run(root, capsys)[1]


def test_repo_wide_allowlist_rejected(tmp_path, capsys):
    root = make_repo(tmp_path, {})
    (root / "tools" / "guard-allowlist.json").write_text(json.dumps(
        {"entries": [{"path": "*", "string": "x", "reason": "y"}]}))
    assert "[allowlist]" in run(root, capsys)[1]


# --- deny list evasion ------------------------------------------------------
@pytest.mark.parametrize("text", [
    "ACME CORP strategy",                   # plain tokens, case
    "AcmeCorpEngine",                       # camel case
    "acme_corp_carousel",                   # snake case
    "acme-corp-reel",                       # kebab case
    "acmecorp",                             # joined multiword
    "zorblaxian",                           # * substring
    "Zorbl\u0430x",                         # Cyrillic homoglyph
    "blorp\u200btown",                      # zero-width split
    "\uff42\uff4c\uff4f\uff52\uff50town",       # fullwidth (NFKC)
    "Bl\u00f3rptown",                        # accent folded
    "see zorblax.ai",
    "blorptown@example.org",
    "cost \u00a4 50",                         # single-char term anywhere
])
def test_deny_variants_fail(tmp_path, capsys, terms, text):
    rc, out = run(make_repo(tmp_path, {"docs/a.md": text + "\n"}), capsys, "--terms", terms)
    assert rc == 1 and "[deny]" in out, out


def test_terms_from_env(tmp_path, capsys, terms, monkeypatch):
    monkeypatch.setenv("GUARD_TERMS_FILE", terms)
    rc, out = run(make_repo(tmp_path, {"docs/a.md": "blorptown\n"}), capsys)
    assert rc == 1 and "[deny]" in out, out


def test_missing_terms_file_is_error(tmp_path, capsys):
    assert run(make_repo(tmp_path, {}), capsys, "--terms", str(tmp_path / "nope.txt"))[0] == 2


# --- other rule classes -----------------------------------------------------
@pytest.mark.parametrize("text", [
    "/" + "Users/someone/x", "C:" + "\\Users\\someone", "My " + "Drive/stuff",
    "Drop" + "box/share", "/" + "Volumes/Files",
])
def test_abspath_fails(tmp_path, capsys, text):
    fails(tmp_path, capsys, {"a.txt": text + "\n"}, "abspath")


def test_secret_fallback_fails(tmp_path, capsys):
    fails(tmp_path, capsys, {"cfg.txt": "key = AKIA" + "ABCDEFGHIJKLMNOP\n"}, "secret")


def test_binary_by_extension(tmp_path, capsys):
    fails(tmp_path, capsys, {"font.woff2": "text"}, "binary")


def test_binary_by_content(tmp_path, capsys):
    fails(tmp_path / "a", capsys, {"notes.txt": b"\x89PNG\r\n\x1a\nrest"}, "binary")
    fails(tmp_path / "b", capsys, {"data.txt": b"abc\x00def"}, "binary")


def test_data_uri_fails(tmp_path, capsys):
    fails(tmp_path, capsys, {"a.css": "src: url(data" + ":font/woff2;base64,AAAA)\n"}, "embed")


def test_large_base64_fails_small_passes(tmp_path, capsys):
    import base64
    big = base64.b64encode(bytes(range(256)) * 2).decode()
    fails(tmp_path / "a", capsys, {"a.js": f"const x = '{big}';\n"}, "embed")
    small = base64.b64encode(bytes(range(100))).decode()
    assert run(make_repo(tmp_path / "b", {"a.js": f"const x = '{small}';\n"}), capsys)[0] == 0


def test_symlink_fails(tmp_path, capsys):
    root = make_repo(tmp_path, {"real.md": "ok\n"})
    try:
        (root / "link.md").symlink_to("real.md")
    except OSError:
        pytest.skip("symlinks not permitted on this runner")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    assert "[symlink]" in run(root, capsys)[1]


def skill_catalog(name="demo", **over):
    s = {"name": name, "category": "research", "tier": "core", "status": "tested", "role": "strategist",
         "deps": [], "paid_services": [], "network": [], "files": [],
         "support": {"claude": True, "codex": True, "windows": True, "mac": True},
         "smoke": {"argv": ["python", "-c", "print(1)"]}}
    s.update(over)
    return {"version": "0.1.0", "skills": [s], "roles": [{"name": "strategist", "skills": [name]}]}


SKILL_OK = "---\nname: demo\ndescription: d\nfiles:\n  - scripts/run.py\n---\nSee [ref](references/a.md) and [web](https://example.org).\n"


def test_skill_ok_passes(tmp_path, capsys):
    root = make_repo(tmp_path, {"skills/demo/SKILL.md": SKILL_OK, "skills/demo/scripts/run.py": "print(1)\n",
                                "skills/demo/references/a.md": "x\n"}, skill_catalog())
    rc, out = run(root, capsys)
    assert rc == 0, out


def test_skill_frontmatter_missing_file(tmp_path, capsys):
    fails(tmp_path, capsys, {"skills/demo/SKILL.md": SKILL_OK, "skills/demo/references/a.md": "x\n"},
          "skillref", skill_catalog())


def test_skill_broken_link(tmp_path, capsys):
    fails(tmp_path, capsys, {"skills/demo/SKILL.md": SKILL_OK, "skills/demo/scripts/run.py": "x\n"},
          "skillref", skill_catalog())


def test_catalog_schema_violation(tmp_path, capsys):
    cat = skill_catalog(tier="premium")
    fails(tmp_path, capsys, {"skills/demo/SKILL.md": "---\nname: demo\n---\n"}, "catalog", cat)


def test_catalog_smoke_executable(tmp_path, capsys):
    cat = skill_catalog(smoke={"argv": ["bash", "-c", "rm -rf /"]})
    out = fails(tmp_path, capsys, {"skills/demo/SKILL.md": "---\nname: demo\n---\n"}, "catalog", cat)
    assert "non-allowlisted" in out


def test_catalog_entry_without_folder(tmp_path, capsys):
    fails(tmp_path, capsys, {}, "catalog", skill_catalog())


def test_folder_without_catalog_entry(tmp_path, capsys):
    fails(tmp_path, capsys, {"skills/orphan/SKILL.md": "---\nname: orphan\n---\n"}, "catalog")


def test_catalog_role_mismatch(tmp_path, capsys):
    cat = skill_catalog()
    cat["roles"][0]["skills"] = []
    fails(tmp_path, capsys, {"skills/demo/SKILL.md": "---\nname: demo\n---\n"}, "catalog", cat)


# --- modes and gitleaks -----------------------------------------------------
def test_project_mode_without_git(tmp_path, capsys):
    proj = tmp_path / "proj"
    (proj / ".kit-personal").mkdir(parents=True)
    (proj / ".kit" / "fonts").mkdir(parents=True)
    (proj / ".kit" / "fonts" / "Inter.woff2").write_bytes(b"wOF2....")  # skipped dir
    (proj / "CLAUDE.md").write_text("hello\n")
    assert guard.main(["--project", str(proj)]) == 0
    (proj / ".kit-personal" / "profile.md").write_text("home: /" + "Users/me\n")
    assert guard.main(["--project", str(proj)]) == 1
    assert "[abspath]" in capsys.readouterr().out


def test_require_gitleaks_missing_is_error(tmp_path, capsys):
    root = make_repo(tmp_path, {"README.md": "ok\n"})
    assert run(root, capsys, "--require-gitleaks")[0] == 2


@pytest.mark.skipif(REAL_WHICH("gitleaks") is None, reason="gitleaks not installed")
def test_gitleaks_detects(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(guard.shutil, "which", REAL_WHICH)
    tok = "ghp_" + "8zQk2LmX9pRt4VwY7bNc3HdJ6sFg1KeA5uTo"  # fake, high entropy
    root = make_repo(tmp_path, {"cfg.env": f"GITHUB_TOKEN={tok}\n"})
    rc, out = run(root, capsys, "--require-gitleaks")
    assert rc == 1 and "(gitleaks)" in out
