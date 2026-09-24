# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Network layer for updates. Injectable: tests pass an object with the same methods."""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request

from . import ow

REPO = "zerato888/content-creation-system"
SHA = re.compile(r"^[0-9a-f]{40}$")


def http_get(url: str, limit: int) -> bytes:
    if not url.startswith("https://"):
        raise ow.KitError(f"solo descargo por HTTPS: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "content-kit-installer",
                                               "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=120) as r:  # noqa: S310 (https enforced above)
        data = r.read(limit + 1)
    if len(data) > limit:
        raise ow.KitError(f"descarga demasiado grande: {url}")
    return data


class GitHubRelease:
    """Resolve a tag to an immutable commit SHA; fetch the codeload archive and kit-manifest for that SHA."""

    def __init__(self, repo: str = REPO, get=http_get):
        self.repo, self.get = repo, get

    def resolve(self, ref: str | None) -> str:
        api = f"https://api.github.com/repos/{self.repo}"
        if ref and SHA.match(ref):
            return ref
        if not ref:
            ref = json.loads(self.get(f"{api}/releases/latest", 2**20))["tag_name"]
        sha = json.loads(self.get(f"{api}/commits/{urllib.parse.quote(ref, safe='')}", 2**22)).get("sha", "")
        if not SHA.match(sha):
            raise ow.KitError(f"no pude resolver {ref!r} a un commit")
        return sha

    def changelog(self, sha: str) -> str:
        try:
            return self.get(f"https://raw.githubusercontent.com/{self.repo}/{sha}/CHANGELOG.md", 2**20).decode(
                "utf-8", "replace")[:3000]
        except Exception:  # noqa: BLE001 - optional
            return ""

    def archive(self, sha: str) -> bytes:
        return self.get(f"https://codeload.github.com/{self.repo}/tar.gz/{sha}", 500 * 2**20)

    def release_manifest(self, sha: str) -> dict:
        return json.loads(self.get(f"https://raw.githubusercontent.com/{self.repo}/{sha}/kit-manifest.json", 2**24))

    def fetch(self, url: str, limit: int) -> bytes:
        return self.get(url, limit)
