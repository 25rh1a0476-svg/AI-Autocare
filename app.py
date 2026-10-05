from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PIL import Image
import sqlite3
from datetime import datetime

from ai.diagnosis import diagnose_vehicle


app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


DATABASE = "autocare.db"


# =========================
# DATABASE CONNECTION
# =========================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# DATABASE INITIALIZATION
# =========================

def initialize_database():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT,
            model TEXT,
            year INTEGER,
            mileage INTEGER,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnoses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            symptoms TEXT,
            diagnosis TEXT,
            severity TEXT,
            confidence REAL,
            estimated_cost TEXT,
            recommendations TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            title TEXT NOT NULL,
            due_date TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT
        )
    """)

    # Add demo vehicle if database is empty
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    vehicle_count = cursor.fetchone()[0]

    if vehicle_count == 0:

        cursor.execute("""
            INSERT INTO vehicles
            (name, brand, model, year, mileage, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "My Car",
            "Toyota",
            "Camry",
            2020,
            45000,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    conn.commit()
    conn.close()


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    conn = get_db()

    vehicles = conn.execute("""
        SELECT * FROM vehicles
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        vehicles=vehicles
    )


# =========================
# DIAGNOSIS PAGE
# =========================

@app.route("/diagnosis")
def diagnosis_page():

    conn = get_db()

    vehicles = conn.execute("""
        SELECT * FROM vehicles
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "diagnosis.html",
        vehicles=vehicles
    )


# =========================
# AI DIAGNOSIS API
# =========================

@app.route("/api/diagnose", methods=["POST"])
def api_diagnose():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid request data."
        }), 400

    vehicle_id = data.get("vehicle_id")
    symptoms = data.get("symptoms", "").strip()

    if not symptoms:
        return jsonify({
            "success": False,
            "message": "Please enter vehicle symptoms."
        }), 400

    # Run AI diagnosis
    result = diagnose_vehicle(symptoms)

    # Save diagnosis
    conn = get_db()

    conn.execute("""
        INSERT INTO diagnoses
        (
            vehicle_id,
            symptoms,
            diagnosis,
            severity,
            confidence,
            estimated_cost,
            recommendations,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        vehicle_id,
        symptoms,
        result["diagnosis"],
        result["severity"],
        result["confidence"],
        result["estimated_cost"],
        "\n".join(result["recommendations"]),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "result": result
    })


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    conn = get_db()

    vehicles = conn.execute("""
        SELECT * FROM vehicles
        ORDER BY id DESC
    """).fetchall()

    diagnoses = conn.execute("""
        SELECT
            diagnoses.*,
            vehicles.name AS vehicle_name
        FROM diagnoses
        LEFT JOIN vehicles
        ON diagnoses.vehicle_id = vehicles.id
        ORDER BY diagnoses.id DESC
    """).fetchall()

    reminders = conn.execute("""
        SELECT
            reminders.*,
            vehicles.name AS vehicle_name
        FROM reminders
        LEFT JOIN vehicles
        ON reminders.vehicle_id = vehicles.id
        ORDER BY reminders.due_date ASC
    """).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        vehicles=vehicles,
        diagnoses=diagnoses,
        reminders=reminders
    )


# =========================
# ADD VEHICLE
# =========================

@app.route("/add_vehicle", methods=["POST"])
def add_vehicle():

    name = request.form.get("name", "").strip()
    brand = request.form.get("brand", "").strip()
    model = request.form.get("model", "").strip()
    year = request.form.get("year", "")
    mileage = request.form.get("mileage", "")

    if not name:
        return redirect(url_for("home"))

    conn = get_db()

    conn.execute("""
        INSERT INTO vehicles
        (
            name,
            brand,
            model,
            year,
            mileage,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        brand,
        model,
        int(year) if year else None,
        int(mileage) if mileage else None,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# =========================
# ADD SERVICE REMINDER
# =========================

@app.route("/add_reminder", methods=["POST"])
def add_reminder():

    vehicle_id = request.form.get("vehicle_id")
    title = request.form.get("title", "").strip()
    due_date = request.form.get("due_date")

    if not vehicle_id or not title:
        return redirect(url_for("dashboard"))

    conn = get_db()

    conn.execute("""
        INSERT INTO reminders
        (
            vehicle_id,
            title,
            due_date,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        vehicle_id,
        title,
        due_date,
        "Pending",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# =========================
# COMPLETE REMINDER
# =========================

@app.route("/complete_reminder/<int:reminder_id>")
def complete_reminder(reminder_id):

    conn = get_db()

    conn.execute("""
        UPDATE reminders
        SET status = ?
        WHERE id = ?
    """, (
        "Completed",
        reminder_id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# =========================
# VEHICLE HEALTH API
# =========================

@app.route("/api/vehicle-health")
def vehicle_health():

    vehicle_id = request.args.get("vehicle_id")

    if not vehicle_id:
        return jsonify({
            "success": False,
            "message": "Vehicle ID is required."
        }), 400

    conn = get_db()

    vehicle = conn.execute("""
        SELECT * FROM vehicles
        WHERE id = ?
    """, (vehicle_id,)).fetchone()

    if not vehicle:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Vehicle not found."
        }), 404

    diagnosis_count = conn.execute("""
        SELECT COUNT(*)
        FROM diagnoses
        WHERE vehicle_id = ?
    """, (vehicle_id,)).fetchone()[0]

    completed_reminders = conn.execute("""
        SELECT COUNT(*)
        FROM reminders
        WHERE vehicle_id = ?
        AND status = 'Completed'
    """, (vehicle_id,)).fetchone()[0]

    pending_reminders = conn.execute("""
        SELECT COUNT(*)
        FROM reminders
        WHERE vehicle_id = ?
        AND status = 'Pending'
    """, (vehicle_id,)).fetchone()[0]

    conn.close()

    # Basic health score
    health_score = 100

    health_score -= diagnosis_count * 5
    health_score += completed_reminders * 2
    health_score -= pending_reminders * 3

    health_score = max(0, min(100, health_score))

    if health_score >= 80:
        condition = "Excellent"
    elif health_score >= 60:
        condition = "Good"
    elif health_score >= 40:
        condition = "Needs Attention"
    else:
        condition = "Critical"

    return jsonify({
        "success": True,
        "vehicle": dict(vehicle),
        "health_score": health_score,
        "condition": condition,
        "diagnosis_count": diagnosis_count,
        "completed_reminders": completed_reminders,
        "pending_reminders": pending_reminders
    })


# =========================
# ERROR HANDLERS
# =========================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "base.html"
    ), 404


@app.errorhandler(500)
def internal_server_error(error):

    return jsonify({
        "success": False,
        "message": "Internal server error."
    }), 500


# =========================
# APPLICATION START
# =========================
# =========================
# AI AUT0CARE CHATBOT
# =========================

@app.route("/api/chat", methods=["POST"])
def ai_chat():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400

    message = data.get("message", "").strip().lower()

    if not message:
        return jsonify({
            "success": False,
            "message": "Please enter a message."
        }), 400

    response = (
        "I can help you with vehicle diagnosis, maintenance, "
        "engine problems, brakes, battery, AC, tyres and service advice."
    )

    if any(word in message for word in [
        "hello", "hi", "hey"
    ]):
        response = (
            "Hello! I am AutoCare-AI. "
            "Tell me about your vehicle problem and I will help you "
            "identify possible causes and maintenance steps."
        )

    elif any(word in message for word in [
        "battery",
        "not starting",
        "not start"
    ]):
        response = (
            "Your vehicle may have a weak or discharged battery. "
            "Check the battery terminals, battery voltage and alternator. "
            "If the battery is old or damaged, replacement may be required."
        )

    elif any(word in message for word in [
        "overheat",
        "overheating",
        "temperature"
    ]):
        response = (
            "Engine overheating can be caused by low coolant, "
            "radiator problems, a cooling fan failure or thermostat issues. "
            "Stop driving if the temperature is extremely high and allow "
            "the engine to cool before inspection."
        )

    elif any(word in message for word in [
        "brake",
        "brakes"
    ]):
        response = (
            "Brake problems should be taken seriously. "
            "Check brake pads, brake fluid and brake discs. "
            "If braking performance is reduced, avoid driving and "
            "get the vehicle inspected immediately."
        )

    elif any(word in message for word in [
        "ac",
        "air conditioner",
        "air conditioning"
    ]):
        response = (
            "If your AC is not cooling, possible causes include "
            "low refrigerant, a dirty cabin filter, compressor problems "
            "or refrigerant leakage."
        )

    elif any(word in message for word in [
        "mileage",
        "fuel",
        "petrol",
        "diesel"
    ]):
        response = (
            "Poor mileage can be caused by low tyre pressure, "
            "dirty air filters, worn spark plugs, fuel-system problems "
            "or aggressive driving. Regular servicing can improve efficiency."
        )

    elif any(word in message for word in [
        "oil",
        "engine oil"
    ]):
        response = (
            "Check your engine oil level regularly. "
            "Low or degraded engine oil can increase engine wear. "
            "Use the manufacturer-recommended oil grade and service interval."
        )

    elif any(word in message for word in [
        "tyre",
        "tire",
        "wheel"
    ]):
        response = (
            "Check tyre pressure, tread depth and uneven tyre wear. "
            "Wheel alignment and balancing should also be checked "
            "if the vehicle pulls to one side or vibrates while driving."
        )

    elif any(word in message for word in [
        "service",
        "maintenance"
    ]):
        response = (
            "Regular vehicle maintenance should include engine oil, "
            "filters, brakes, tyres, battery, coolant and fluid inspections. "
            "Follow the service schedule recommended by your vehicle manufacturer."
        )

    return jsonify({
        "success": True,
        "response": response
    })
    # =========================
# VEHICLE IMAGE INSPECTION
# =========================

@app.route("/api/image-inspection", methods=["POST"])
def image_inspection():

    if "image" not in request.files:
        return jsonify({
            "success": False,
            "message": "Please upload a vehicle image."
        }), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({
            "success": False,
            "message": "No image selected."
        }), 400

    allowed_extensions = {
        "jpg",
        "jpeg",
        "png",
        "webp"
    }

    extension = image.filename.rsplit(".", 1)[-1].lower()

    if extension not in allowed_extensions:
        return jsonify({
            "success": False,
            "message": "Only JPG, JPEG, PNG and WEBP images are supported."
        }), 400

    filename = secure_filename(image.filename)

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    image.save(file_path)

    try:
        with Image.open(file_path) as img:
            width, height = img.size

    except Exception:
        return jsonify({
            "success": False,
            "message": "Invalid image file."
        }), 400

    # Demo visual inspection engine
    # A real computer vision model can be connected later.

    result = {
        "condition": "Image received successfully",
        "severity": "Inspection Required",
        "confidence": 75,
        "observations": [
            "Vehicle image was successfully processed.",
            f"Image resolution: {width} x {height}",
            "A detailed physical inspection is recommended."
        ],
        "recommendations": [
            "Check visible body damage.",
            "Inspect tyres, lights and external components.",
            "For mechanical issues, perform an OBD diagnostic scan.",
            "Consult a qualified mechanic for confirmation."
        ],
        "estimated_cost": "₹500 - ₹10,000"
    }

    return jsonify({
        "success": True,
        "image": "/" + file_path.replace("\\", "/"),
        "result": result
    })
    # =========================
# IMAGE INSPECTION PAGE
# =========================

@app.route("/image-inspection")
def image_inspection_page():
    return render_template("image-inspection.html")
if __name__ == "__main__":   

    initialize_database()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )