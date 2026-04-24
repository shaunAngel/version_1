const BASE_URL = "https://spruce-dab-catnip.ngrok-free.dev";

const statusText = document.getElementById("status-text");

function updateStatus(message, type = "info") {
    statusText.textContent = message;

    // optional color feedback
    statusText.style.color =
        type === "success" ? "#22c55e" :
        type === "error" ? "#ef4444" :
        "#ffffff";
}


// =========================
// 📊 SEND ATTENDANCE
// =========================
async function sendAttendance() {
    updateStatus("⏳ Sending attendance...");

    try {
        const response = await fetch(`${BASE_URL}/send-message`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                phone: "917680053973",
                message: "📊 Attendance Update:\n\nAkash was PRESENT today.\nOverall Attendance: 92%"
            })
        });

        const data = await response.json();

        if (data.status === "sent") {
            updateStatus("✅ Attendance sent to WhatsApp!", "success");
        } else {
            updateStatus("❌ Failed to send attendance", "error");
        }

    } catch (error) {
        console.error(error);
        updateStatus("❌ Backend not reachable", "error");
    }
}


// =========================
// 📄 SEND REPORT + PDF
// =========================
async function sendReport() {
    updateStatus("⏳ Generating report and sending...");

    try {
        const response = await fetch(`${BASE_URL}/send-report`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                phone: "917680053973"
            })
        });

        const data = await response.json();

        console.log("Backend response:", data);

        if (data.status === "success") {
            updateStatus("✅ Report + PDF sent to WhatsApp!", "success");
        } else {
            updateStatus("❌ Failed to send report", "error");
        }

    } catch (error) {
        console.error(error);
        updateStatus("❌ Backend not reachable", "error");
    }
}


// =========================
// 🔗 BUTTON BINDINGS
// =========================
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("btn-attendance").addEventListener("click", sendAttendance);
    document.getElementById("btn-report").addEventListener("click", sendReport);
});