from datetime import datetime, timezone


def get_rank(xp: int) -> str:
    if xp < 50:
        return "🌱 Beginner"
    if xp < 150:
        return "⚡ Junior PM"
    if xp < 300:
        return "🔥 Strong PM"
    return "🚀 Product Master"


def progress_bar(percent: int) -> str:
    filled = int(percent / 20)
    return "🟩" * filled + "⬜" * (5 - filled)


def update_streak(user: dict) -> None:
    today = datetime.now(timezone.utc).date().isoformat()
    last = user.get("last_activity_date")
    streak = user.get("streak", 0)
    if last == today:
        return
    if last:
        prev = datetime.fromisoformat(last).date()
        delta = (datetime.now(timezone.utc).date() - prev).days
        user["streak"] = streak + 1 if delta == 1 else 1
    else:
        user["streak"] = 1
    user["last_activity_date"] = today
