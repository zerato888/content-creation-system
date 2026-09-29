# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Metricool publisher with simulated answers: no network, no key, nothing sent by default."""
import json
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engines" / "publish"))
import metricool  # noqa: E402
import zernio  # noqa: E402

REAL = metricool.Metricool
FUTURE = "2099-10-01T18:00"


class Resp:
    def __init__(self, body="", status=200, headers=None):
        self.body, self.status, self.headers = body, status, headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self.body.encode("utf-8")


class Fake:
    """Answers like Metricool: simple uploads, a scheduler that can refuse one network."""

    def __init__(self, fail=(), multipart=False, status_override=None):
        self.calls, self.fail, self.multipart, self.status_override = [], set(fail), multipart, status_override

    def __call__(self, req):
        url, method = req.full_url, req.get_method()
        body = json.loads(req.data) if req.data and req.headers.get("Content-type") == "application/json" else None
        self.calls.append((method, url, body, dict(req.headers)))
        if self.status_override:
            raise urllib.error.HTTPError(url, self.status_override, "x", {}, None)
        if "/admin/simpleProfiles" in url:
            return Resp(json.dumps({"data": [{"id": 7, "label": "Mi marca"}]}))
        if "upload-transactions" in url and method == "PUT" and body:
            if self.multipart:
                return Resp(json.dumps({"data": {"uploadType": "MULTIPART", "uploadId": "U", "key": "K", "parts": [
                    {"partNumber": 1, "presignedUrl": "https://s3.example/p1", "startByte": 0, "partSize": 3}]}}))
            return Resp(json.dumps({"data": {"uploadType": "SIMPLE", "presignedUrl": "https://s3.example/up",
                                             "fileUrl": "https://cdn.example/f.png"}}))
        if "upload-transactions" in url and method == "PATCH":
            return Resp(json.dumps({"data": {"fileUrl": "https://cdn.example/big.png"}}))
        if url.startswith("https://s3.example"):
            return Resp("", headers={"ETag": "e1"})
        if "/v2/scheduler/posts" in url:
            net = body["providers"][0]["network"]
            if net in self.fail:
                return Resp(json.dumps({"error": "no"}), 200)
            return Resp(json.dumps({"data": {"id": f"P-{net}"}}))
        raise AssertionError(url)


def client(fake):
    return REAL(key="K", user="U", blog="B", opener=fake)


def args(tmp_path, *extra):
    for f in ("a.png", "b.png"):
        (tmp_path / f).write_bytes(b"png")
    (tmp_path / "c.txt").write_text("Caption ñ", encoding="utf-8")
    return ["post", "--images", str(tmp_path / "a.png"), str(tmp_path / "b.png"), "--caption", str(tmp_path / "c.txt"),
            "--at", FUTURE, *extra]


def test_selftest():
    assert metricool.selftest() == 3


