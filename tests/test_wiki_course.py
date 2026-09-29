# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Offline: wiki-lint sobre la wiki de juguete y la ingesta de un curso de juguete (2 lecciones)."""
import json
import shutil
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIX = REPO / "tests" / "fixtures"
sys.path.insert(0, str(REPO / "engines"))
sys.path.insert(0, str(REPO / "engines" / "course"))
import wiki_lint  # noqa: E402
import course  # noqa: E402
import qc  # noqa: E402


def wiki_copy(tmp_path):
    dst = tmp_path / "wiki"
    shutil.copytree(FIX / "wiki-example" / "wiki", dst)
    return dst


def test_example_wiki_is_clean(tmp_path):
    r = wiki_lint.lint(wiki_copy(tmp_path), today=date(2026, 1, 10))
    assert not any(r[k] for k in ("broken", "orphans", "not_in_index", "frontmatter", "stale")), r
    assert wiki_lint.main(["--wiki", str(FIX / "wiki-example" / "wiki")]) in (0, 1)  # CLI corre


def test_lint_finds_problems(tmp_path):
    w = wiki_copy(tmp_path)
    (w / "concepts" / "suelta.md").write_text("---\ntitle: Suelta\n---\nve a [[no-existe]]\n", encoding="utf-8")
    r = wiki_lint.lint(w, stale_days=30, today=date(2026, 6, 1))
    assert r["broken"] == {"suelta": ["no-existe"]}
    assert "suelta" in r["orphans"] and "suelta" in r["not_in_index"]
    assert r["frontmatter"]["suelta"] == ["type", "created", "updated"]
    assert ("hook-simple", 151) in r["stale"]
    assert wiki_lint.main(["--wiki", str(w)]) == 1


def test_words_to_lines():
    words = [{"text": "hola", "start": 0.0, "end": 1.0}, {"text": "mundo.", "start": 1.0, "end": 2.0},
             {"text": "otra", "start": 65.0, "end": 66.0}]
    assert course.words_to_lines(words) == ["[00:00] hola mundo.", "[01:05] otra"]


def test_qc_toy_course_passes(tmp_path):
    t = tmp_path / "transcripts"
    shutil.copytree(FIX / "course-toy" / "transcripts", t)
    assert qc.run(t) == 0
    assert all(r["ok"] for r in json.loads((t / "qc.json").read_text(encoding="utf-8")).values())


def test_qc_blocks_bad_lessons(tmp_path):
    ok = "# Hook claro\n\n" + "\n".join(f"[00:{i * 5:02d}] el hook claro número {i}" for i in range(10))
    (tmp_path / "a.md").write_text(ok, encoding="utf-8")
    (tmp_path / "b.md").write_text(ok.replace("Hook claro", "Oferta"), encoding="utf-8")
    (tmp_path / "loop.md").write_text("# Bucle\n\n" + "\n".join("[00:0%d] lo mismo" % i for i in range(8)), encoding="utf-8")
    (tmp_path / "corte.md").write_text(ok.replace("Hook claro", "Corte largo"), encoding="utf-8")
    assert qc.run(tmp_path, durations={"corte.md": 600}) == 1
    r = json.loads((tmp_path / "qc.json").read_text(encoding="utf-8"))
    assert r["a.md"]["ok"]
    assert any("idéntico" in p for p in r["b.md"]["problemas"])
    assert any("bucle" in p for p in r["loop.md"]["problemas"])
    assert any("corte" in p for p in r["corte.md"]["problemas"])


def test_index_and_registry(tmp_path):
    t = tmp_path / "transcripts"
    shutil.copytree(FIX / "course-toy" / "transcripts", t)
    qc.run(t)
    out = course.build_index(t, "Curso de Juguete", tmp_path)
    assert out == {"slug": "curso-de-juguete", "ok": 2, "pendientes": 0}
    reg = (tmp_path / ".kit-personal" / "cursos.md").read_text(encoding="utf-8")
    assert "| Curso de Juguete | [[curso-de-juguete]] | 2 | 0 |" in reg
    course.build_index(t, "Curso de Juguete", tmp_path)  # idempotente: una sola fila
    assert (tmp_path / ".kit-personal" / "cursos.md").read_text(encoding="utf-8").count("| Curso de Juguete |") == 1
    assert wiki_lint.lint(tmp_path / "wiki")["broken"] == {}


def test_connect_block_cap_and_consult():
    spec = {"course": "Juguete", "folder": "knowledge/juguete", "cap": 2, "pages": [
        {"path": "a.md", "tags": ["copy"], "when": "escribir hooks"},
        {"path": "b.md", "tags": ["copy"], "when": "tema puntual", "consult": True},
        {"path": "c.md", "tags": ["copy"], "when": "otro"}]}
    b = course.connect_block(spec)
    assert "- [copy] Leé `a.md` cuando: escribir hooks" in b
    assert "- [curso-consulta] Leé `b.md`" in b and "c.md" not in b and "quedaron fuera" in b
