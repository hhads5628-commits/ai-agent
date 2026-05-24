from services.lesson_enricher import enrich_lesson_for_clarity


def test_enriches_short_theory_into_practicum_format():
    lesson = {
        "title": "Проблема и сегмент",
        "blocks": [
            {"type": "intro", "text": "start"},
            {"type": "theory", "text": "Короткая теория"},
        ],
    }

    enriched = enrich_lesson_for_clarity(lesson)
    theory = next(b for b in enriched["blocks"] if b["type"] == "theory")["text"]

    assert "Теория в формате практикума" in theory
    assert "Мини-кейс" in theory
    assert len(theory) > 900


def test_keeps_long_theory_unchanged():
    long_text = "A" * 950
    lesson = {
        "title": "Long",
        "blocks": [{"type": "theory", "text": long_text}],
    }

    enriched = enrich_lesson_for_clarity(lesson)

    assert enriched["blocks"][0]["text"] == long_text
