#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Publish guard: a tripwire that fails on absolute paths,
secrets, binaries, embedded payloads, symlinks, broken skill references and an
invalid catalog, plus an optional private term list kept outside the repo. Stdlib only, Python 3.11+. Rules are documented in docs/GUARD.md.

Usage:
  python tools/guard.py --repo [--root DIR] [--require-gitleaks] [--terms FILE]
  python tools/guard.py --project DIR [--require-gitleaks] [--terms FILE]
Exit: 0 clean, 1 violations found, 2 usage/tool error.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

# --- optional private term list ------------------------------------------
# Never stored in the repo. Loaded from --terms FILE or $GUARD_TERMS_FILE:
# one term per line, "#" comments, a trailing "*" also matches inside a longer
# token. Multiword terms match as consecutive tokens or one concatenated token.
# A line that is a single non-alphanumeric character (e.g. a currency sign)
# matches that character anywhere.
DENY_C: list = []
DENY_CHARS: set = set()


def load_terms(path: str) -> None:
    DENY_C.clear()
    DENY_CHARS.clear()
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        term = raw.strip()
        if not term or term.startswith("#"):
            continue
        if len(term) == 1 and not term.isalnum():
            DENY_CHARS.add(term)
            continue
        sub = term.endswith("*")
        parts = tokens(normalize(term.rstrip("*")))
        if parts:
            DENY_C.append((" ".join(parts), parts, "".join(parts), sub))


ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u200e\u200f\u2060\u2061\u2062\u2063\u2064\ufeff\u00ad\u180e"), None)
# Latin lookalikes from Cyrillic and Greek (NFKC already folds fullwidth/compat forms).
HOMOGLYPHS = str.maketrans({
    "\u0430": "a", "\u0432": "b", "\u0435": "e", "\u043a": "k", "\u043c": "m", "\u043d": "h", "\u043e": "o", "\u0440": "p",
    "\u0441": "c", "\u0442": "t", "\u0443": "y", "\u0445": "x", "\u0456": "i", "\u0458": "j", "\u0455": "s", "\u0501": "d",
    "\u0261": "g", "\u051b": "q", "\u051d": "w", "\u04cf": "l",
    "\u0410": "A", "\u0412": "B", "\u0415": "E", "\u041a": "K", "\u041c": "M", "\u041d": "H", "\u041e": "O", "\u0420": "P",
    "\u0421": "C", "\u0422": "T", "\u0423": "Y", "\u0425": "X", "\u0406": "I", "\u0408": "J", "\u0405": "S",
    "\u03b1": "a", "\u03b5": "e", "\u03b9": "i", "\u03ba": "k", "\u03bd": "v", "\u03bf": "o", "\u03c1": "p", "\u03c4": "t",
    "\u03c5": "u", "\u03c7": "x", "\u0391": "A", "\u0392": "B", "\u0395": "E", "\u0396": "Z", "\u0397": "H", "\u0399": "I",
    "\u039a": "K", "\u039c": "M", "\u039d": "N", "\u039f": "O", "\u03a1": "P", "\u03a4": "T", "\u03a5": "Y", "\u03a7": "X",
})

