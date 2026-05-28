import pandas as pd
import sqlite3
import os
from datetime import datetime

def generate_report():

    selected_date = input(
        "Enter Date (MM-DD-YYYY): "
    ).strip()

    try:

        datetime.strptime(
            selected_date,
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

    query = """
    SELECT *
    FROM attendance
    WHERE Date = ?
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(selected_date,)
    )

    conn.close()

    if df.empty:

        print(
            "\nERROR: No attendance records found."
        )

        return

    if not os.path.exists("reports"):

        os.makedirs("reports")

    file_name = (
        f"reports/BSCPE 1-6_Attendance_Report_{selected_date}.xlsx"
    )

    df.to_excel(
        file_name,
        index=False
    )

    print(
        "\nAttendance report generated successfully."
    )

    print(
        f"Saved at: {file_name}"
    )