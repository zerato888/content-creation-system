# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Commands: install, update, uninstall, status, rollback, service, cache-clean, migrate-brands, release-manifest."""
from __future__ import annotations

import argparse
import contextlib
import http.client
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import uuid
from pathlib import Path

from . import core, ow, service
from .core import KitError, Log, Lock, Tx, safe_path, sha256_bytes, sha256_file

REPO_ROOT = Path(__file__).resolve().parents[1]
KIT_DIRS = ("engines", "presets", "cc", "knowledge", "onboarding", "hooks")
KIT_FILES = ("catalog.json", "requirements.lock", "package.json", "package-lock.json", "launch.py")
TOOL_DIRS = {"claude": ".claude/skills", "codex": ".agents/skills"}
RUNTIME_DIRS = ("venv", "venv.old", "node_modules", "ms-playwright", "fonts")
MANIFEST = ".kit/manifest.json"
CC_RUNNING = ".kit/cc.running"  # written by .kit/cc/server/app.py while it serves
TRACKED_SECRET = re.compile(r"(^|/)(\.env(\..*)?|.*\.pem|.*\.key|id_rsa|id_ed25519)$|^\.kit-personal/")
KREF = re.compile(r"(?<![\w./-])knowledge/")
FRONT = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.S)
OS_KEY = "windows" if os.name == "nt" else "mac"


# ---------------------------------------------------------------- source reading

