import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================
# 🧠 AI INTENT DETECTION
# =========================
def detect_intent(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
You are an intent classifier for a school chatbot.

Classify the message into ONE of these intents:
attendance, report, fee, counselling, holiday, transport, unknown

Examples:
- "how is my child doing" → report
- "show performance" → report
- "marks" → report
- "progress report" → report
- "attendance today" → attendance
- "is he absent" → attendance
- "fees pending" → fee
- "any payment due" → fee
- "need help" → counselling
- "talk to counsellor" → counselling
- "bus details" → transport

Return ONLY the intent word.
"""
                },
                {"role": "user", "content": message}
            ],
            max_tokens=10
        )

        return response.choices[0].message.content.strip().lower()

    except Exception as e:
        print("Intent AI Error:", e)

        # 🔥 STRONG FALLBACK (VERY IMPORTANT)
        msg = message.lower()

        if any(x in msg for x in ["attendance", "absent", "present"]):
            return "attendance"

        elif any(x in msg for x in ["report", "marks", "performance", "doing", "progress"]):
            return "report"

        elif "fee" in msg or "payment" in msg:
            return "fee"

        elif any(x in msg for x in ["counselling", "help", "support"]):
            return "counselling"

        elif "holiday" in msg:
            return "holiday"

        elif any(x in msg for x in ["bus", "transport"]):
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

        # 🔥 fallback logic (never fails)
        math = profile['math_score']
        science = profile['science_score']
        english = profile['english_score']

        insights = []
        weak = []

        if math >= 75:
            insights.append("strong in Math")
        elif math < 60:
            weak.append("Math")

        if science >= 75:
            insights.append("good in Science")
        elif science < 60:
            weak.append("Science")

        if english >= 75:
            insights.append("doing well in English")
        elif english < 60:
            weak.append("English")

        msg = f"{student['username']} is "

        if insights:
            msg += ", ".join(insights)
        else:
            msg += "showing average performance"

        if weak:
            msg += f", but needs improvement in {', '.join(weak)}"

        msg += "."

        return msg