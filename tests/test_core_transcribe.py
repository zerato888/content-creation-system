# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Offline tests for engines/video/transcribe.py (no ffmpeg, no whisper needed)."""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "engines" / "video"))
import transcribe as tx  # noqa: E402


@pytest.mark.parametrize("bad", ["http://x/a.mp4", "https://x/a.mp4", "concat:a.mp4|b.mp4",
                                 "file:a.mp4", "rtmp://h/live", "pipe:0"])
def test_rejects_urls_and_protocols(bad):
    with pytest.raises(tx.MediaRejected):
        tx.check_media_input(bad)


@pytest.mark.parametrize("name", ["list.m3u8", "list.m3u", "list.ffconcat"])
def test_rejects_playlist_suffixes(tmp_path, name):
    f = tmp_path / name
    f.write_text("x", encoding="utf-8")
    with pytest.raises(tx.MediaRejected):
        tx.check_media_input(f)


@pytest.mark.parametrize("head", ["#EXTM3U\n#EXTINF:1\nhttp://x", "ffconcat version 1.0\nfile a.mp4"])
def test_rejects_playlist_content_with_media_extension(tmp_path, head):
    f = tmp_path / "trap.mp4"
    f.write_text(head, encoding="utf-8")
    with pytest.raises(tx.MediaRejected):
        tx.check_media_input(f)


def test_accepts_plain_local_file_and_missing_file_fails(tmp_path):
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"\x00\x00\x00\x18ftypmp42")
    assert tx.check_media_input(f) == f.resolve()
    with pytest.raises(tx.MediaRejected):
        tx.check_media_input(tmp_path / "nope.mp4")


def test_ffmpeg_and_ffprobe_argv_carry_protocol_whitelist(tmp_path):
    for argv in (tx.ffmpeg_decode_argv(tmp_path / "a.mp4", tmp_path / "a.wav"),
                 tx.ffprobe_argv(tmp_path / "a.mp4")):
        i = argv.index("-protocol_whitelist")
        assert argv[i + 1] == "file,pipe"
        assert all(isinstance(a, str) for a in argv)
    dec = tx.ffmpeg_decode_argv(tmp_path / "a.mp4", tmp_path / "a.wav")
    assert dec.index("-protocol_whitelist") < dec.index("-i")


def test_fallback_order_and_first_available_wins(monkeypatch):
    calls = []

    def missing(name):
        def fn(*a):
            calls.append(name)
            raise tx.BackendMissing(name)
        return fn

    def ok(name):
        def fn(*a):
            calls.append(name)
            return [{"text": "hola", "start": 0.0, "end": 0.3}]
        return fn

    monkeypatch.setattr(tx, "BACKENDS", [("faster-whisper", missing("faster-whisper")),
                                         ("openai-whisper", missing("openai-whisper")),
                                         ("mlx-whisper", missing("mlx-whisper")),
                                         ("whisper.cpp", ok("whisper.cpp"))])
    name, words = tx.run_backends("a.wav", None, "small")
    assert name == "whisper.cpp" and calls == ["faster-whisper", "openai-whisper", "mlx-whisper", "whisper.cpp"]


def test_default_backend_order():
    assert [n for n, _ in tx.BACKENDS] == ["faster-whisper", "openai-whisper", "mlx-whisper", "whisper.cpp"]


def test_real_backends_report_missing_imports(monkeypatch):
    import builtins
    real_import = builtins.__import__
    blocked = {"faster_whisper", "whisper", "mlx_whisper"}

    def fake_import(name, *a, **k):
        if name.split(".")[0] in blocked:
            raise ImportError(name)
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setattr(tx.shutil, "which", lambda n: None)
    with pytest.raises(tx.BackendMissing) as exc:
        tx.run_backends("a.wav", None, "small")
    for name in ("faster-whisper", "openai-whisper", "mlx-whisper", "whisper.cpp"):
        assert name in str(exc.value)


def test_whisper_cpp_needs_model_in_shared_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(tx.shutil, "which", lambda n: "/bin/whisper-cli" if n == "whisper-cli" else None)
    monkeypatch.setattr(tx.kit_platform, "whisper_model_dir", lambda: tmp_path)
    with pytest.raises(tx.BackendMissing, match="ggml-small.bin"):
        tx._cpp(tmp_path / "a.wav", None, "small")


def test_whisper_cpp_argv_language_only_when_given():
    assert "-l" not in tx.whisper_cpp_argv("w", "m.bin", "a.wav", "o")
    argv = tx.whisper_cpp_argv("w", "m.bin", "a.wav", "o", "es")
    assert argv[argv.index("-l") + 1] == "es" and "-oj" in argv


def test_model_default_small_and_large_needs_flag(monkeypatch):
    monkeypatch.delenv("KIT_WHISPER_MODEL", raising=False)
    assert tx.resolve_model(None) == "small"
    with pytest.raises(tx.BackendMissing):
        tx.resolve_model("large-v3")
    with pytest.raises(tx.BackendMissing):
        monkeypatch.setenv("KIT_WHISPER_MODEL", "medium")
        tx.resolve_model(None)
    assert tx.resolve_model("large-v3", allow_large=True) == "large-v3"


def test_adapters():
    flat = tx.adapt_flat_words({"segments": [{"text": " hi", "start": 0, "end": 1,
                                              "words": [{"word": " hola ", "start": 0.0004, "end": 0.9996}]}]})
    assert flat == [{"text": "hola", "start": 0.0, "end": 1.0}]
    seg_only = tx.adapt_flat_words({"segments": [{"text": " frase ", "start": 1, "end": 2}]})
    assert seg_only == [{"text": "frase", "start": 1, "end": 2}]
    cpp = tx.adapt_whisper_cpp({"transcription": [
        {"text": " Hola,", "offsets": {"from": 0, "to": 400}},
        {"text": "[MUSIC]", "offsets": {"from": 400, "to": 500}},
        {"text": " .", "offsets": {"from": 500, "to": 510}}]})
    assert cpp == [{"text": "Hola,", "start": 0.0, "end": 0.4}]


def test_transcribe_words_contract(monkeypatch, tmp_path):
    media = tmp_path / "a.wav"
    media.write_bytes(b"RIFF0000WAVE")
    monkeypatch.setattr(tx.subprocess, "run", lambda *a, **k: None)
    monkeypatch.setattr(tx, "run_backends", lambda wav, lang, model: (
        "fake", [{"text": "hola", "start": 0.0, "end": 0.2}]))
    words = tx.transcribe_words(media)
    assert words == [{"text": "hola", "start": 0.0, "end": 0.2}]
    assert set(words[0]) == {"text", "start", "end"}


def test_group_blocks_pairs_lines_and_breaks_on_pause():
    words = [{"t": t, "s": i * 0.3, "e": i * 0.3 + 0.2} for i, t in enumerate("a b c d e f".split())]
    blocks = tx.group_blocks(words, max_words_per_line=2)
    assert [len(b["lines"]) for b in blocks] == [2, 1]
    paused = [{"t": "uno", "s": 0, "e": .2}, {"t": "dos", "s": 1.0, "e": 1.2}]
    assert len(tx.group_blocks(paused)) == 2


def test_no_hardcoded_absolute_paths():
    src = (REPO / "engines" / "video" / "transcribe.py").read_text(encoding="utf-8")
    for bad in ("/usr/local/" + "share", "/" + "Users/", "hyper" + "frames", "C:" + "\\\\", "/" + "opt/"):
        assert bad not in src
