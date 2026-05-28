import sqlite3
from datetime import datetime, timedelta

# CREATE SESSION
def create_session():

    subject_code = input(
        "Enter Subject Code: "
    ).strip()

    section_code = input(
        "Enter Section Code: "
    ).strip()

    class_date = input(
        "Enter Date (MM-DD-YYYY): "
    ).strip()

    if (
        subject_code == "" or
        section_code == "" or
        class_date == ""
    ):

        print(
            "\nERROR: All fields are required."
        )

        return

    try:

        datetime.strptime(
            class_date,
            "%m-%d-%Y"
        )

    except ValueError:

        print(
            "\nERROR: Invalid date format."
        )

        return

    conn = sqlite3.connect(
        "database/attendance.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM attendance_session
    """)

    cursor.execute("""
    INSERT INTO attendance_session
    VALUES (?, ?, ?, ?, ?)
    """, (
        subject_code,
        section_code,
        class_date,
        None,
        None
    ))

    conn.commit()
    conn.close()

    print("\nSESSION CREATED SUCCESSFULLY")

# GENERATE QR SESSION
def generate_qr_session():

    conn = sqlite3.connect(
        "database/attendance.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM attendance_session
    """)

    session = cursor.fetchone()

    if not session:

        print(
            "\nERROR: No attendance session found."
        )

        conn.close()
        return

    (
        subject_code,
        section_code,
        class_date,
        start_time,
        late_limit
    ) = session

    start_time = input(
        "Enter Start Time (HH:MM AM/PM): "
    ).strip()

    if start_time == "":

        print(
            "\nERROR: Start time is required."
        )

        conn.close()
        return

    try:

        datetime.strptime(
            start_time,
            "%I:%M %p"
        )

    except ValueError:

        print(
            "\nERROR: Invalid time format."
        )

        conn.close()
        return

    cursor.execute("""
    UPDATE attendance_session
    SET start_time = ?
    WHERE subject_code = ?
    """, (
        start_time,
        subject_code
    ))

    cursor.execute("""
    DELETE FROM qr_session
    """)

    current_time = datetime.now().strftime(
        "%m-%d-%Y %I:%M %p"
    )

    cursor.execute("""
    INSERT INTO qr_session
    VALUES (?, ?)
    """, (
        "ACTIVE",
        current_time
    ))

    conn.commit()
    conn.close()

    print("\n========== QR SESSION ==========")

    print(f"Subject Code : {subject_code}")
    print(f"Section Code : {section_code}")
    print(f"Class Date   : {class_date}")
    print(f"Start Time   : {start_time}")
    print(f"Late Limit   : 15 minutes from start time (applied during QR/Facial Recognition)")

    print("\nQR Code Session Generated.")


# MARK ATTENDANCE
def mark_attendance(student):

    conn = sqlite3.connect(
        "database/attendance.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM attendance_session
    """)

    session = cursor.fetchone()

    if not session:

        print(
            "\nERROR: No active attendance session."
        )

        conn.close()
        return
   
    (
        subject_code,
        section_code,
        class_date,
        start_time,
        late_limit
    ) = session

    current_datetime = datetime.now()

    current_date = current_datetime.strftime(
        "%m-%d-%Y"
    )

    current_time = current_datetime.strftime(
        "%I:%M %p"
    )

    start_datetime = datetime.strptime(
        f"{class_date} {start_time}",
        "%m-%d-%Y %I:%M %p"
    )

    late_limit_datetime = start_datetime + timedelta(minutes=15)

    if current_datetime > late_limit_datetime:

        status = "Late"

    else:

        status = "Present"

    cursor.execute("""
    SELECT *
    FROM attendance
    WHERE "Student Number" = ?
    AND Date = ?
    """, (
        student["Student Number"],
        current_date
    ))

    existing = cursor.fetchone()

    if existing:

        print(
            "\nERROR: Attendance already recorded."
        )

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

        print(
            f"\nAttendance marked as {status}."
        )

    conn.close()


# =========================
# MANUAL TAGGING
# =========================
def manual_tagging():

    student_number = input(
        "Enter Student Number: "
    ).strip()

    class_date = input(
        "Enter Date (MM-DD-YYYY): "
    ).strip()

    new_status = input(
        "Enter New Status: "
    ).strip().title()

    valid_status = [
        "Present",
        "Late",
        "Absent"
    ]

    if new_status not in valid_status:

        print(
            "\nERROR: Invalid status."
        )

        return

    conn = sqlite3.connect(
        "database/attendance.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE attendance
    SET Status = ?
    WHERE "Student Number" = ?
    AND Date = ?
    """, (
        new_status,
        student_number,
        class_date
    ))

    conn.commit()
    conn.close()

    print(
        "\nAttendance updated successfully."
    )


# CHANGE USERNAME
def change_admin_username():

    current_username = input(
        "Enter Current Username: "
    ).strip()

    password = input(
        "Enter Password: "
    ).strip()

    new_username = input(
        "Enter New Username: "
    ).strip()

    conn = sqlite3.connect(
        "database/attendance.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM admins
    WHERE username = ?
    AND password = ?
    """, (
        current_username,
        password
    ))

    admin = cursor.fetchone()

    if admin:

        cursor.execute("""
        UPDATE admins
        SET username = ?
        WHERE username = ?
        """, (
            new_username,
            current_username
        ))

        conn.commit()

        print(
            "\nUsername changed successfully."
        )

    else:

        print(
            "\nERROR: Invalid username or password."
        )

    conn.close()


# CHANGE PASSWORD
def change_admin_password():

    username = input(
        "Enter Admin Username: "
    ).strip()

    current_password = input(
        "Enter Current Password: "
    ).strip()

    new_password = input(
        "Enter New Password: "
    ).strip()

    conn = sqlite3.connect(
        "database/attendance.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM admins
    WHERE username = ?
    AND password = ?
    """, (
        username,
        current_password
    ))

    admin = cursor.fetchone()

    if admin:

        cursor.execute("""
        UPDATE admins
        SET password = ?
        WHERE username = ?
        """, (
            new_password,
            username
        ))

        conn.commit()

        print(
            "\nPassword changed successfully."
        )

    else:

        print(
            "\nERROR: Invalid current password."
        )

    conn.close()