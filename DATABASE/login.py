import sqlite3

# STUDENT LOGIN
def student_login():

    student_number = input(
        "Enter Student Number: "
    ).strip()

    if student_number == "":

        print("Invalid input. Please enter a valid Student Number.")
        return None

    conn = sqlite3.connect(
        "database/attendance.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        "Last Name",
        "First Name",
        "Middle Name",
        "Subject Code",
        "Section Code"
    FROM students
    WHERE "Student Number" = ?
    """, (student_number,))

    student = cursor.fetchone()

    conn.close()

    if student:

        (
            last_name,
            first_name,
            middle_name,
            subject_code,
            section_code
        ) = student

        print("\nLOGIN SUCCESSFUL")

        print(
            f"Name: "
            f"{first_name} "
            f"{middle_name} "
            f"{last_name}"
        )

        print(
            f"Section: {section_code}"
        )

        return {
            "Student Number": student_number,
            "Last Name": last_name,
            "First Name": first_name,
            "Middle Name": middle_name,
            "Subject Code": subject_code,
            "Section Code": section_code
        }

    else:

        print(
            "\nERROR: Student not found."
        )

        return None

# ADMIN LOGIN
def admin_login():

    username = input(
        "Enter Admin Username: "
    ).strip()

    password = input(
        "Enter Password: "
    ).strip()

    if username == "" or password == "":

        print(
            "\nERROR: Username and Password cannot be empty."
        )

        return False

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
        password
    ))

    admin = cursor.fetchone()

    conn.close()

    if admin:

        print(
            "\nADMIN LOGIN SUCCESSFUL"
        )

        return True

    else:

        print(
            "\nERROR: Invalid admin account."
        )

        return False