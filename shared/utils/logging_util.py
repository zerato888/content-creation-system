"""Minimal structured logging to stderr — no external deps, no config."""
import sys


def log(event: str, **fields) -> None:
    """Print `event key=value key=value...` to stderr."""
    parts = [event] + [f"{k}={v}" for k, v in fields.items()]
    print(" ".join(parts), file=sys.stderr)


def demo():
    log("skill.start", skill="content-carousel", route="educational")
    log("skill.error", skill="content-carousel", missing_key="MAGNIFIC_KEY")
    print("logging_util: demo ran (visually inspect stderr output above)")


if __name__ == "__main__":
    demo()
