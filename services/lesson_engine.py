MAX_LESSON_MESSAGE_LENGTH = 3500


def _safe_lesson_text(text):
    text = str(text or "").strip()
    if not text:
        return "⚠️ Пустой блок урока. Переходим дальше."
    return text if len(text) <= MAX_LESSON_MESSAGE_LENGTH else text[:MAX_LESSON_MESSAGE_LENGTH - 1] + "…"


def _normalize_keywords(raw_keywords):
    if not isinstance(raw_keywords, list):
        return []
    return [str(word).strip().lower() for word in raw_keywords if str(word).strip()]


def _build_answer_coach_feedback(
    success,
    matched_keywords=None,
    missing_keywords=None,
    skill="general",
    **_,
):
    matched_keywords = matched_keywords or []
    missing_keywords = missing_keywords or []

    if success:
        strengths = []
        if matched_keywords:
            strengths.append(f"попал в ключевые элементы: {', '.join(matched_keywords[:3])}")
        strengths.append("ответ по теме и с понятной логикой")
        return (
            "\n\n🧠 Разбор ответа\n"
            f"Сильные стороны: {('; '.join(strengths)).capitalize()}.\n"
            "Что улучшить: добавь чуть больше конкретики и измеримости."
        )

    weak_parts = []
    if missing_keywords:
        weak_parts.append(f"не хватает акцента на: {', '.join(missing_keywords[:3])}")
    weak_parts.append("мало конкретики в формулировке")
    return (
        "\n\n🧠 Разбор ответа\n"
        "Сильные стороны: видно попытку ответить по теме.\n"
        f"Зоны роста: {('; '.join(weak_parts)).capitalize()}.\n"
        f"Микро-коррекция: переформулируй через шаблон 'кто → контекст → эффект' (навык: {skill})."
    )


async def continue_lesson(update, user, lesson):
    step = user.get("lesson_step", 0)
    blocks = lesson.get("blocks", [])
    if step >= len(blocks):
        await show_summary(update, user)
        return

    block = blocks[step]
    block_type = (block.get("type") or "").strip().lower()
    if block_type == "case":
        block_type = "practice"
    user["current_block"] = f"{step + 1}/{len(blocks)} • {block_type}"

    if block_type in {"intro", "theory", "reflection", "summary"}:
        await update.message.reply_text(_safe_lesson_text(block.get("text", "")))
        user["lesson_step"] += 1
        return

    if block_type == "quiz":
        user["waiting_for_answer"] = True
        user["current_block_type"] = "quiz"
        await update.message.reply_text(_safe_lesson_text(block.get("question", "")))
        return

    if block_type == "practice":
        user["waiting_for_answer"] = True
        user["current_block_type"] = "practice"
        await update.message.reply_text(_safe_lesson_text(block.get("task", "")))
        return

    await update.message.reply_text("⚠️ Неизвестный блок урока. Пропускаю.")
    user["lesson_step"] += 1


async def process_answer(update, user, text, lesson):
    if not user.get("waiting_for_answer"):
        return None
    blocks = lesson.get("blocks", [])
    step = user.get("lesson_step", 0)
    if step >= len(blocks):
        return None

    block = blocks[step]
    keywords = _normalize_keywords(block.get("keywords", []))
    answer_text = (text or "").lower().strip()
    matched = [w for w in keywords if w in answer_text]
    missing = [w for w in keywords if w not in answer_text]
    success = bool(answer_text) and (len(matched) >= max(1, (len(keywords) + 1) // 2) if keywords else True)
    skill = block.get("skill", "general")

    if success:
        user["xp"] += 20
        user["strengths"] = list(set(user.get("strengths", []) + [skill]))
        feedback_text = block.get("success_text", "✅ Отлично. Сильный ответ.")
        feedback_text += _build_answer_coach_feedback(
            success=True,
            matched_keywords=matched,
            missing_keywords=missing,
            skill=skill,
        )
        await update.message.reply_text(feedback_text)
    else:
        user["xp"] += 5
        if skill not in user.get("weak_topics", []):
            user.setdefault("weak_topics", []).append(skill)
        feedback = block.get("fail_text", "⚠️ Нужно точнее. Попробуй указать контекст, мотивацию и ожидаемый прогресс.")
        feedback += _build_answer_coach_feedback(
            success=False,
            matched_keywords=matched,
            missing_keywords=missing,
            skill=skill,
        )
        await update.message.reply_text(feedback)

    user["waiting_for_answer"] = False
    user["lesson_step"] += 1
    return {"skill": skill, "success": success}


async def show_summary(update, user):
    user["lesson_finished"] = True
    user["lesson_started"] = False
    lesson_name = user.get("active_lesson")
    if lesson_name and lesson_name not in user.get("completed_lessons", []):
        user["completed_lessons"].append(lesson_name)
        user["xp"] += 30
    user["daily_quests"]["lesson"] = True
    await update.message.reply_text("🎉 Lesson complete! +30 XP\nНажми 🚀 начать обучение для следующего unlock урока.")
