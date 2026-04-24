def format_attendance(data):
    present = sum(1 for d in data if d["status"] == "PRESENT")
    total = len(data)

    return f"📊 Attendance: {present}/{total} classes present."


def format_results(data):
    msg = "📊 Results:\n"
    for d in data:
        msg += f"Score: {d['score']}/{d['total']} ({d['percentage']}%)\n"

    return msg