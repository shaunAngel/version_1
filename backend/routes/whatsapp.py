from fastapi import APIRouter, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from services.db_service import *
from services.intent_service import detect_intent
from services.message_service import *

router = APIRouter()

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()

    incoming_msg = form.get("Body")
    sender = form.get("From").replace("whatsapp:", "")

    parent = get_parent_by_phone(sender)

    resp = MessagingResponse()

    if not parent:
        resp.message("❌ Parent not registered.")
        return Response(str(resp), media_type="application/xml")

    children = get_children(parent["id"])
    student_id = children[0]  # simple demo

    intent = detect_intent(incoming_msg)

    if intent == "attendance":
        data = get_attendance(student_id)
        reply = format_attendance(data)

    elif intent == "result":
        data = get_results(student_id)
        reply = format_results(data)

    else:
        reply = "🤖 Ask about attendance or results."

    resp.message(reply)
    return Response(str(resp), media_type="application/xml")