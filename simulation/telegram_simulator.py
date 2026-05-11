from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from ai.memory import remember_feedback
from gamification.progression import update_streak
from services.lesson_engine import continue_lesson, process_answer, show_summary
from services.state_initializer import ensure_user_state

TEST_LESSON = {
    "title": "JTBD Basics",
    "blocks": [
        {"type": "intro", "text": "Welcome"},
        {"type": "theory", "text": "Theory"},
        {"type": "quiz", "question": "What is JTBD?", "keywords": ["context", "progress"], "success_text": "Good", "fail_text": "Bad", "skill": "jtbd"},
        {"type": "practice", "task": "Describe user case", "keywords": ["outcome", "motivation"], "success_text": "Great", "fail_text": "Improve", "skill": "case_thinking"},
        {"type": "summary", "text": "Done"},
    ],
}


@dataclass
class SimProfile:
    name: str
    difficulty: str
    answers: list[str] = field(default_factory=list)
    spam_next: int = 0
    interrupt_once: bool = False
    restart_mid_lesson: bool = False
    corrupted_state: bool = False


SIM_USERS: dict[str, SimProfile] = {
    "beginner": SimProfile("beginner", "beginner", ["context progress", "outcome motivation"]),
    "junior": SimProfile("junior", "junior", ["context progress", "outcome motivation"]),
    "strong_learner": SimProfile("strong learner", "middle", ["context progress", "outcome motivation"]),
    "weak_learner": SimProfile("weak learner", "beginner", ["idk", "wrong"]),
    "inactive_user": SimProfile("inactive", "beginner", ["", ""], interrupt_once=True),
    "confused_user": SimProfile("confused", "junior", ["???", "i dont know"], spam_next=2),
    "speed_learner": SimProfile("speed", "middle", ["context progress", "outcome motivation"], spam_next=4),
    "edge_case_user": SimProfile("edge", "beginner", ["", "outcome"], restart_mid_lesson=True, corrupted_state=True),
}


class DummyMessage:
    def __init__(self):
        self.outbox: list[str] = []

    async def reply_text(self, text, reply_markup=None):
        self.outbox.append(text)


class DummyUpdate:
    def __init__(self):
        self.message = DummyMessage()


async def run_full_flow(profile: SimProfile) -> dict[str, Any]:
    user = ensure_user_state({"id": profile.name, "difficulty": profile.difficulty})
    user["lesson_started"] = True
    user["active_lesson"] = "jtbd"
    user["current_lesson_data"] = TEST_LESSON
    update = DummyUpdate()

    if profile.corrupted_state:
        user.pop("daily_quests", None)
        user = ensure_user_state(user)

    update_streak(user)

    answer_idx = 0
    loops = 0
    restarted = False
    while not user.get("lesson_finished") and loops < 30:
        loops += 1
        if profile.interrupt_once and loops == 1:
            user["lesson_started"] = False
            user["lesson_started"] = True

        await continue_lesson(update, user, TEST_LESSON)

        for _ in range(profile.spam_next):
            await continue_lesson(update, user, TEST_LESSON)

        if profile.restart_mid_lesson and (not restarted) and user.get("lesson_step", 0) == 2:
            user["lesson_step"] = 1
            restarted = True

        if user.get("waiting_for_answer"):
            answer = profile.answers[answer_idx] if answer_idx < len(profile.answers) else ""
            answer_idx += 1
            result = await process_answer(update, user, answer, TEST_LESSON)
            if result:
                remember_feedback(user, result["skill"], result["success"], answer)

        if user.get("lesson_step", 0) >= len(TEST_LESSON["blocks"]):
            await show_summary(update, user)

    # duplicate completion safety
    completed_before = len(user.get("completed_lessons", []))
    await show_summary(update, user)
    duplicate_completion_safe = len(user.get("completed_lessons", [])) == completed_before

    return {"user": user, "messages": update.message.outbox, "loops": loops, "duplicate_completion_safe": duplicate_completion_safe}


def run_full_flow_sync(profile: SimProfile) -> dict[str, Any]:
    return asyncio.run(run_full_flow(profile))
