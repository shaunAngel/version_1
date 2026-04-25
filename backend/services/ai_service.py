import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================
# 🧠 AI INTENT DETECTION (FINAL)
# =========================
def detect_intent(message):
    msg = message.lower()

    # =========================
    # 🔥 SMART NATURAL QUERIES (HIGHEST PRIORITY)
    # =========================

    # REPORT
    if any(q in msg for q in [
        "how is my child", "how is my child doing",
        "child performance", "academic progress",
        "performance summary"
    ]):
        return "report"

    # ATTENDANCE
    if any(q in msg for q in [
        "attendance percentage", "today attendance",
        "was my child present", "how is attendance"
    ]):
        return "attendance"

    # FEES
    if any(q in msg for q in [
        "fees pending", "payment due",
        "fee details", "balance amount",
        "pay fees"
    ]):
        return "fee"

    # COUNSELLING
    if any(q in msg for q in [
        "needs help", "student stress",
        "behavioral issues", "guidance support"
    ]):
        return "counselling"

    # TRANSPORT
    if any(q in msg for q in [
        "bus details", "where is the bus",
        "driver number", "pickup timing"
    ]):
        return "transport"

    # HOLIDAY
    if any(q in msg for q in [
        "is tomorrow a holiday",
        "holiday list", "leave tomorrow",
        "upcoming holidays"
    ]):
        return "holiday"

    # =========================
    # 🤖 AI CLASSIFICATION
    # =========================
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
Classify into ONE word ONLY:
attendance, report, fee, counselling, holiday, transport, unknown
"""
                },
                {"role": "user", "content": message}
            ],
            max_tokens=5
        )

        intent = response.choices[0].message.content.strip().lower()

        # 🔥 NORMALIZATION
        if intent in ["fees", "finance", "payment", "due", "dues", "amount"]:
            return "fee"

        if intent in ["bus", "vehicle"]:
            return "transport"

        if intent in ["help", "support"]:
            return "counselling"

        if intent in ["leave"]:
            return "holiday"

        if intent in ["attendance", "report", "fee", "counselling", "holiday", "transport"]:
            return intent

        print("⚠️ AI gave:", intent)

    except Exception as e:
        print("Intent AI Error:", e)

    # =========================
    # 🔥 FALLBACK (NEVER FAILS)
    # =========================

    if any(word in msg for word in ["fee", "fees", "pending", "due", "payment", "balance", "amount", "ఫీజు"]):
        return "fee"

    elif any(word in msg for word in ["attendance", "present", "absent", "హాజరు"]):
        return "attendance"

    elif any(word in msg for word in ["report", "marks", "grade", "result", "performance", "రిపోర్ట్"]):
        return "report"

    elif any(word in msg for word in ["counselling", "help", "support", "సహాయం"]):
        return "counselling"

    elif any(word in msg for word in ["holiday", "leave", "సెలవు"]):
        return "holiday"

    elif any(word in msg for word in ["bus", "transport", "route", "బస్"]):
        return "transport"

    else:
        return "unknown"


# =========================
# 🧠 AI PERFORMANCE INSIGHT
# =========================
def generate_ai_insight(student, profile):
    try:
        prompt = f"""
Student Name: {student['username']}
Math: {profile['math_score']}
Science: {profile['science_score']}
English: {profile['english_score']}

Give a short 2-line performance insight for parents.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful school assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI Error:", e)

        # 🔥 fallback
        return f"{student['username']} is performing well academically with steady progress."