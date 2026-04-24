import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Body
from fastapi.responses import Response, FileResponse
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

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
# 🌐 LANGUAGE DETECTION
# =========================
def detect_language(message):
    for ch in message:
        if '\u0C00' <= ch <= '\u0C7F':
            return "telugu"
    return "english"


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
# 📲 GENERIC WHATSAPP SEND
# =========================
@app.post("/send-message")
def send_message(data: dict = Body(...)):
    try:
        to_number = data.get("phone")
        message = data.get("message")

        if not to_number.startswith("+"):
            to_number = "+" + to_number

        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )

        client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
            body=message,
            to=f"whatsapp:{to_number}"
        )

        return {"status": "sent"}

    except Exception as e:
        print("SEND MESSAGE ERROR:", e)
        return {"status": "failed"}


# =========================
# 📄 SEND REPORT (FRONTEND)
# =========================
@app.post("/send-report")
def send_report(data: dict = Body(...)):
    try:
        phone = data.get("phone")

        if not phone.startswith("+"):
            phone = "+" + phone

        parent = get_parent_by_phone(phone)
        if not parent:
            return {"status": "failed"}

        student_id = get_children(parent["id"])[0]
        student = get_student(student_id)
        profile = get_profile(student_id)

        pdf_path = generate_pdf(student['username'], {
            "math": profile['math_score'],
            "science": profile['science_score'],
            "english": profile['english_score']
        })

        pdf_url = f"https://spruce-dab-catnip.ngrok-free.dev/pdf/{pdf_path}"

        ai_feedback = generate_ai_insight(student, profile)

        message = f"""📄 Student Report Card

Name: {student['username']}

Subjects:
- Math: {profile['math_score']}%
- Science: {profile['science_score']}%
- English: {profile['english_score']}%

🧠 AI Insight:
{ai_feedback}

📄 Download Report:
{pdf_url}
"""

        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )

        client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
            body=message,
            to=f"whatsapp:{phone}"
        )

        return {"status": "success"}

    except Exception as e:
        print("SEND REPORT ERROR:", e)
        return {"status": "failed"}


# =========================
# 🤖 TWILIO WEBHOOK
# =========================
@app.post("/webhook")
async def webhook(request: Request):
    form = await request.form()

    msg = form.get("Body", "")
    intent = detect_intent(msg)
    lang = detect_language(msg)

    sender = form.get("From").replace("whatsapp:", "")

    resp = MessagingResponse()

    parent = get_parent_by_phone(sender)

    if not parent:
        resp.message("❌ Number not registered")
        return Response(str(resp), media_type="application/xml")

    student_id = get_children(parent["id"])[0]
    student = get_student(student_id)
    profile = get_profile(student_id)

    # =========================
    # 📊 ATTENDANCE
    # =========================
    if intent == "attendance":
        data = get_attendance(student_id)

        present = sum(1 for d in data if d["status"] == "PRESENT")
        total = len(data)
        percent = round((present/total)*100, 2)

        if lang == "telugu":
            reply = f"""📊 హాజరు నివేదిక:

పేరు: {student['username']}
రోల్ నం: {profile['roll_number']}
తరగతి: {student['class']} | విభాగం: A

మొత్తం హాజరు: {percent}%
"""
        else:
            reply = f"""📊 Daily Attendance Report:

Name: {student['username']}
Roll No: {profile['roll_number']}
Class: {student['class']} | Section: A

Overall Attendance: {percent}%
"""

    # =========================
    # 💰 FEES
    # =========================
    elif intent == "fee":
        if lang == "telugu":
            reply = """💰 ఫీజు సమాచారం:

మీ పిల్లకు ₹25,000 ఫీజు బాకీ ఉంది.
చెల్లించవలసిన తేది: 30 సెప్టెంబర్

దయచేసి ఆలస్యం కాకుండా చెల్లించండి.

📞 సహాయం: +91 9123456780
"""
        else:
            reply = """💰 Fee Update:

Your ward has a pending fee balance of ₹25,000.
Due Date: 30 September.

Kindly clear the dues.

📞 Contact: +91 9123456780
"""

    # =========================
    # 🧠 COUNSELLING
    # =========================
    elif intent == "counselling":
        if lang == "telugu":
            reply = f"""🧠 కౌన్సెలింగ్ సూచన:

మీ పిల్ల {student['username']} చదువులో కొన్ని సవాళ్లు ఎదుర్కొంటున్నారు.

మేము కౌన్సెలింగ్ సూచిస్తున్నాము.

📞 కౌన్సెలర్: +91 9876543210
"""
        else:
            reply = f"""🧠 Counselling Recommendation:

Your ward {student['username']} is facing academic challenges.

We recommend counselling.

📞 Counsellor: +91 9876543210
"""

    # =========================
    # 🚌 TRANSPORT
    # =========================
    elif intent == "transport":
        if lang == "telugu":
            reply = """🚌 రవాణా సమాచారం:

బస్ నం: TS09 AB 1234

📞 డ్రైవర్: +91 9012345678
"""
        else:
            reply = """🚌 Transport Information:

Bus No: TS09 AB 1234

📞 Driver: +91 9012345678
"""

    # =========================
    # 📄 REPORT
    # =========================
    elif intent == "report":

        pdf_path = generate_pdf(student['username'], {
            "math": profile['math_score'],
            "science": profile['science_score'],
            "english": profile['english_score']
        })

        pdf_url = f"https://spruce-dab-catnip.ngrok-free.dev/pdf/{pdf_path}"

        ai_feedback = generate_ai_insight(student, profile)

        if lang == "telugu":
            reply = f"""📄 విద్యార్థి రిపోర్ట్

పేరు: {student['username']}

గణితం: {profile['math_score']}%
సైన్స్: {profile['science_score']}%
ఇంగ్లీష్: {profile['english_score']}%

🧠 విశ్లేషణ:
{ai_feedback}

📄 డౌన్‌లోడ్:
{pdf_url}
"""
        else:
            reply = f"""📄 Student Report Card

Name: {student['username']}

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
    # 🎉 HOLIDAY
    # =========================
    elif intent == "holiday":
        if lang == "telugu":
            reply = "🎉 సెలవుల జాబితా అందుబాటులో ఉంది."
        else:
            reply = "🎉 Holiday list available."

    else:
        reply = "Try: attendance / fee / counselling / holiday / report / transport"

    resp.message(reply)
    return Response(str(resp), media_type="application/xml")