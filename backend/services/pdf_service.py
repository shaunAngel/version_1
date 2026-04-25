from fpdf import FPDF

def generate_pdf(name, data):
    file_path = f"{name}_report.pdf"

    pdf = FPDF()
    pdf.add_page()

    # ===== HEADER =====
    pdf.set_fill_color(30, 136, 229)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, "STUDENT REPORT CARD", 0, 1, "C", fill=True)

    pdf.ln(5)

    # Reset text color
    pdf.set_text_color(0, 0, 0)

    # ===== PHOTO =====
    img_x, img_y, img_w, img_h = 150, 25, 35, 40
    try:
        pdf.image("akash.jpg", x=img_x, y=img_y, w=img_w, h=img_h)
    except:
        pass

    # ===== STUDENT DETAILS =====
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Student Details", 0, 1)

    pdf.set_font("Arial", "", 11)

    # keep width limited so it doesn't overlap image
    pdf.cell(120, 7, f"Name: {name}", 0, 1)
    pdf.cell(120, 7, "Roll No: A123", 0, 1)
    pdf.cell(120, 7, "Attendance: 50.0%", 0, 1)
    pdf.cell(120, 7, "BMI: 17.75", 0, 1)

    pdf.ln(4)

    # ===== ACADEMIC PERFORMANCE =====
    pdf.set_fill_color(200, 200, 200)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 9, "Academic Performance", 0, 1, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Math: {data['math']}%", 0, 1)
    pdf.cell(0, 7, f"Science: {data['science']}%", 0, 1)
    pdf.cell(0, 7, f"English: {data['english']}%", 0, 1)

    pdf.cell(0, 7, "Overall: 80% | Grade: A", 0, 1)

    pdf.ln(4)

    # ===== PERFORMANCE INDICATOR =====
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Performance Indicator", 0, 1)

    def draw_bar(label, value, color):
        pdf.set_font("Arial", "", 10)
        pdf.cell(35, 6, label)

        bar_width = 110
        filled_width = (value / 100) * bar_width

        # background
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(bar_width, 6, "", 0, 0, fill=True)

        # filled bar
        pdf.set_xy(pdf.get_x() - bar_width, pdf.get_y())
        pdf.set_fill_color(*color)
        pdf.cell(filled_width, 6, "", 0, 0, fill=True)

        pdf.cell(0, 6, f" {value}%", 0, 1)

    draw_bar("Math", data['math'], (39, 174, 96))       # green
    draw_bar("Science", data['science'], (241, 196, 15)) # yellow
    draw_bar("English", data['english'], (39, 174, 96))

    pdf.ln(4)

    # ===== EXTRACURRICULAR =====
    pdf.set_fill_color(200, 200, 200)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 9, "Extracurricular Activities", 0, 1, fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, "Art: A", 0, 1)
    pdf.cell(0, 7, "Sports: B", 0, 1)
    pdf.cell(0, 7, "Dance: A", 0, 1)
    pdf.cell(0, 7, "Music: B", 0, 1)

    pdf.ln(4)

    # ===== TEACHER FEEDBACK =====
    pdf.set_fill_color(240, 230, 180)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 9, "Teacher Feedback", 0, 1, fill=True)

    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0, 6,
        f"{name} shows consistent academic performance across subjects.\n"
        "He actively participates in both classroom and extracurricular activities.\n"
        "There is scope for improvement in analytical thinking, especially in Science.\n"
        "With continued effort, he is expected to achieve higher excellence."
    )

    pdf.output(file_path)
    return file_path