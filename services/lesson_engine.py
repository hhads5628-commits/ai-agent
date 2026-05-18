# services/lesson_engine.py

MAX_LESSON_MESSAGE_LENGTH = 3500


def _safe_lesson_text(text):
    if not isinstance(text, str):
        text = str(text or "")

    text = text.strip()

    if not text:
        return "⚠️ Пустой блок урока. Переходим дальше."

    if len(text) <= MAX_LESSON_MESSAGE_LENGTH:
        return text

    return text[:MAX_LESSON_MESSAGE_LENGTH - 1] + "…"


def _normalize_keywords(raw_keywords):
    if not isinstance(raw_keywords, list):
        return []

    return [
        str(word).strip().lower()
        for word in raw_keywords
        if str(word).strip()
    ]


def _build_direction_feedback(
    answer_text,
    matched_keywords,
    missed_keywords
):
    text = (answer_text or "").strip().lower()
    if not text:
        return ""

    direction = [
        "\n\n🧭 Куда двигаемся дальше:"
    ]

    if matched_keywords:
        direction.append(
            "• Ты уже в верном направлении: есть базовые элементы ответа."
        )

    if missed_keywords:
        direction.append(
            "• Следующий шаг: добавь недостающие элементы по одному, "
            "а не пытайся переписать всё с нуля."
        )
        direction.append(
            "• План на 1 итерацию: выбери 2 пункта из «Добавь идеи» "
            "и встрои их в короткий сценарий."
        )

    direction.append(
        "• Формула сильного ответа: "
        "контекст пользователя → конкретное действие → ручная проверка ценности."
    )

    question_like = text.count("?")
    if question_like == 0:
        direction.append(
            "• Добавь 1-2 конкретных вопроса к пользователю, "
            "чтобы ответ был проверяемым."
        )

    if not missed_keywords and matched_keywords:
        return "\n\n🧭 Куда двигаемся дальше:\n• Отлично, вектор верный. Добавь больше конкретики из реального опыта пользователя."

    return "\n".join(direction)


def _build_teacher_style_feedback(answer_text):
    text = (answer_text or "").strip()
    lowered = text.lower()
    if not text:
        return ""

    strengths = []
    weak_points = []
    next_steps = []

    if "?" in text:
        strengths.append("есть вопросы — ты не просто декларируешь, а исследуешь")
    else:
        weak_points.append("ответ без вопросов: сложно проверить гипотезу на реальных людях")
        next_steps.append("добавь минимум 2 открытых вопроса, начинающихся с «как», «что», «расскажи»")

    past_markers = ["последний раз", "недавно", "в прошлый", "когда ты"]
    if any(marker in lowered for marker in past_markers):
        strengths.append("ты опираешься на прошлый опыт пользователя")
    else:
        weak_points.append("мало фокуса на реальных прошлых действиях пользователя")
        next_steps.append("добавь вопрос: «Расскажи про последний раз, когда ты решал эту задачу»")

    emotion_markers = ["бесило", "злило", "раздражало", "стресс", "обидно", "устал"]
    if any(marker in lowered for marker in emotion_markers):
        strengths.append("затронуты эмоции — это помогает найти настоящую боль")
    else:
        weak_points.append("нет фокуса на эмоциях, а именно они показывают глубину боли")
        next_steps.append("добавь вопрос: «Что в этом процессе бесило или злило сильнее всего?»")

    if len(text.split()) >= 20:
        strengths.append("ответ достаточно развёрнутый, есть материал для анализа")
    else:
        weak_points.append("ответ слишком короткий: пока мало контекста для сильного вывода")
        next_steps.append("добавь 1 конкретный кейс пользователя: контекст → действие → результат")

    lines = ["\n\n🧠 Разбор как преподаватель:"]
    if strengths:
        lines.append("• Сильные стороны: " + "; ".join(strengths[:3]) + ".")
    if weak_points:
        lines.append("• Слабые места: " + "; ".join(weak_points[:3]) + ".")
    if next_steps:
        lines.append("• Как усилить следующий ответ: " + " | ".join(next_steps[:3]) + ".")

    return "\n".join(lines)


def _build_final_mini_test():
    return (
        "\n\n📝 Мини‑тест (4 вопроса)\n"
        "1) Какой вопрос лучше для CustDev?\n"
        "A) Ты бы купил этот продукт?\n"
        "B) Расскажи про последний раз, когда ты решал эту задачу.\n"
        "C) Тебе в целом нравится идея?\n\n"
        "2) Что лучше всего показывает настоящую боль пользователя?\n"
        "A) Вежливое согласие\n"
        "B) Общие рассуждения\n"
        "C) Сильные эмоции и конкретные примеры\n\n"
        "3) Что делать после 2 интервью?\n"
        "A) Срочно строить продукт\n"
        "B) Дождаться паттернов на серии интервью\n"
        "C) Игнорировать обратную связь\n\n"
        "4) MVP на старте — это:\n"
        "A) Минимальная ценность + ручная проверка спроса\n"
        "B) Сразу сложный AI‑продукт\n"
        "C) Полный функционал до первых пользователей\n\n"
        "Отправь ответы в формате: 1B, 2C, 3B, 4A."
    )