# --- other rules -----------------------------------------------------------
# Written so the pattern source does not match itself.
ABS_PATH = [
    re.compile(r"/User[s]/"),
    re.compile(r"\b[A-Za-z]:[\\/]+User[s][\\/]", re.I),
    re.compile(r"\bMy[ _-]?Driv[e]\b", re.I),
    re.compile(r"\bDropbo[x]\b", re.I),
    re.compile(r"/Volume[s]/"),
]
SECRET_FALLBACK = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{32,}"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
]
DATA_URI = re.compile(r"data:[\w.+/-]*;base64,", re.I)
B64_RUN = re.compile(r"[A-Za-z0-9+/_-]{120,}={0,2}")
B64_MAX_DECODED = 256  # bytes
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico", ".tif", ".tiff", ".heic",
    ".psd", ".ai", ".aep", ".prproj", ".mogrt", ".mp4", ".mov", ".m4v", ".avi", ".mkv",
    ".webm", ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".ttf", ".otf",
    ".woff", ".woff2", ".eot", ".zip", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar",
    ".pdf", ".exe", ".dll", ".so", ".dylib", ".bin", ".pyc", ".db", ".sqlite", ".npy",
    ".pt", ".onnx", ".gguf", ".safetensors",
}
MAGIC = [
    b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"%PDF", b"PK\x03\x04", b"\x1f\x8b", b"BZh",
    b"\xfd7zXZ", b"7z\xbc\xaf", b"Rar!", b"wOFF", b"wOF2", b"OTTO", b"\x00\x01\x00\x00",
    b"RIFF", b"RIFX", b"ID3", b"OggS", b"fLaC", b"8BPS", b"MZ", b"\x7fELF",
    b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"SQLite format 3",
]
SMOKE_EXECUTABLES = {"python", "node", "ffmpeg"}
PROJECT_PATHS = [".kit", ".kit-personal", ".claude/skills", ".claude/agents", ".agents/skills",
                 "CLAUDE.md", "AGENTS.md"]
PROJECT_SKIP_DIRS = {"venv", ".venv", "node_modules", "ms-playwright", "fonts", "backup", "__pycache__"}
ALLOWLIST_FILE = "tools/guard-allowlist.json"


class Findings(list):
    def add(self, rule: str, path: str, line: int | None, msg: str) -> None:
        self.append((rule, path, line, msg))


# --- normalization ---------------------------------------------------------
def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(ZERO_WIDTH).translate(HOMOGLYPHS)
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def tokens(text: str) -> list[str]:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)
    return re.findall(r"[a-z0-9]+", text.lower())


def deny_hits(line: str) -> list[str]:
    norm = normalize(line)
    hits = []
    hits += [f"char U+{ord(c):04X}" for c in DENY_CHARS if c in norm]
    toks = tokens(norm)
    for name, parts, joined, sub in DENY_C:
        n = len(parts)
        found = any(toks[i:i + n] == parts for i in range(len(toks) - n + 1))
        found = found or (n > 1 and joined in toks)
        found = found or (sub and any(joined in t for t in toks))
        if found:
            hits.append(name)
    return hits


# --- allowlist -------------------------------------------------------------
def load_allowlist(root: Path, f: Findings) -> list[dict]:
    p = root / ALLOWLIST_FILE
    if not p.exists():
        return []
    try:
        entries = json.loads(p.read_text(encoding="utf-8"))["entries"]
    except (ValueError, KeyError) as e:
        f.add("allowlist", ALLOWLIST_FILE, None, f"unreadable allowlist: {e}")
        return []
    good = []
    for i, e in enumerate(entries):
        if not all(isinstance(e.get(k), str) and e.get(k) for k in ("path", "string", "reason")):
            f.add("allowlist", ALLOWLIST_FILE, None, f"entry {i} needs non-empty path, string, reason")
        elif e["path"] in ("*", "**", "**/*"):
            f.add("allowlist", ALLOWLIST_FILE, None, f"entry {i}: repo-wide path not allowed")
        else:
            good.append(e)
    return good


def strip_allowed(rel: str, text: str, allow: list[dict]) -> str:
    for e in allow:
        # The allowlist file may name its own exact strings; nothing else.
        if fnmatch.fnmatchcase(rel, e["path"]) or rel == ALLOWLIST_FILE:
            text = text.replace(e["string"], " " * len(e["string"]))
    return text


# --- per-file checks -------------------------------------------------------
def is_binary(data: bytes) -> bool:
    head = data[:8192]
    if b"\x00" in head:
        return True
    if len(data) >= 12 and data[4:8] == b"ftyp":
        return True
    return any(head.startswith(m) for m in MAGIC)


def b64_too_big(run: str) -> bool:
    s = run.replace("-", "+").replace("_", "/")
    s = s + "=" * (-len(s) % 4)
    try:
        return len(base64.b64decode(s, validate=True)) > B64_MAX_DECODED
    except (binascii.Error, ValueError):
        return False


