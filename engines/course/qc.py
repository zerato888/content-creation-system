#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Control de calidad de transcripciones de un curso, ANTES de escribir la wiki.

Cada lección es un .md: título en la 1ª línea ("# ..."), líneas "[mm:ss] texto".
Frena: texto repetido entre lecciones, rachas de líneas iguales, huecos de más de 90 s,
exceso de "[Música]", casi vacía, y corte (la transcripción termina mucho antes que el video).
Avisa (no frena): el arranque no menciona nada del título.
Escribe <carpeta>/qc.json. Salida 1 si alguna falla: esas lecciones quedan "pendientes".
La duración se toma de un video/audio hermano (mismo nombre) si ffprobe está disponible.

Uso: python3 .kit/launch.py course qc <carpeta_transcripts>
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

STOP = set("de la el los las un una y o en a para por con del que como tu tus su sus mi es al lo se".split())
MEDIA = (".mp4", ".mov", ".mkv", ".webm", ".m4a", ".mp3", ".wav")
MIN_COVER = 0.6  # la transcripción debe cubrir al menos este tramo del video
norm = lambda s: unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()


def parse(p: Path):
    lines = p.read_text(encoding="utf-8").splitlines()
    title = lines[0].lstrip("# ").strip() if lines else p.stem
    rows = [(int(m[1]) * 60 + int(m[2]), m[3].strip()) for l in lines
            if (m := re.match(r"\[(\d+):(\d\d)\]\s*(.*)", l))]
    return title, rows


def media_seconds(p: Path):
    for ext in MEDIA:
        m = p.with_suffix(ext)
        if m.is_file():
            try:
                import kit_platform  # engines/ en el path lo pone main()
                out = subprocess.run([kit_platform.ffprobe(), "-v", "error", "-show_entries", "format=duration",
                                      "-of", "csv=p=0", str(m)], capture_output=True, text=True, timeout=60).stdout
                return float(out.strip())
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, ImportError):
                return None
    return None


def check(p: Path, duration=None):
    title, rows = parse(p)
    probs = []
    if len(rows) < 5:
        return title, ["casi vacía (menos de 5 líneas)"], ""
    body = " ".join(t for _, t in rows)
    mus = sum("musica" in norm(t) for _, t in rows)
    if mus / len(rows) > 0.2:
        probs.append(f"[Música] en {mus}/{len(rows)} líneas (la transcripción alucinó)")
    run = best = 1
    for a, b in zip(rows, rows[1:]):
        run = run + 1 if norm(a[1]) == norm(b[1]) else 1
        best = max(best, run)
    if best >= 4:
        probs.append(f"racha de {best} líneas iguales (bucle)")
    gaps = [b[0] - a[0] for a, b in zip(rows, rows[1:])]
    if gaps and max(gaps) > 90:
        probs.append(f"hueco de {max(gaps)} s")
    if duration and rows[-1][0] < duration * MIN_COVER:
        probs.append(f"corte: la transcripción llega a {rows[-1][0]} s y el video dura {int(duration)} s")
    tw = {w for w in re.findall(r"[a-z0-9]+", norm(title)) if len(w) > 3 and w not in STOP}
    head = norm(" ".join(t for _, t in rows[:40]))
    if tw and not any(w in head for w in tw):
        probs.append("AVISO: el arranque no menciona nada del título (revisar a ojo)")
    return title, probs, hashlib.sha1(norm(body).encode()).hexdigest()


def run(folder, durations=None) -> int:
    folder, durations = Path(folder), durations or {}
    res, seen = {}, {}
    for p in sorted(folder.rglob("*.md")):
        rel = str(p.relative_to(folder)).replace("\\", "/")
        title, probs, h = check(p, durations.get(rel, media_seconds(p)))
        if h and h in seen:
            probs.append(f"texto idéntico a {seen[h]} (lección repetida, o video equivocado)")
        seen.setdefault(h, rel)
        res[rel] = {"titulo": title, "ok": not [x for x in probs if not x.startswith("AVISO")], "problemas": probs}
    (folder / "qc.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = {f for f, r in res.items() if not r["ok"]}
    print(f"{len(res) - len(bad)}/{len(res)} pasan")
    for f, r in res.items():
        if r["problemas"]:
            print("PENDIENTE" if f in bad else "aviso", f, "-", "; ".join(r["problemas"]))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    sys.exit(run(sys.argv[1]) if len(sys.argv) > 1 else print(__doc__) or 2)
