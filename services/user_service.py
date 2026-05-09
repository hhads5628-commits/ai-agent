import json
import os

# ======================
# ПАПКА USERS
# ======================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

USERS_DIR = os.path.join(
    BASE_DIR,
    "data",
    "users"
)

# создаём папку если нет
os.makedirs(USERS_DIR, exist_ok=True)

# ======================
# ПУТЬ ПОЛЬЗОВАТЕЛЯ
# ======================

def get_user_file(chat_id):

    return os.path.join(
        USERS_DIR,
        f"{chat_id}.json"
    )

# ======================
# ЗАГРУЗКА
# ======================

def load_user(chat_id):

    file_path = get_user_file(chat_id)

    # новый пользователь
    if not os.path.exists(file_path):

        return {
            "name": "Игрок",

            "goal": "Стать Product Manager",

            "track": "General PM",

            "difficulty": "Beginner",

            "learning_style": "Теория + практика",

            "daily_time": "30 минут",

            "active_lesson": None,

            "completed_lessons": [],

            "xp": 0,

            "tasks_done": 0
        }

    with open(file_path, "r", encoding="utf-8") as f:

        return json.load(f)

# ======================
# СОХРАНЕНИЕ
# ======================

def save_user(chat_id, data):

    file_path = get_user_file(chat_id)

    with open(file_path, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )