from ai.memory import ensure_user_memory
from analytics.tracker import ensure_analytics


def ensure_user_state(user: dict) -> dict:
    defaults = {
        "name": "Игрок",
        "goal": "Стать Product Manager",
        "track": "General PM",
        "difficulty": "junior",
        "learning_style": "Теория + практика",
        "daily_time": "30 минут",
        "active_lesson": "jtbd",
        "completed_lessons": [],
        "xp": 0,
        "tasks_done": 0,
        "lesson_step": 0,
        "waiting_for_answer": False,
        "weak_topics": [],
        "strengths": [],
        "answer_analytics": [],
        "lesson_started": False,
        "lesson_finished": False,
        "current_lesson_data": None,
        "current_block": "Не начат",
        "streak": 0,
        "daily_quests": {"lesson": False, "practice_cases": 0, "xp_today": 0},
        "achievements": [],
    }
    for k, v in defaults.items():
        user.setdefault(k, v)
    ensure_user_memory(user)
    ensure_analytics(user)
    return user
