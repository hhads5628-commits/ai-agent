from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from analytics.tracker import track_practice, track_visit
from ai.memory import remember_feedback
from gamification.progression import get_rank, progress_bar, update_streak
from handlers.home import show_home
from handlers.keyboards import get_main_keyboard
from models.constants import LESSONS, LESSON_TITLES
from services.lesson_engine import continue_lesson, process_answer
from services.lesson_generator import generate_lesson
from services.state_initializer import ensure_user_state
from services.user_service import load_user, save_user
from config import get_required_env

BOT_TOKEN = get_required_env("BOT_TOKEN")


def next_locked_lesson(user: dict) -> str:
    done = set(user.get("completed_lessons", []))
    for lesson in LESSONS:
        if lesson not in done:
            return lesson
    return LESSONS[-1]


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    normalized = text.strip().lower()
    chat_id = update.effective_chat.id
    user = ensure_user_state(load_user(chat_id))
    track_visit(user)
    update_streak(user)

    lesson = user.get("current_lesson_data")
    if user.get("waiting_for_answer") and lesson:
        result = await process_answer(update, user, text, lesson)
        if result:
            track_practice(user, result.get("skill", ""), result.get("success", False))
            remember_feedback(user, result.get("skill", ""), result.get("success", False), text)
        save_user(chat_id, user)
        return

    if text == "🚀 начать обучение":
        if user.get("lesson_started") and not user.get("lesson_finished"):
            await update.message.reply_text("📚 Урок уже активен. Нажми ➡️ далее", reply_markup=get_main_keyboard(user))
            return

        user["active_lesson"] = next_locked_lesson(user)
        user["lesson_started"] = True
        user["lesson_finished"] = False
        if not user.get("current_lesson_data") or user.get("lesson_finished"):
            await update.message.reply_text("🧠 AI создаёт adaptive lesson...")
            user["current_lesson_data"] = generate_lesson(topic=user["active_lesson"], level=user["difficulty"])
            user["lesson_step"] = 0
        save_user(chat_id, user)
        await continue_lesson(update, user, user["current_lesson_data"])
        save_user(chat_id, user)
        return

    cleaned_next = normalized.replace("➡️", "").replace("➡", "").strip()
    if cleaned_next.startswith("далее") and user.get("lesson_started"):
        if not lesson:
            user["current_lesson_data"] = generate_lesson(topic=user["active_lesson"], level=user["difficulty"])
            user["lesson_step"] = 0
        await continue_lesson(update, user, user["current_lesson_data"])
        save_user(chat_id, user)
        return

    if text == "⏸ выйти из урока":
        user["lesson_started"] = False
        save_user(chat_id, user)
        await update.message.reply_text("⏸ Урок сохранён.", reply_markup=get_main_keyboard(user))
        return

    if text == "👤 профиль":
        mem = user.get("user_memory", {})
        await update.message.reply_text(
            f"👤 Профиль\n⭐ XP: {user['xp']}\n🏆 {get_rank(user['xp'])}\n🔥 Streak: {user.get('streak', 0)}\n"
            f"Strong: {', '.join(mem.get('strong_topics', [])) or 'Нет'}\nWeak: {', '.join(mem.get('weak_topics', [])) or 'Нет'}",
            reply_markup=get_main_keyboard(user),
        )
        return

    if text == "🗺 roadmap":
        done = set(user.get("completed_lessons", []))
        current = next_locked_lesson(user)
        rows = []
        for lesson_name in LESSONS:
            if lesson_name in done:
                icon = "✅"
            elif lesson_name == current:
                icon = "🔄"
            else:
                icon = "🔒"
            rows.append(f"{icon} {LESSON_TITLES.get(lesson_name, lesson_name.upper())}")
        percent = int((len(done) / len(LESSONS)) * 100)
        await update.message.reply_text("🧠 PRODUCT ROADMAP\n\n" + "\n".join(rows) + f"\n\n{progress_bar(percent)} {percent}%")
        return

    if text == "📊 прогресс":
        done = len(user.get("completed_lessons", []))
        total = len(LESSONS)
        percent = int((done / total) * 100)
        await update.message.reply_text(f"📊 Прогресс\n{progress_bar(percent)} {percent}%\n✅ {done}/{total}\n⭐ XP: {user['xp']}")
        return

    await show_home(update, user)
    save_user(chat_id, user)


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
print("🔥 AI PRODUCT COACH RUNNING")
app.run_polling()
