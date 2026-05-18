from services.feedback.coach_feedback import build_answer_coach_feedback


def test_coach_feedback_includes_teacher_block_for_short_answer():
    out = build_answer_coach_feedback("идея норм")
    assert "🧠 Разбор как преподаватель" in out
    assert "эмоции" in out


def test_coach_feedback_respects_full_coverage_direction():
    out = build_answer_coach_feedback(
        "как ты решал это в прошлый раз? что бесило?",
        coverage={"matched_keywords": ["боль"], "missed_keywords": []},
    )
    assert "вектор верный" in out
