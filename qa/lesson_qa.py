from collections import Counter

REQUIRED_BLOCKS = ["intro", "theory", "reflection", "quiz", "practice", "summary"]


def evaluate_lesson_quality(lesson: dict) -> dict:
    blocks = lesson.get("blocks", [])
    types = [str(b.get("type", "")).lower() for b in blocks]
    texts = [b.get("text") or b.get("question") or b.get("task") or "" for b in blocks]

    logic_ok = all(t in types for t in REQUIRED_BLOCKS if t in {"intro", "theory", "quiz", "practice"})
    repeated = [item for item, n in Counter([t.strip().lower() for t in texts if t]).items() if n > 1]

    case_quality_ok = any("case" in (b.get("task", "").lower() + b.get("question", "").lower()) for b in blocks if isinstance(b, dict))
    feedback_quality_ok = all(
        bool(b.get("success_text")) and bool(b.get("fail_text"))
        for b in blocks
        if str(b.get("type", "")).lower() in {"quiz", "practice", "case"}
    )
    difficulty_balance_ok = len([b for b in blocks if str(b.get("type", "")).lower() in {"quiz", "practice", "case"}]) >= 2

    return {
        "logic_ok": logic_ok,
        "case_quality_ok": case_quality_ok,
        "feedback_quality_ok": feedback_quality_ok,
        "repetition_ok": len(repeated) == 0,
        "difficulty_balance_ok": difficulty_balance_ok,
        "repeated_fragments": repeated,
    }
