from __future__ import annotations

import asyncio

from services.lesson_engine import process_answer


class DummyMessage:
    def __init__(self):
        self.outbox = []

    async def reply_text(self, text, reply_markup=None):
        self.outbox.append(text)


class DummyUpdate:
    def __init__(self):
        self.message = DummyMessage()


async def check_evaluator() -> dict:
    lesson = {"blocks": [{"type": "quiz", "keywords": ["context", "progress"], "skill": "jtbd", "success_text": "Good feedback", "fail_text": "Need context"}]}

    # true positive
    user_ok = {"id": "qa-evaluator", "waiting_for_answer": True, "lesson_step": 0, "xp": 0, "weak_topics": []}
    ok_update = DummyUpdate()
    ok = await process_answer(ok_update, user_ok, "context and progress", lesson)

    # false positive guard
    user_bad = {"id": "qa-evaluator", "waiting_for_answer": True, "lesson_step": 0, "xp": 0, "weak_topics": []}
    bad_update = DummyUpdate()
    bad = await process_answer(bad_update, user_bad, "totally unrelated", lesson)

    # false negative guard (partial should fail by current strict logic, full should pass)
    user_full = {"id": "qa-evaluator", "waiting_for_answer": True, "lesson_step": 0, "xp": 0, "weak_topics": []}
    full = await process_answer(DummyUpdate(), user_full, "context progress", lesson)

    # empty response
    user_empty = {"id": "qa-evaluator", "waiting_for_answer": True, "lesson_step": 0, "xp": 0, "weak_topics": []}
    empty = await process_answer(DummyUpdate(), user_empty, "", lesson)

    repetitive_feedback = len(set(bad_update.message.outbox)) == len(bad_update.message.outbox)

    return {
        "correct_positive": bool(ok and ok["success"]),
        "false_positive_guard": bool(bad and not bad["success"]),
        "false_negative_guard": bool(full and full["success"]),
        "illogical_feedback_guard": user_bad["xp"] == 5,
        "empty_response_handled": bool(empty and not empty["success"]),
        "non_empty_feedback": all(bool(msg.strip()) for msg in (ok_update.message.outbox + bad_update.message.outbox)),
        "non_repetitive_feedback": repetitive_feedback,
    }


def check_evaluator_sync() -> dict:
    return asyncio.run(check_evaluator())
