# services/lesson_engine.py

MAX_LESSON_MESSAGE_LENGTH = 3500


def _safe_lesson_text(text):
    if not isinstance(text, str):
        text = str(text or "")

    if len(text) <= MAX_LESSON_MESSAGE_LENGTH:
        return text

    return text[:MAX_LESSON_MESSAGE_LENGTH - 1] + "…"

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

        user[
            "waiting_for_answer"
        ] = True

        user[
            "current_block_type"
        ] = "quiz"

        await update.message.reply_text(

            _safe_lesson_text(current_block.get(
                "question",
                ""
            ))
        )

        return

    # =====================================================
    # PRACTICE
    # =====================================================

    if block_type == "practice":

        user[
            "waiting_for_answer"
        ] = True

        user[
            "current_block_type"
        ] = "practice"

        await update.message.reply_text(

            _safe_lesson_text(current_block.get(
                "task",
                ""
            ))
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

    keywords = current_block.get(
        "keywords",
        []
    )

    success = False

    # =====================================================
    # KEYWORD CHECK
    # =====================================================

    for word in keywords:

        if word.lower() in text.lower():

            success = True
            break

    # =====================================================
    # SUCCESS
    # =====================================================

    if success:

        await update.message.reply_text(

            _safe_lesson_text(current_block.get(
                "success_text",
                "🔥 Хороший ответ"
            ))
        )

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

        await update.message.reply_text(

            _safe_lesson_text(current_block.get(
                "fail_text",
                "⚠️ Попробуй ещё глубже"
            ))
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

    # =====================================================
    # NEXT STEP
    # =====================================================

    user[
        "waiting_for_answer"
    ] = False

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

    await update.message.reply_text(

        _safe_lesson_text(
            "🏁 Урок завершён\n\n"

        "📊 Разбор обучения\n\n"

        f"🔥 Сильные стороны:\n"
        f"• {strengths_text}\n\n"

        f"⚠️ Слабые стороны:\n"
        f"• {weak_text}\n\n"

        "✅ Что было в уроке:\n"
        "• большая теория\n"
        "• вопросы\n"
        "• практика\n"
        "• AI feedback\n"
        "• анализ ответов\n\n"

            "⭐ +25 XP"
        )
    )

    user["xp"] += 25
    user["lesson_finished"] = True
    user["lesson_started"] = False
    user["waiting_for_answer"] = False
    user["current_lesson_data"] = None
    user["current_block"] = "Завершён"
