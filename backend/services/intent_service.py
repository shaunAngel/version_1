def detect_intent(message: str):
    msg = message.lower()

    if "attendance" in msg:
        return "attendance"
    elif "result" in msg or "score" in msg:
        return "result"
    else:
        return "general"