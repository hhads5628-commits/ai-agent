EMOTION_MARKERS = (
    "бесит", "бесило", "злит", "раздраж", "обидно",
    "стресс", "тревог", "рад", "доволен", "устал"
)


def needs_emotion_prompt(text: str) -> bool:
    lowered = (text or "").lower()
    return not any(marker in lowered for marker in EMOTION_MARKERS)
