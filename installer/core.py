# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Lock, journaled transactions, JSON-lines log, safe archive extraction, shared caches, deps."""
from __future__ import annotations

import io
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tarfile
import time
import uuid
from pathlib import Path

from . import ow  # engines/onboard_write.py: shared file primitives

KitError, safe_path, sha256_bytes, sha256_file = ow.KitError, ow.safe_path, ow.sha256_bytes, ow.sha256_file
atomic_write, make_parents, proc_start = ow.atomic_write, ow.make_parents, ow.proc_start

LOCK, JOURNAL, PREV = ".kit.lock", ".kit-journal.json", ".kit-prev"
KIT_ROOTS = (".kit", ".claude/skills", ".agents/skills", ".claude/agents")
LIMITS = {"files": 10_000, "total": 500 * 2**20, "ratio": 100}


class Conflict(KitError):
    pass


class LockLost(KitError):
    pass


class SimulatedCrash(BaseException):
    """Test hook: stops a transaction mid-way without any cleanup."""


# ---------------------------------------------------------------- log

class Log:
    """`.kit/install.log`: JSON lines, kit-relative paths, scrubbed messages."""

    def __init__(self, root: Path):
        self.root = root

    def __call__(self, action: str, path: str = "", status: str = "ok", error: BaseException | None = None,
                 message: str | None = None) -> None:
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "action": action, "path": path, "status": status}
        if error is not None:
            rec["error_class"] = type(error).__name__
            message = str(error)
        if message:
            rec["message"] = scrub(message)
        try:
            p = make_parents(self.root, ".kit/install.log")
            with open(p, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except (OSError, KitError):
            pass


def scrub(msg: str) -> str:
    home = str(Path.home())
    return ow.redact(msg.replace(home, "~") if home and home != "/" else msg)


# ---------------------------------------------------------------- lock

class Lock:
    def __init__(self, root: Path, command: str, confirm, log: Log):
        self.root, self.command, self.confirm, self.log = root, command, confirm, log
        self.nonce: str | None = None

    @property
    def path(self) -> Path:
        return safe_path(self.root, LOCK)

    def read(self) -> dict | None:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None
        except (ValueError, OSError):
            return {}

    @staticmethod
    def is_stale(old: dict) -> bool:
        """Stale only if same host and no live process with that pid AND start time."""
        if not old or old.get("host") != socket.gethostname() or not isinstance(old.get("pid"), int):
            return False
        return proc_start(old["pid"]) != old.get("start")

    def acquire(self) -> None:
        for _ in range(2):
            try:
                self.nonce = ow.create_lock(self.root, self.command)["nonce"]
                return
            except FileExistsError:
                old = self.read()
                if old is None:
                    continue
                if not self.is_stale(old):
                    who = f"pid {old.get('pid')}, '{old.get('command')}'" if old else "contenido ilegible"
                    raise KitError(f"otro comando del kit tiene el candado .kit.lock ({who}). "
                                   f"Esperá a que termine. Si estás seguro de que no corre nada, borrá .kit.lock a mano.")
                if not self.confirm(f"Candado viejo de un proceso que ya no existe (pid {old.get('pid')}, "
                                    f"'{old.get('command')}'). ¿Lo borro y reviso si quedó algo a medias?",
                                    stale_lock=True):
                    raise KitError("candado viejo sin borrar; no hice nada.")
                self.log("lock-clear-stale", LOCK, message=json.dumps(old, sort_keys=True))
                self.path.unlink()
        raise KitError("no pude tomar el candado .kit.lock")

    def check(self) -> None:
        cur = self.read()
        if not cur or cur.get("nonce") != self.nonce:
            raise LockLost("perdí el candado .kit.lock (otro proceso lo tomó); me detengo sin confirmar cambios.")

    def release(self) -> None:
        cur = self.read()
        if cur and cur.get("nonce") == self.nonce:
            self.path.unlink()


# ---------------------------------------------------------------- transactions

def _write_journal(root: Path, j: dict) -> None:
    atomic_write(safe_path(root, JOURNAL), json.dumps(j, indent=1, sort_keys=True).encode("utf-8"))


def _prune(root: Path, rel: str) -> None:
    """Remove empty parent dirs of rel, only inside kit-owned roots."""
    parts = rel.split("/")[:-1]
    while parts:
        d = "/".join(parts)
        if not any(d == k or d.startswith(k + "/") for k in KIT_ROOTS):
            return
        p = safe_path(root, d)
        try:
            p.rmdir()
        except OSError:
            return
        parts.pop()


class Tx:
    """Journaled rename-into-place. Crash-recoverable, not atomic.

    ops: list of (rel, bytes) to write or (rel, None) to delete. Before anything
    moves, new content is staged under .kit-prev/<txid>/stage and the journal
    (.kit-journal.json at the root) records before/after hashes per step.
    """

    def __init__(self, root: Path, lock: Lock, log: Log, command: str):
        self.root, self.lock, self.log, self.command = root, lock, log, command
        self.txid = f"{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"

    def run(self, ops: list[tuple[str, bytes | None]], fail_at: int | None = None) -> None:
        root, base = self.root, f"{PREV}/{self.txid}"
        steps = []
        for i, (rel, data) in enumerate(ops):
            before = sha256_file(safe_path(root, rel))
            if before and before.startswith("!"):
                raise KitError(f"{rel}: no es un archivo común; no lo toco")
            if data is not None:
                atomic_write(make_parents(root, f"{base}/stage/{i}"), data)
            steps.append({"rel": rel, "before": before,
                          "after": sha256_bytes(data) if data is not None else None, "done": False})
        j = {"txid": self.txid, "command": self.command, "state": "applying", "steps": steps}
        _write_journal(root, j)
        for i, s in enumerate(steps):
            if fail_at is not None and i == fail_at:
                raise SimulatedCrash(i)
            self.lock.check()
            p = safe_path(root, s["rel"])
            if s["before"] is not None:
                os.replace(p, make_parents(root, f"{base}/old/{i}"))
            if s["after"] is not None:
                make_parents(root, s["rel"])
                os.replace(safe_path(root, f"{base}/stage/{i}"), safe_path(root, s["rel"]))
            else:
                _prune(root, s["rel"])
            s["done"] = True
            _write_journal(root, j)
            self.log("delete" if s["after"] is None else "write", s["rel"])
        self.lock.check()
        j["state"] = "committed"
        _write_journal(root, j)
        finish(root, j)
        self.log(self.command, "", "committed", message=f"tx {self.txid}, {len(steps)} cambios")


def finish(root: Path, j: dict) -> None:
    """Post-commit cleanup: keep the last tx's old/ files for `rollback`, drop the rest."""
    prev = safe_path(root, PREV)
    if j["command"] == "uninstall":
        shutil.rmtree(prev, ignore_errors=True)
    else:
        shutil.rmtree(prev / j["txid"] / "stage", ignore_errors=True)
        for d in prev.iterdir() if prev.is_dir() else []:
            if d.is_dir() and d.name != j["txid"]:
                shutil.rmtree(d, ignore_errors=True)
        atomic_write(make_parents(root, f"{PREV}/last.json"), json.dumps(j, sort_keys=True).encode("utf-8"))
    safe_path(root, JOURNAL).unlink(missing_ok=True)


def recover(root: Path, log: Log) -> bool:
    """Roll back an unfinished transaction. Returns True if one was found.

    Never overwrites or deletes a file whose hash matches neither the recorded
    before- nor after-hash; if any exist, nothing is changed and Conflict lists them.
    """
    jp = safe_path(root, JOURNAL)
    if not jp.exists():
        return False
    try:
        j = json.loads(jp.read_text(encoding="utf-8"))
    except ValueError:
        raise KitError(".kit-journal.json ilegible; revisalo a mano antes de seguir.")
    if j.get("state") == "committed":
        finish(root, j)
        return True
    base = f"{PREV}/{j['txid']}"
    actions, conflicts = [], []
    for i in reversed(range(len(j["steps"]))):
        s = j["steps"][i]
        p = safe_path(root, s["rel"])
        cur, old = sha256_file(p), safe_path(root, f"{base}/old/{i}")
        if old.exists() and sha256_file(old) != s["before"]:
            conflicts.append(f"{s['rel']} (la copia de respaldo no coincide)")
        elif s["after"] is not None and cur == s["after"]:
            actions.append((i, s, True))
        elif cur is None and old.exists():
            actions.append((i, s, False))
        elif cur != s["before"]:
            conflicts.append(s["rel"])
    if conflicts:
        log("recover", "", "conflict", message=f"{len(conflicts)} archivo(s) cambiados después del corte")
        raise Conflict("quedó una operación a medias y estos archivos cambiaron después del corte; "
                       "no los toco:\n  - " + "\n  - ".join(conflicts) +
                       "\nMovelos a otro lado (o devolvelos a como estaban) y volvé a correr el comando.")
    for i, s, remove_new in actions:
        p = safe_path(root, s["rel"])
        if remove_new:
            p.unlink()
        old = safe_path(root, f"{base}/old/{i}")
        if old.exists():
            os.replace(old, make_parents(root, s["rel"]))
        elif remove_new:
            _prune(root, s["rel"])
        log("recover-restore", s["rel"])
    shutil.rmtree(safe_path(root, base), ignore_errors=True)
    jp.unlink()
    log("recover", "", "rolled-back", message=f"tx {j['txid']}")
    return True


# ---------------------------------------------------------------- safe extraction

def safe_extract(archive: bytes, out: Path, strip: int = 1, limits: dict = LIMITS) -> None:
    """Extract a tar(.gz) with no links, devices, absolute/drive paths or '..', within size limits."""
    out = Path(os.path.realpath(out))
    total, count, cap = 0, 0, min(limits["total"], limits["ratio"] * max(len(archive), 1))
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:*") as tf:
        for m in tf:
            count += 1
            if count > limits["files"]:
                raise KitError("archivo rechazado: demasiadas entradas")
            raw = m.name.replace("\\", "/")
            if raw.startswith("/") or (len(raw) > 1 and raw[1] == ":") or ".." in raw.split("/"):
                raise KitError(f"archivo rechazado: ruta insegura {m.name!r}")
            if not (m.isreg() or m.isdir()):
                raise KitError(f"archivo rechazado: {m.name!r} es un enlace o dispositivo")
            rel = "/".join(p for p in raw.split("/")[strip:] if p)
            if not rel:
                continue
            ow.check_rel(rel)
            if m.isdir():
                make_parents(out, rel + "/.d")
                continue
            total += m.size
            if total > cap:
                raise KitError("archivo rechazado: tamaño descomprimido fuera de límite")
            src = tf.extractfile(m)
            data = src.read(m.size + 1) if src else b""
            if len(data) != m.size:
                raise KitError(f"archivo rechazado: tamaño inconsistente en {m.name!r}")
            p = make_parents(out, rel)
            with open(p, "wb") as fh:
                fh.write(data)
            safe_path(out, rel)  # containment re-check after writing


# ---------------------------------------------------------------- shared heavy cache (fix 6)

def cache_root() -> Path:
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "content-kit"
    return Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "content-kit"


def cached_fetch(key: str, name: str, url: str, sha256: str, size_mb: int, fetch, confirm) -> Path | None:
    """SHA-256-verified download into the shared cache, reused across projects. None if declined."""
    ow.check_rel(key)
    ow.check_rel(name)
    p = cache_root() / key / sha256[:16] / name
    if p.is_file() and sha256_file(p) == sha256:
        return p
    if not confirm(f"Descargar {name} (~{size_mb} MB) a la caché compartida {scrub(str(p.parent))}? "
                   f"Se reutiliza entre proyectos y no se borra al desinstalar (usá cache-clean)."):
        return None
    data = fetch(url, (size_mb + 50) * 2**20)
    if sha256_bytes(data) != sha256:
        raise KitError(f"{name}: el hash no coincide con el fijado; descarga descartada")
    p.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(p, data)
    return p


def cache_clean(confirm) -> bool:
    c = cache_root()
    if not c.exists():
        print("La caché compartida está vacía.")
        return False
    if not confirm(f"Borrar la caché compartida {scrub(str(c))} (modelos y navegadores de todos los proyectos)?"):
        return False
    shutil.rmtree(c)
    return True


# ---------------------------------------------------------------- fonts and deps

FONTS_LOCK = ".kit/presets/captions/fonts.lock.json"


def install_fonts(root: Path, fetch, confirm, log: Log) -> None:
    lockf = safe_path(root, FONTS_LOCK)
    if not lockf.is_file():
        print(f"Sin {FONTS_LOCK}: se usan tipografías del sistema.")
        return
    fonts = [f for f in json.loads(lockf.read_text(encoding="utf-8")).get("fonts", [])
             if re.fullmatch(r"[0-9a-f]{64}", str(f.get("sha256", "")))]  # TODO entries are skipped
    if not fonts or not confirm(f"Descargar {len(fonts)} tipografías libres (OFL) con hash fijado a .kit/fonts/?"):
        return
    for f in fonts:
        if "/" in f["file"] or "\\" in f["file"]:
            raise KitError(f"nombre de tipografía inválido: {f['file']!r}")
        rel = f".kit/fonts/{ow.check_rel(f['file'])}"
        p = safe_path(root, rel)
        if sha256_file(p) == f["sha256"]:
            continue
        data = fetch(f["url"], 30 * 2**20)
        if sha256_bytes(data) != f["sha256"]:
            raise KitError(f"{f['file']}: el hash no coincide; descarga descartada")
        atomic_write(make_parents(root, rel), data)
        log("font", rel)
    d = safe_path(root, ".kit/fonts")
    conf = (f'<?xml version="1.0"?>\n<!DOCTYPE fontconfig SYSTEM "fonts.dtd">\n<fontconfig>\n'
            f"  <dir>{d.as_posix()}</dir>\n  <cachedir>{d.as_posix()}/.cache</cachedir>\n</fontconfig>\n")
    atomic_write(make_parents(root, ".kit/fonts/fonts.conf"), conf.encode("utf-8"))


VENV, VENV_OLD, STAMP = ".kit/venv", ".kit/venv.old", ".kit/venv/.kit-req.sha256"


def _rmtree_inside(root: Path, rel: str) -> None:
    p = safe_path(root, rel)  # refuses a symlink anywhere on the way: never deletes outside the project
    if p.is_dir():
        shutil.rmtree(p)


def _build_venv(root: Path, req: Path, log: Log) -> bool:
    """Fresh .kit/venv from the hash-pinned lock. The previous one waits in .kit/venv.old and comes
    back if anything fails, so a failed install never leaves a half-updated environment."""
    venv = safe_path(root, VENV)
    _rmtree_inside(root, VENV_OLD)
    had = venv.exists()
    if had:
        os.replace(venv, safe_path(root, VENV_OLD))
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        bindir = safe_path(root, f"{VENV}/{'Scripts' if os.name == 'nt' else 'bin'}")
        vpy = bindir / ("python.exe" if os.name == "nt" else "python")  # a link to the base Python: expected
        subprocess.run([str(vpy), "-m", "pip", "install", "--require-hashes", "--no-deps", "-r", str(req)],
                       check=True)
        atomic_write(safe_path(root, STAMP), (sha256_file(req) + "\n").encode("utf-8"))
    except (OSError, subprocess.CalledProcessError, KitError) as e:
        log("deps-python", VENV, "error", e)
        with_err = None
        try:
            _rmtree_inside(root, VENV)
            if had:
                os.replace(safe_path(root, VENV_OLD), safe_path(root, VENV))
        except (OSError, KitError) as e2:
            with_err = e2
            log("deps-python-restore", VENV, "error", e2)
        print("No pude instalar las dependencias de Python (ver .kit/install.log)."
              + (" Dejé .kit/venv como estaba." if had and not with_err else ""))
        return False
    _rmtree_inside(root, VENV_OLD)
    log("deps-python", VENV)
    return True


def install_deps(root: Path, confirm, log: Log, *, update: bool = False) -> bool:
    """Per-project deps. A missing lock or tool gives a clear message, never a crash.

    Every path is checked with safe_path before anything runs or is written, so a .kit/venv (or
    .kit/node_modules) that is a symlink to somewhere else is refused, not executed or modified.
    update=True: reconcile an existing .kit/venv with the (new) lock; returns False if that failed
    or was declined, so the caller can put the previous code back.
    """
    kit = safe_path(root, ".kit")
    req = safe_path(root, ".kit/requirements.lock")
    ok = True
    if not req.is_file():
        print("Sin .kit/requirements.lock: no se instalan dependencias de Python (los motores que las "
              "necesiten lo avisan al usarse).")
    else:
        venv, stamp = safe_path(root, VENV), safe_path(root, STAMP)
        current = stamp.is_file() and stamp.read_text(encoding="utf-8").strip() == sha256_file(req)
        if current:
            pass  # already installed from this exact lock
        elif update and not venv.exists():
            pass  # never installed here: nothing to reconcile
        elif confirm("Crear .kit/venv e instalar dependencias de Python con hashes fijados?"
                     if not venv.exists() else
                     "Las dependencias cambiaron: ¿rehago .kit/venv con las nuevas (hashes fijados)?"):
            ok = _build_venv(root, req, log)
            if not ok and not update:
                print("El resto del kit funciona.")
        else:
            ok = not update
    if (kit / "package-lock.json").is_file():
        safe_path(root, ".kit/node_modules")  # a symlinked node_modules is refused before npm writes into it
        npm = shutil.which("npm")
        if not npm:
            print("Node/npm no está instalado: las skills que usan Node quedan sin usar hasta instalarlo "
                  "(Node 18+). El resto funciona.")
        elif confirm("Instalar dependencias de Node en .kit (npm ci --ignore-scripts)?"):
            try:
                subprocess.run([npm, "ci", "--ignore-scripts", "--prefix", str(kit)], check=True)
                log("deps-node", ".kit/node_modules")
            except (OSError, subprocess.CalledProcessError) as e:
                log("deps-node", ".kit/node_modules", "error", e)
                print("npm ci falló (ver .kit/install.log). El resto del kit funciona.")
    return ok
