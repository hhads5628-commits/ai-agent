from gamification.progression import get_rank
from handlers.keyboards import get_main_keyboard
from models.constants import LESSON_TITLES


async def show_home(update, user: dict):
    active = user.get("active_lesson", "jtbd")
    quests = user.get("daily_quests", {})
    text = (
        "🏠 AI Product Coach\n\n"
        f"📚 Current lesson: {LESSON_TITLES.get(active, active.upper())}\n"
        f"🔥 Streak: {user.get('streak', 0)} days\n"
        f"⭐ XP: {user['xp']}\n"
        f"🏆 Rank: {get_rank(user['xp'])}\n\n"
        "🎯 Daily quests:\n"
        f"{'✅' if quests.get('lesson') else '⬜'} 1 lesson\n"
        f"{'✅' if quests.get('practice_cases', 0) >= 2 else '⬜'} 2 practice cases\n"
        f"{'✅' if quests.get('xp_today', 0) >= 50 else '⬜'} 50 XP\n\n"
        f"➡️ Next action: {'продолжай урок' if user.get('lesson_started') else 'нажми 🚀 начать обучение'}"
    )
    await update.message.reply_text(text, reply_markup=get_main_keyboard(user))
