#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Read a named secret at call time: OS credential store first, then the environment.

  macOS    Keychain generic password, service "content-kit", account = NAME
           add one:  security add-generic-password -s content-kit -a OPENAI_API_KEY -w
  Windows  Credential Manager generic credential, target "content-kit:NAME"
           add one:  cmdkey /generic:content-kit:OPENAI_API_KEY /user:kit /pass
  else     environment variable NAME

Values are never printed, logged or written. The CLI only says whether a secret
exists and where it came from:
  python .kit/engines/kit_secrets.py check OPENAI_API_KEY
Engines call get_secret(NAME). Load this file by path (importlib) or append
.kit/engines to sys.path; never prepend it, or it shadows the stdlib `secrets`.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

SERVICE = "content-kit"
_NAME = re.compile(r"^[A-Z][A-Z0-9_]{1,63}$")


def _keychain(name: str) -> str | None:
    try:
        r = subprocess.run(["security", "find-generic-password", "-s", SERVICE, "-a", name, "-w"],
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.rstrip("\n") or None if r.returncode == 0 else None


def _wincred(name: str) -> str | None:
    import ctypes
    from ctypes import wintypes

    class CREDENTIAL(ctypes.Structure):
        _fields_ = [("Flags", wintypes.DWORD), ("Type", wintypes.DWORD), ("TargetName", wintypes.LPWSTR),
                    ("Comment", wintypes.LPWSTR), ("LastWritten", wintypes.FILETIME),
                    ("CredentialBlobSize", wintypes.DWORD), ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
                    ("Persist", wintypes.DWORD), ("AttributeCount", wintypes.DWORD),
                    ("Attributes", ctypes.c_void_p), ("TargetAlias", wintypes.LPWSTR),
                    ("UserName", wintypes.LPWSTR)]

    adv = ctypes.WinDLL("advapi32", use_last_error=True)
    adv.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                              ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
    pcred = ctypes.POINTER(CREDENTIAL)()
    if not adv.CredReadW(f"{SERVICE}:{name}", 1, 0, ctypes.byref(pcred)):  # CRED_TYPE_GENERIC
        return None
    try:
        c = pcred.contents
        raw = ctypes.string_at(c.CredentialBlob, c.CredentialBlobSize)
    finally:
        adv.CredFree(pcred)
    # cmdkey stores UTF-16LE; other tools may store UTF-8.
    try:
        val = raw.decode("utf-16-le") if len(raw) % 2 == 0 and b"\x00" in raw else raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return val or None


def lookup(name: str) -> tuple[str | None, str]:
    """(value, source). source is 'keychain', 'credential-manager', 'env' or 'missing'."""
    if not _NAME.match(name):
        raise ValueError("secret names are UPPER_SNAKE_CASE, e.g. OPENAI_API_KEY")
    if sys.platform == "darwin":
        v = _keychain(name)
        if v:
            return v, "keychain"
    elif os.name == "nt":
        v = _wincred(name)
        if v:
            return v, "credential-manager"
    v = os.environ.get(name)
    return (v, "env") if v else (None, "missing")


def get_secret(name: str) -> str | None:
    return lookup(name)[0]


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2 or argv[0] != "check":
        print("usage: kit_secrets.py check NAME", file=sys.stderr)
        return 2
    try:
        _, src = lookup(argv[1])
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    print(f"{argv[1]}: {'found (' + src + ')' if src != 'missing' else 'missing'}")
    return 0 if src != "missing" else 1


if __name__ == "__main__":
    sys.exit(main())
