import json

from services.lesson_enricher import enrich_lesson_for_clarity

# ======================
# LOAD LESSON
# ======================

def load_lesson(
    lesson_name
):

    path = (
        f"lessons/{lesson_name}.json"
    )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        lesson = json.load(file)

    return enrich_lesson_for_clarity(lesson)
