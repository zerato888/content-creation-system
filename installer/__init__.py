# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Per-project installer for the content kit. Stdlib only, Python 3.11+.

Run through install.sh / install.ps1, or `python -m installer <command>`.
"""
import importlib.util
import sys
from pathlib import Path

if sys.version_info < (3, 11):
    raise SystemExit("El kit necesita Python 3.11 o más nuevo.")

# engines/onboard_write.py holds the file primitives shared with onboarding (it must
# also run on its own from .kit/engines). Loaded by path so engines/ never enters sys.path.
_p = Path(__file__).resolve().parents[1] / "engines" / "onboard_write.py"
_spec = importlib.util.spec_from_file_location("installer.ow", _p)
ow = importlib.util.module_from_spec(_spec)
sys.modules["installer.ow"] = ow
_spec.loader.exec_module(ow)
