from __future__ import annotations

from models.constants import LESSONS


def validate_progression_state(user: dict) -> list[str]:
    errors: list[str] = []
    completed = user.get("completed_lessons", [])

    if user.get("active_lesson") is not None and user.get("active_lesson") not in LESSONS:
        errors.append("active_lesson invalid")

    if len(completed) != len(set(completed)):
        errors.append("duplicate lesson completion")

    if any(lesson not in LESSONS for lesson in completed):
        errors.append("roadmap contains unknown lesson")

    if user.get("xp", -1) < 0:
        errors.append("negative xp")

    if user.get("streak", -1) < 0:
        errors.append("negative streak")

    if not isinstance(user.get("achievements", []), list):
        errors.append("achievements not list")

    return errors
