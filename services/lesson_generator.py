# services/lesson_generator.py

from openai import OpenAI
import json

from config import get_env, get_required_env

# =====================================================
# DEEPSEEK CLIENT
# =====================================================

client = OpenAI(
    api_key=get_required_env("DEEPSEEK_API_KEY"),
    base_url=get_env("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
)

# =====================================================
# GENERATE LESSON
# =====================================================

def generate_lesson(
    topic,
    level="junior"
):

    prompt = f"""

Создай глубокий edtech урок
в стиле Яндекс Практикума.

Тема:
{topic}

Уровень:
{level}

# СТРУКТУРА УРОКА

1. intro
2. theory
3. case
4. reflection
5. quiz
6. practice
7. summary

# ТРЕБОВАНИЯ

- теория должна быть длинной
- объяснение через реальные кейсы
- storytelling
- ощущение преподавателя
- human tone
- deep explanation
- practical thinking
- product mindset
- mini article style
- не сухой текст

# ВЕРНИ JSON

Пример структуры:

{{
  "title": "JTBD",

  "blocks": [

    {{
      "type": "intro",

      "text": "..."
    }},

    {{
      "type": "theory",

      "text": "..."
    }},

    {{
      "type": "reflection",

      "text": "..."
    }},

    {{
      "type": "quiz",

      "question": "...",

      "keywords": [
        "..."
      ],

      "success_text": "...",

      "fail_text": "...",

      "skill": "..."
    }},

    {{
      "type": "practice",

      "task": "...",

      "keywords": [
        "..."
      ],

      "success_text": "...",

      "fail_text": "...",

      "skill": "..."
    }}

  ]
}}

"""

    # =====================================================
    # DEEPSEEK REQUEST
    # =====================================================

    response = client.chat.completions.create(

        model=get_env("DEEPSEEK_MODEL", "deepseek-chat"),

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.7
    )

    # =====================================================
    # RESPONSE CONTENT
    # =====================================================

    content = (
        response
        .choices[0]
        .message
        .content
    )

    # =====================================================
    # REMOVE MARKDOWN
    # =====================================================

    content = (
        content
        .replace(
            "```json",
            ""
        )
        .replace(
            "```",
            ""
        )
        .strip()
    )

    # =====================================================
    # SAFE JSON PARSE
    # =====================================================

    try:

        lesson = json.loads(
            content
        )

    # =====================================================
    # FALLBACK LESSON
    # =====================================================

    except Exception:

        lesson = {

            "title": topic,

            "blocks": [

                {
                    "type": "intro",

                    "text": (
                        f"📚 Урок: {topic.upper()}\n\n"

                        "Сегодня ты изучишь тему\n"
                        "через theory + practice."
                    )
                },

                {
                    "type": "theory",

                    "text": (
                        "📘 DeepSeek вернул\n"
                        "нестабильный JSON.\n\n"

                        "Но AI generation уже работает.\n\n"

                        "Следующий шаг:\n"
                        "сделать production parser."
                    )
                }

            ]
        }

    # =====================================================
    # RETURN LESSON
    # =====================================================

    return lesson