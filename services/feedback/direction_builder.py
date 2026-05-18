def build_direction_block(answer_text: str, matched_keywords, missed_keywords) -> str:
    text = (answer_text or "").strip().lower()
    direction = ["\n\n🧭 Куда двигаемся дальше:"]

    if matched_keywords:
        direction.append("• Ты уже в верном направлении: есть базовые элементы ответа.")

    if missed_keywords:
        direction.append(
            "• Следующий шаг: добавь недостающие элементы по одному, "
            "а не пытайся переписать всё с нуля."
        )
        direction.append(
            "• План на 1 итерацию: выбери 2 пункта из «Добавь идеи» "
            "и встрои их в короткий сценарий."
        )

    direction.append(
        "• Формула сильного ответа: "
        "контекст пользователя → конкретное действие → ручная проверка ценности."
    )

    if text.count("?") == 0:
        direction.append(
            "• Добавь 1-2 конкретных вопроса к пользователю, "
            "чтобы ответ был проверяемым."
        )

    if not missed_keywords and matched_keywords:
        return (
            "\n\n🧭 Куда двигаемся дальше:\n"
            "• Отлично, вектор верный. Добавь больше конкретики из реального опыта пользователя."
        )

    return "\n".join(direction)
