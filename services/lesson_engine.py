# services/lesson_engine.py

from services.feedback.coach_feedback import build_answer_coach_feedback
from services.feedback.validator import normalize_keywords, validate_answer
from services.roadmap.progression import apply_lesson_rewards
from services.roadmap.roadmap_engine import summarize_progress
from services.tests.mini_test_engine import build_final_mini_test

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
    return normalize_keywords(raw_keywords)


def _build_answer_coach_feedback(answer_text, coverage=None):
    return build_answer_coach_feedback(answer_text=answer_text, coverage=coverage)


def _build_final_mini_test():
    return build_final_mini_test()


async def continue_lesson(update, user, lesson):
    step = user.get("lesson_step", 0)
    blocks = lesson.get("blocks", [])

    if step >= len(blocks):
        await show_summary(update, user)
        return

    current_block = blocks[step]
    user["current_block"] = f"{step + 1}/{len(blocks)} • {current_block.get('type', 'block')}"

    block_type = (current_block.get("type") or "").strip().lower()
    if block_type == "case":
        block_type = "practice"

    if block_type in {"intro", "theory", "reflection"}:
        await update.message.reply_text(_safe_lesson_text(current_block.get("text", "")))
        user["lesson_step"] += 1
        return

    if block_type == "quiz":
        question_text = _safe_lesson_text(current_block.get("question", ""))
        if question_text.startswith("⚠️ Пустой блок урока"):
            await update.message.reply_text("⚠️ Вопрос в этом блоке пустой. Пропускаю дальше.")
            user["lesson_step"] += 1
            await continue_lesson(update, user, lesson)
            return

        user["waiting_for_answer"] = True
        user["current_block_type"] = "quiz"
        user["answer_attempts"] = 0
        await update.message.reply_text(question_text)
        return

    if block_type == "practice":
        task_text = _safe_lesson_text(current_block.get("task", ""))
        if task_text.startswith("⚠️ Пустой блок урока"):
            await update.message.reply_text("⚠️ Практическое задание пустое. Пропускаю дальше.")
            user["lesson_step"] += 1
            await continue_lesson(update, user, lesson)
            return

        user["waiting_for_answer"] = True
        user["current_block_type"] = "practice"
        user["answer_attempts"] = 0
        await update.message.reply_text(task_text)
        return

    await update.message.reply_text(
        _safe_lesson_text(current_block.get("text", "⚠️ Неизвестный блок урока. Пропускаю и иду дальше."))
    )
    user["lesson_step"] += 1


async def process_answer(update, user, text, lesson):
    if not user.get("waiting_for_answer"):
        return

    blocks = lesson.get("blocks", [])
    step = user.get("lesson_step", 0)
    if step >= len(blocks):
        return

    current_block = blocks[step]
    answer_text = (text or "").lower().strip()
    if answer_text in {"далее", "➡️ далее", "➡ далее"}:
        await update.message.reply_text("✍️ Сначала дай ответ на вопрос. Я проверю и дам персональный разбор.")
        return

    validation = validate_answer(answer_text, current_block.get("keywords", []))
    matched_keywords = validation.matched_keywords
    missed_keywords = validation.missed_keywords
    keywords = _normalize_keywords(current_block.get("keywords", []))

    if validation.success:
        feedback_text = _safe_lesson_text(current_block.get("success_text", "🔥 Хороший ответ"))

        if keywords:
            matched = ", ".join(matched_keywords[:5]) or "—"
            missing = ", ".join(missed_keywords[:5]) or "—"
            feedback_text += (
                "\n\n🧩 Почему ответ засчитан:\n"
                f"Совпало опорных идей: {len(matched_keywords)}/{len(keywords)} "
                f"(минимум: {validation.min_required})\n"
                f"✅ Учтено: {matched}\n"
                f"➡️ Для усиления добавь: {missing}"
            )

        feedback_text += _build_answer_coach_feedback(
            answer_text=answer_text,
            coverage={"matched_keywords": matched_keywords, "missed_keywords": missed_keywords},
        )
        await update.message.reply_text(feedback_text)

        strengths = user.get("strengths", [])
        strengths.append(current_block.get("skill", "Thinking"))
        user["strengths"] = strengths
    else:
        attempts = user.get("answer_attempts", 0) + 1
        user["answer_attempts"] = attempts

        feedback_text = _safe_lesson_text(current_block.get("fail_text", "⚠️ Пока не засчитано. Давай докрутим ответ."))

        if keywords:
            matched = ", ".join(matched_keywords[:5]) or "пока нет точных попаданий"
            expected = ", ".join(missed_keywords[:5]) or "все ключевые идеи уже упомянуты"
            feedback_text += (
                "\n\n📌 Что усилить в ответе:\n"
                f"Покрытие опорных идей: {len(matched_keywords)}/{len(keywords)} "
                f"(нужно минимум: {validation.min_required})\n"
                f"✅ Уже есть: {matched}\n"
                f"➕ Добавь идеи: {expected}"
            )

        feedback_text += _build_answer_coach_feedback(
            answer_text=answer_text,
            coverage={"matched_keywords": matched_keywords, "missed_keywords": missed_keywords},
        )
        feedback_text += "\n\n💬 Напиши новый ответ, и я проверю его ещё раз."

        weak_topics = user.get("weak_topics", [])
        weak_topics.append(current_block.get("skill", "Thinking"))
        user["weak_topics"] = weak_topics

        if attempts < 2:
            await update.message.reply_text(feedback_text)
            return

        await update.message.reply_text(
            feedback_text + "\n\n➡️ Переходим дальше, но к этому навыку вернёмся в следующих уроках."
        )

    user["waiting_for_answer"] = False
    user["answer_attempts"] = 0

    analytics = user.get("answer_analytics", [])
    analytics.append(
        {
            "block_type": user.get("current_block_type", "unknown"),
            "success": validation.success,
            "matched": len(matched_keywords),
            "expected": len(keywords),
        }
    )
    user["answer_analytics"] = analytics

    user["lesson_step"] += 1
    await continue_lesson(update, user, lesson)


async def show_summary(update, user):
    strengths = user.get("strengths", [])
    weak_topics = user.get("weak_topics", [])

    strengths_text = "\n• ".join(strengths) if strengths else "Пока нет"
    weak_text = "\n• ".join(weak_topics) if weak_topics else "Пока нет"

    summary = summarize_progress(user.get("answer_analytics", []))

    await update.message.reply_text(
        _safe_lesson_text(
            "🏁 Урок завершён\n\n"
            "📊 Разбор обучения\n\n"
            f"🔥 Сильные стороны:\n• {strengths_text}\n\n"
            f"⚠️ Слабые стороны:\n• {weak_text}\n\n"
            "🧠 Аналитика ответов:\n"
            f"• Засчитано: {summary['passed']}/{summary['answered']}\n"
            f"• Средняя полнота ответа: {summary['avg_coverage']}%\n\n"
            "✅ Что было в уроке:\n"
            "• большая теория\n"
            "• вопросы\n"
            "• практика\n"
            "• AI feedback\n"
            "• анализ ответов\n\n"
            "⭐ +25 XP"
        )
        + _build_final_mini_test()
    )

    apply_lesson_rewards(user, xp_gain=25)
