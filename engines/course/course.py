#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Ingesta de cursos: transcribir lecciones, controlar calidad, armar índice y conectar a los agentes.

  python3 .kit/launch.py course transcribe VIDEO SALIDA.md "Título de la lección" [--lang es]
  python3 .kit/launch.py course qc CARPETA_TRANSCRIPTS
  python3 .kit/launch.py course index CARPETA_TRANSCRIPTS --course "Nombre" [--project .]
  python3 .kit/launch.py course connect connect.json

Las lecciones de una carpeta son `modulo/NN-slug.md` (título en la 1ª línea, líneas `[mm:ss] texto`).
`index` solo incluye las lecciones que pasaron el control (qc.json); las otras quedan pendientes.
`connect` imprime el bloque para pegar en el rol (nunca lo escribe solo: la persona aprueba).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import qc  # noqa: E402

REGISTRY_HEAD = "# Cursos\n\n| Curso | Ficha | Lecciones | Pendientes | Fecha |\n|---|---|---|---|---|\n"


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "curso"


def words_to_lines(words, max_s: float = 8.0) -> list[str]:
    """[{"text","start","end"}] -> líneas '[mm:ss] frase' de unos 8 s o hasta un punto."""
    lines, buf, t0 = [], [], None
    for w in words:
        if t0 is None:
            t0 = w["start"]
        buf.append(w["text"])
        if w["end"] - t0 >= max_s or re.search(r"[.!?]$", w["text"]):
            lines.append(f"[{int(t0) // 60:02d}:{int(t0) % 60:02d}] {' '.join(buf)}")
            buf, t0 = [], None
    if buf:
        lines.append(f"[{int(t0) // 60:02d}:{int(t0) % 60:02d}] {' '.join(buf)}")
    return lines


def transcribe_lesson(video: str, out: str, title: str, lang: str | None = None, words=None) -> int:
    if words is None:
        from video import transcribe as tx  # engines/video/transcribe.py
        words = tx.transcribe_words(video, lang)
    lines = words_to_lines(words)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(f"# {title}\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(lines)} líneas -> {out} (corré 'course qc' antes de usar)")
    return 0


def build_index(folder: Path, course: str, project: Path) -> dict:
    """Escribe wiki/sources/<slug>-indice.md, wiki/entities/<slug>.md y la fila de .kit-personal/cursos.md."""
    slug, today = slugify(course), date.today().isoformat()
    res = json.loads((folder / "qc.json").read_text(encoding="utf-8"))
    ok = {f: r for f, r in res.items() if r["ok"]}
    pend = {f: r for f, r in res.items() if not r["ok"]}
    rows = []
    for f in sorted(ok):
        mod, name = (f.split("/", 1) + [""])[:2] if "/" in f else ("", f)
        rows.append(f"- {mod or 'general'} / {ok[f]['titulo']} — `{f}`")
    pend_rows = [f"- {r['titulo']} — {'; '.join(r['problemas'])}" for r in pend.values()]
    wiki = project / "wiki"
    (wiki / "sources").mkdir(parents=True, exist_ok=True)
    (wiki / "entities").mkdir(parents=True, exist_ok=True)
    fm = lambda title, typ, extra="": (f"---\ntitle: {title}\ntype: {typ}\ncreated: {today}\nupdated: {today}\n"
                                        f"tags: [curso]\n{extra}---\n\n")
    (wiki / "sources" / f"{slug}-indice.md").write_text(
        fm(f"Índice de {course}", "source", f"origin: transcripciones locales de {course}\ningested: {today}\n")
        + f"# Índice de {course}\n\nLecciones que pasaron el control de calidad ({len(ok)}):\n\n"
        + "\n".join(rows) + ("\n\nPendientes (no se usan hasta re-descargar):\n\n" + "\n".join(pend_rows) if pend else "")
        + f"\n\nFicha del curso: [[{slug}]]\n", encoding="utf-8")
    (wiki / "entities" / f"{slug}.md").write_text(
        fm(course, "entity") + f"# {course}\n\nCurso ingerido el {today}. {len(ok)} lecciones listas, {len(pend)} pendientes.\n\n"
        f"Índice: [[{slug}-indice]]\n\nQué aprendimos y cómo se usa: completar tras escribir las páginas de frameworks "
        f"(cada una cita lección y minuto).\n", encoding="utf-8")
    reg = project / ".kit-personal" / "cursos.md"
    reg.parent.mkdir(parents=True, exist_ok=True)
    text = reg.read_text(encoding="utf-8") if reg.is_file() else REGISTRY_HEAD
    row = f"| {course} | [[{slug}]] | {len(ok)} | {len(pend)} | {today} |"
    lines = [l for l in text.splitlines() if not l.startswith(f"| {course} |")]
    reg.write_text("\n".join(lines).rstrip("\n") + "\n" + row + "\n", encoding="utf-8")
    return {"slug": slug, "ok": len(ok), "pendientes": len(pend)}


def connect_block(spec: dict) -> str:
    """spec: {"course","folder","cap","pages":[{"path","tags":[..],"when","consult":bool}]} -> texto para el rol."""
    cap = int(spec.get("cap", 12))
    pages = spec["pages"]
    out = [f"## Conocimiento: {spec['course']}",
           f"Curso (índice: `{spec['folder']}/README.md`). Leé solo lo que la tarea pide. Las marcadas `[curso-consulta]` "
           "se abren solo si la tarea toca ese tema. Si el curso contradice la ficha de marca de la persona o sus "
           "lecciones, ganan ellas y lo decís."]
    for p in pages[:cap]:
        tag = "curso-consulta" if p.get("consult") else ", ".join(p["tags"])
        out.append(f"- [{tag}] Leé `{p['path']}` cuando: {p['when']}")
    if len(pages) > cap:
        out.append(f"<!-- {len(pages) - cap} páginas quedaron fuera por el tope de {cap}; elegí cuáles pesan más -->")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("transcribe")
    t.add_argument("video"); t.add_argument("out"); t.add_argument("title"); t.add_argument("--lang")
    q = sub.add_parser("qc"); q.add_argument("folder")
    i = sub.add_parser("index"); i.add_argument("folder"); i.add_argument("--course", required=True)
    i.add_argument("--project", default=".")
    c = sub.add_parser("connect"); c.add_argument("spec")
    a = ap.parse_args(argv)
    if a.cmd == "transcribe":
        return transcribe_lesson(a.video, a.out, a.title, a.lang)
    if a.cmd == "qc":
        return qc.run(a.folder)
    if a.cmd == "index":
        print(json.dumps(build_index(Path(a.folder), a.course, Path(a.project)), ensure_ascii=False))
        return 0
    print(connect_block(json.loads(Path(a.spec).read_text(encoding="utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
