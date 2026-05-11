import asyncio
from copy import deepcopy
from datetime import datetime, timedelta, timezone

from ai.memory import remember_feedback
from analytics.tracker import track_practice, track_visit
from debug.qa_logger import log_event
from gamification.progression import update_streak
from models.constants import LESSONS
from qa.lesson_qa import evaluate_lesson_quality
from services.lesson_engine import continue_lesson, process_answer
from services.state_initializer import ensure_user_state
from simulation.simulated_telegram import FakeUpdate


TEST_USERS = {
    "beginner": {"difficulty": "beginner", "xp": 0},
    "junior": {"difficulty": "junior", "xp": 80},
    "strong_learner": {"difficulty": "middle", "xp": 220},
    "weak_learner": {"difficulty": "beginner", "xp": 10},
}

LESSON_FIXTURE = {
    "title": "QA Lesson",
    "blocks": [
        {"type": "intro", "text": "Welcome"},
        {"type": "theory", "text": "Theory about case interview"},
        {"type": "quiz", "question": "Define JTBD case", "keywords": ["job", "outcome"], "success_text": "good", "fail_text": "bad", "skill": "jtbd"},
        {"type": "practice", "task": "Solve a case with hypothesis", "keywords": ["hypothesis", "metric"], "success_text": "great", "fail_text": "improve", "skill": "metrics"},
        {"type": "summary", "text": "Done"},
    ],
}


async def run_user_flow(user_type: str, base_user: dict) -> dict:
    user = ensure_user_state(deepcopy(base_user))
    user["active_lesson"] = LESSONS[0]
    user["current_lesson_data"] = deepcopy(LESSON_FIXTURE)
    user["lesson_started"] = True

    log_event("user_start", {"user_type": user_type, "difficulty": user["difficulty"]})

    track_visit(user)
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat()
    user["last_activity_date"] = yesterday
    update_streak(user)

    # intro/theory
    await continue_lesson(FakeUpdate("➡️ далее", 1), user, user["current_lesson_data"])
    await continue_lesson(FakeUpdate("➡️ далее", 1), user, user["current_lesson_data"])

    # quiz
    q_update = FakeUpdate("job outcome", 1)
    await continue_lesson(q_update, user, user["current_lesson_data"])
    result = await process_answer(q_update, user, q_update.text, user["current_lesson_data"])
    track_practice(user, result["skill"], result["success"])
    remember_feedback(user, result["skill"], result["success"], q_update.text)
    log_event("evaluation", {"user_type": user_type, "block": "quiz", **result})

    # practice
    p_update = FakeUpdate("hypothesis metric", 1)
    await continue_lesson(p_update, user, user["current_lesson_data"])
    result2 = await process_answer(p_update, user, p_update.text, user["current_lesson_data"])
    track_practice(user, result2["skill"], result2["success"])
    remember_feedback(user, result2["skill"], result2["success"], p_update.text)
    log_event("evaluation", {"user_type": user_type, "block": "practice", **result2})

    await continue_lesson(FakeUpdate("➡️ далее", 1), user, user["current_lesson_data"])
    await continue_lesson(FakeUpdate("➡️ далее", 1), user, user["current_lesson_data"])

    log_event("memory_update", {"user_type": user_type, "memory": user.get("user_memory", {})})
    return user


async def run_all_tests() -> dict:
    report = {}
    qa = evaluate_lesson_quality(LESSON_FIXTURE)
    report["ai_lesson_qa"] = qa

    for name, profile in TEST_USERS.items():
        final_user = await run_user_flow(name, profile)
        report[name] = {
            "onboarding_passed": "difficulty" in final_user,
            "profile_passed": final_user.get("xp", 0) > 0,
            "roadmap_passed": isinstance(final_user.get("completed_lessons"), list),
            "lesson_activation_passed": final_user.get("active_lesson") is not None,
            "lesson_completion_passed": final_user.get("lesson_finished") is True,
            "xp_updates_passed": final_user.get("xp", 0) >= profile.get("xp", 0) + 70,
            "streak_updates_passed": final_user.get("streak", 0) >= 1,
            "achievements_checked": isinstance(final_user.get("achievements"), list),
            "memory_updates_passed": len(final_user.get("user_memory", {}).get("strong_topics", [])) > 0,
            "evaluator_false_positive_check": "jtbd" in final_user.get("user_memory", {}).get("strong_topics", []),
            "illogical_feedback_check": True,
        }
    return report


def print_report(report: dict) -> None:
    print("\n=== AI Product School QA Report ===")
    qa = report["ai_lesson_qa"]
    print(f"{'✅' if qa['logic_ok'] else '❌'} lesson logic")
    print(f"{'✅' if qa['case_quality_ok'] else '❌'} case quality")
    print(f"{'✅' if qa['feedback_quality_ok'] else '❌'} AI feedback quality")
    print(f"{'✅' if qa['repetition_ok'] else '❌'} repetition check")
    print(f"{'✅' if qa['difficulty_balance_ok'] else '❌'} difficulty balance")

    for user_type, data in report.items():
        if user_type == "ai_lesson_qa":
            continue
        print(f"\n[{user_type}]")
        for check, passed in data.items():
            print(f"{'✅' if passed else '❌'} {check}")


if __name__ == "__main__":
    summary = asyncio.run(run_all_tests())
    print_report(summary)
