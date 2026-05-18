from .direction_builder import build_direction_block
from .emotional_feedback import needs_emotion_prompt


OPEN_STARTS = (
    "что", "как", "почему", "зачем",
    "опиши", "расскажи", "вспомни", "когда"
)
CLOSED_MARKERS = (
    "да или нет", "да/нет", "купил бы", "будете ли",
    "будешь ли", "хотели бы", "нравится ли"
)


def build_answer_coach_feedback(answer_text, coverage=None):
    text = (answer_text or "").strip().lower()
    if not text:
        return ""

    coverage = coverage or {}
    matched_keywords = coverage.get("matched_keywords") or []
    missed_keywords = coverage.get("missed_keywords") or []

    direction_block = build_direction_block(
        answer_text=text,
        matched_keywords=matched_keywords,
        missed_keywords=missed_keywords,
    )

    lines = []
    questions = [part.strip() for part in text.split("?") if part.strip()]
    question_count = text.count("?")

    open_questions = 0
    closed_questions = 0
    for raw in questions:
        trimmed = raw.strip(" .,!?:;")
        if trimmed.startswith(OPEN_STARTS):
            open_questions += 1
        if any(marker in trimmed for marker in CLOSED_MARKERS) or " ли " in f" {trimmed} ":
            closed_questions += 1

    if question_count:
        lines.append(f"• Вопросов в ответе: {question_count}")
        lines.append(f"• Открытых формулировок: {open_questions}")
    if closed_questions:
        lines.append("• Вижу вопросы, на которые можно ответить «да/нет». Для CustDev лучше переформулировать их в открытые.")
    if "последний" not in text and "в прошлый" not in text:
        lines.append("• Добавь вопрос про реальный прошлый опыт: «Расскажи про последний раз, когда…».")
    if needs_emotion_prompt(text):
        lines.append("• Добавь вопрос про эмоции: «Что в этом процессе бесило/злило сильнее всего?».")

    teacher_block = ""
    if lines:
        teacher_block = "\n\n🧠 Разбор как преподаватель:\n" + "\n".join(lines)

    return direction_block + teacher_block
