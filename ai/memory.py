from debug.qa_logger import log_memory_change

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

    log_memory_change(
        str(user.get("id", "unknown")),
        mem.get("weak_topics", []),
        mem.get("strong_topics", []),
        len(mem.get("mistakes", [])),
    )
