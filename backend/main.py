from fastapi import FastAPI, Request
from fastapi.responses import Response, FileResponse
from twilio.twiml.messaging_response import MessagingResponse

from services.db_service import (
    get_parent_by_phone,
    get_children,
    get_student,
    get_attendance,
    get_results,
    get_profile
)

from services.pdf_service import generate_pdf

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Backend running 🚀"}


# ✅ Serve PDF properly
@app.get("/pdf/{filename}")
def get_pdf(filename: str):
    return FileResponse(filename, media_type='application/pdf')


@app.post("/webhook")
async def webhook(request: Request):
    form = await request.form()

    msg = form.get("Body", "").lower()
    sender = form.get("From").replace("whatsapp:", "")

    print("Message:", msg)
    print("Sender:", sender)

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
    if "attendance" in msg:
        data = get_attendance(student_id)

        subjects = ["Math", "Science", "English", "Social", "Computer"]

        report = "📊 Daily Attendance Report:\n\n"
        report += f"{student['username']}\n\n"

        for i, d in enumerate(data):
            subject = subjects[i % len(subjects)]
            report += f"{subject} → {d['status']}\n"

        present = sum(1 for d in data if d["status"] == "PRESENT")
        total = len(data)

        report += f"\nOverall Attendance: {round((present/total)*100, 2)}%"

        reply = report

    # =========================
    # 💰 FEES
    # =========================
    elif "fee" in msg:
        reply = """💰 Fee Update:

Your ward has a pending fee balance of ₹25,000.
Due Date: 30 September.

Kindly clear the dues at the earliest to avoid late penalties.

📞 For assistance, please contact the Front Office: +91 9123456780"""

    # =========================
    # 🧠 COUNSELLING
    # =========================
    elif "counselling" in msg:
        reply = f"""🧠 Counselling Recommendation:

We would like to bring to your attention that your ward, {student['username']}, has been facing certain academic and behavioral challenges.

We recommend scheduling a session with the school counsellor.

📞 Counsellor Contact: +91 9876543210
🕘 Available Hours: 9:00 AM – 4:00 PM"""

    # =========================
    # 🎉 HOLIDAYS
    # =========================
    elif "holiday" in msg:
        reply = """🎉 Holiday Notice:

The list of holidays for this semester.
More details: https://school-portal.com/holidays"""

    # =========================
    # 🚌 TRANSPORT
    # =========================
    elif "transport" in msg or "bus" in msg:
        reply = """🚌 Transport Information:

Your ward is assigned to Bus No: TS09 AB 1234

📞 Driver Contact: +91 9012345678"""

    # =========================
    # 📄 REPORT (FIXED LINK)
    # =========================
    elif "report" in msg:
        pdf_path = generate_pdf(student['username'], {
            "math": profile['math_score'],
            "science": profile['science_score'],
            "english": profile['english_score']
        })

        reply = f"""📄 Student Report Card

Name: {student['username']}
Cumulative Attendance: 50.0%

Subjects:
- Math: {profile['math_score']}%
- Science: {profile['science_score']}%
- English: {profile['english_score']}%

Physical Stats:
Height: {profile['height']} cm
Weight: {profile['weight']} kg

Overall Performance: Good 👍

📄 Download Report:
https://spruce-dab-catnip.ngrok-free.dev/pdf/{pdf_path}
"""

    else:
        reply = "Try: attendance / fee / counselling / holiday / report / transport"

    resp.message(reply)

    return Response(str(resp), media_type="application/xml")