# =====================================================
# UNIVERSAL LESSON ENGINE
# =====================================================
#
# Этот engine НЕ зависит от темы.
#
# Он умеет:
# • intro
# • theory
# • reflection
# • quiz
# • practice
# • review
# • summary
#
# Любой урок:
# JTBD / SQL / MVP / Analytics
# проходит через одинаковую архитектуру.
#
# Контент уроков будет отдельно:
# lessons/*.json
#
# =====================================================

# =====================================================
# CONTINUE LESSON
# =====================================================

async def continue_lesson(
    update,
    user,
    lesson
):

    step = user.get(
        "lesson_step",
        0
    )

    blocks = lesson.get(
        "blocks",
        []
    )

    # =====================================================
    # LESSON FINISHED
    # =====================================================

    if step >= len(blocks):

        await show_summary(
            update,
            user
        )

        return

    current_block = blocks[step]
    user["current_block"] = (
        f"{step + 1}/{len(blocks)} • "
        f"{current_block.get('type', 'block')}"
    )

    block_type = (
        current_block.get("type")
        or ""
    ).strip().lower()

    # Backward compatibility:
    # old/generated lessons can contain `case` blocks.
    # These blocks are interactive and should behave
    # like "practice".
    if block_type == "case":
        block_type = "practice"

    # =====================================================
    # INTRO
    # =====================================================

    if block_type == "intro":

        await update.message.reply_text(

            _safe_lesson_text(current_block.get(
                "text",
                ""
            ))
        )

        user["lesson_step"] += 1

        return

    # =====================================================
    # THEORY
    # =====================================================

    if block_type == "theory":

        await update.message.reply_text(

            _safe_lesson_text(current_block.get(
                "text",
                ""
            ))
        )

        user["lesson_step"] += 1

        return

    # =====================================================
    # REFLECTION
    # =====================================================

    if block_type == "reflection":

        await update.message.reply_text(

            _safe_lesson_text(current_block.get(
                "text",
                ""
            ))
        )

        user["lesson_step"] += 1

        return

    # =====================================================
    # QUIZ
    # =====================================================

    if block_type == "quiz":
        question_text = _safe_lesson_text(
            current_block.get(
                "question",
                ""
            )
        )

        if question_text.startswith("⚠️ Пустой блок урока"):
            await update.message.reply_text(
                "⚠️ Вопрос в этом блоке пустой. Пропускаю дальше."
            )
            user["lesson_step"] += 1
            await continue_lesson(update, user, lesson)
            return

        user[
            "waiting_for_answer"
        ] = True

        user[
            "current_block_type"
        ] = "quiz"
        user["answer_attempts"] = 0

        await update.message.reply_text(
            question_text
        )

        return

    # =====================================================
    # PRACTICE
    # =====================================================

    if block_type == "practice":
        task_text = _safe_lesson_text(
            current_block.get(
                "task",
                ""
            )
        )

        if task_text.startswith("⚠️ Пустой блок урока"):
            await update.message.reply_text(
                "⚠️ Практическое задание пустое. Пропускаю дальше."
            )
            user["lesson_step"] += 1
            await continue_lesson(update, user, lesson)
            return

        user[
            "waiting_for_answer"
        ] = True

        user[
            "current_block_type"
        ] = "practice"
        user["answer_attempts"] = 0

        await update.message.reply_text(
            task_text
        )

        return

    # =====================================================
    # UNKNOWN BLOCK TYPE
    # =====================================================
    #
    # Prevent lesson from getting stuck on unexpected
    # block types by moving forward.
    await update.message.reply_text(
        _safe_lesson_text(
            current_block.get(
                "text",
                "⚠️ Неизвестный блок урока. Пропускаю и иду дальше."
            )
        )
    )

    user["lesson_step"] += 1

    return

# =====================================================
# PROCESS ANSWER
# =====================================================

