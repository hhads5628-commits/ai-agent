def ensure_user_memory(user: dict) -> None:
    user.setdefault("user_memory", {
        "weak_topics": [],
        "strong_topics": [],
        "mistakes": [],
        "last_activity": "",
    })


def remember_feedback(user: dict, skill: str, success: bool, answer: str) -> None:
    ensure_user_memory(user)
    mem = user["user_memory"]
    if success:
        if skill and skill not in mem["strong_topics"]:
            mem["strong_topics"].append(skill)
        if skill in mem["weak_topics"]:
            mem["weak_topics"].remove(skill)
    else:
        if skill and skill not in mem["weak_topics"]:
            mem["weak_topics"].append(skill)
        mem["mistakes"].append({"skill": skill, "answer": answer[:200]})