def test_dry_run_sends_nothing_and_reads_no_key(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(metricool.Metricool, "__init__", lambda *a, **k: pytest.fail("dry run touched Metricool"))
    monkeypatch.setattr(metricool.kit_secrets, "get_secret", lambda n: pytest.fail("dry run read a secret"))
    assert metricool.main(args(tmp_path, "--platforms", "instagram,facebook", "--first-comment", "¿A o B?")) == 0
    out = capsys.readouterr().out
    assert "no se envió nada" in out and "primera imagen" in out and "¿A o B?" in out


@pytest.mark.parametrize("extra,msg", [
    (["--at", "mañana"], "--at va como"), (["--at", "2020-01-01T10:00"], "ya pasó"),
    (["--tz", "Mars/Base"], "zona horaria"), (["--platforms", "myspace"], "desconocida"),
])
def test_bad_inputs(tmp_path, extra, msg):
    with pytest.raises(SystemExit) as e:
        metricool.main(args(tmp_path) + extra)
    assert msg in str(e.value)


def test_missing_key_message_names_the_secret(monkeypatch):
    monkeypatch.setattr(metricool.kit_secrets, "get_secret", lambda n: None)
    with pytest.raises(SystemExit) as e:
        metricool.Metricool()
    assert "METRICOOL_API_KEY" in str(e.value) and "security add-generic-password" in str(e.value)


def test_user_and_blog_come_from_the_secret_store(monkeypatch):
    vals = {"METRICOOL_API_KEY": "k1", "METRICOOL_USER_ID": "u9", "METRICOOL_BLOG_ID": "b5"}
    monkeypatch.setattr(metricool.kit_secrets, "get_secret", vals.get)
    m = metricool.Metricool(opener=Fake())
    assert (m.key, m.user, m.blog) == ("k1", "u9", "b5")
    vals.pop("METRICOOL_BLOG_ID")
    with pytest.raises(SystemExit) as e:
        metricool.Metricool(opener=Fake())
    assert "METRICOOL_BLOG_ID" in str(e.value)
    assert not [n for n in ("USER_ID = \"", "BLOG_ID = \"") if n in Path(metricool.__file__).read_text(encoding="utf-8")]


def test_confirm_uploads_then_schedules_each_network_with_first_comment(tmp_path, monkeypatch):
    fake = Fake()
    monkeypatch.setattr(metricool, "Metricool", lambda **k: client(fake))
    assert metricool.main(args(tmp_path, "--platforms", "instagram,facebook,tiktok", "--first-comment", "¿A o B?",
                               "--confirm")) == 0
    posts = [c for c in fake.calls if "/v2/scheduler/posts" in c[1]]
    assert [p[2]["providers"][0]["network"] for p in posts] == ["instagram", "facebook", "tiktok"]
    ig, fb, tt = (p[2] for p in posts)
    assert ig["firstCommentText"] == fb["firstCommentText"] == "¿A o B?" and "firstCommentText" not in tt
    assert len(ig["media"]) == 2 and len(fb["media"]) == 1
    assert ig["publicationDate"] == {"dateTime": FUTURE + ":00", "timezone": "America/Costa_Rica"}
    assert all("userId=U" in c[1] and "blogId=B" in c[1] and c[3]["X-mc-auth"] == "K" for c in posts)
    rec = json.loads((tmp_path / "c.metricool.json").read_text(encoding="utf-8"))
    assert rec["results"]["instagram"] == "P-instagram"


def test_same_piece_is_not_sent_twice(tmp_path, monkeypatch):
    fake = Fake()
    monkeypatch.setattr(metricool, "Metricool", lambda **k: client(fake))
    a = args(tmp_path, "--confirm")
    assert metricool.main(a) == 0
    n = len(fake.calls)
    with pytest.raises(SystemExit) as e:
        metricool.main(a)
    assert "ya se programó" in str(e.value) and len(fake.calls) == n
    assert metricool.main(a + ["--again"]) == 0


def test_partial_failure_keeps_ids_and_says_do_not_repeat(tmp_path, monkeypatch):
    fake = Fake(fail={"facebook"})
    monkeypatch.setattr(metricool, "Metricool", lambda **k: client(fake))
    with pytest.raises(SystemExit) as e:
        metricool.main(args(tmp_path, "--platforms", "instagram,facebook", "--confirm"))
    assert "facebook" in str(e.value) and "no lo repitas" in str(e.value)
    rec = json.loads((tmp_path / "c.metricool.json").read_text(encoding="utf-8"))
    assert list(rec["results"]) == ["instagram"] and "facebook" in rec["errors"]


def test_multipart_upload_and_video_reel_body(tmp_path):
    fake = Fake(multipart=True)
    (tmp_path / "r.mp4").write_bytes(b"abc")
    assert client(fake).upload(tmp_path / "r.mp4") == "https://cdn.example/big.png"
    b = metricool.build_body("instagram", "h", ["u"], FUTURE, "UTC", "video", "")
    assert b["instagramData"]["type"] == "REEL" and "firstCommentText" not in b


def test_auth_and_network_errors_are_clear(tmp_path):
    with pytest.raises(SystemExit) as e:
        client(Fake(status_override=401)).blogs()
    assert "rechazó la clave" in str(e.value)

    def down(req):
        raise urllib.error.URLError("no route")
    with pytest.raises(SystemExit) as e:
        metricool.Metricool(key="K", user="U", blog="B", opener=down).blogs()
    assert "sin conexión" in str(e.value) and "ya quedó programado" in str(e.value)


def test_accounts_lists_blogs(monkeypatch, capsys):
    fake = Fake()
    monkeypatch.setattr(metricool, "Metricool", lambda **k: client(fake))
    assert metricool.main(["accounts"]) == 0
    assert "7: Mi marca" in capsys.readouterr().out
    assert "blogId" not in fake.calls[0][1]  # listing brands does not need one


def test_zernio_via_flag_dispatches(monkeypatch):
    seen = []
    monkeypatch.setattr(metricool, "main", lambda argv: seen.append(argv) or 0)
    assert zernio.main(["--via", "metricool", "post", "--caption", "c"]) == 0
    assert zernio.main(["post", "--via=metricool"]) == 0
    assert seen == [["post", "--caption", "c"], ["post"]]
    with pytest.raises(SystemExit) as e:
        zernio.main(["--via", "otra", "accounts"])
    assert "zernio o metricool" in str(e.value)
    assert zernio.pop_via(["accounts"]) == ("zernio", ["accounts"])
