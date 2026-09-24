# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Command Center UI (cc/web): syntax, CSP-safe markup, no HTML injection sinks, no owner data,
and every API route the UI calls exists on the server."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
WEB = REPO / "cc" / "web"
sys.path.insert(0, str(REPO))
from cc.server import app as ccapp  # noqa: E402

JS = sorted(WEB.rglob("*.js"))
HTML = sorted(WEB.rglob("*.html"))
TEXT_EXT = {".js", ".html", ".css"}
OPTIONAL_ROUTES = set()


def test_tree_is_text_only():
    assert JS and HTML
    for path in WEB.rglob("*"):
        if path.is_file():
            assert path.suffix in TEXT_EXT, f"not a text asset: {path}"


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
@pytest.mark.parametrize("path", JS, ids=lambda p: p.name)
def test_js_parses(path):
    result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("path", JS, ids=lambda p: p.name)
def test_no_html_sinks(path):
    src = path.read_text(encoding="utf-8")
    for sink in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function",
                 "setAttribute(\"style\"", "setAttribute('style'", "setAttribute(\"on", "javascript:"):
        assert sink not in src, f"{path.name}: {sink}"
    assert not re.search(r"setTimeout\(\s*[\"'`]", src), f"{path.name}: string setTimeout"


@pytest.mark.parametrize("path", HTML, ids=lambda p: p.name)
def test_html_is_csp_clean(path):
    src = path.read_text(encoding="utf-8")
    assert not re.search(r"\son[a-z]+\s*=", src, re.I), "inline event handler"
    assert not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", src, re.I), "inline script"
    assert "<style" not in src.lower() and not re.search(r"\sstyle\s*=", src, re.I), "inline style"
    assert not re.search(r"(src|href)=\"(https?:)?//", src, re.I), "external resource"


def test_locale_currency_timezone_come_from_config():
    # The UI reads locale, currency and timezone from /api/config; no literals in the web assets.
    tz = re.compile(r"\b(?:America|Europe|Asia|Africa|Australia|Pacific|Atlantic)/[A-Za-z_]+")
    # Only a neutral fallback (USD, used before /api/config answers) may appear as a literal.
    currency_key = re.compile(r"currency\s*(?::|\|\|)\s*[\"'`](?!USD[\"'`])[A-Z]{3}[\"'`]")
    # "en-CA" is allowed only as the YYYY-MM-DD formatting trick; display locale comes from config.
    locale_lit = re.compile(r"[\"'`](?!en-CA[\"'`])[a-z]{2}-[A-Z]{2}[\"'`]")
    embed = re.compile(r"data:[a-z]+/[a-z0-9.+-]+;base64", re.I)
    for path in WEB.rglob("*"):
        if path.is_file():
            src = path.read_text(encoding="utf-8")
            for rx in (tz, currency_key, locale_lit, embed):
                assert not rx.search(src), f"{path.name}: {rx.search(src).group(0)}"
    assert any("/api/config" in p.read_text(encoding="utf-8") for p in JS), "UI must load /api/config"


def test_css_loads_nothing_external():
    for path in WEB.rglob("*.css"):
        for url in re.findall(r"url\(\s*[\"']?([^\"')]+)", path.read_text(encoding="utf-8")):
            assert not re.match(r"(https?:)?//|data:", url), f"{path.name}: {url}"


def test_every_api_route_called_exists():
    routes = set(ccapp.GET_ROUTES) | set(ccapp.POST_ROUTES)
    called = set()
    for path in JS:
        called |= set(re.findall(r"[\"'`](/api/[a-z0-9/_-]+)", path.read_text(encoding="utf-8")))
    assert called, "the UI should call the API"
    missing = called - routes - OPTIONAL_ROUTES
    assert not missing, f"UI calls unknown routes: {sorted(missing)}"