def scan_file(root: Path, rel: str, allow: list[dict], f: Findings) -> None:
    p = root / rel
    if p.is_symlink():
        f.add("symlink", rel, None, "symlinks are not allowed")
        return
    if not p.is_file():
        return
    if Path(rel).suffix.lower() in BINARY_EXT:
        f.add("binary", rel, None, "binary file extension")
        return
    data = p.read_bytes()
    if is_binary(data):
        f.add("binary", rel, None, "binary content (magic bytes or NUL)")
        return
    text = strip_allowed(rel, data.decode("utf-8", errors="replace"), allow)
    for n, line in enumerate(text.splitlines(), 1):
        for term in deny_hits(line):
            f.add("deny", rel, n, f"deny-list term: {term}")
        for rx in ABS_PATH:
            if rx.search(line):
                f.add("abspath", rel, n, f"absolute/owner path: {rx.pattern}")
        for rx in SECRET_FALLBACK:
            if rx.search(line):
                f.add("secret", rel, n, "secret-shaped value (regex fallback)")
        if DATA_URI.search(line):
            f.add("embed", rel, n, "data: URI with base64 payload")
        for m in B64_RUN.finditer(line):
            if b64_too_big(m.group(0)):
                f.add("embed", rel, n, f"base64 run decodes to > {B64_MAX_DECODED} bytes")


# --- SKILL.md references ---------------------------------------------------
MD_LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")


def frontmatter_files(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    out, in_files = [], False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^files:\s*(.*)$", line)
        if m:
            val = m.group(1).strip()
            if val.startswith("["):
                out += [x.strip().strip("'\"") for x in val.strip("[]").split(",") if x.strip()]
            in_files = not val
            continue
        if in_files:
            m = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if m:
                out.append(m.group(1).strip("'\""))
            elif line.strip() and not line.startswith((" ", "\t")):
                in_files = False
    return out


def inside(root: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def check_skill(root: Path, rel: str, f: Findings) -> None:
    p = root / rel
    text = p.read_text(encoding="utf-8", errors="replace")
    for ref in frontmatter_files(text):
        t = p.parent / ref
        if os.path.isabs(ref) or not inside(root, t) or not t.exists():
            f.add("skillref", rel, None, f"frontmatter files: entry missing or outside tree: {ref}")
    for n, line in enumerate(text.splitlines(), 1):
        for m in MD_LINK.finditer(line):
            ref = m.group(1)
            if re.match(r"^[a-z][a-z0-9+.-]*:", ref, re.I) or ref.startswith("#"):
                continue
            ref = ref.split("#", 1)[0]
            t = p.parent / ref
            if not ref or os.path.isabs(ref) or not inside(root, t) or not t.exists():
                f.add("skillref", rel, n, f"broken relative link: {m.group(1)}")


# --- catalog ---------------------------------------------------------------
SUPPORTED_KEYWORDS = {"$schema", "$id", "$defs", "$ref", "title", "description", "type",
                      "properties", "required", "additionalProperties", "items", "enum",
                      "const", "pattern", "minItems", "minLength", "uniqueItems"}
TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def validate(inst, schema: dict, root_schema: dict, path: str = "$") -> list[str]:
    """Minimal JSON Schema (draft 2020-12 subset) validator. Unknown keywords are errors."""
    errs = []
    unknown = set(schema) - SUPPORTED_KEYWORDS
    if unknown:
        return [f"{path}: schema uses unsupported keywords {sorted(unknown)}"]
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            return [f"{path}: unsupported $ref {ref}"]
        return validate(inst, root_schema["$defs"][ref.split("/")[-1]], root_schema, path)
    if "type" in schema:
        ts = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]

        def ok(t):
            if t == "integer":
                return isinstance(inst, int) and not isinstance(inst, bool)
            if t == "number":
                return isinstance(inst, (int, float)) and not isinstance(inst, bool)
            return isinstance(inst, TYPES[t]) and not (t != "boolean" and isinstance(inst, bool))
        if not any(ok(t) for t in ts):
            return [f"{path}: expected {'/'.join(ts)}"]
    if "const" in schema and inst != schema["const"]:
        errs.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and inst not in schema["enum"]:
        errs.append(f"{path}: must be one of {schema['enum']}")
    if isinstance(inst, str):
        if "pattern" in schema and not re.search(schema["pattern"], inst):
            errs.append(f"{path}: does not match {schema['pattern']}")
        if len(inst) < schema.get("minLength", 0):
            errs.append(f"{path}: too short")
    if isinstance(inst, list):
        if len(inst) < schema.get("minItems", 0):
            errs.append(f"{path}: needs at least {schema['minItems']} items")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in inst}) != len(inst):
            errs.append(f"{path}: items must be unique")
        if "items" in schema:
            for i, x in enumerate(inst):
                errs += validate(x, schema["items"], root_schema, f"{path}[{i}]")
    if isinstance(inst, dict):
        for k in schema.get("required", []):
            if k not in inst:
                errs.append(f"{path}: missing required '{k}'")
        props = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for k, v in inst.items():
            if k in props:
                errs += validate(v, props[k], root_schema, f"{path}.{k}")
            elif extra is False:
                errs.append(f"{path}: unexpected property '{k}'")
            elif isinstance(extra, dict):
                errs += validate(v, extra, root_schema, f"{path}.{k}")
    return errs


