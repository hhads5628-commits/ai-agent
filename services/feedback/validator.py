from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ValidationResult:
    matched_keywords: List[str]
    missed_keywords: List[str]
    min_required: int
    success: bool


def normalize_keywords(raw_keywords):
    if not isinstance(raw_keywords, list):
        return []

    return [
        str(word).strip().lower()
        for word in raw_keywords
        if str(word).strip()
    ]


def validate_answer(answer_text: str, keywords):
    normalized_answer = (answer_text or "").lower().strip()
    normalized_keywords = normalize_keywords(keywords)

    matched_keywords = [
        word
        for word in normalized_keywords
        if word in normalized_answer
    ]
    missed_keywords = [
        word
        for word in normalized_keywords
        if word not in normalized_answer
    ]

    min_required = 1
    if normalized_keywords:
        min_required = max(1, (len(normalized_keywords) + 1) // 2)

    success = (
        len(matched_keywords) >= min_required
        if normalized_keywords
        else bool(normalized_answer)
    )

    return ValidationResult(
        matched_keywords=matched_keywords,
        missed_keywords=missed_keywords,
        min_required=min_required,
        success=success,
    )
