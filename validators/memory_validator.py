from __future__ import annotations


def validate_memory(user: dict) -> list[str]:
    mem = user.get("user_memory", {})
    errors: list[str] = []

    for field in ["weak_topics", "strong_topics", "mistakes"]:
        if not isinstance(mem.get(field, []), list):
            errors.append(f"memory field {field} not list")

    weak = set(mem.get("weak_topics", []))
    strong = set(mem.get("strong_topics", []))
    if weak.intersection(strong):
        errors.append("same topic in weak and strong")

    for mistake in mem.get("mistakes", []):
        if not isinstance(mistake, dict) or "skill" not in mistake:
            errors.append("corrupted mistake entry")
            break

    return errors
