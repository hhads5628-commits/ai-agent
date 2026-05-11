from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

LOG_PATH = Path(__file__).resolve().parent / "qa_debug.log"


def _write(event: str, payload: Dict[str, Any]) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "payload": payload,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_user_action(user_id: str, action: str, extra: Dict[str, Any] | None = None) -> None:
    _write("user_action", {"user_id": user_id, "action": action, "extra": extra or {}})


def log_ai_decision(user_id: str, decision: str, details: Dict[str, Any] | None = None) -> None:
    _write("ai_decision", {"user_id": user_id, "decision": decision, "details": details or {}})


def log_lesson_transition(user_id: str, from_step: int, to_step: int, block_type: str) -> None:
    _write(
        "lesson_transition",
        {"user_id": user_id, "from_step": from_step, "to_step": to_step, "block_type": block_type},
    )


def log_evaluation_score(user_id: str, skill: str, success: bool, matched_keywords: int) -> None:
    _write(
        "evaluation_score",
        {"user_id": user_id, "skill": skill, "success": success, "matched_keywords": matched_keywords},
    )


def log_memory_change(user_id: str, weak_topics: list[str], strong_topics: list[str], mistakes_count: int) -> None:
    _write(
        "memory_change",
        {
            "user_id": user_id,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "mistakes_count": mistakes_count,
        },
    )
