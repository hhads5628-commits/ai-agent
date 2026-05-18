def apply_lesson_rewards(user, xp_gain=25):
    user["xp"] += xp_gain

    completed_lessons = user.get("completed_lessons", [])
    active_lesson = user.get("active_lesson")

    if active_lesson and active_lesson not in completed_lessons:
        completed_lessons.append(active_lesson)

    user["completed_lessons"] = completed_lessons
    user["lesson_finished"] = True
    user["lesson_started"] = False
    user["waiting_for_answer"] = False
    user["current_lesson_data"] = None
    user["current_block"] = "Завершён"
    user["answer_analytics"] = []
