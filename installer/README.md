# installer

Per-project installer, stdlib only (Python 3.11+). Entry points: `install.sh`
(macOS/Linux) and `install.ps1` (Windows), both thin wrappers around
`python -m installer`.

Commands: `install` (`--core`, `--module X`, `--target DIR`, `--yes`,
`--answers FILE`, `--dry-run`, `--fonts`), `update` (`--to TAG`,
`--confirm-sha SHA`, `--keep-mine`/`--take-new`), `uninstall`, `status`,
`rollback`, `service on|off|status` (always-on Command Center), `cache-clean`, `migrate-brands`, and for maintainers
`release-manifest` (prints `kit-manifest.json` for the current checkout).

- `core.py`: lock (`.kit.lock`), journaled transactions (`.kit-journal.json`,
  `.kit-prev/<txid>/`), recovery, JSON-lines log, safe tar extraction, shared
  heavy cache, fonts and dependency helpers.
- `cli.py`: planning (catalog, collisions, ownership, orphans) and commands.
- `service.py`: macOS LaunchAgent / Windows logon Scheduled Task, recorded in
  the manifest, removed by `uninstall`. OS calls go through one `run()` (mocked in tests).
- `net.py`: GitHub release resolution by immutable commit SHA. Injectable.
- File primitives shared with onboarding live in `engines/onboard_write.py`,
  because that file must also run on its own from `.kit/engines/`.

Update and uninstall run from the kit folder (the one with `install.sh`),
pointing `--target` at the project. The installed project does not carry the
installer. Contract: see the "Security & robustness contract" in the plan.
