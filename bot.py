# bot.py

from telegram import (
    Update,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters
)

from services.user_service import (
    load_user,
    save_user
)

from services.lesson_engine import (
    continue_lesson,
    process_answer
)

from services.lesson_generator import (
    generate_lesson
)

# ======================
# TOKEN
# ======================

BOT_TOKEN = "8235831309:AAFvZtDc6FDDN1cZAO6LH61Dv_ByoVlXqaY"

# ======================
# LESSONS
# ======================

LESSONS = [
    "jtbd",
    "custdev",
    "mvp"
]

# ======================
# XP
# ======================

def get_rank(xp):

    if xp < 50:
        return "🌱 Beginner"

    elif xp < 150:
        return "⚡ Junior PM"

    elif xp < 300:
        return "🔥 Strong PM"

    return "🚀 Product Master"

# ======================
# PROGRESS BAR
# ======================

def progress_bar(percent):

    filled = int(percent / 20)

    empty = 5 - filled

    return (
        "🟩" * filled +
        "⬜" * empty
    )

# ======================
# DYNAMIC KEYBOARD
# ======================

def get_main_keyboard(user):

    # lesson mode
    if user.get(
        "lesson_started"
    ):

        return ReplyKeyboardMarkup(
            [
                ["➡️ далее"],
                ["⏸ выйти из урока"]
            ],
            resize_keyboard=True
        )

    # normal mode
    return ReplyKeyboardMarkup(
        [
            ["🚀 начать обучение"],
            ["📊 прогресс", "👤 профиль"],
            ["🗺 roadmap"],
            ["⚙️ настройки обучения"]
        ],
        resize_keyboard=True
    )

# ======================
# HOME
# ======================

async def show_home(
    update,
    user
):

    active_lesson = user.get(
        "active_lesson",
        "jtbd"
    )

    # active session
    if (
        user.get(
            "lesson_started"
        )
        and not user.get(
            "lesson_finished"
        )
    ):

        text = (

            f"📚 Продолжаем обучение\n\n"

            f"Текущий урок:\n"
            f"{active_lesson.upper()}\n\n"

            f"📍 Последний блок:\n"
            f"{user['current_block']}\n\n"

            f"🧠 AI помнит где ты остановился.\n\n"

            f"➡️ Нажми далее"
        )

    else:

        text = (

            f"🏠 AI Product School\n\n"

            f"📚 Текущий урок:\n"
            f"{active_lesson.upper()}\n\n"

            f"🎓 Формат:\n"
            f"• теория как в Практикуме\n"
            f"• кейсы\n"
            f"• практика\n"
            f"• AI feedback\n"
            f"• анализ слабых сторон\n\n"

            f"⭐ XP: {user['xp']}\n"
            f"🏆 {get_rank(user['xp'])}\n\n"

            f"🚀 Нажми:\n"
            f"начать обучение"
        )

    await update.message.reply_text(
        text,
        reply_markup=get_main_keyboard(user)
    )

# ======================
# MAIN HANDLER
# ======================

