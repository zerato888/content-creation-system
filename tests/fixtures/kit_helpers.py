# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Shared helpers for the installer tests. The fixture catalog is independent of the real one."""
import hashlib
import io
import json
import shutil
import sys
import tarfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIX = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

from installer import cli, core, ow  # noqa: E402

SHA = "a" * 40


def make_src(tmp: Path, name: str = "src") -> Path:
    src = tmp / name
    shutil.copytree(FIX / "kit-src", src)
    shutil.copy(REPO / "catalog.schema.json", src / "catalog.schema.json")
    shutil.copytree(REPO / "onboarding", src / "onboarding")
    shutil.copytree(REPO / "skills" / "onboard", src / "skills" / "onboard")
    shutil.copytree(REPO / "cc", src / "cc", ignore=shutil.ignore_patterns("__pycache__", "web"))
    for f in ("onboard_write.py", "kit_secrets.py"):
        shutil.copy(REPO / "engines" / f, src / "engines" / f)
    shutil.copy(REPO / "launch.py", src / "launch.py")
    return src


def yes(msg, stale_lock=False, sha=False):
    return not stale_lock and not sha


def run(src: Path, target: Path, *args: str, **kw) -> int:
    kw.setdefault("confirm", yes)
    return cli.main([*args, "--target", str(target), "--source", str(src), "--yes"], **kw)


def tree(root: Path, skip=(".kit/install.log",)) -> dict:
    out = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if p.is_file() and rel not in skip:
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def tarball(src: Path, top: str = "kit-" + SHA) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for p in sorted(src.rglob("*")):
            tf.add(p, arcname=f"{top}/{p.relative_to(src).as_posix()}", recursive=False)
    return buf.getvalue()


class FakeRelease:
    def __init__(self, src: Path, sha: str = SHA, manifest: dict | None = None):
        self.sha, self.data = sha, tarball(src)
        self.manifest = manifest or cli.build_release_manifest(src)

    def resolve(self, ref):
        return self.sha

    def changelog(self, sha):
        return "demo changelog"

    def archive(self, sha):
        assert sha == self.sha
        return self.data

    def release_manifest(self, sha):
        assert sha == self.sha
        return self.manifest

    def fetch(self, url, limit):
        raise AssertionError("no network in tests")


def answers(name: str) -> Path:
    return FIX / f"answers-{name}.yaml"


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))
