import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import Response, FileResponse
from twilio.twiml.messaging_response import MessagingResponse

from services.ai_service import generate_ai_insight, detect_intent
from services.db_service import (
    get_parent_by_phone,
    get_children,
    get_student,
    get_attendance,
    get_profile
)
from services.pdf_service import generate_pdf

app = FastAPI()

# =========================
# 🌐 CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🏠 HOME
# =========================
@app.get("/")
def home():
    return {"message": "Backend running 🚀"}

# =========================
# 📄 SERVE PDF
# =========================
@app.get("/pdf/{filename}")
def get_pdf(filename: str):
    return FileResponse(filename, media_type='application/pdf')

# =========================
# 📅 SEND ATTENDANCE
# =========================
@app.get("/send-attendance")
def send_attendance():
    print("\n===== ATTENDANCE GENERATED =====")

    attendance_text = """📊 Daily Attendance Report:

Name: Akash
Roll No: A123
Class: 5 | Section: A

Math → PRESENT
Science → ABSENT

Overall Attendance: 50.0%
"""
    print(attendance_text)

    return {"status": "success"}

# =========================
# 📄 SEND REPORT
# =========================
@app.post("/send-report")
def send_report():
    try:
        student = {"username": "Akash"}
        profile = {
            "math_score": 80,
            "science_score": 75,
            "english_score": 85
        }

        attendance_percent = 50.0

        pdf_path = generate_pdf(student['username'], {
            "math": profile['math_score'],
            "science": profile['science_score'],
            "english": profile['english_score']
        })

        pdf_url = f"https://spruce-dab-catnip.ngrok-free.dev/pdf/{pdf_path}"

        ai_feedback = "Akash is strong in Math, good in Science, doing well in English."

        message = f"""📄 Student Report Card

Name: {student['username']}
Cumulative Attendance: {attendance_percent}%

Subjects:
- Math: {profile['math_score']}%
- Science: {profile['science_score']}%
- English: {profile['english_score']}%

🧠 AI Insight:
{ai_feedback}

📄 Download Report:
{pdf_url}
"""

        print("\n===== REPORT GENERATED =====")
        print(message)

        return {"status": "success"}

    except Exception as e:
        print("SEND REPORT ERROR:", e)
        return {"status": "failed"}

## =========================
# 🌐 LANGUAGE DETECTION
# =========================
def detect_language(message):
    for ch in message:
        if '\u0C00' <= ch <= '\u0C7F':
            return "telugu"
    return "english"