def check_catalog(root: Path, f: Findings) -> None:
    cat_p, sch_p = root / "catalog.json", root / "catalog.schema.json"
    if not cat_p.exists() or not sch_p.exists():
        f.add("catalog", "catalog.json", None, "catalog.json and catalog.schema.json are required")
        return
    try:
        cat = json.loads(cat_p.read_text(encoding="utf-8"))
        sch = json.loads(sch_p.read_text(encoding="utf-8"))
    except ValueError as e:
        f.add("catalog", "catalog.json", None, f"invalid JSON: {e}")
        return
    errs = validate(cat, sch, sch)
    for e in errs:
        f.add("catalog", "catalog.json", None, e)
    if errs:
        return
    names = [s["name"] for s in cat["skills"]]
    roles = {r["name"]: r for r in cat["roles"]}
    for dup in {n for n in names if names.count(n) > 1}:
        f.add("catalog", "catalog.json", None, f"duplicate skill {dup}")
    for s in cat["skills"]:
        n = s["name"]
        if not (root / "skills" / n / "SKILL.md").is_file():
            f.add("catalog", "catalog.json", None, f"skill '{n}' has no skills/{n}/SKILL.md")
        if s["role"] not in roles:
            f.add("catalog", "catalog.json", None, f"skill '{n}' names unknown role '{s['role']}'")
        elif n not in roles[s["role"]]["skills"]:
            f.add("catalog", "catalog.json", None, f"role '{s['role']}' does not list skill '{n}'")
        argv = s["smoke"]["argv"]
        if argv[0] not in SMOKE_EXECUTABLES:
            f.add("catalog", "catalog.json", None, f"skill '{n}' smoke uses non-allowlisted executable '{argv[0]}'")
        for ref in s["files"]:
            t = root / "skills" / n / ref
            if os.path.isabs(ref) or not inside(root, t) or not t.exists():
                f.add("catalog", "catalog.json", None, f"skill '{n}' lists missing file {ref}")
    for r in roles.values():
        for n in r["skills"]:
            if n not in names:
                f.add("catalog", "catalog.json", None, f"role '{r['name']}' lists unknown skill '{n}'")
    sk = root / "skills"
    if sk.is_dir():
        for d in sorted(x.name for x in sk.iterdir() if x.is_dir()):
            if d not in names:
                f.add("catalog", f"skills/{d}", None, "skill folder not listed in catalog.json")


