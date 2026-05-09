import json

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

    return lesson