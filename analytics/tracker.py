def ensure_analytics(user: dict) -> None:
    user.setdefault("analytics", {
        "retention_visits": 0,
        "completed_lessons": 0,
        "xp_gain_total": 0,
        "hardest_topics": {},
        "streak_best": 0,
        "practice_performance": [],
    })


def track_visit(user: dict) -> None:
    ensure_analytics(user)
    user["analytics"]["retention_visits"] += 1


def track_practice(user: dict, skill: str, success: bool) -> None:
    ensure_analytics(user)
    user["analytics"]["practice_performance"].append({"skill": skill, "success": success})
    if not success and skill:
        hard = user["analytics"]["hardest_topics"]
        hard[skill] = hard.get(skill, 0) + 1
