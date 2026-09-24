# Publish guard (`tools/guard.py`)

A tripwire, not proof. It blocks the common ways private or unlicensed material
leaks into the public tree. A human review of the full tree before each release
is still mandatory.

## Running it

```
python tools/guard.py --repo [--root DIR] [--require-gitleaks] [--terms FILE]
python tools/guard.py --project <dir> [--require-gitleaks] [--terms FILE]
```

- `--repo` scans every git-tracked (and staged) file: `git ls-files --cached`.
  It is what CI runs and what gates publishing.
- `--project <dir>` scans an installed project without needing git: `.kit/`,
  `.kit-personal/`, `.claude/skills/`, `.claude/agents/`, `.agents/skills/`,
  `CLAUDE.md`, `AGENTS.md`. Heavy dependency folders are skipped: `venv`,
  `.venv`, `node_modules`, `ms-playwright`, `fonts`, `backup`, `__pycache__`.
  The allowlist and catalog checks apply only in `--repo` mode.
- Exit codes: `0` clean, `1` findings, `2` usage or tool error (for example
  `--require-gitleaks` with no gitleaks on PATH, or gitleaks crashing).
- Stdlib only, Python 3.11+.

Each finding prints as `path[:line]: [rule] message`.

## Rules

### `deny` — optional private term list
- Off by default. Pass `--terms FILE` (or set `GUARD_TERMS_FILE`) to point at
  a private list you keep outside the repo. The list is never committed.
- Format: one term per line, `#` starts a comment, blank lines are ignored.
  A trailing `*` also matches inside a longer token (use it for distinctive
  names only). A line that is a single non-alphanumeric character matches that
  character anywhere.
- Matching pipeline, per line:
  1. Unicode NFKC (folds fullwidth and compatibility forms).
  2. Zero-width and soft-hyphen characters removed.
  3. Cyrillic and Greek Latin-lookalikes folded to Latin.
  4. Accents removed (NFKD, combining marks dropped).
  5. Identifier splitting: camelCase, PascalCase and acronym boundaries become
     spaces; the text is lowercased and split into `[a-z0-9]+` tokens, so snake,
     kebab, dotted and path forms split too.
- A term matches when its words appear as consecutive whole tokens. Multiword
  terms also match as one concatenated token. Whole-token matching keeps
  ordinary words that merely contain a term from tripping.

### `abspath` — machine paths
Regexes (case-insensitive where it matters): a `/User[s]/` home prefix, a
Windows drive `X:\User[s]\` prefix, the cloud-folder names `My Driv[e]` and
`Dropbo[x]`, and a `/Volume[s]/` mount prefix.

### `secret`
- gitleaks, when on PATH: `gitleaks dir` on a temporary copy of exactly the
  files the guard scanned (so untracked caches do not count), plus `gitleaks git` in
  `--repo` mode once a commit exists. `--require-gitleaks` makes it mandatory
  (CI does this, with a pinned, SHA-256-verified gitleaks).
- Always, as a best-effort fallback: private-key headers, AWS access key IDs,
  GitHub tokens, `sk-` style API keys, Slack tokens, Google API keys.

### `binary`
- By extension: images, design and video project files, audio, video, fonts,
  archives, PDFs, executables and libraries, databases, model weights.
- By content: a NUL byte in the first 8 KB, a known magic number (PNG, JPEG,
  GIF, PDF, ZIP, gzip, bzip2, xz, 7z, RAR, WOFF/WOFF2/OTF/TTF, RIFF/RIFX, ID3,
  Ogg, FLAC, PSD, PE, ELF, Mach-O, SQLite), or an ISO-BMFF `ftyp` box (MP4/MOV).

### `embed` — payloads hidden in text
- Any `data:<type>;base64,` URI.
- Any base64 (or base64url) run of 120+ characters that decodes to more than
  256 bytes.

### `symlink`
Any tracked symlink, file or directory, is rejected.

### `skillref` — SKILL.md references
For every `SKILL.md`:
- Each path in the frontmatter `files:` list (block or inline list) must exist,
  relative to the skill folder, and stay inside the tree.
- Each relative markdown link or image must exist and stay inside the tree.
  URLs with a scheme (`https:`, `mailto:` ...) and `#anchors` are skipped.

### `catalog`
- `catalog.json` and `catalog.schema.json` must exist at the root.
- `catalog.json` is validated against the schema by a small built-in validator
  (JSON Schema draft 2020-12 subset: `type`, `properties`, `required`,
  `additionalProperties`, `items`, `enum`, `const`, `pattern`, `minItems`,
  `minLength`, `uniqueItems`, local `$ref`). A schema keyword outside this
  subset is itself an error, so the schema cannot silently stop being checked.
- Cross-checks: skill names unique; every catalog skill has
  `skills/<name>/SKILL.md`; every `skills/<dir>/` is in the catalog; every
  skill's `role` exists and that role lists it back; roles list only known
  skills; every `files` entry exists; `smoke.argv[0]` is one of `python`,
  `node`, `ffmpeg`.

### `allowlist`
Exceptions live in `tools/guard-allowlist.json`. Each entry is
`{"path": <glob>, "string": <exact text>, "reason": <why>}`.
- Only the exact, case-sensitive string is blanked, and only in files whose
  repo-relative path matches the glob. The same name anywhere else in that file
  still fails. There are no file-wide exemptions, and a repo-wide glob (`*`,
  `**`, `**/*`) is rejected.
- Entries only matter when your private term list contains words that also
  appear in public, required text. The shipped entries cover the copyright and
  license notice lines and the public repository path in the files that need it.
- The allowlist file itself may contain its own listed strings.

## Tests
`tests/test_guard.py` seeds one violation per rule class in a temporary repo
and asserts failure, and checks boundary cases that must pass. The deny rule is
tested with an invented fixture term list.