# =========================
# 🤖 WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):
    form = await request.form()

    msg = form.get("Body", "")
    intent = detect_intent(msg)
    language = detect_language(msg)   # 🔥 NEW LINE

    sender = form.get("From").replace("whatsapp:", "")
    resp = MessagingResponse()

    parent = get_parent_by_phone(sender)

    if not parent:
        resp.message("❌ Number not registered")
        return Response(str(resp), media_type="application/xml")

    student_id = get_children(parent["id"])[0]
    student = get_student(student_id)
    profile = get_profile(student_id)

    if not profile:
        resp.message("❌ Student data not found")
        return Response(str(resp), media_type="application/xml")

    # =========================
    # 📊 ATTENDANCE
    # =========================
    if intent == "attendance":
        data = get_attendance(student_id)
        present = sum(1 for d in data if d["status"] == "PRESENT")
        total = len(data)
        percent = round((present / total) * 100, 2)

        if language == "telugu":
            reply = f"""📊 హాజరు నివేదిక

పేరు: {student['username']}
హాజరు: {percent}%"""
        else:
            reply = f"""📊 Attendance Report

Name: {student['username']}
Attendance: {percent}%"""

    # =========================
    # 📄 REPORT
    # =========================
    elif intent == "report":
        data = get_attendance(student_id)
        present = sum(1 for d in data if d["status"] == "PRESENT")
        total = len(data)
        percent = round((present / total) * 100, 2)

        pdf_path = generate_pdf(student['username'], {
            "math": profile['math_score'],
            "science": profile['science_score'],
            "english": profile['english_score']
        })

        pdf_url = f"https://spruce-dab-catnip.ngrok-free.dev/pdf/{pdf_path}"
        ai_feedback = generate_ai_insight(student, profile)

        if language == "telugu":
            reply = f"""📄 రిపోర్ట్ కార్డ్

పేరు: {student['username']}
మొత్తం హాజరు: {percent}%

విషయాలు:
- గణితం: {profile['math_score']}%
- సైన్స్: {profile['science_score']}%
- ఇంగ్లీష్: {profile['english_score']}%

🧠 విశ్లేషణ:
{ai_feedback}

📄 డౌన్‌లోడ్:
{pdf_url}
"""
        else:
            reply = f"""📄 Student Report Card

Name: {student['username']}
Cumulative Attendance: {percent}%

Subjects:
- Math: {profile['math_score']}%
- Science: {profile['science_score']}%
- English: {profile['english_score']}%

🧠 AI Insight:
{ai_feedback}

📄 Download Report:
{pdf_url}
"""

    # =========================
    # 💰 FEES
    # =========================
    elif intent == "fee":
        if language == "telugu":
            reply = """💰 ఫీజు సమాచారం:

మీ పిల్లకు ₹2,05,000 ఫీజు బాకీ ఉంది.
చెల్లించవలసిన తేది: 25 ఏప్రిల్

దయచేసి ఆలస్యం కాకుండా చెల్లించండి.

📞 సహాయం: +91 9123456780
"""
        else:
            reply = """💰 Fee Update:

Your ward has a pending fee balance of ₹2,05,000.
Due Date: 25 April.

Kindly clear the dues at the earliest to avoid late penalties.

📞 For assistance, please contact the Front Office: +91 9123456780
"""

    # =========================
    # 🧠 COUNSELLING
    # =========================
    elif intent == "counselling":
        if language == "telugu":
            reply = """🧠 కౌన్సెలింగ్ సూచన:

మీ పిల్లవాడు ఇటీవల కొంత విద్యా మరియు ప్రవర్తనా సమస్యలను ఎదుర్కొంటున్నాడు.

మా ఉపాధ్యాయులు అదనపు మార్గదర్శకం అవసరం ఉందని గమనించారు.

📞 కౌన్సిలర్: +91 9876543210
🕘 సమయం: 9 AM – 4 PM

మీ పిల్లవారి అభివృద్ధికి మేము ఎల్లప్పుడూ మీతో ఉన్నాము.
"""
        else:
            reply = """🧠 Counselling Recommendation:

We would like to bring to your attention that your ward, Akash, has been facing certain academic and behavioral challenges.

We strongly recommend scheduling a session with the school counsellor.

📞 Counsellor Contact: +91 9876543210
🕘 Available Hours: 9:00 AM – 4:00 PM
"""

    # =========================
    # 🚌 TRANSPORT
    # =========================
    elif intent == "transport":
        if language == "telugu":
            reply = """🚌 రవాణా సమాచారం:

మీ పిల్లవాడు ఈ బస్సుకు కేటాయించబడ్డారు:

బస్ నం: TS09 AB 1234

📞 డ్రైవర్ సంప్రదింపు: +91 9012345678
"""
        else:
            reply = """🚌 Transport Information:

Your ward is assigned to Bus No: TS09 AB 1234

📞 Driver Contact: +91 9012345678
"""

    # =========================
    # 🎉 HOLIDAY
    # =========================
    elif intent == "holiday":
        if language == "telugu":
            reply = """🎉 సెలవు సమాచారం:

రేపు పాఠశాలకు సెలవు ఉంది.
"""
        else:
            reply = """🎉 Holiday Notice:

Tomorrow is declared a holiday due to a school event.
"""

    else:
        reply = "Try: attendance / report / fees / transport / counselling"

    print("\n===== WHATSAPP REPLY =====")
    print(reply)

    resp.message(reply)
    return Response(str(resp), media_type="application/xml")