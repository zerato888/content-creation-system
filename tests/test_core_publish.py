# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Zernio publisher: payload and account match offline; the dry run never touches the network or the key."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engines" / "publish"))
import zernio  # noqa: E402


def test_selftest():
    assert zernio.selftest() == 3


def test_dry_run_sends_nothing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(zernio.Zernio, "__init__", lambda *a, **k: pytest.fail("dry run touched Zernio"))
    (tmp_path / "r.mp4").write_bytes(b"x")
    (tmp_path / "c.txt").write_text("Caption", encoding="utf-8")
    rc = zernio.main(["post", "--handle", "@m", "--video", str(tmp_path / "r.mp4"), "--caption",
                      str(tmp_path / "c.txt"), "--at", "2026-10-01T18:00"])
    assert rc == 0 and "no se envió nada" in capsys.readouterr().out


@pytest.mark.parametrize("args,msg", [
    (["--images", "a.png"], "entre 2 y 10"),
    (["--video", "r.mp4", "--at", "mañana"], "--at va como"),
    (["--video", "r.mp4", "--platforms", "myspace"], "desconocida"),
])
def test_bad_inputs(tmp_path, monkeypatch, args, msg):
    monkeypatch.chdir(tmp_path)
    for f in ("a.png", "r.mp4"):
        (tmp_path / f).write_bytes(b"x")
    (tmp_path / "c.txt").write_text("C", encoding="utf-8")
    base = ["post", "--handle", "@m", "--caption", "c.txt", "--at", "2026-10-01T18:00"]
    with pytest.raises(SystemExit) as e:
        zernio.main(base + args)
    assert msg in str(e.value)