# --- gitleaks --------------------------------------------------------------
def run_gitleaks(root: Path, files: list[str], repo: bool, require: bool, f: Findings) -> int:
    exe = shutil.which("gitleaks")
    if not exe:
        if require:
            print("guard: gitleaks is required (--require-gitleaks) but not on PATH", file=sys.stderr)
            return 2
        print("guard: gitleaks not found; using best-effort regex fallback only", file=sys.stderr)
        return 0
    # Scan exactly the guard's file set: copy it to a temp dir so untracked
    # caches, build output and .git do not count.
    tmp = tempfile.mkdtemp(prefix="guard-gitleaks-")
    for rel in files:
        src = root / rel
        if src.is_file() and not src.is_symlink():
            dst = Path(tmp) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
    cmds = [[exe, "dir", "--no-banner", "--redact", "--exit-code", "1", tmp]]
    if repo and subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "-q", "HEAD"],
                               capture_output=True).returncode == 0:
        cmds.append([exe, "git", "--no-banner", "--redact", "--exit-code", "1", str(root)])
    for cmd in cmds:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 1:
            f.add("secret", "(gitleaks)", None, f"gitleaks {cmd[1]} reported leaks:\n{r.stdout}{r.stderr}")
        elif r.returncode != 0:
            print(f"guard: gitleaks failed ({r.returncode}): {r.stderr}", file=sys.stderr)
            shutil.rmtree(tmp, ignore_errors=True)
            return 2
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


# --- file collection -------------------------------------------------------
def repo_files(root: Path) -> list[str]:
    r = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"guard: not a git repository: {root}")
    return [x for x in r.stdout.decode("utf-8").split("\0") if x]


def project_files(root: Path) -> list[str]:
    out = []
    for top in PROJECT_PATHS:
        p = root / top
        if p.is_symlink() or p.is_file():
            out.append(top)
            continue
        for dirpath, dirnames, filenames in os.walk(p):
            d = Path(dirpath)
            keep = []
            for x in dirnames:
                if (d / x).is_symlink():
                    out.append((d / x).relative_to(root).as_posix())
                elif x not in PROJECT_SKIP_DIRS:
                    keep.append(x)
            dirnames[:] = keep
            out += [(d / x).relative_to(root).as_posix() for x in filenames]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--repo", action="store_true", help="scan git-tracked files")
    g.add_argument("--project", metavar="DIR", help="scan an installed project's kit paths")
    ap.add_argument("--root", default=None, help="repo root for --repo (default: git toplevel of cwd)")
    ap.add_argument("--require-gitleaks", action="store_true")
    ap.add_argument("--terms", metavar="FILE", default=None,
                    help="optional private term list kept outside the repo (or $GUARD_TERMS_FILE)")
    a = ap.parse_args(argv)
    terms = a.terms or os.environ.get("GUARD_TERMS_FILE")
    DENY_C.clear()
    DENY_CHARS.clear()
    if terms:
        try:
            load_terms(terms)
        except OSError as e:
            print(f"guard: cannot read terms file: {e}", file=sys.stderr)
            return 2

    if a.repo:
        base = Path(a.root or ".").resolve()
        r = subprocess.run(["git", "-C", str(base), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"guard: not a git repository: {base}", file=sys.stderr)
            return 2
        root = Path(r.stdout.strip())
        files = repo_files(root)
    else:
        root = Path(a.project).resolve()
        if not root.is_dir():
            print(f"guard: no such directory: {root}", file=sys.stderr)
            return 2
        files = project_files(root)

    f = Findings()
    allow = load_allowlist(root, f) if a.repo else []
    for rel in files:
        scan_file(root, rel, allow, f)
        if Path(rel).name == "SKILL.md" and (root / rel).is_file() and not (root / rel).is_symlink():
            check_skill(root, rel, f)
    if a.repo:
        check_catalog(root, f)
    rc = run_gitleaks(root, files, a.repo, a.require_gitleaks, f)
    if rc:
        return rc
    for rule, path, line, msg in f:
        print(f"{path}{':' + str(line) if line else ''}: [{rule}] {msg}")
    print(f"guard: {len(files)} files scanned, {len(f)} finding(s)", file=sys.stderr)
    return 1 if f else 0


if __name__ == "__main__":
    sys.exit(main())
