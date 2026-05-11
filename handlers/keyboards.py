from telegram import ReplyKeyboardMarkup


def get_main_keyboard(user: dict) -> ReplyKeyboardMarkup:
    if user.get("lesson_started"):
        return ReplyKeyboardMarkup([["➡️ далее"], ["⏸ выйти из урока"]], resize_keyboard=True)
    return ReplyKeyboardMarkup(
        [["🚀 начать обучение"], ["📊 прогресс", "👤 профиль"], ["🗺 roadmap", "📚 выбрать урок"], ["⚙️ настройки обучения"]],
        resize_keyboard=True,
    )
