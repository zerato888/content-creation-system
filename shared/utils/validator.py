"""Shared validation primitives every skill script uses for loud, actionable failures."""


class ValidationError(Exception):
    """Raised when a skill's precondition isn't met. Message must be actionable."""


def require(condition: bool, message: str) -> None:
    """Raise ValidationError(message) if condition is falsy."""
    if not condition:
        raise ValidationError(message)


def require_keys(check_result: dict, skill_name: str, env_example_path: str) -> None:
    """Raise ValidationError with a copy-pasteable fix if any keys are missing.

    `check_result` is the dict returned by key_manager.check_keys().
    """
    missing = check_result.get("missing", [])
    if missing:
        keys_list = ", ".join(missing)
        raise ValidationError(
            f"[{skill_name}] Missing required key(s): {keys_list}. "
            f"Add them to .env (see {env_example_path} for the full list), "
            f"then re-run this skill."
        )


def demo():
    require(True, "unused")
    try:
        require(False, "expected failure message")
        raise AssertionError("should have raised")
    except ValidationError as e:
        assert str(e) == "expected failure message"

    try:
        require_keys({"missing": ["MAGNIFIC_KEY"], "present": []}, "content-carousel", ".env.example")
        raise AssertionError("should have raised")
    except ValidationError as e:
        assert "MAGNIFIC_KEY" in str(e)
        assert "content-carousel" in str(e)

    require_keys({"missing": [], "present": ["MAGNIFIC_KEY"]}, "content-carousel", ".env.example")

    print("validator: all checks passed")


if __name__ == "__main__":
    demo()