def _validator():
    spec = importlib.util.spec_from_file_location("kit_guard", REPO_ROOT / "tools" / "guard.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.validate


def walk(src: Path, top: str) -> list[tuple[str, Path]]:
    """Files under src/top as (posix rel to src, path). Refuses any symlink; never follows one."""
    out = []
    base = src / top
    if base.is_symlink():
        raise KitError(f"la fuente contiene un enlace simbólico: {top}")
    if base.is_file():
        return [(top, base)]
    for dirpath, dirnames, filenames in os.walk(base):
        d = Path(dirpath)
        for x in dirnames + filenames:
            if (d / x).is_symlink():
                raise KitError(f"la fuente contiene un enlace simbólico: {(d / x).relative_to(src).as_posix()}")
        skip = ("__pycache__", ".git", "node_modules") + (("tests",) if top == "cc" else ())
        dirnames[:] = sorted(x for x in dirnames if x not in skip)
        for x in sorted(filenames):
            if x == ".DS_Store" or x.endswith(".pyc"):
                continue
            out.append(((d / x).relative_to(src).as_posix(), d / x))
    return out


def load_catalog(src: Path) -> dict:
    try:
        cat = json.loads((src / "catalog.json").read_text(encoding="utf-8"))
        schema = json.loads((src / "catalog.schema.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise KitError(f"catálogo ilegible en la fuente: {type(e).__name__}")
    errs = _validator()(cat, schema, schema)
    names = [s["name"] for s in cat.get("skills", [])] + [r["name"] for r in cat.get("roles", [])]
    errs += [f"nombre inválido: {n!r}" for n in names if not ow.IDENT.match(n)]
    if errs:
        raise KitError("catalog.json no pasa el esquema:\n  - " + "\n  - ".join(errs[:20]))
    return cat


def release_sha(src: Path) -> str:
    if not (src / ".git").exists():
        return "local"
    try:
        r = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20)
    except OSError:
        return "local"
    return r.stdout.strip() if r.returncode == 0 else "local"


def build_release_manifest(src: Path) -> dict:
    """Maintainers: `python -m installer release-manifest > kit-manifest.json` from a clean checkout."""
    if (src / ".git").exists():
        r = subprocess.run(["git", "-C", str(src), "ls-files", "-z"], capture_output=True, check=True)
        rels = [x for x in r.stdout.decode("utf-8").split("\0") if x]
    else:
        rels = [rel for rel, _ in walk(src, ".")]
    rels = [x[2:] if x.startswith("./") else x for x in rels]
    return {"files": {rel: sha256_file(src / rel) for rel in sorted(rels) if rel != "kit-manifest.json"}}


def verify_release(src: Path, rm: dict) -> None:
    want = rm.get("files") if isinstance(rm, dict) else None
    if not isinstance(want, dict):
        raise KitError("kit-manifest.json de la versión es inválido; actualización abortada")
    have = {rel: sha256_file(p) for rel, p in walk(src, ".") if rel.removeprefix("./") != "kit-manifest.json"}
    have = {k.removeprefix("./"): v for k, v in have.items()}
    bad = sorted(set(want) ^ set(have)) + sorted(k for k in want if k in have and want[k] != have[k])
    if bad:
        raise KitError("la descarga no coincide con kit-manifest.json de ese commit (" + ", ".join(bad[:10]) +
                       "); actualización abortada, no cambié nada")


# ---------------------------------------------------------------- rendering

def role_file(name: str, desc: str, text: str) -> str:
    text = KREF.sub(".kit/knowledge/", text)
    if not FRONT.match(text):
        text = f"---\nname: {name}\ndescription: {desc or name}\n---\n\n" + text
    return text


def role_section(text: str) -> str:
    body = FRONT.sub("", KREF.sub(".kit/knowledge/", text), count=1)
    return re.sub(r"^(#{1,4}) ", lambda m: "#" * (len(m.group(1)) + 2) + " ", body, flags=re.M).strip()


# ---------------------------------------------------------------- planning

class Plan:
    def __init__(self):
        self.ops: list[tuple[str, bytes | None]] = []
        self.report: list[str] = []
        self.backups: list[tuple[str, Path]] = []
        self.manifest: dict = {}

    def show(self, root: Path) -> None:
        for rel, data in self.ops:
            cur = sha256_file(safe_path(root, rel))
            print(f"  {'-' if data is None else '+' if cur is None else '~'} {rel}")
        for r in self.report:
            print(f"  ! {r}")


def read_manifest(root: Path) -> dict | None:
    p = safe_path(root, MANIFEST)
    if not p.is_file():
        return None
    try:
        m = json.loads(p.read_text(encoding="utf-8"))
        m["files"] = {e["path"]: e["sha256"] for e in m.get("files", [])}
        return m
    except (ValueError, TypeError, KeyError):
        raise KitError(".kit/manifest.json ilegible; no sigo para no tocar archivos que no sé si son del kit.")


def select(cat: dict, old: dict | None, core_flag: bool, modules: list[str], report: list[str]) -> list[str]:
    skills = {s["name"]: s for s in cat["skills"]}
    want = set(old.get("skills", [])) if old else set()
    if core_flag or not old:
        want |= {n for n, s in skills.items() if s["tier"] == "core"}
    want |= set(modules)
    out = []
    for n in sorted(want):
        s = skills.get(n)
        if s is None:
            report.append(f"{n}: no existe en el catálogo de esta versión")
        elif s["status"] != "tested":
            report.append(f"{n}: próximamente (todavía no pasó su prueba; no se puede instalar)")
        elif not s["support"].get(OS_KEY, False):
            report.append(f"{n}: no disponible en este sistema operativo")
        else:
            out.append(n)
    return out


def compute(src: Path, root: Path, old: dict | None, *, core_flag=False, modules=(), tools=None,
            answers=None, choose=lambda rel: "keep", release="local") -> Plan:
    pl = Plan()
    cat = load_catalog(src)
    asked = tools or (answers or {}).get("tools") or (old or {}).get("tools") or ow.detect_tools()
    tools = [t for t in asked if t in TOOL_DIRS]
    names = select(cat, old, core_flag, list(modules) + list((answers or {}).get("modules", [])), pl.report)
    skills = {s["name"]: s for s in cat["skills"]}

    desired: dict[str, tuple[bytes, str]] = {}  # rel -> (data, group)
    for n in names:
        files = walk(src, f"skills/{n}")
        if not any(r == f"skills/{n}/SKILL.md" for r, _ in files):
            pl.report.append(f"{n}: falta SKILL.md en la fuente; se omite")
            continue
        for t in tools:
            if not skills[n]["support"].get(t, False):
                pl.report.append(f"{n}: no disponible para {t}")
                continue
            for rel, p in files:
                desired[f"{TOOL_DIRS[t]}/{n}/{rel[len('skills/' + n) + 1:]}"] = (p.read_bytes(), f"{t}:{n}")
    installed = sorted({g.split(":", 1)[1] for _, g in desired.values()})
    roles_md = []
    for r in cat["roles"]:
        if not set(r["skills"]) & set(installed):
            continue
        rp = src / "agents" / f"{r['name']}.md"
        if rp.is_symlink() or not rp.is_file():
            pl.report.append(f"rol {r['name']}: falta agents/{r['name']}.md en la fuente")
            continue
        text = rp.read_text(encoding="utf-8")
        roles_md.append(role_section(text))
        if "claude" in tools:
            desired[f".claude/agents/{r['name']}.md"] = (role_file(r["name"], r.get("description", ""), text)
                                                         .encode("utf-8"), f"role:{r['name']}")
    roles_text = "\n\n".join(roles_md) + ("\n" if roles_md else "")
    desired[".kit/roles.md"] = (roles_text.encode("utf-8"), "kit")
    for top in KIT_DIRS + KIT_FILES:
        if (src / top).exists() or (src / top).is_symlink():
            for rel, p in walk(src, top):
                desired[f".kit/{rel}"] = (p.read_bytes(), "kit")

    old_files = dict((old or {}).get("files", {}))
    kept = {r for r in (old or {}).get("user_owned", []) if sha256_file(safe_path(root, r)) is not None}
    # collisions: user-owned files in the way make the whole group unavailable
    blocked = set()
    for rel, (data, group) in desired.items():
        cur = sha256_file(safe_path(root, rel))
        if cur and cur.startswith("!"):
            raise KitError(f"{rel}: hay un enlace simbólico o carpeta en el destino; me niego a escribir ahí")
        if rel not in old_files and rel not in kept and cur is not None:
            pl.report.append(f"{rel}: ya existe y no es del kit; lo dejo como está")
            if group != "kit":
                blocked.add(group)
    for g in sorted(blocked):
        pl.report.append(f"{g.split(':', 1)[1]} ({g.split(':')[0]}): no disponible por archivos tuyos en su lugar")
    new_files: dict[str, str] = {}
    for rel, (data, group) in sorted(desired.items()):
        if group in blocked:
            continue
        if rel in kept:
            continue
        cur, new = sha256_file(safe_path(root, rel)), sha256_bytes(data)
        if rel in old_files:
            if cur not in (None, old_files[rel], new):  # modified by the user
                if choose(rel) == "keep":
                    pl.report.append(f"{rel}: lo modificaste; se conserva el tuyo (ahora es tuyo, no del kit)")
                    kept.add(rel)
                    continue
                pl.backups.append((rel, safe_path(root, rel)))
            new_files[rel] = new
            if cur != new:
                pl.ops.append((rel, data))
        elif cur is None:
            new_files[rel] = new
            pl.ops.append((rel, data))
    for rel, h in sorted(old_files.items()):  # orphans: kit-owned, gone from this release
        if rel in desired:
            continue
        cur = sha256_file(safe_path(root, rel))
        if cur is None:
            continue
        if cur != h and choose(rel) == "keep":
            pl.report.append(f"{rel}: ya no es parte del kit y lo modificaste; queda como tuyo")
            continue
        pl.backups.append((rel, safe_path(root, rel)))
        pl.ops.append((rel, None))

    personal, notes = ow.plan(root, answers, tools=tools, roles_md=roles_text,
                              skills=[n for n in installed], overwrite_personal=False,
                              templates=src / "onboarding" if (src / "onboarding").is_dir() else ow.TEMPLATES)
    pl.report += notes
    pl.ops += sorted(personal.items())
    pl.manifest = {"format": 1, "kit_version": cat["version"], "release": release, "tools": tools,
                   "skills": installed, "files": new_files,
                   "unavailable": sorted(g.split(":", 1)[1] for g in blocked),
                   "user_owned": sorted(r for r in kept if r in desired)}
    if (old or {}).get("service"):
        pl.manifest["service"] = old["service"]
    # files as [{path, sha256}] rather than {path: hash}: a "secrets.py": "<hex>" pair looks like a leak to gitleaks
    disk = {**pl.manifest, "files": [{"path": r, "sha256": h} for r, h in sorted(new_files.items())]}
    mdata = (json.dumps(disk, indent=1, sort_keys=True) + "\n").encode("utf-8")
    mp = safe_path(root, MANIFEST)
    if not (mp.is_file() and mp.read_bytes() == mdata):
        pl.ops.append((MANIFEST, mdata))
    return pl


def uninstall_plan(root: Path, old: dict) -> Plan:
    pl = Plan()
    for rel, h in sorted(old.get("files", {}).items()):
        cur = sha256_file(safe_path(root, rel))
        if cur == h:
            pl.ops.append((rel, None))
        elif cur is not None:
            pl.report.append(f"{rel}: lo modificaste; no lo borro")
    if safe_path(root, MANIFEST).is_file():
        pl.ops.append((MANIFEST, None))
    # the kit's hook entries point at .kit/hooks/, which is about to go: take them out of the tool configs
    for fname, tool in ((".claude/settings.json", "claude"), (".codex/hooks.json", "codex")):
        p = safe_path(root, fname)
        if not p.is_file():
            continue
        try:
            data = ow._load_json_obj(p.read_bytes(), fname)
            before = json.dumps(data, sort_keys=True)
            ow._merge_hooks(data, tool, [], fname)
        except KitError as e:
            pl.report.append(str(e))
            continue
        if json.dumps(data, sort_keys=True) != before:
            pl.ops.append((fname, (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")))
    for fname, style in (("CLAUDE.md", "md"), ("AGENTS.md", "md"), (".gitignore", "hash")):
        p = safe_path(root, fname)
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        new = ow.remove_block(text, fname)
        if new != text:
            pl.ops.append((fname, None if not new.strip() else new.encode("utf-8")))
    return pl


# ---------------------------------------------------------------- session helpers

def cc_running(root: Path) -> bool:
    """True while a live Command Center holds .kit/cc.running; a stale marker is cleared.
    Call it with the lifecycle lock held: a starting server registers under the same lock."""
    p = safe_path(root, CC_RUNNING)
    if not p.is_file():
        return False
    if ow.cc_live(root):
        return True
    p.unlink(missing_ok=True)
    return False


def refuse_if_running(root: Path, what: str) -> None:
    if cc_running(root):
        raise KitError(f"el Command Center está corriendo; cerralo (o `service off`) antes de {what}.")


def write_manifest_key(root: Path, key: str, value) -> None:
    p = safe_path(root, MANIFEST)
    m = json.loads(p.read_text(encoding="utf-8"))
    if value is None:
        m.pop(key, None)
    else:
        m[key] = value
    core.atomic_write(p, (json.dumps(m, indent=1, sort_keys=True) + "\n").encode("utf-8"))


def service_off(root: Path, m: dict, log: Log) -> None:
    """Unregister and stop. The ownership record is cleared only once both are verified;
    otherwise it stays (so a later `service off` / uninstall can finish) and the error is reported."""
    rec = m["service"]
    try:
        service.remove(rec)
    except KitError as e:
        log("service-off", rec["label"], "error", e)
        raise
    for _ in range(100):  # the server removes its marker on SIGTERM
        if not cc_running(root):
            break
        time.sleep(0.1)
    else:
        log("service-off", rec["label"], "error", message="still running")
        raise KitError("quité el registro del servicio pero el Command Center sigue corriendo; "
                       "cerralo (o reiniciá la sesión) y volvé a correr `service off`.")
    write_manifest_key(root, "service", None)
    log("service-off", rec["label"])


def service_on(root: Path, log: Log) -> dict:
    """Register with a pending ownership record written FIRST, so a crash between registering and
    recording never leaves a service that uninstall cannot find (see recover_service)."""
    rec = service.record(root)
    write_manifest_key(root, "service", {**rec, "pending": True})
    try:
        rec = service.install(root)
    except BaseException:
        with contextlib.suppress(Exception):  # compensate; if even that fails the pending record stays
            service.remove(rec)
            write_manifest_key(root, "service", None)
        raise
    write_manifest_key(root, "service", rec)
    log("service-on", rec["label"])
    return rec


def recover_service(root: Path, log: Log) -> None:
    """A pending service record means an interrupted `service on`: keep it if the OS has it, else drop it."""
    try:
        m = read_manifest(root)
    except KitError:
        return
    rec = (m or {}).get("service")
    if not rec or not rec.get("pending"):
        return
    rec = {k: v for k, v in rec.items() if k != "pending"}
    if service.status(rec) == "no registrado":
        write_manifest_key(root, "service", None)
        log("service-recover", rec["label"], message="dropped")
    else:
        write_manifest_key(root, "service", rec)
        log("service-recover", rec["label"], message="kept")

def check_tracked_secrets(root: Path) -> None:
    if not (root / ".git").exists() or not shutil.which("git"):
        return
    r = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True)
    bad = [x for x in r.stdout.decode("utf-8", "replace").split("\0") if x and TRACKED_SECRET.search(x)]
    if bad:
        raise KitError(
            "tu repositorio git ya guarda archivos que suelen tener claves: " + ", ".join(bad[:5]) +
            ".\nNo sigo. Para arreglarlo: 1) rotá (cambiá) esas claves en el servicio, 2) `git rm --cached <archivo>`, "
            "3) borralos del historial con `git filter-repo --invert-paths --path <archivo>` (o BFG), "
            "4) volvé a correr el instalador.")


@contextlib.contextmanager
def session(root: Path, command: str, confirm, log: Log):
    lock = Lock(root, command, confirm, log)
    lock.acquire()
    try:
        if core.recover(root, log):
            print("Había una operación a medias; la deshice y dejé todo como estaba antes.")
        recover_service(root, log)
        yield lock
    finally:
        lock.release()


def apply(root: Path, pl: Plan, lock: Lock, log: Log, command: str, args, confirm, fail_at=None) -> int:
    if not pl.ops:
        for r in pl.report:
            print(f"  ! {r}")
        print("Todo al día: no hay nada que cambiar.")
        return 0
    print(f"Cambios propuestos ({len(pl.ops)}):  + nuevo  ~ reemplaza  - borra")
    pl.show(root)
    if args.dry_run:
        print("(simulación: no se cambió nada)")
        return 0
    if not confirm("¿Aplico estos cambios?"):
        print("Cancelado: no se cambió nada.")
        return 1
    if pl.backups:
        bdir = f".kit/backup/{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        for rel, p in pl.backups:
            core.atomic_write(core.make_parents(root, f"{bdir}/{rel}"), p.read_bytes())
        print(f"Copia de tus versiones anteriores en {bdir}/")
    Tx(root, lock, log, command).run(pl.ops, fail_at=fail_at)
    print("Listo.")
    return 0


# ---------------------------------------------------------------- commands

def cmd_install(root, args, confirm, choose, net, fail_at=None) -> int:
    src = Path(os.path.realpath(args.source or REPO_ROOT))
    answers = None
    if args.answers:
        try:
            answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise KitError(f"--answers: no pude leer el archivo como JSON ({type(e).__name__})")
    root.mkdir(parents=True, exist_ok=True)
    log = Log(root)
    check_tracked_secrets(root)
    with session(root, "install", confirm, log) as lock:  # held through deps, fonts and service
        old = read_manifest(root)
        if not args.dry_run:
            refuse_if_running(root, "reinstalar")
        pl = compute(src, root, old, core_flag=args.core, modules=args.module, tools=args.tool, answers=answers,
                     choose=choose, release=release_sha(src))
        rc = apply(root, pl, lock, log, "install", args, confirm, fail_at)
        if rc == 0 and not args.dry_run:
            core.install_deps(root, confirm, log)
            if args.fonts:
                core.install_fonts(root, net.fetch, confirm, log)
            if (answers or {}).get("service") is True and not read_manifest(root).get("service"):
                if service.PLATFORM == "other":
                    print("El servicio siempre encendido solo existe en macOS y Windows; prendelo a mano con serve.")
                else:
                    _service_on_asked(root, args, confirm, log)
            if not safe_path(root, ".kit-personal/profile.md").is_file():
                print("Siguiente paso: abrí el proyecto en Claude Code o Codex y pedí \"hagamos el onboarding\".")
    return rc


def cmd_update(root, args, confirm, choose, net, fail_at=None) -> int:
    log = Log(root)
    with session(root, "update", confirm, log) as lock:  # held through the dependency reconcile
        old = read_manifest(root)
        if not old:
            raise KitError("no hay un kit instalado en esta carpeta; usá install.")
        refuse_if_running(root, "actualizar")
        sha = net.resolve(args.to)
        print(f"Versión pedida: {args.to or 'la última'}  ->  commit {sha}")
        cl = net.changelog(sha)
        if cl:
            print(cl)
        if args.confirm_sha:
            if args.confirm_sha != sha:
                raise KitError(f"--confirm-sha no coincide con el commit resuelto ({sha}); no hice nada.")
        elif not confirm(f"¿Confirmás instalar exactamente el commit {sha}?", sha=True):
            print("Cancelado.")
            return 1
        data = net.archive(sha)
        with tempfile.TemporaryDirectory(prefix="kit-update-") as td:
            core.safe_extract(data, Path(td))
            verify_release(Path(td), net.release_manifest(sha))
            pl = compute(Path(td), root, old, choose=choose, release=sha)
            rc = apply(root, pl, lock, log, "update", args, confirm, fail_at)
        if rc != 0 or args.dry_run:
            return rc
        # the new code needs the new lock: reconcile .kit/venv, or go back to the old code + old venv
        if core.install_deps(root, confirm, log, update=True):
            return 0
        if pl.ops:
            rb, _ = rollback_plan(root)
            apply(root, rb, lock, log, "rollback", args, lambda *a, **k: True)
        raise KitError("las dependencias de la versión nueva no se pudieron instalar; volví el kit a la "
                       "versión anterior y .kit/venv quedó como estaba (detalle en .kit/install.log).")


def cmd_uninstall(root, args, confirm, choose, net, fail_at=None) -> int:
    log = Log(root)
    with session(root, "uninstall", confirm, log) as lock:
        old = read_manifest(root)
        if not old:
            print("No hay un kit instalado acá.")
            return 0
        if old.get("service"):
            if args.dry_run:
                print(f"  - servicio siempre encendido {old['service']['label']}")
            elif confirm("¿Quito el servicio siempre encendido del Command Center?"):
                service_off(root, old, log)
                old.pop("service")
            else:
                print("Cancelado: no se cambió nada.")
                return 1
        if not args.dry_run:
            refuse_if_running(root, "desinstalar")
        rc = apply(root, uninstall_plan(root, old), lock, log, "uninstall", args, confirm, fail_at)
        if rc == 0 and not args.dry_run:
            for d in RUNTIME_DIRS + ("cc.port", "cc.service.log"):
                p = safe_path(root, f".kit/{d}")  # refuses a symlink: never deletes outside the project
                shutil.rmtree(p) if p.is_dir() else p.unlink(missing_ok=True)
            kit = safe_path(root, ".kit")
            for c in sorted(kit.rglob("__pycache__"), reverse=True) if kit.is_dir() else []:  # left by running cc
                if c.is_dir() and not c.is_symlink():
                    shutil.rmtree(c, ignore_errors=True)
            for d in sorted((x for x in kit.rglob("*") if x.is_dir()), reverse=True) if kit.is_dir() else []:
                with contextlib.suppress(OSError):
                    d.rmdir()  # only empty ones
            for d in (".agents", ".claude"):  # left empty once their kit-owned subfolders are gone
                with contextlib.suppress(OSError, KitError):
                    safe_path(root, d).rmdir()
            print("Quedan intactos: .kit-personal/ (tus datos), tu contenido fuera de los marcadores, "
                  ".kit/backup/ y .kit/install.log. La caché compartida se borra aparte con cache-clean.")
    return rc


def rollback_plan(root: Path) -> tuple[Plan | None, dict | None]:
    lp = safe_path(root, f"{core.PREV}/last.json")
    if not lp.is_file():
        return None, None
    j = json.loads(lp.read_text(encoding="utf-8"))
    base, pl, bad = f"{core.PREV}/{j['txid']}", Plan(), []
    for i in reversed(range(len(j["steps"]))):
        s = j["steps"][i]
        if sha256_file(safe_path(root, s["rel"])) != s["after"]:
            bad.append(s["rel"])
            continue
        pl.ops.append((s["rel"], safe_path(root, f"{base}/old/{i}").read_bytes() if s["before"] else None))
    if bad:
        raise core.Conflict("no puedo deshacer: estos archivos cambiaron después:\n  - " + "\n  - ".join(bad))
    return pl, j


def cmd_rollback(root, args, confirm, choose, net, fail_at=None) -> int:
    log = Log(root)
    with session(root, "rollback", confirm, log) as lock:
        if not args.dry_run:
            refuse_if_running(root, "deshacer")
        pl, j = rollback_plan(root)
        if pl is None:
            print("No hay una operación anterior para deshacer.")
            return 0
        print(f"Deshacer '{j['command']}' ({j['txid']}):")
        return apply(root, pl, lock, log, "rollback", args, confirm, fail_at)


def cmd_status(root, args, confirm, choose, net, fail_at=None) -> int:
    log = Log(root)
    try:
        ctx = session(root, "status", confirm, log)
        ctx.__enter__()
    except KitError as e:
        print(f"Estado: {e}")
        return 3 if isinstance(e, core.Conflict) else 0
    try:
        m = read_manifest(root)
        if not m:
            print("No hay un kit instalado acá.")
            return 0
        mod = [r for r, h in m["files"].items() if sha256_file(safe_path(root, r)) != h]
        print(f"Kit {m['kit_version']} (commit {m['release']}), herramientas: {', '.join(m['tools'])}")
        print(f"Skills: {', '.join(m['skills']) or '-'}")
        if m.get("unavailable"):
            print(f"No disponibles (archivos tuyos en su lugar): {', '.join(m['unavailable'])}")
        print(f"Archivos del kit: {len(m['files'])}, modificados por vos: {len(mod)}")
        for r in mod[:20]:
            print(f"  ~ {r}")
        if cc_running(root):
            print("El Command Center está corriendo.")
        if m.get("service"):
            print(f"Servicio siempre encendido: {service.status(m['service'])}")
        return 0
    finally:
        ctx.__exit__(None, None, None)


def _service_on_asked(root, args, confirm, log) -> int:
    """`service on` body; the caller holds the lifecycle lock."""
    refuse_if_running(root, "dejarlo como servicio (ya corre a mano)")
    where = "~/Library/LaunchAgents" if service.PLATFORM == "mac" else "el Programador de tareas"
    if args.dry_run or not confirm(f"¿Dejo el Command Center siempre encendido? (se registra en {where}, "
                                   "arranca al iniciar sesión, se reinicia si se cae y se quita al desinstalar)"):
        print("No instalé el servicio.")
        return 0
    rec = service_on(root, log)
    print(f"Listo: servicio {rec['label']}. Pedí el enlace con `python .kit/launch.py open --browser`.")
    return 0


def cmd_service(root, args, confirm, choose, net, fail_at=None, action=None) -> int:
    action = action or args.action or "status"
    log = Log(root)
    with session(root, "service", confirm, log):
        m = read_manifest(root)
        if not m:
            raise KitError("no hay un kit instalado en esta carpeta; usá install.")
        rec = m.get("service")
        if action == "status":
            print(f"Servicio siempre encendido: {service.status(rec) if rec else 'apagado (no instalado)'}")
            return 0
        if action == "off":
            if rec:
                service_off(root, m, log)
            print("Servicio quitado: el Command Center ya no arranca solo.")
            return 0
        if rec:
            print(f"Ya está instalado ({service.status(rec)}).")
            return 0
        return _service_on_asked(root, args, confirm, log)


def cmd_cache_clean(root, args, confirm, choose, net, fail_at=None) -> int:
    core.cache_clean(confirm)
    return 0


def cmd_migrate_brands(root, args, confirm, choose, net, fail_at=None) -> int:
    log = Log(root)
    with session(root, "migrate-brands", confirm, log):
        d = safe_path(root, ".kit-personal/brands")
        files = sorted(p for p in d.glob("*.json") if p.is_file() and not p.is_symlink()) if d.is_dir() else []
        changes = []
        for p in files:
            try:
                b = json.loads(p.read_text(encoding="utf-8"))
            except ValueError:
                print(f"  ! {p.name}: JSON inválido, lo salteo")
                continue
            if not isinstance(b, dict):
                continue
            if not isinstance(b.get("voice"), dict) or "logo_text" not in b or "tone" in b:
                shown = str(b.get("display_name") or b.get("name") or p.stem)
                new = ow.brand_doc({"name": p.stem, "display_name": shown, "kind": b.get("kind", "brand"),
                                    "task_prefix": b.get("task_prefix"), "tone": str(b.get("tone") or ""),
                                    "colors": b.get("colors") if isinstance(b.get("colors"), dict) else {},
                                    "fonts": b.get("fonts") if isinstance(b.get("fonts"), dict) else {}}, b)
            else:
                new = dict(b)
            new["schema_version"] = 1
            if new != b:
                changes.append((p, new))
        if not changes:
            print("Las marcas ya están en el formato actual.")
            return 0
        for p, _ in changes:
            print(f"  ~ .kit-personal/brands/{p.name}")
        if args.dry_run or not confirm("¿Actualizo el formato de estas marcas (con copia previa)?"):
            return 0
        bdir = safe_path(root, f".kit-personal/brands/.backup-{time.strftime('%Y%m%d-%H%M%S')}")
        bdir.mkdir(parents=True, exist_ok=True)
        for p, new in changes:
            shutil.copy2(p, bdir / p.name)
            core.atomic_write(p, (json.dumps(new, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode())
            log("migrate-brand", f".kit-personal/brands/{p.name}")
        return 0


COMMANDS = {"install": cmd_install, "update": cmd_update, "uninstall": cmd_uninstall, "status": cmd_status,
            "rollback": cmd_rollback, "service": cmd_service, "cache-clean": cmd_cache_clean, "migrate-brands": cmd_migrate_brands}


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="install", description="Instalador por proyecto del kit de contenido.")
    ap.add_argument("command", choices=[*COMMANDS, "release-manifest"])
    ap.add_argument("action", nargs="?", choices=("on", "off", "status"), help="service: on, off o status")
    ap.add_argument("--target", default=".", help="carpeta del proyecto (por defecto, la actual)")
    ap.add_argument("--yes", action="store_true", help="aceptar las confirmaciones (no el commit de un update)")
    ap.add_argument("--dry-run", action="store_true", help="mostrar los cambios sin aplicarlos")
    ap.add_argument("--answers", help="respuestas de onboarding (JSON) para una instalación sin preguntas")
    ap.add_argument("--core", action="store_true", help="instalar el núcleo (por defecto en la primera instalación)")
    ap.add_argument("--module", action="append", default=[], help="sumar un módulo probado (repetible)")
    ap.add_argument("--tool", action="append", choices=list(TOOL_DIRS), help="claude y/o codex (por defecto ambos)")
    ap.add_argument("--fonts", action="store_true", help="descargar las tipografías libres fijadas")
    ap.add_argument("--to", help="update: etiqueta o commit de destino (por defecto la última versión)")
    ap.add_argument("--confirm-sha", help="update sin preguntas: el commit exacto que aprobás")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--keep-mine", action="store_true", help="update: conservar tus archivos modificados")
    g.add_argument("--take-new", action="store_true", help="update: tomar los nuevos (con copia de los tuyos)")
    ap.add_argument("--clear-stale-lock", action="store_true", help="borrar un candado de un proceso muerto")
    ap.add_argument("--source", help=argparse.SUPPRESS)
    return ap


def main(argv: list[str] | None = None, *, net=None, confirm=None, fail_at: int | None = None) -> int:
    with contextlib.suppress(Exception):
        sys.stdout.reconfigure(errors="replace")
    args = parser().parse_args(argv)
    if args.command == "release-manifest":
        print(json.dumps(build_release_manifest(Path(args.source or REPO_ROOT)), indent=1, sort_keys=True))
        return 0
    interactive = sys.stdin.isatty()

    def ask(msg: str) -> bool:
        if not interactive:
            print(f"{msg} -> no (sin terminal interactiva)")
            return False
        return input(f"{msg} [s/N] ").strip().lower() in ("s", "si", "sí", "y", "yes")

    def default_confirm(msg: str, stale_lock: bool = False, sha: bool = False) -> bool:
        if stale_lock:
            return args.clear_stale_lock or ask(msg)
        if sha:  # the release commit is never auto-approved by --yes
            return ask(msg)
        return args.yes or ask(msg)

    def choose(rel: str) -> str:
        if args.take_new:
            return "take"
        if args.keep_mine or args.yes or not interactive:
            return "keep"
        a = input(f"{rel} tiene cambios tuyos. [c]onservar el mío / [t]omar el nuevo (guardo copia del tuyo): ")
        return "take" if a.strip().lower().startswith("t") else "keep"

    if net is None:
        from .net import GitHubRelease
        net = GitHubRelease()
    root = Path(os.path.realpath(args.target))
    log = Log(root) if root.is_dir() else None
    try:
        return COMMANDS[args.command](root, args, confirm or default_confirm, choose, net, fail_at)
    except KitError as e:
        if log:
            log(args.command, "", "error", e)
        print(f"Error: {core.scrub(str(e))}", file=sys.stderr)
        return 3 if isinstance(e, core.Conflict) else 2
    except (urllib.error.URLError, http.client.HTTPException, TimeoutError, ConnectionError) as e:
        if log:  # URLError and friends are OSErrors: catch them first, they are not a disk problem
            log(args.command, "", "error", e)
        print(f"Error de red: no pude conectarme para descargar ({core.scrub(str(e))}). Revisá tu conexión "
              "a internet y volvé a intentar; no cambié nada.", file=sys.stderr)
        return 4
    except OSError as e:
        if log:
            log(args.command, "", "error", e)
        print(f"Error del sistema de archivos: {core.scrub(str(e))} (detalle en .kit/install.log)", file=sys.stderr)
        return 2
