"""Reads .env-style files without external deps and reports on required keys."""
from pathlib import Path


def _parse_env(env_path: str) -> dict:
    path = Path(env_path)
    if not path.exists():
        return {}
    pairs = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs[key.strip()] = value.strip().strip('"').strip("'")
    return pairs


def get_key(name: str, env_path: str = ".env") -> str | None:
    """Return the value of `name` from `env_path`, or None if absent/empty."""
    return _parse_env(env_path).get(name) or None


def check_keys(required: list[str], env_path: str = ".env") -> dict:
    """Check which of `required` keys are present (non-empty) in `env_path`.

    Returns {"missing": [...], "present": [...]}.
    """
    values = _parse_env(env_path)
    missing = [k for k in required if not values.get(k)]
    present = [k for k in required if values.get(k)]
    return {"missing": missing, "present": present}


def demo():
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("FOO=bar\nBAZ=\n# comment\nQUX=  quoted value  \n")
        path = f.name

    assert get_key("FOO", path) == "bar"
    assert get_key("BAZ", path) is None
    assert get_key("MISSING", path) is None
    assert get_key("QUX", path) == "quoted value"

    result = check_keys(["FOO", "BAZ", "MISSING"], path)
    assert result == {"missing": ["BAZ", "MISSING"], "present": ["FOO"]}

    Path(path).unlink()
    print("key_manager: all checks passed")


if __name__ == "__main__":
    demo()
