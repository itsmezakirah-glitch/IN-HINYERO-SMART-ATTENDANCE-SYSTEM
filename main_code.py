# MAIN CODE - INTEGRATING FACIAL RECOGNITION, DATABASE, AND SECURITY SYSTEM
# Will serve as a Flask app

# -------------------------------------IMPORTS-------------------------------------
import sys
import os
import sqlite3
import json
import secrets
import csv
import base64
import qrcode
import pandas as pd
import numpy as np
import cv2
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from geopy.distance import geodesic
from flask import Flask, request, jsonify, send_file

sys.path.append(os.path.join(os.path.dirname(__file__), "FACIAL_RECOGNITION_APP"))
from backend import face_app, reference_embeddings, reference_names, cosine_similarity, detect_blink


# -------------------------------------Codes/Functions-------------------------------------
class BaseManager(ABC):
    @abstractmethod
    def verify(self):
        pass


class DataManagement(BaseManager):

    def __init__(self):                             
        self.__db_path  = "DATABASE/database/attendance.db"
        self.__csv_path = "DATABASE/BSCPE-1-6.csv"
        os.makedirs("DATABASE/database", exist_ok=True)
        self.setup()

    def verify(self):                                
        pass

    def parse_name(self, full_name):                
        per_parts = full_name.strip().upper().split()  

        if len(per_parts) < 3:
            return None

        last_name      = per_parts[-1]
        middle_initial = per_parts[-2].strip(".")
        first_name     = " ".join(per_parts[:-2])

        return first_name, middle_initial, last_name

    def setup(self):
        conn   = sqlite3.connect(self.__db_path)
        cursor = conn.cursor()

        # STUDENTS TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            "Student Number" TEXT PRIMARY KEY,
            "Last Name"      TEXT,
            "First Name"     TEXT,
            "Middle Name"    TEXT,
            "Subject Code"   TEXT,
            "Section Code"   TEXT
        )
        """)

        # ATTENDANCE TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            "Student Number" TEXT,
            "Last Name"      TEXT,
            "First Name"     TEXT,
            "Middle Name"    TEXT,
            "Subject Code"   TEXT,
            "Section Code"   TEXT,
            "Date"           TEXT,
            "Time"           TEXT,
            "Status"         TEXT
        )
        """)

        # ADMINS TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            "Student Number" TEXT PRIMARY KEY,
            "Last Name"      TEXT,
            "First Name"     TEXT,
            "Middle Name"    TEXT
        )
        """)

        cursor.execute("SELECT COUNT(*) FROM students")
        if cursor.fetchone()[0] == 0:
            with open(self.__csv_path, newline='', encoding='utf-8') as f:  
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute("""
                    INSERT OR IGNORE INTO students
                    ("Student Number", "Last Name", "First Name", "Middle Name", "Subject Code", "Section Code")
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        row["Student Number"].strip(),
                        row["Last Name"].strip(),
                        row["First Name"].strip(),
                        row["Middle Name"].strip(),
                        row["Subject Code"].strip(),
                        row["Section Code"].strip()
                    ))

        cursor.execute("SELECT COUNT(*) FROM admins")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
            INSERT INTO admins ("Student Number", "Last Name", "First Name", "Middle Name")
            VALUES (?, ?, ?, ?)
            """, [
                ("2025-17202-MN-0", "LAS MARIAS", "BRIAN JOSH",  "MAGTANUM"),
                ("2025-02554-MN-0", "ALMONIA",    "ANIKA JODEL", "RENOLAYAN")
            ])

        conn.commit()
        conn.close()
        print("[INFO] Database ready.")

    def student_login(self, student_number, full_name):  
        if not student_number or not full_name:
            return None, "Student number and full name required."

        parsed = self.parse_name(full_name)
        if not parsed:
            return None, "Invalid name format."

        first_name, middle_initial, last_name = parsed

        conn   = sqlite3.connect(self.__db_path)        
        cursor = conn.cursor()
        cursor.execute("""
        SELECT
            "Last Name",
            "First Name",
            "Middle Name",
            "Subject Code",
            "Section Code"
        FROM students
        WHERE "Student Number"            = ?
        AND   "First Name"                = ?
        AND   "Last Name"                 = ?
        AND   SUBSTR("Middle Name", 1, 1) = ?
        """, (student_number, first_name, last_name, middle_initial))

        student = cursor.fetchone()
        conn.close()

        if student:
            last_name, first_name, middle_name, subject_code, section_code = student
            return {
                "Student Number": student_number,
                "Last Name":      last_name,
                "First Name":     first_name,
                "Middle Name":    middle_name,
                "Subject Code":   subject_code,
                "Section Code":   section_code
            }, None

        return None, "Student not found."

    def admin_login(self, student_number):              
        if not student_number:
            return False

        conn   = sqlite3.connect(self.__db_path)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM admins
        WHERE "Student Number" = ?
        """, (student_number,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def mark_attendance(self, student, cutoff_time=None):
        conn   = sqlite3.connect(self.__db_path)        
        cursor = conn.cursor()

        current_datetime = datetime.now()
        current_date     = current_datetime.strftime("%m-%d-%Y")
        current_time     = current_datetime.strftime("%I:%M %p")

        # DETERMINE STATUS
        status = "Present"
        if cutoff_time:
            now    = datetime.now().strftime("%H:%M")
            status = "Late" if now > cutoff_time else "Present"

        cursor.execute("""
        SELECT *
        FROM attendance
        WHERE "Student Number" = ?
        AND Date = ?
        """, (student["Student Number"], current_date))

        existing = cursor.fetchone()

        if existing:
            conn.close()
            return False, "Attendance already recorded."

        else:
            cursor.execute("""
            INSERT INTO attendance
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student["Student Number"],
                student["Last Name"],
                student["First Name"],
                student["Middle Name"],
                student["Subject Code"],
                student["Section Code"],
                current_date,
                current_time,
                status
            ))

            conn.commit()
            conn.close()
            return True, f"Attendance marked as {status}."

    def generate_report(self, selected_date=None):      
        if selected_date:
            try:
                datetime.strptime(selected_date, "%m-%d-%Y")
            except ValueError:
                return None, "Invalid date format."

        conn = sqlite3.connect(self.__db_path)          

        if selected_date:
            df = pd.read_sql_query(
                "SELECT * FROM attendance WHERE Date = ?",
                conn,
                params=(selected_date,)
            )
        else:
            df = pd.read_sql_query("SELECT * FROM attendance", conn)

        conn.close()

        if df.empty:
            return None, "No attendance records found."

        os.makedirs("reports", exist_ok=True)

        file_name = f"reports/BSCPE 1-6_Attendance_Report_{selected_date or 'all'}.xlsx"

        df.to_excel(file_name, index=False)

        return file_name, None


class Facial_Recognition(BaseManager):

    def __init__(self):
        self.__face_app             = face_app
        self.__reference_embeddings = reference_embeddings
        self.__reference_names      = reference_names

    def verify(self, image_b64):                        
        try:
            image_bytes = base64.b64decode(image_b64)
            np_arr      = np.frombuffer(image_bytes, np.uint8)
            frame       = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        except Exception as e:
            return None, f"Could not decode image: {e}"

        faces = self.__face_app.get(frame)
        if not faces:
            return None, "No face detected."

        if not self.__reference_embeddings:
            return None, "No reference faces loaded."

        for face in faces:
            embedding    = face.embedding
            similarities = [cosine_similarity(embedding, ref) for ref in self.__reference_embeddings]
            best_idx     = int(np.argmax(similarities))
            best_score   = similarities[best_idx]

            if best_score >= 0.5:                       
                return self.__reference_names[best_idx], round(best_score, 4)

        return None, "Face not recognized."

    def detect_blink(self, image_b64):                  
        try:
            image_bytes = base64.b64decode(image_b64)
            np_arr      = np.frombuffer(image_bytes, np.uint8)
            frame       = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        except Exception:
            return False

        return detect_blink(frame)


class Security_checker(BaseManager):

    def __init__(self):
        self.__allowed_location = (14.599010080486975, 121.00538519569768)
        self.__radius           = 50
        self.__qr_database      = "qr_database.json"   

    def verify(self):
        pass

    def check_location(self, lat, lon):                 
        user_location = (lat, lon)
        distance      = geodesic(self.__allowed_location, user_location).meters
        allowed       = distance <= self.__radius
        return allowed, round(distance, 2)

    def generate_qr_code(self, token, base_url="http://127.0.0.1:5000",):
        if os.path.exists(self.__qr_database):
            with open(self.__qr_database, "r") as f:
                data = json.load(f)
        else:
            data = {}

        data[token] = str(date.today())

        with open(self.__qr_database, "w") as f:
            json.dump(data, f)

        qr_data  = f"{base_url}/scan/{token}"
        img      = qrcode.make(qr_data)
        os.makedirs("qr_codes", exist_ok=True)
        filename = f"qr_codes/{token}.png"
        img.save(filename)

        return token, filename

    def validate_qr_code(self, token):                  
        if not os.path.exists(self.__qr_database):
            return False, "No QR database found."

        with open(self.__qr_database, "r") as f:
            data = json.load(f)

        if token not in data:
            return False, "Invalid QR code."

        return True, "QR code valid."



# ATTENDANCE SYSTEM — Flask App 
class AttendanceSystem:

    def __init__(self):
        self.__app      = Flask(__name__)
        self.__db       = DataManagement()
        self.__face     = Facial_Recognition()
        self.__security = Security_checker()
        self.__cutoff   = None
        self.__register_routes()

    def __register_routes(self):

        # Base UI Route Engine
        @self.__app.route("/", methods=["GET"])
        def render_home_portal():
            from flask import render_template
            return render_template("index.html")
        
        # Login 
        @self.__app.route("/login", methods=["POST"])
        def login():
            data           = request.get_json(silent=True)
            student_number = data.get("student_number", "").strip()
            full_name      = data.get("full_name", "").strip()

            if not student_number or not full_name:
                return jsonify({"status": "error", "message": "Student number and full name required."}), 400

            student, error = self.__db.student_login(student_number, full_name)
            if not student:
                return jsonify({"status": "error", "message": error}), 404

            is_admin = self.__db.admin_login(student_number)

            return jsonify({
                "status":   "success",
                "is_admin": is_admin,
                "student":  student,
                "requires_face_scan": True  # both admin and student need face scan
            })

        # Location Check 
        @self.__app.route("/check-location", methods=["POST"])
        def check_location():
            data = request.get_json(silent=True)
            lat  = data.get("latitude")
            lon  = data.get("longitude")

            if lat is None or lon is None:
                return jsonify({"status": "error", "message": "Latitude and longitude required."}), 400

            allowed, distance = self.__security.check_location(lat, lon)

            return jsonify({
                "status":   "allowed" if allowed else "denied",
                "distance": distance,
                "message":  "Access granted." if allowed else "You are not inside CEA building."
            })

        # Validate QR
        @self.__app.route("/scan/<token>", methods=["GET"])
        def scan_qr(token):
            valid, message = self.__security.validate_qr_code(token)
            return jsonify({
                "status":  "valid" if valid else "invalid",
                "message": message
            })

        # Face Verify
        @self.__app.route("/verify-face", methods=["POST"])
        def verify_face():
            data           = request.get_json(silent=True)
            image_b64      = data.get("image")
            is_blink_check = data.get("blink_check", False)
            student_number = data.get("student_number")

            if not image_b64:
                return jsonify({"status": "error", "message": "Missing image."}), 400

            if is_blink_check:
                blinked = self.__face.detect_blink(image_b64)
                return jsonify({"blinked": blinked})

            recognized_id, result = self.__face.verify(image_b64)

            if not recognized_id:
                return jsonify({"status": "unverified", "message": result})

            if recognized_id != student_number:
                return jsonify({"status": "unverified", "message": "Face does not match Student Number."})

            return jsonify({"status": "verified", "confidence": result})

        # Mark Attendance 
        @self.__app.route("/mark-attendance", methods=["POST"])
        def mark_attendance():
            data    = request.get_json(silent=True)
            student = data.get("student")

            if not student:
                return jsonify({"status": "error", "message": "Missing student data."}), 400

            success, message = self.__db.mark_attendance(student, self.__cutoff)
            return jsonify({
                "status":  "success" if success else "error",
                "message": message
            })

        # Generate QR (admin only) 
        @self.__app.route("/generate-qr", methods=["POST"])
        def generate_qr():
            data           = request.get_json(silent=True)
            student_number = data.get("student_number")

            if not self.__db.admin_login(student_number):
                return jsonify({"status": "error", "message": "Unauthorized."}), 403

            token, filename = self.__security.generate_qr_code()
            return jsonify({
                "status":  "success",
                "token":   token,
                "file":    filename
            })

        # Set Cutoff Time (admin only) 
        @self.__app.route("/set-cutoff", methods=["POST"])
        def set_cutoff():
            data           = request.get_json(silent=True)
            student_number = data.get("student_number")
            cutoff         = data.get("cutoff_time")  # format: "HH:MM"

            if not self.__db.admin_login(student_number):
                return jsonify({"status": "error", "message": "Unauthorized."}), 403

            self.__cutoff = cutoff
            return jsonify({
                "status":  "success",
                "message": f"Cutoff time set to {cutoff}."
            })

        # Generate Report (admin only) 
        @self.__app.route("/report", methods=["POST"])
        def generate_report():
            data           = request.get_json(silent=True)
            student_number = data.get("student_number")
            selected_date  = data.get("date")  # optional, format: "MM-DD-YYYY"

            if not self.__db.admin_login(student_number):
                return jsonify({"status": "error", "message": "Unauthorized."}), 403

            file_name, error = self.__db.generate_report(selected_date)

            if error:
                return jsonify({"status": "error", "message": error}), 404

            return send_file(file_name, as_attachment=True)

    def run(self):
        self.__app.run(debug=True, host="0.0.0.0", port=5000)



if __name__ == "__main__":
    system = AttendanceSystem()
    system.run()