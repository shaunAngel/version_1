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

Classify the message into ONE word from:
attendance, report, fee, counselling, holiday, transport, unknown

Understand both English and Telugu.

Examples:
"attendance" → attendance
"how is attendance" → attendance
"నా పిల్ల హాజరు ఎంత" → attendance
"report card" → report
"రిపోర్ట్ చూపించు" → report
"fees pending" → fee
"ఫీజు ఎంత" → fee

Return ONLY one word.
"""
                },
                {"role": "user", "content": message}
            ],
            max_tokens=10
        )

        return response.choices[0].message.content.strip().lower()

    except Exception as e:
        print("Intent AI Error:", e)

        msg = message.lower()

        # 🔥 ADD TELUGU KEYWORDS HERE
        if "attendance" in msg or "హాజరు" in msg:
            return "attendance"
        elif "report" in msg or "రిపోర్ట్" in msg:
            return "report"
        elif "fee" in msg or "ఫీజు" in msg:
            return "fee"
        elif "counselling" in msg or "సహాయం" in msg:
            return "counselling"
        elif "holiday" in msg or "సెలవు" in msg:
            return "holiday"
        elif "bus" in msg or "transport" in msg or "బస్" in msg:
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
def detect_language(message):
    # simple Telugu unicode check
    for ch in message:
        if '\u0C00' <= ch <= '\u0C7F':
            return "telugu"
    return "english"       