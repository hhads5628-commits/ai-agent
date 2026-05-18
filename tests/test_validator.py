from services.feedback.validator import validate_answer


def test_validator_success_with_keyword_coverage():
    result = validate_answer("mvp и ценность", ["mvp", "ценность", "проверка"])
    assert result.success is True
    assert result.min_required == 2


def test_validator_without_keywords_accepts_non_empty():
    result = validate_answer("любой ответ", [])
    assert result.success is True
