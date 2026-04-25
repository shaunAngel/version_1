from utils.supabase_client import supabase


def get_parent_by_phone(phone):
    res = supabase.table("user").select("*").eq("phone_number", phone).execute()
    return res.data[0] if res.data else None


def get_children(parent_id):
    res = supabase.table("parent_student_link").select("student_id").eq("parent_id", parent_id).execute()
    return [r["student_id"] for r in res.data]


def get_student(student_id):
    return supabase.table("user").select("*").eq("id", student_id).execute().data[0]


def get_attendance(student_id):
    return supabase.table("attendance").select("*").eq("student_id", student_id).execute().data


def get_results(student_id):
    return supabase.table("assignment_submission").select("*").eq("user_id", student_id).execute().data


def get_profile(student_id):
    result = supabase.table("student_profile").select("*").eq("student_id", student_id).execute().data

    if not result:
        return None

    return result[0]