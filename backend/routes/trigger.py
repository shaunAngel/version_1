from fastapi import APIRouter
from services.db_service import *
from services.message_service import *
from services.twilio_service import send_whatsapp

router = APIRouter()

@router.get("/send-attendance/{parent_phone}")
def send_attendance(parent_phone: str):

    parent = get_parent_by_phone(parent_phone)
    children = get_children(parent["id"])

    student_id = children[0]

    data = get_attendance(student_id)
    msg = format_attendance(data)

    send_whatsapp(parent_phone, msg)

    return {"status": "sent"}


@router.get("/send-result/{parent_phone}")
def send_result(parent_phone: str):

    parent = get_parent_by_phone(parent_phone)
    children = get_children(parent["id"])

    student_id = children[0]

    data = get_results(student_id)
    msg = format_results(data)

    send_whatsapp(parent_phone, msg)

    return {"status": "sent"}