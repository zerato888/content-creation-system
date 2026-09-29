# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""reel.py: silence math and filter graph offline; a real cut when ffmpeg is present."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engines" / "video"))
import reel  # noqa: E402


def test_selftest():
    assert reel.selftest() == 3


@pytest.mark.skipif(not shutil.which(reel.kit_platform.ffmpeg()), reason="sin ffmpeg")
def test_cut_removes_silence(tmp_path):
    ff = reel.kit_platform.ffmpeg()
    src = tmp_path / "grab.mp4"
    audio = "sine=f=440:d=1,apad=pad_dur=1.5[a0];sine=f=440:d=1[a1];[a0][a1]concat=n=2:v=0:a=1[a]"
    subprocess.run([ff, "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=180x320:r=30:d=3.5",
                    "-filter_complex", audio, "-map", "0:v", "-map", "[a]", "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(src)], check=True)
    out = reel.cut(src, min_sil=0.4, pad=0.1)
    assert out.is_file()
    assert reel.probe_duration(out) < reel.probe_duration(src) - 1.0