async def handle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text
    normalized_text = (
        text.strip().lower()
        if text
        else ""
    )

    chat_id = update.effective_chat.id

    user = load_user(chat_id)

    # ======================
    # SAFE INIT
    # ======================

    if "xp" not in user:
        user["xp"] = 0

    if "completed_lessons" not in user:
        user["completed_lessons"] = []

    if "lesson_step" not in user:
        user["lesson_step"] = 0

    if "waiting_for_answer" not in user:
        user["waiting_for_answer"] = False

    if "weak_topics" not in user:
        user["weak_topics"] = []

    if "strengths" not in user:
        user["strengths"] = []

    if "lesson_started" not in user:
        user["lesson_started"] = False

    if "lesson_finished" not in user:
        user["lesson_finished"] = False

    if "current_lesson_data" not in user:
        user["current_lesson_data"] = None

    if "current_block" not in user:
        user["current_block"] = "Не начат"

    if "difficulty" not in user:
        user["difficulty"] = "Junior"

    if "daily_time" not in user:
        user["daily_time"] = "30 минут"

    if "learning_style" not in user:
        user["learning_style"] = "Глубокая теория"

    if (
        "active_lesson" not in user
        or user["active_lesson"] not in LESSONS
    ):

        user["active_lesson"] = "jtbd"

    active_lesson = user.get(
        "active_lesson",
        "jtbd"
    )

    # ======================
    # GET CACHED LESSON
    # ======================

    lesson = user.get(
        "current_lesson_data"
    )

    # ======================
    # WAITING ANSWER
    # ======================

    if (
        user.get(
            "waiting_for_answer"
        )
        and lesson
    ):

        await process_answer(
            update,
            user,
            text,
            lesson
        )

        save_user(chat_id, user)

        return

    # ======================
    # START LESSON
    # ======================

    if text == "🚀 начать обучение":

        # lesson already active
        if (
            user.get(
                "lesson_started"
            )
            and not user.get(
                "lesson_finished"
            )
        ):

            await update.message.reply_text(

                f"📚 Урок уже активен\n\n"

                f"Текущий урок:\n"
                f"{active_lesson.upper()}\n\n"

                f"📍 Последний блок:\n"
                f"{user['current_block']}\n\n"

                f"➡️ Нажми далее",

                reply_markup=get_main_keyboard(user)
            )

            return

        has_saved_lesson = (
            user.get("current_lesson_data")
            and user.get("lesson_step", 0) > 0
            and not user.get("lesson_finished")
        )

        user["lesson_started"] = True
        user["lesson_finished"] = False
        user["waiting_for_answer"] = False

        if has_saved_lesson:

            lesson = user["current_lesson_data"]

            await update.message.reply_text(
                "📚 Нашёл сохранённый урок.\n"
                "Продолжаем с последнего блока."
            )

        else:

            user["lesson_step"] = 0
            user["weak_topics"] = []
            user["strengths"] = []

            await update.message.reply_text(
                "🧠 AI создаёт урок...\n\n"
                "Это может занять 5-15 секунд."
            )

            lesson = generate_lesson(
                topic=active_lesson,
                level=user["difficulty"]
            )

            user["current_lesson_data"] = lesson

        save_user(chat_id, user)

        await continue_lesson(
            update,
            user,
            lesson
        )

        save_user(chat_id, user)

        return

    # ======================
    # NEXT STEP
    # ======================

    cleaned_next_command = (
        normalized_text
        .replace("➡️", "")
        .replace("➡", "")
        .replace("​", "")
        .replace("﻿", "")
        .strip()
    )

    is_next_command = cleaned_next_command == "далее"

    if (
        is_next_command
        and user.get("lesson_started")
    ):

        if not lesson:

            user["lesson_step"] = 0
            user["waiting_for_answer"] = False

            await update.message.reply_text(
                "⚠️ Сессия урока сбросилась. "
                "Восстанавливаю урок, подожди 5-15 секунд."
            )

            lesson = generate_lesson(
                topic=active_lesson,
                level=user["difficulty"]
            )

            user["current_lesson_data"] = lesson

        await continue_lesson(
            update,
            user,
            lesson
        )

        save_user(chat_id, user)

        return

    # ======================
    # EXIT LESSON
    # ======================

    if text == "⏸ выйти из урока":

        user["lesson_started"] = False

        save_user(chat_id, user)

        await update.message.reply_text(

            f"⏸ Урок сохранён\n\n"

            f"📚 {active_lesson.upper()}\n"
            f"📍 Последний блок:\n"
            f"{user['current_block']}\n\n"

            f"Ты можешь вернуться позже.",

            reply_markup=get_main_keyboard(user)
        )

        return

    # ======================
    # SETTINGS
    # ======================

    if text == "⚙️ настройки обучения":

        await update.message.reply_text(

            f"⚙️ Настройки обучения\n\n"

            f"📚 Уровень:\n"
            f"{user['difficulty']}\n\n"

            f"⏱ Темп:\n"
            f"{user['daily_time']}\n\n"

            f"🧠 Стиль:\n"
            f"{user['learning_style']}\n\n"

            f"🎯 AI подстраивает\n"
            f"уроки под эти параметры.",

            reply_markup=get_main_keyboard(user)
        )

        return

    # ======================
    # SELECT LESSON
    # ======================

    if text.lower() in LESSONS:

        user["active_lesson"] = (
            text.lower()
        )

        user["lesson_step"] = 0

        user["waiting_for_answer"] = False

        user["lesson_started"] = False

        user["current_lesson_data"] = None

        save_user(chat_id, user)

        await update.message.reply_text(

            f"📚 Урок выбран:\n"
            f"{text.upper()}\n\n"

            f"🚀 Нажми:\n"
            f"начать обучение",

            reply_markup=get_main_keyboard(user)
        )

        return

    # ======================
    # PROFILE
    # ======================

    if text == "👤 профиль":

        weak = (
            "\n• ".join(
                user["weak_topics"]
            )
            if user["weak_topics"]
            else "Нет"
        )

        strengths = (
            "\n• ".join(
                user["strengths"]
            )
            if user["strengths"]
            else "Нет"
        )

        await update.message.reply_text(

            f"👤 Профиль\n\n"

            f"⭐ XP: {user['xp']}\n"
            f"🏆 {get_rank(user['xp'])}\n\n"

            f"📚 Активный урок:\n"
            f"{active_lesson.upper()}\n\n"

            f"📚 Уровень:\n"
            f"{user['difficulty']}\n\n"

            f"⏱ Темп:\n"
            f"{user['daily_time']}\n\n"

            f"🔥 Сильные стороны:\n"
            f"• {strengths}\n\n"

            f"⚠️ Слабые стороны:\n"
            f"• {weak}",

            reply_markup=get_main_keyboard(user)
        )

        return

    # ======================
    # ROADMAP
    # ======================

    if text == "🗺 roadmap":

        total = len(LESSONS)

        done = len(
            user["completed_lessons"]
        )

        percent = int(
            (done / total) * 100
        )

        roadmap = (
            "🧠 PRODUCT ROADMAP\n\n"

            "━━━━━━━━━━━\n\n"

            "🌱 FOUNDATION\n\n"
        )

        for lesson_name in LESSONS:

            if lesson_name == active_lesson:

                roadmap += (
                    f"🔄 {lesson_name.upper()}\n"
                )

                continue

            if lesson_name in user[
                "completed_lessons"
            ]:

                roadmap += (
                    f"✅ {lesson_name.upper()}\n"
                )

            else:

                roadmap += (
                    f"⚪ {lesson_name.upper()}\n"
                )

        roadmap += (

            f"\n━━━━━━━━━━━\n\n"

            f"🏆 LEVEL\n"
            f"{get_rank(user['xp'])}\n\n"

            f"📈 Progress\n"
            f"{progress_bar(percent)} "
            f"{percent}%"
        )

        await update.message.reply_text(
            roadmap,
            reply_markup=get_main_keyboard(user)
        )

        return

    # ======================
    # PROGRESS
    # ======================

    if text == "📊 прогресс":

        total = len(LESSONS)

        done = len(
            user["completed_lessons"]
        )

        percent = int(
            (done / total) * 100
        )

        await update.message.reply_text(

            f"📊 Прогресс\n\n"

            f"{progress_bar(percent)} "
            f"{percent}%\n\n"

            f"✅ Завершено уроков:\n"
            f"{done}/{total}\n\n"

            f"⭐ XP: {user['xp']}\n"
            f"🏆 {get_rank(user['xp'])}",

            reply_markup=get_main_keyboard(user)
        )

        return

    # ======================
    # DEFAULT
    # ======================

    await show_home(
        update,
        user
    )

# ======================
# APP
# ======================

app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .build()
)

# ======================
# HANDLER
# ======================

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle
    )
)

# ======================
# START
# ======================

print("🔥 AI PRODUCT SCHOOL RUNNING")

app.run_polling()
