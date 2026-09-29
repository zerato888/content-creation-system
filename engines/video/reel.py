# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Reel from a talking-head recording, without a video editor.

    python .kit/launch.py reel cut <video> [--noise -35] [--min-silence 0.45] [--pad 0.12]
        -> <video>.cut.mp4 + <video>.cut_plan.json   (silences removed; original untouched)
    python .kit/launch.py captions transcribe <video>.cut.mp4 --lang es   (review the text!)
    python .kit/launch.py reel build <video>.cut.mp4 --brand B --base-preset P --margin-v-frac 0.2
        [--hook-preset H] [--broll plan.json] [--music bed.mp3 --music-db -22] [--out reel.mp4]
        -> 1080x1920 H.264 with burned captions, b-roll cutaways over the voice, flat music bed.

B-roll plan (JSON list): [{"start": 2.0, "end": 4.5, "file": "assets/broll/x.mp4"}, ...]
Times are on the CUT video. The voice always stays; b-roll only covers the picture.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_platform  # noqa: E402
import captions as cap  # noqa: E402

W, H = 1080, 1920
SIL = re.compile(r"silence_(start|end): (-?[\d.]+)")


def probe_duration(video: Path) -> float:
    out = subprocess.run([kit_platform.ffprobe(), "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(video)], capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def keep_segments(silences: list[tuple[float, float]], dur: float, pad: float) -> list[tuple[float, float]]:
    """Complement of the silences, each kept span widened by `pad` so words are not clipped."""
    keep, t = [], 0.0
    for s, e in silences:
        if s - t > 0.05:
            keep.append((max(0.0, t - pad if t else 0.0), min(dur, s + pad)))
        t = e
    if dur - t > 0.05:
        keep.append((max(0.0, t - pad if t else 0.0), dur))
    merged = []
    for a, b in keep:  # padding can make neighbours overlap
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    return merged


def detect_silences(video: Path, noise_db: float, min_sil: float) -> list[tuple[float, float]]:
    err = subprocess.run([kit_platform.ffmpeg(), "-nostdin", "-hide_banner", "-i", str(video), "-af",
                          f"silencedetect=noise={noise_db}dB:d={min_sil}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    marks = SIL.findall(err)
    out, start = [], None
    for kind, val in marks:
        if kind == "start":
            start = max(0.0, float(val))
        elif start is not None:
            out.append((start, float(val)))
            start = None
    if start is not None:
        out.append((start, probe_duration(video)))
    return out


def cut(video: Path, noise_db=-35.0, min_sil=0.45, pad=0.12) -> Path:
    dur = probe_duration(video)
    keep = keep_segments(detect_silences(video, noise_db, min_sil), dur, pad)
    if not keep:
        raise SystemExit("ERROR: no encontré voz en el video (¿está en silencio?)")
    parts = "".join(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];"
                    f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[a{i}];" for i, (a, b) in enumerate(keep))
    fc = parts + "".join(f"[v{i}][a{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=1:a=1[v][a]"
    out = video.with_name(video.stem + ".cut.mp4")
    subprocess.run([kit_platform.ffmpeg(), "-nostdin", "-y", "-v", "error", "-i", str(video), "-filter_complex", fc,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(out)], check=True)
    plan = {"source": video.name, "duration_in": round(dur, 3), "kept": [[round(a, 3), round(b, 3)] for a, b in keep],
            "duration_out": round(sum(b - a for a, b in keep), 3)}
    video.with_name(video.stem + ".cut_plan.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
    print(f"{out}  ({plan['duration_in']}s -> {plan['duration_out']}s, {len(keep)} partes)")
    return out


def load_broll(plan_path: Path | None, base: Path, dur: float) -> list[dict]:
    if not plan_path:
        return []
    items = json.loads(plan_path.read_text(encoding="utf-8"))
    out = []
    for it in items:
        f = (base / it["file"]).resolve()
        if not f.is_file():
            raise SystemExit(f"ERROR: no existe el clip de b-roll {it['file']}")
        s, e = float(it["start"]), float(it["end"])
        if not 0 <= s < e <= dur + 0.05:
            raise SystemExit(f"ERROR: b-roll {it['file']} fuera del video ({s}-{e}, dura {dur:.2f}s)")
        out.append({"file": f, "start": s, "end": min(e, dur)})
    return out


def filter_graph(broll: list[dict], ass: Path, fonts: Path, music: bool, music_db: float) -> str:
    fit = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
    g = [f"[0:v]{fit},fps=30[base]"]
    last = "base"
    for i, b in enumerate(broll, start=1):
        g.append(f"[{i}:v]{fit},fps=30,trim=0:{b['end'] - b['start']:.3f},setpts=PTS-STARTPTS+{b['start']:.3f}/TB[b{i}]")
        g.append(f"[{last}][b{i}]overlay=eof_action=pass:enable='between(t,{b['start']:.3f},{b['end']:.3f})'[o{i}]")
        last = f"o{i}"
    g.append(f"[{last}]subtitles=filename={cap.filter_path(ass)}:fontsdir={cap.filter_path(fonts)}[v]")
    if music:  # flat bed under the voice: one constant level, no ducking
        m = len(broll) + 1
        g.append(f"[{m}:a]volume={music_db}dB[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]")
    return ";".join(g)


def build(video: Path, brand: str | None, base_preset: str, hook_preset: str | None, margin_v: float,
          broll_plan: Path | None, music: Path | None, music_db: float, out: Path | None,
          annotated: str | None = None) -> Path:
    words = Path(str(video) + ".captions.json")
    if not words.is_file():
        raise SystemExit(f"ERROR: falta {words.name}: primero `captions transcribe {video.name}` y revisá el texto")
    dur = probe_duration(video)
    broll = load_broll(broll_plan, broll_plan.parent if broll_plan else video.parent, dur)
    art, tagged, presets, brand_data = cap.build_from_files(str(words), base_preset, hook_preset, annotated, brand)
    font_map = cap.load_font_map()
    resolved = cap.resolve_fonts(cap.used_families(presets, font_map), font_map)
    meta = {"w": W, "h": H, "fps": 30, "dur": dur}
    ass_text = cap.build_ass_from_preset({"video": meta, "blocks": cap.group_for_render(tagged, presets)}, presets,
                                         font_map, margin_v, brand_data,
                                         font_names={f: n for f, (n, _) in resolved.items()},
                                         font_files={n: f for n, f in resolved.values()})
    out = out or video.with_name(video.name.replace(".cut", "") .rsplit(".", 1)[0] + ".reel.mp4")
    ff = cap.ffmpeg_with_libass()
    with tempfile.TemporaryDirectory() as td:
        ass = Path(td) / "captions.ass"
        ass.write_text(ass_text, encoding="utf-8", newline="\n")
        fonts = cap.prepare_fonts_dir(resolved, td)
        argv = [ff, "-nostdin", "-y", "-v", "error", "-i", str(video)]
        for b in broll:
            argv += ["-i", str(b["file"])]
        if music:
            argv += ["-stream_loop", "-1", "-i", str(music)]
        argv += ["-filter_complex", filter_graph(broll, ass, Path(fonts), bool(music), music_db),
                 "-map", "[v]", "-map", "[a]" if music else "0:a", "-t", f"{dur:.3f}",
                 "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
        subprocess.run(argv, check=True, env=cap.render_env(td, fonts))
    print(out)
    return out


def selftest() -> int:
    k = keep_segments([(1.0, 2.0), (3.0, 3.5)], 5.0, 0.1)
    assert k == [(0.0, 1.1), (1.9, 3.1), (3.4, 5.0)], k
    assert keep_segments([(0.0, 1.0)], 3.0, 0.1) == [(0.9, 3.0)]
    assert keep_segments([(1.0, 1.1)], 3.0, 0.2) == [(0.0, 3.0)]  # padding merges tiny gaps
    g = filter_graph([{"file": Path("x.mp4"), "start": 1.0, "end": 2.0}], Path("a.ass"), Path("f"), True, -22)
    assert "between(t,1.000,2.000)" in g and "amix" in g and "[1:a]" not in g and "[2:a]" in g
    return 3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("cut", help="quitar silencios")
    c.add_argument("video")
    c.add_argument("--noise", type=float, default=-35.0, help="dB bajo los que cuenta como silencio")
    c.add_argument("--min-silence", type=float, default=0.45)
    c.add_argument("--pad", type=float, default=0.12)
    b = sub.add_parser("build", help="subtítulos + b-roll + música -> reel final")
    b.add_argument("video")
    b.add_argument("--brand")
    b.add_argument("--base-preset", required=True)
    b.add_argument("--hook-preset")
    b.add_argument("--annotated-text")
    b.add_argument("--margin-v-frac", type=float, required=True)
    b.add_argument("--broll")
    b.add_argument("--music")
    b.add_argument("--music-db", type=float, default=-22.0)
    b.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        if a.selftest:
            print(f"reel selftest OK ({selftest()} casos)")
        elif a.cmd == "cut":
            cut(Path(a.video), a.noise, a.min_silence, a.pad)
        elif a.cmd == "build":
            if not 0.0 < a.margin_v_frac < 1.0:
                raise SystemExit("ERROR: --margin-v-frac va entre 0 y 1")
            build(Path(a.video), a.brand, a.base_preset, a.hook_preset, a.margin_v_frac,
                  Path(a.broll) if a.broll else None, Path(a.music) if a.music else None, a.music_db,
                  Path(a.out) if a.out else None, a.annotated_text)
        else:
            ap.error("usar --selftest, cut o build")
    except (cap.ContractViolation, subprocess.CalledProcessError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
