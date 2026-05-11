from __future__ import annotations

from collections import Counter


def evaluate_lesson_quality(lesson: dict) -> dict:
    blocks = lesson.get("blocks", [])
    block_types = [b.get("type", "") for b in blocks]
    counts = Counter(block_types)

    checks = {
        "logical_flow": all(t in block_types for t in ["intro", "theory", "quiz", "practice", "summary"]),
        "case_quality": any(b.get("type") in {"case", "practice"} and len((b.get("task") or "")) > 10 for b in blocks),
        "feedback_quality": all((b.get("success_text") and b.get("fail_text")) for b in blocks if b.get("type") in {"quiz", "practice", "case"}),
        "repetition_ok": max(counts.values(), default=0) <= max(3, len(blocks) - 1),
        "difficulty_balance": any(b.get("keywords") for b in blocks if b.get("type") in {"quiz", "practice", "case"}),
    }
    return checks