async def process_answer(
    update,
    user,
    text,
    lesson
):

    if not user.get(
        "waiting_for_answer"
    ):

        return

    blocks = lesson.get(
        "blocks",
        []
    )

    step = user.get(
        "lesson_step",
        0
    )

    if step >= len(blocks):

        return

    current_block = blocks[
        step
    ]

    keywords = _normalize_keywords(
        current_block.get(
            "keywords",
            []
        )
    )

    answer_text = (text or "").lower().strip()

    if answer_text in {"далее", "➡️ далее", "➡ далее"}:
        await update.message.reply_text(
            "✍️ Сначала дай ответ на вопрос. Я проверю и дам персональный разбор."
        )
        return
    matched_keywords = [
        word
        for word in keywords
        if word in answer_text
    ]

    missed_keywords = [
        word
        for word in keywords
        if word not in answer_text
    ]

    # Require meaningful coverage: at least half of the
    # expected ideas (rounded up) for keyword-based blocks.
    # If no keywords are configured, keep backward-compatible
    # behavior and accept any non-empty answer.
    min_required = 1
    if keywords:
        min_required = max(1, (len(keywords) + 1) // 2)

    success = (
        len(matched_keywords) >= min_required
        if keywords
        else bool(answer_text.strip())
    )

    # =====================================================
    # SUCCESS
    # =====================================================

    if success:

        feedback_text = _safe_lesson_text(current_block.get(
            "success_text",
            "🔥 Хороший ответ"
        ))

        if keywords:
            matched = ", ".join(matched_keywords[:5]) or "—"
            missing = ", ".join(missed_keywords[:5]) or "—"
            feedback_text += (
                "\n\n🧩 Почему ответ засчитан:\n"
                f"Совпало опорных идей: {len(matched_keywords)}/{len(keywords)} "
                f"(минимум: {min_required})\n"
                f"✅ Учтено: {matched}\n"
                f"➡️ Для усиления добавь: {missing}"
            )
            feedback_text += _build_direction_feedback(
                answer_text=answer_text,
                matched_keywords=matched_keywords,
                missed_keywords=missed_keywords
            )
            feedback_text += _build_teacher_style_feedback(answer_text)

        await update.message.reply_text(feedback_text)

        strengths = user.get(
            "strengths",
            []
        )

        strengths.append(
            current_block.get(
                "skill",
                "Thinking"
            )
        )

        user[
            "strengths"
        ] = strengths

    # =====================================================
    # FAIL
    # =====================================================

    else:

        attempts = user.get("answer_attempts", 0) + 1
        user["answer_attempts"] = attempts

        feedback_text = _safe_lesson_text(current_block.get(
            "fail_text",
            "⚠️ Пока не засчитано. Давай докрутим ответ."
        ))

        if keywords:
            matched = ", ".join(matched_keywords[:5]) or "пока нет точных попаданий"
            expected = ", ".join(missed_keywords[:5]) or "все ключевые идеи уже упомянуты"
            feedback_text += (
                "\n\n📌 Что усилить в ответе:\n"
                f"Покрытие опорных идей: {len(matched_keywords)}/{len(keywords)} "
                f"(нужно минимум: {min_required})\n"
                f"✅ Уже есть: {matched}\n"
                f"➕ Добавь идеи: {expected}"
            )
            feedback_text += _build_direction_feedback(
                answer_text=answer_text,
                matched_keywords=matched_keywords,
                missed_keywords=missed_keywords
            )

        feedback_text += _build_teacher_style_feedback(answer_text)

        feedback_text += (
            "\n\n💬 Напиши новый ответ, и я проверю его ещё раз."
        )

        weak_topics = user.get(
            "weak_topics",
            []
        )

        weak_topics.append(
            current_block.get(
                "skill",
                "Thinking"
            )
        )

        user[
            "weak_topics"
        ] = weak_topics

        if attempts < 2:
            await update.message.reply_text(feedback_text)
            return

        await update.message.reply_text(
            feedback_text + "\n\n➡️ Переходим дальше, но к этому навыку вернёмся в следующих уроках."
        )

    # =====================================================
    # NEXT STEP
    # =====================================================

    user[
        "waiting_for_answer"
    ] = False
    user["answer_attempts"] = 0

    analytics = user.get("answer_analytics", [])
    analytics.append({
        "block_type": user.get("current_block_type", "unknown"),
        "success": success,
        "matched": len(matched_keywords),
        "expected": len(keywords)
    })
    user["answer_analytics"] = analytics

    user[
        "lesson_step"
    ] += 1

    await continue_lesson(
        update,
        user,
        lesson
    )

# =====================================================
# SUMMARY
# =====================================================

async def show_summary(
    update,
    user
):

    strengths = user.get(
        "strengths",
        []
    )

    weak_topics = user.get(
        "weak_topics",
        []
    )

    strengths_text = (
        "\n• ".join(strengths)
        if strengths
        else "Пока нет"
    )

    weak_text = (
        "\n• ".join(weak_topics)
        if weak_topics
        else "Пока нет"
    )

    analytics = user.get("answer_analytics", [])
    answered = len(analytics)
    passed = len([
        row for row in analytics
        if row.get("success")
    ])
    avg_coverage = 0

    if answered:
        coverage_sum = 0
        for row in analytics:
            expected = row.get("expected", 0)
            matched = row.get("matched", 0)
            if expected > 0:
                coverage_sum += int((matched / expected) * 100)
            else:
                coverage_sum += 100

        avg_coverage = int(coverage_sum / answered)

    await update.message.reply_text(

        _safe_lesson_text(
            "🏁 Урок завершён\n\n"

        "📊 Разбор обучения\n\n"

        f"🔥 Сильные стороны:\n"
        f"• {strengths_text}\n\n"

        f"⚠️ Слабые стороны:\n"
        f"• {weak_text}\n\n"

        "🧠 Аналитика ответов:\n"
        f"• Засчитано: {passed}/{answered}\n"
        f"• Средняя полнота ответа: {avg_coverage}%\n\n"

        "✅ Что было в уроке:\n"
        "• большая теория\n"
        "• вопросы\n"
        "• практика\n"
        "• AI feedback\n"
        "• анализ ответов\n\n"

            "⭐ +25 XP"
        ) + _build_final_mini_test()
    )

    user["xp"] += 25

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
