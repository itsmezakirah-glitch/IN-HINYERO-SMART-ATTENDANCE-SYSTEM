import sqlite3
import os

# CREATE DATABASE FOLDER
if not os.path.exists("database"):
    os.makedirs("database")

# CONNECT DATABASE
conn = sqlite3.connect("database/attendance.db")
cursor = conn.cursor()

# STUDENTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    "Student Number" TEXT PRIMARY KEY,
    "Last Name" TEXT,
    "First Name" TEXT,
    "Middle Name" TEXT,
    "Subject Code" TEXT,
    "Section Code" TEXT
)
""")

# ADMIN TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

# DEFAULT ADMIN ACCOUNT
cursor.execute("""
INSERT OR IGNORE INTO admins
VALUES ('admin', 'admin123')
""")

# ATTENDANCE SESSION TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance_session (
    subject_code TEXT,
    section_code TEXT,
    class_date TEXT,
    start_time TEXT,
    late_limit TEXT
)
""")

# QR SESSION TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS qr_session (
    qr_status TEXT,
    created_at TEXT
)
""")

# ATTENDANCE TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    "Student Number" TEXT,
    "Last Name" TEXT,
    "First Name" TEXT,
    "Middle Name" TEXT,
    "Subject Code" TEXT,
    "Section Code" TEXT,
    "Date" TEXT,
    "Time" TEXT,
    "Status" TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully.")